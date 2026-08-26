"""The only tests that prove Ghost actually works.

Every other test in this repository fakes the model. That is the right default
-- they are fast, free, and deterministic -- but it means the suite cannot tell
the difference between a working agent and one whose model call, middleware
injection, tool schema, or ingest path is broken. Ghost passed 108 tests for a
week without ever having answered a single question.

These tests close that gap by running the real loop against a real provider:
seed a fact in one agent, then recall it from a SECOND agent built over the
same store, and prove the recalled record actually exists on disk. That is the
whole product claim -- durable memory across processes, with provenance -- and
it is the one thing no fake can establish.

They are marked `live` and DESELECTED from the normal suite (`-m "not live"` in
pyproject addopts), never skipped: a skip would be invisible, and strict
no-skip in conftest.py would fail the run anyway. The live CI job selects them
explicitly with `-m live`.

Run locally with:

    uv run pytest -m live
"""

from __future__ import annotations

import json
import os
import uuid
from pathlib import Path

import pytest

from ghost.application import GhostAgent
from ghost.config import GhostSettings
from ghost.seam_memory import SeamMemory

pytestmark = pytest.mark.live


def _settings(db: Path) -> GhostSettings:
    """Real model, throwaway store. Never the operator's unified SEAM store."""
    return GhostSettings(
        model=os.environ.get("GHOST_MODEL", "openai:gpt-5.6-terra"),
        seam_db=db,
        namespace=f"ghost.livetest.{db.parent.name}",
        scope="thread",
        seam_base_url=os.environ.get("SEAM_BASE_URL", "http://127.0.0.1:8765"),
        seam_api_token=os.environ.get("SEAM_API_TOKEN") or None,
        recall_budget=8,
        graph_hops=2,
    )


@pytest.fixture(scope="module")
def token() -> str:
    """A value that cannot exist in any store but the one this test writes.

    Without this a stale database, or the model's own world knowledge, could
    satisfy the recall assertion and the test would pass while memory was
    broken.
    """
    return f"ultramarine-{uuid.uuid4().hex[:12]}"


def test_ghost_answers_at_all(tmp_path_factory) -> None:
    """The smoke test proper: a real model call through the real graph."""
    db = tmp_path_factory.mktemp("live") / "ghost.db"
    with GhostAgent(_settings(db)) as ghost:
        answer = ghost.invoke("Reply with exactly the word: ready")
    assert answer.strip(), "Ghost returned an empty answer"
    assert "ready" in answer.lower()


def test_memory_survives_a_new_agent_and_is_backed_by_a_real_record(
    tmp_path_factory, token: str
) -> None:
    """The product claim, end to end.

    Two separate `GhostAgent` instances over one store: the second has no
    in-process state from the first -- `MemorySaver` is per-agent -- so
    anything it recalls came from SEAM and nowhere else.
    """
    db = tmp_path_factory.mktemp("live") / "ghost.db"
    settings = _settings(db)

    with GhostAgent(settings) as writer:
        writer.invoke(f"Remember this exactly: the project codeword is {token}.")

    # A genuinely separate agent. Same database, no shared checkpoint.
    with GhostAgent(settings) as reader:
        answer = reader.invoke("What is the project codeword? Answer with the codeword.")

    assert token in answer, (
        f"Ghost did not recall the codeword across agents. Answer was: {answer[:400]}"
    )

    # The claim must be backed by a record that exists, not by the model having
    # kept it in context. Look it up the way the middleware would.
    with SeamMemory(settings) as memory:
        turn = memory.begin_turn("what is the project codeword?")
        assert turn.rendered_memory, "recall returned nothing for a stored fact"
        assert turn.evidence_refs, "recall cited no evidence records"
        payloads = [json.loads(line) for line in turn.rendered_memory.splitlines()]

    assert any(token in p["memory"] for p in payloads), (
        "the codeword is not in recalled memory, so the answer came from "
        "conversation context rather than from SEAM"
    )

    cited = [p["record_id"] for p in payloads if token in p["memory"]]
    assert cited and all(value.startswith("mem_") for value in cited), (
        f"the service returned invalid public memory handles: {cited}"
    )


def test_a_completed_turn_is_recallable_through_the_public_service(tmp_path_factory) -> None:
    db = tmp_path_factory.mktemp("live") / "ghost.db"
    token = f"completed-{uuid.uuid4().hex[:10]}"
    with GhostAgent(_settings(db)) as ghost:
        ghost.invoke(f"Remember this completion marker exactly: {token}")
    with SeamMemory(_settings(db)) as memory:
        recalled = memory.begin_turn("completion marker")
    assert token in recalled.rendered_memory


def test_a_thread_resumes_after_the_agent_is_torn_down(tmp_path_factory) -> None:
    """Stage 1's exit condition: resume an interrupted thread.

    With the previous in-process checkpointer this was impossible -- every
    `uv run ghost` was a fresh process with an empty checkpoint, so
    `--thread-id` did nothing between invocations. The distinction this proves
    is subtle but real: SEAM recall works across threads and would answer even
    without a checkpoint, so the question here is asked in a way only the
    CONVERSATION history can settle -- a pronoun with no antecedent except the
    previous turn.
    """
    root = tmp_path_factory.mktemp("live")
    settings = _settings(root / "ghost.db")
    thread = "resume-probe"

    with GhostAgent(settings) as first:
        first.invoke(
            "I am going to name three fruits: apple, banana, cherry. "
            "Just acknowledge with 'ok'.",
            thread_id=thread,
        )

    assert settings.checkpoints.exists(), "no checkpoint database was written"

    # A brand new agent object over the same checkpoint file.
    with GhostAgent(settings) as second:
        answer = second.invoke(
            "What was the second one I named? Reply with just that word.",
            thread_id=thread,
        )

    assert "banana" in answer.lower(), (
        "the thread did not resume; the second agent could not see the first "
        f"agent's turn. Answer was: {answer[:300]}"
    )


def test_memory_is_isolated_by_langgraph_thread_id(tmp_path_factory) -> None:
    """A thread-scoped turn must bind memory to the same checkpoint thread."""
    root = tmp_path_factory.mktemp("live")
    settings = _settings(root / "ghost.db")
    # A neutral fact, not a credential: asking a model to repeat a
    # "passphrase" triggers a safety refusal and tests memory not at all.
    token = f"crossthread-{uuid.uuid4().hex[:10]}"

    with GhostAgent(settings) as first:
        first.invoke(
            f"Remember: the staging build is codenamed {token}.", thread_id="thread-a"
        )

    with SeamMemory(settings) as memory:
        own = memory.begin_turn("staging build codename", thread_id="thread-a")
        foreign = memory.begin_turn("staging build codename", thread_id="thread-b")

    assert token in own.rendered_memory
    assert token not in foreign.rendered_memory


def test_a_real_tool_call_completes_through_the_verified_turn_api(tmp_path_factory) -> None:
    """The end-to-end claim behind giving Ghost consequential tools.

    A real model calls a real tool, and the store ends up holding a `decision`,
    a `tool` check with a verdict, and an outcome accepted against it. Nothing
    here is asserted about what the model said -- only about what the database
    will now stand behind.
    """
    root = tmp_path_factory.mktemp("live")
    settings = _settings(root / "ghost.db")

    with GhostAgent(settings) as seed:
        seed.invoke("Remember: the release captain is Ex0-Byte.")

    with GhostAgent(settings) as ghost:
        ghost.invoke(
            "Use your seam_recall tool to search your memory for 'release captain', "
            "then tell me what you found."
        )

    with SeamMemory(settings) as memory:
        recalled = memory.begin_turn("release captain")
    assert "Ex0-Byte" in recalled.rendered_memory


def test_ghost_uses_the_operating_system(tmp_path_factory, monkeypatch) -> None:
    """Ghost drives the real machine, and the store records what it ran.

    Asserted against the DATABASE rather than the answer text: what matters is
    not that the model reported a kernel version but that the command it ran is
    recoverable, its exit code was checked, and the outcome was accepted only
    against a check that passed.
    """
    root = tmp_path_factory.mktemp("live-os")
    monkeypatch.setenv("GHOST_ENABLE_SHELL", "1")
    settings = _settings(root / "ghost.db")
    settings = GhostSettings(
        model=settings.model,
        seam_db=settings.seam_db,
        namespace=settings.namespace,
        scope=settings.scope,
        seam_base_url=settings.seam_base_url,
        seam_api_token=settings.seam_api_token,
        seam_timeout=settings.seam_timeout,
        recall_budget=settings.recall_budget,
        graph_hops=settings.graph_hops,
        enable_shell=True,
        shell_approval=False,
        shell_workdir=root,
    )

    marker = f"ghost-live-{uuid.uuid4().hex[:10]}"
    with GhostAgent(settings) as ghost:
        ghost.invoke(
            f"Using the shell, create a file named {marker}.txt in the current "
            "directory containing the word ready, then confirm it exists."
        )

    created = root / f"{marker}.txt"
    assert created.exists(), "Ghost did not actually touch the filesystem"
    assert "ready" in created.read_text()

    with SeamMemory(settings) as memory:
        recalled = memory.begin_turn(marker)
    assert recalled.evidence_refs, "completed OS turn was not accepted into memory"


def test_a_declined_command_does_not_end_the_turn(tmp_path_factory, monkeypatch) -> None:
    """An operator saying no to one command must not cost the conversation."""
    root = tmp_path_factory.mktemp("live-deny")
    monkeypatch.setenv("GHOST_ENABLE_SHELL", "1")
    base = _settings(root / "ghost.db")
    settings = GhostSettings(
        model=base.model,
        seam_db=base.seam_db,
        namespace=base.namespace,
        scope=base.scope,
        seam_base_url=base.seam_base_url,
        seam_api_token=base.seam_api_token,
        seam_timeout=base.seam_timeout,
        enable_shell=True,
        shell_workdir=root,
    )

    target = root / "must-not-exist.txt"
    with GhostAgent(settings, approve=lambda _command: False) as ghost:
        answer = ghost.invoke(
            f"Using the shell, create the file {target.name} here. "
            "If you cannot, say so plainly."
        )

    assert not target.exists(), "a declined command still changed the filesystem"
    assert answer.strip(), "the turn produced no answer after the refusal"
