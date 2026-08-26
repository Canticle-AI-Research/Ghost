"""Ghost's half of the public reasoning-lifecycle contract.

The private SEAM suite proves graph storage and acceptance enforcement. These
tests prove Ghost sends bounded decisions and checks through the opaque HTTP
boundary and never claims a failed check passed.
"""

from __future__ import annotations

from pathlib import Path

from ghost.application import extract_tool_attempts
from ghost.config import GhostSettings
from ghost.lifecycle import ToolAttempt
from ghost.seam_memory import SeamMemory


def _settings() -> GhostSettings:
    return GhostSettings(
        model="openai:test-model",
        seam_db=Path("unused.db"),
        namespace="ghost.test",
        scope="thread",
        graph_hops=1,
    )


def test_tool_attempts_cross_the_opaque_actions_route(seam_http) -> None:
    with SeamMemory(_settings(), client=seam_http) as memory:
        turn = memory.begin_turn("read the notes")
        ids = memory.record_actions(
            turn,
            [
                ToolAttempt(
                    name="read_file",
                    request='{"path":"notes.md"}',
                    output="hi",
                    ok=True,
                    exit_code=0,
                    duration_ms=4.5,
                )
            ],
        )

    path, payload = seam_http.calls[-1]
    assert path == "/v1/agent/turns/actions"
    assert ids == ("verify-0",)
    assert payload["turn_id"] == turn.run_id
    assert payload["attempts"] == [
        {
            "name": "read_file",
            "request": '{"path":"notes.md"}',
            "output": "hi",
            "ok": True,
            "exit_code": 0,
            "duration_ms": 4.5,
        }
    ]


def test_failed_tool_is_recorded_but_not_returned_as_support(seam_http) -> None:
    with SeamMemory(_settings(), client=seam_http) as memory:
        turn = memory.begin_turn("read a missing file")
        ids = memory.record_actions(
            turn,
            [ToolAttempt(name="read_file", request="{}", output="boom", ok=False)],
        )

    assert ids == ()
    attempt = seam_http.calls[-1][1]["attempts"][0]
    assert attempt["ok"] is False


def test_no_tools_avoids_an_empty_network_write(seam_http) -> None:
    with SeamMemory(_settings(), client=seam_http) as memory:
        turn = memory.begin_turn("answer directly")
        before = len(seam_http.calls)
        assert memory.record_actions(turn, []) == ()
    assert len(seam_http.calls) == before


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
    result = {"messages": [_Msg(tool_calls=[{"id": "c1", "name": "bash", "args": {}}])]}
    (attempt,) = extract_tool_attempts(result)
    assert not attempt.ok


def test_a_turn_with_no_tools_extracts_nothing() -> None:
    assert extract_tool_attempts({"messages": [_Msg(content="just an answer")]}) == ()
