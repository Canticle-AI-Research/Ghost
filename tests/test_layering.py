"""The three-layer split, asserted rather than described.

    SEAM SDK          durable memory (no LLM framework dependency at all)
    ghost.lifecycle   what a turn is, and what it owes SEAM
    ghost.application LangChain / DeepAgents / model wiring

The value of the split is that the rules a memory-backed turn must obey --
recall before write, ingest only what completed, close the run on every path
out -- are properties of SEAM's contract rather than of any harness. If they
leak into the adapter, swapping the harness silently drops them; if the adapter
leaks into the lifecycle, the harness stops being swappable.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src" / "ghost"
FRAMEWORKS = ("langchain", "langgraph", "deepagents")


def _imported_frameworks(path: Path) -> list[str]:
    """Frameworks a module actually IMPORTS.

    Parsed rather than grepped: every one of these files names LangChain and
    DeepAgents in its prose, because the prose is about the boundary between
    them. A text search would flag the documentation as a violation.
    """

    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    # `langchain_core` and `langchain_openai` are LangChain too. Matching only
    # on a trailing dot missed them, which let tools.py -- which imports
    # langchain_core.tools -- report as framework-free.
    return sorted(
        {
            f
            for f in FRAMEWORKS
            for m in modules
            if m == f or m.startswith(f"{f}.") or m.startswith(f"{f}_")
        }
    )


@pytest.mark.parametrize("module", ["lifecycle.py", "seam_memory.py", "config.py", "context.py"])
def test_lower_layers_import_no_agent_framework(module: str) -> None:
    """Layers 1 and 2 must stay framework-free."""
    found = _imported_frameworks(SRC / module)
    assert not found, (
        f"{module} references {found}. It belongs to a layer that must run "
        "unchanged under a different agent harness."
    )


def test_the_turn_rules_live_in_the_lifecycle_not_the_adapter() -> None:
    """The specific rules worth protecting, checked by name.

    `application.py` may build the graph and pick the model; it must not own
    when SEAM is written, because that is the part a harness swap would lose.
    """
    lifecycle = (SRC / "lifecycle.py").read_text(encoding="utf-8")
    adapter = (SRC / "application.py").read_text(encoding="utf-8")

    for rule in ("begin_turn", "complete_turn", "fail_turn"):
        assert rule in lifecycle, f"{rule} is not in the lifecycle layer"
        assert rule not in adapter, (
            f"{rule} is called from application.py; the turn contract has "
            "leaked into the framework adapter"
        )


def test_the_adapter_is_the_only_place_frameworks_appear() -> None:
    """Everything framework-shaped should be confined to two files."""
    offenders = {}
    for path in sorted(SRC.glob("*.py")):
        hits = _imported_frameworks(path)
        if hits:
            offenders[path.name] = hits
    assert set(offenders) <= {"application.py", "middleware.py", "tools.py"}, (
        f"agent-framework references escaped the adapter layer: {offenders}"
    )


def test_lifecycle_can_drive_a_graph_that_is_not_langchain() -> None:
    """The claim the split exists to support, demonstrated.

    A plain object satisfying `AgentGraph` runs a full turn with no LangChain
    involved anywhere -- which is what makes the harness replaceable.
    """
    from ghost.lifecycle import run_turn
    from ghost.seam_memory import SeamTurn

    calls: list[str] = []

    class NotLangChain:
        def invoke(self, input, *, context, config):
            calls.append("invoked")
            assert config == {"configurable": {"thread_id": "t-1"}}
            return {"messages": [type("M", (), {"content": "answered"})()]}

    class Memory:
        def begin_turn(self, user_input):
            calls.append("begin")
            return SeamTurn("run-1", "", ())

        def complete_turn(self, turn, **kwargs):
            calls.append("complete")
            return ()

        def fail_turn(self, turn, **kwargs):
            calls.append("fail")

        def close(self):
            pass

    answer = run_turn(
        memory=Memory(), graph=NotLangChain(), user_input="hi", thread_id="t-1"
    )
    assert answer == "answered"
    assert calls == ["begin", "invoked", "complete"], (
        "recall must happen before the turn is written, so an answer cannot "
        f"cite the memory it creates; got {calls}"
    )


MODULE_LINE_CEILING = 450


def test_no_module_grows_into_a_god_file() -> None:
    """Cap module size so responsibilities split before they fuse.

    A module that accumulates every concern cannot be reviewed, tested in
    isolation, or replaced. This is a ratchet, not a style preference: the
    ceiling exists to force the split at the point where it is still cheap.
    """
    oversized = []
    roots = [SRC, SRC.parents[1] / "tools"]
    for root in roots:
        for module in sorted(root.rglob("*.py")):
            if "__pycache__" in module.parts:
                continue
            lines = len(module.read_text(encoding="utf-8").splitlines())
            if lines > MODULE_LINE_CEILING:
                oversized.append(f"{module.name}: {lines} lines")
    assert not oversized, (
        f"modules over {MODULE_LINE_CEILING} lines; split them rather than raising "
        f"the ceiling: {oversized}"
    )
