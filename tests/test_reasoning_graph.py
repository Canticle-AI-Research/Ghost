"""A turn produces a checked reasoning graph, not a flat outcome.

This is the difference between Ghost and an agent that writes a log file. A log
records what the model said it did. SEAM records a `decision`, a `tool` check
with a verdict, and an outcome that the store REFUSES to accept unless those
checks passed -- so "the action succeeded" becomes a property the database
enforces rather than a claim the model makes about itself.

That enforcement is what makes write tools, and eventually operating-system
control, safe to add: an unverified action cannot commit.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from ghost.application import extract_tool_attempts
from ghost.config import GhostSettings
from ghost.lifecycle import ToolAttempt
from ghost.seam_memory import SeamMemory


def _settings(db: Path) -> GhostSettings:
    return GhostSettings(
        model="openai:test-model",
        seam_db=db,
        namespace="ghost.test",
        scope="thread",
        graph_hops=1,
    )


def _outcome_statuses(db: Path) -> dict[str, int]:
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
    return dict(rows)


# --- recording actions -----------------------------------------------------


def test_a_tool_call_becomes_a_decision_and_a_passed_check(tmp_path: Path) -> None:
    db = tmp_path / "g.db"
    with SeamMemory(_settings(db), allow_pgvector_env=False) as memory:
        turn = memory.begin_turn("read the notes")
        ids = memory.record_actions(
            turn,
            [ToolAttempt(name="read_file", request='{"path":"notes.md"}', output="hi", ok=True)],
        )
        assert len(ids) == 1

    connection = sqlite3.connect(db)
    try:
        kinds = [r[0] for r in connection.execute("select kind from reasoning_node")]
        checks = connection.execute(
            "select check_kind, check_ref, verdict from reasoning_verification"
        ).fetchall()
    finally:
        connection.close()

    assert "decision" in kinds, f"no decision node was recorded: {kinds}"
    assert checks == [("tool", "read_file", "passed")]


def test_a_failed_tool_is_recorded_but_does_not_support_the_outcome(tmp_path: Path) -> None:
    """The load-bearing asymmetry: failures are visible, not supporting."""
    db = tmp_path / "g.db"
    with SeamMemory(_settings(db), allow_pgvector_env=False) as memory:
        turn = memory.begin_turn("read a missing file")
        ids = memory.record_actions(
            turn,
            [ToolAttempt(name="read_file", request="{}", output="boom", ok=False, exit_code=1)],
        )
        assert ids == (), "a failed check was offered as outcome support"

    connection = sqlite3.connect(db)
    try:
        verdicts = [r[0] for r in connection.execute("select verdict from reasoning_verification")]
    finally:
        connection.close()
    assert verdicts == ["failed"], "the failure was dropped instead of recorded"


def test_raw_tool_output_is_never_stored(tmp_path: Path) -> None:
    """The property that makes it safe to hand SEAM shell output.

    Command output routinely carries environment, tokens, and paths. SEAM keeps
    a length and a digest so the result stays provable, and discards the text.
    """
    secret = "AKIA-not-a-real-key-000000"
    db = tmp_path / "g.db"
    with SeamMemory(_settings(db), allow_pgvector_env=False) as memory:
        turn = memory.begin_turn("run a command")
        memory.record_actions(
            turn, [ToolAttempt(name="bash", request="env", output=secret, ok=True)]
        )

    blob = Path(db).read_bytes()
    assert secret.encode() not in blob, "raw tool output was persisted into the store"

    connection = sqlite3.connect(db)
    try:
        row = connection.execute(
            "select result_length, result_sha256 from reasoning_verification"
        ).fetchone()
    finally:
        connection.close()
    assert row[0] == len(secret) and row[1], "the digest that replaces the output is missing"


def test_a_turn_with_passed_checks_finalizes_verified(tmp_path: Path) -> None:
    db = tmp_path / "g.db"
    with SeamMemory(_settings(db), allow_pgvector_env=False) as memory:
        turn = memory.begin_turn("do the thing")
        ids = memory.record_actions(
            turn, [ToolAttempt(name="read_file", request="{}", output="ok", ok=True)]
        )
        memory.complete_turn(
            turn,
            user_input="do the thing",
            assistant_output="done",
            thread_id="t",
            turn_id="1",
            verification_ids=ids,
        )
    assert _outcome_statuses(db).get("accepted"), "the verified outcome was not accepted"


def test_a_turn_whose_only_tool_failed_still_completes(tmp_path: Path) -> None:
    """A failed tool does not fail the turn -- the model may have recovered --
    but the outcome is finalized unverified rather than claiming support."""
    db = tmp_path / "g.db"
    with SeamMemory(_settings(db), allow_pgvector_env=False) as memory:
        turn = memory.begin_turn("try something")
        ids = memory.record_actions(
            turn, [ToolAttempt(name="read_file", request="{}", output="", ok=False)]
        )
        memory.complete_turn(
            turn,
            user_input="try something",
            assistant_output="I could not read that file.",
            thread_id="t",
            turn_id="1",
            verification_ids=ids,
        )
    assert _outcome_statuses(db).get("accepted"), "the turn did not complete"


def test_seam_refuses_an_outcome_verified_by_a_failed_check(tmp_path: Path) -> None:
    """Stated as a test because the whole design rests on it being enforced."""
    with SeamMemory(_settings(tmp_path / "g.db"), allow_pgvector_env=False) as memory:
        turn = memory.begin_turn("do the thing")
        run = memory._sdk.reasoning(turn.run_id)
        node = run.add_node("decision", "bash: rm -rf /")
        bad = run.verify(
            str(node["node_id"]),
            check_kind="tool",
            check_ref="bash",
            verdict="failed",
            summary="refused",
            exit_code=1,
        )
        with pytest.raises(ValueError, match="passed verifications"):
            run.finalize_verified(
                "pretend it worked", verification_ids=[str(bad["verification_id"])]
            )


# --- adapter translation ---------------------------------------------------


class _Msg:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def test_extract_pairs_requests_to_results_by_id() -> None:
    result = {
        "messages": [
            _Msg(tool_calls=[{"id": "c1", "name": "seam_recall", "args": {"query": "x"}}]),
            _Msg(tool_call_id="c1", content="a record", status="success"),
        ]
    }
    (attempt,) = extract_tool_attempts(result)
    assert attempt.name == "seam_recall" and attempt.ok
    assert "query" in attempt.request and attempt.output == "a record"


def test_extract_marks_an_errored_tool_as_failed() -> None:
    result = {
        "messages": [
            _Msg(tool_calls=[{"id": "c1", "name": "read_file", "args": {}}]),
            _Msg(tool_call_id="c1", content="ToolError: outside roots", status="error"),
        ]
    }
    (attempt,) = extract_tool_attempts(result)
    assert not attempt.ok and attempt.exit_code == 1


def test_a_request_with_no_result_is_a_failure_not_a_silent_drop() -> None:
    """A turn that ended before the tool returned must not look clean."""
    result = {"messages": [_Msg(tool_calls=[{"id": "c1", "name": "bash", "args": {}}])]}
    (attempt,) = extract_tool_attempts(result)
    assert not attempt.ok


def test_a_turn_with_no_tools_extracts_nothing() -> None:
    assert extract_tool_attempts({"messages": [_Msg(content="just an answer")]}) == ()
