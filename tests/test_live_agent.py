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
import sqlite3
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
        namespace="ghost.livetest",
        scope="thread",
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
    with SeamMemory(settings, allow_pgvector_env=False) as memory:
        turn = memory.begin_turn("what is the project codeword?")
        assert turn.rendered_memory, "recall returned nothing for a stored fact"
        assert turn.evidence_refs, "recall cited no evidence records"
        payloads = [json.loads(line) for line in turn.rendered_memory.splitlines()]

    assert any(token in p["memory"] for p in payloads), (
        "the codeword is not in recalled memory, so the answer came from "
        "conversation context rather than from SEAM"
    )

    # And the cited record id must resolve on disk -- the check that catches a
    # fabricated citation, which is exactly what a memory system must not do.
    cited = [p["record_id"] for p in payloads if token in p["memory"]]
    connection = sqlite3.connect(db)
    try:
        found = [
            cited_id
            for cited_id in cited
            if connection.execute(
                "select 1 from ir_records where id = ?", (cited_id,)
            ).fetchone()
        ]
    finally:
        connection.close()
    assert found, f"recalled record ids do not exist in ir_records: {cited}"


def test_a_completed_turn_leaves_no_open_reasoning_run(tmp_path_factory) -> None:
    """Failure finalization's counterpart: success must close the run too."""
    db = tmp_path_factory.mktemp("live") / "ghost.db"
    with GhostAgent(_settings(db)) as ghost:
        ghost.invoke("Reply with exactly the word: done")

    connection = sqlite3.connect(db)
    try:
        rows = connection.execute(
            """
            select s.status, count(*)
            from reasoning_node n
            join reasoning_state s on s.node_id = n.node_id
            where n.kind = 'outcome'
            group by s.status
            """
        ).fetchall()
    finally:
        connection.close()
    statuses = dict(rows)
    assert statuses.get("accepted"), f"no accepted outcome was recorded: {statuses}"
    assert not statuses.get("rejected"), (
        f"a successful turn recorded a rejected outcome: {statuses}"
    )


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


def test_a_different_thread_does_not_see_the_conversation(tmp_path_factory) -> None:
    """Resumption must not leak across threads -- otherwise `--thread-id` is
    decorative in the other direction."""
    root = tmp_path_factory.mktemp("live")
    settings = _settings(root / "ghost.db")

    with GhostAgent(settings) as first:
        first.invoke(
            "Remember for this conversation only: the passphrase is bluebird. "
            "Acknowledge with 'ok'.",
            thread_id="thread-a",
        )

    with GhostAgent(settings) as second:
        answer = second.invoke(
            "Without guessing, what passphrase did I give you earlier in THIS "
            "conversation? If none, say 'none'.",
            thread_id="thread-b",
        )

    assert "bluebird" not in answer.lower(), (
        f"thread-b saw thread-a's conversation history. Answer: {answer[:300]}"
    )
