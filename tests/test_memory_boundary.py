"""ADR-0001 enforcement: DeepAgents must never own memory.

ADR-0001 items 6 and 7 say LangGraph checkpoints hold execution state, not
semantic truth, and that DeepAgents working files and stores do not replace
SEAM memory. Until now that was a sentence in a document — nothing stopped a
future edit, or a deepagents default change, from quietly standing up a second
memory system next to SEAM.

`create_deep_agent` takes `memory`, `store`, and `backend`. Any of the three
installs deepagents' own memory or filesystem middleware into the graph, at
which point Ghost has two things claiming to remember, only one of which has
provenance, MIRL compilation, or a trust boundary. These tests fail if that
ever happens.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from ghost import application
from ghost.application import GhostAgent
from ghost.config import GhostSettings


def _settings() -> GhostSettings:
    return GhostSettings(
        model="openai:test-model",
        seam_db=Path("unused.db"),
        namespace="ghost.test",
        scope="thread",
    )


class _Memory:
    def begin_turn(self, user_input, *, thread_id): ...
    def complete_turn(self, turn, **kwargs): ...
    def close(self) -> None: ...


@pytest.fixture
def captured(monkeypatch) -> dict[str, Any]:
    """Build a real GhostAgent, capturing what it hands to deepagents."""
    seen: dict[str, Any] = {}

    def fake_create(**kwargs: Any) -> object:
        seen.update(kwargs)
        return object()

    monkeypatch.setattr(application, "create_deep_agent", fake_create)
    monkeypatch.setattr(application, "_init_model", lambda settings: "model")
    GhostAgent(_settings(), memory=_Memory())
    return seen


@pytest.mark.parametrize("parameter", ["memory", "store", "backend"])
def test_ghost_never_hands_deepagents_a_memory_surface(captured, parameter) -> None:
    """The three parameters that would create a second memory system."""
    assert captured.get(parameter) is None, (
        f"GhostAgent passes `{parameter}` to create_deep_agent. That installs "
        "deepagents' own memory/filesystem middleware alongside SEAM, giving "
        "Ghost two stores that claim to remember — and only SEAM has MIRL, "
        "provenance, and a trust boundary. See ADR-0001 items 6 and 7."
    )


def test_checkpointer_is_execution_state_only(captured) -> None:
    """ADR-0001 item 6. The checkpoint is now persistent, which is the point --
    a thread must survive a restart -- so the invariant is no longer "it is in
    memory". It is that the checkpoint holds where the conversation got to and
    SEAM holds what is remembered, and that the two never share a file.
    """
    checkpointer = captured.get("checkpointer")
    assert checkpointer is not None, "the agent lost its checkpointer"
    module = type(checkpointer).__module__
    assert module.startswith("langgraph.checkpoint"), (
        f"checkpointer is {type(checkpointer).__name__} from {module}; it must "
        "remain a LangGraph checkpoint, not a memory store"
    )


def test_checkpoints_never_share_a_database_with_seam(tmp_path) -> None:
    """The new failure mode a persistent checkpoint introduces.

    An in-memory saver could not collide with the MIRL store. A SQLite one can,
    and pointing it at seam.db would put LangGraph's message history inside the
    database whose whole contract is that MIRL is canonical.
    """
    settings = GhostSettings(
        model="openai:test",
        seam_db=tmp_path / "seam.db",
        namespace="ghost.test",
        scope="thread",
    )
    assert settings.checkpoints != settings.seam_db
    assert settings.checkpoints.name != settings.seam_db.name

    explicit = GhostSettings(
        model="openai:test",
        seam_db=tmp_path / "seam.db",
        namespace="ghost.test",
        scope="thread",
        checkpoint_db=tmp_path / "seam.db",
    )
    assert explicit.checkpoints == explicit.seam_db, (
        "this assertion documents that an operator CAN still collide them by "
        "setting GHOST_CHECKPOINT_DB to the SEAM path; if that is ever "
        "rejected at startup, tighten this test to expect the rejection"
    )


def test_seam_recall_is_the_only_memory_middleware(captured) -> None:
    """Exactly one thing may put remembered text in front of the model."""
    middleware = captured.get("middleware") or []
    names = [type(m).__name__ for m in middleware]
    assert names == ["SeamRecallMiddleware"], (
        f"Ghost's middleware stack is {names}; only SeamRecallMiddleware may "
        "inject recalled memory into the prompt"
    )


def test_the_built_graph_installs_no_deepagents_memory_node() -> None:
    """The end-to-end check: build the real graph and inspect what landed.

    Catches the case the kwarg tests cannot -- a deepagents release that starts
    installing memory or filesystem middleware by DEFAULT, with no change on
    Ghost's side at all.
    """
    from deepagents import create_deep_agent

    from ghost.context import GhostTurnContext
    from ghost.middleware import SeamRecallMiddleware

    graph = create_deep_agent(
        model="anthropic:claude-opus-5",
        name="boundary-probe",
        system_prompt="probe",
        middleware=[SeamRecallMiddleware()],
        context_schema=GhostTurnContext,
    )
    nodes = " ".join(graph.get_graph().nodes)
    for forbidden in ("Memory", "Filesystem", "Store"):
        assert forbidden not in nodes, (
            f"deepagents now installs a {forbidden} middleware by default "
            f"(graph nodes: {nodes}). Ghost would have a second memory system "
            "it never asked for. Pin the deepagents version and review before "
            "upgrading -- see ADR-0001."
        )


def test_seam_adapter_imports_no_agent_framework() -> None:
    """The property that makes the framework choice reversible.

    `seam_memory.py` is the whole SEAM integration and it must stay plain
    Python. As long as it imports nothing from LangChain, LangGraph, or
    deepagents, swapping the agent harness costs `application.py` and
    `middleware.py` and nothing else -- the memory layer ports unchanged.
    """
    source = (
        Path(__file__).resolve().parents[1] / "src" / "ghost" / "seam_memory.py"
    ).read_text(encoding="utf-8")
    for framework in ("langchain", "langgraph", "deepagents"):
        assert framework not in source.lower(), (
            f"seam_memory.py now references {framework}. The SEAM adapter must "
            "stay framework-free so the agent harness remains replaceable."
        )
