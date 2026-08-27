"""Ghost's half of the public reasoning-lifecycle contract.

The private SEAM suite proves graph storage and acceptance enforcement. These
tests prove Ghost sends bounded decisions and checks through the opaque HTTP
boundary and never claims a failed check passed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from ghost.application import extract_tool_attempts
from ghost.command_result import CommandResult
from ghost.config import GhostSettings
from ghost.lifecycle import ToolAttempt, run_turn
from ghost.seam_memory import SeamMemory, SeamTurn


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


def test_extract_preserves_a_nonzero_command_result() -> None:
    result = {
        "messages": [
            _Msg(tool_calls=[{"id": "c1", "name": "run_command", "args": {}}]),
            _Msg(
                tool_call_id="c1",
                name="run_command",
                content="exit=3 duration_ms=4\n",
                status="success",
                artifact=CommandResult(exit_code=3, duration_ms=4.5).to_artifact(),
            ),
        ]
    }
    (attempt,) = extract_tool_attempts(result)
    assert attempt.name == "run_command"
    assert attempt.ok is False
    assert attempt.exit_code == 3
    assert attempt.duration_ms == 4.5


@pytest.mark.parametrize(
    "artifact",
    [
        None,
        {},
        {
            **CommandResult(exit_code=3, duration_ms=4.5).to_artifact(),
            "ok": True,
        },
    ],
)
def test_extract_fails_closed_on_an_invalid_command_artifact(artifact: object) -> None:
    result = {
        "messages": [
            _Msg(tool_calls=[{"id": "c1", "name": "run_command", "args": {}}]),
            _Msg(
                tool_call_id="c1",
                name="run_command",
                content="exit=0 duration_ms=4\n",
                status="success",
                artifact=artifact,
            ),
        ]
    }
    (attempt,) = extract_tool_attempts(result)
    assert attempt.ok is False
    assert attempt.exit_code is None
    assert attempt.duration_ms is None


@pytest.mark.parametrize("status", [None, "bogus", "pending"])
def test_extract_rejects_a_non_success_command_transport(status: object) -> None:
    message = _Msg(
        tool_call_id="c1",
        name="run_command",
        content="exit=0 duration_ms=4\n",
        artifact=CommandResult(exit_code=0, duration_ms=4.5).to_artifact(),
    )
    if status is not None:
        message.status = status
    result = {
        "messages": [
            _Msg(tool_calls=[{"id": "c1", "name": "run_command", "args": {}}]),
            message,
        ]
    }
    (attempt,) = extract_tool_attempts(result)
    assert attempt.ok is False
    assert attempt.exit_code is None


def test_extract_rejects_a_mismatched_result_name() -> None:
    result = {
        "messages": [
            _Msg(tool_calls=[{"id": "c1", "name": "run_command", "args": {}}]),
            _Msg(
                tool_call_id="c1",
                name="read_file",
                content="exit=0 duration_ms=4\n",
                status="success",
                artifact=CommandResult(exit_code=0, duration_ms=4.5).to_artifact(),
            ),
        ]
    }
    (attempt,) = extract_tool_attempts(result)
    assert attempt.ok is False
    assert attempt.exit_code is None


def test_extract_rejects_a_result_that_precedes_its_request() -> None:
    result = {
        "messages": [
            _Msg(
                tool_call_id="c1",
                name="run_command",
                content="exit=0 duration_ms=4\n",
                status="success",
                artifact=CommandResult(exit_code=0, duration_ms=4.5).to_artifact(),
            ),
            _Msg(tool_calls=[{"id": "c1", "name": "run_command", "args": {}}]),
        ]
    }
    (attempt,) = extract_tool_attempts(result)
    assert attempt.ok is False
    assert attempt.exit_code is None


def test_extract_rejects_every_request_when_a_call_id_is_reused() -> None:
    artifact = CommandResult(exit_code=0, duration_ms=4.5).to_artifact()
    result = {
        "messages": [
            _Msg(
                tool_calls=[
                    {"id": "c1", "name": "run_command", "args": {"command": "old"}}
                ]
            ),
            _Msg(
                tool_call_id="c1",
                name="run_command",
                content="exit=0 duration_ms=4\n",
                status="success",
                artifact=artifact,
            ),
            _Msg(
                tool_calls=[
                    {"id": "c1", "name": "run_command", "args": {"command": "new"}}
                ]
            ),
        ]
    }
    attempts = extract_tool_attempts(result)
    assert len(attempts) == 2
    assert all(not attempt.ok and attempt.exit_code is None for attempt in attempts)


def test_blank_call_id_is_recorded_as_failed_evidence(seam_http) -> None:
    artifact = CommandResult(exit_code=0, duration_ms=4.5).to_artifact()
    result = {
        "messages": [
            _Msg(tool_calls=[{"id": "", "name": "run_command", "args": {}}]),
            _Msg(
                tool_call_id="",
                name="run_command",
                content="exit=0 duration_ms=4\n",
                status="success",
                artifact=artifact,
            ),
        ]
    }

    (attempt,) = extract_tool_attempts(result)
    assert attempt.ok is False
    assert attempt.exit_code is None
    with SeamMemory(_settings(), client=seam_http) as memory:
        turn = memory.begin_turn("run it", thread_id="thread-a")
        assert memory.record_actions(turn, [attempt]) == ()


def test_valid_zero_exit_returns_passed_seam_support(seam_http) -> None:
    result = {
        "messages": [
            _Msg(tool_calls=[{"id": "c1", "name": "run_command", "args": {}}]),
            _Msg(
                tool_call_id="c1",
                name="run_command",
                content="exit=0 duration_ms=4\n",
                status="success",
                artifact=CommandResult(exit_code=0, duration_ms=4.5).to_artifact(),
            ),
        ]
    }

    (attempt,) = extract_tool_attempts(result)
    assert attempt.ok is True
    assert attempt.exit_code == 0
    assert attempt.duration_ms == 4.5
    with SeamMemory(_settings(), client=seam_http) as memory:
        turn = memory.begin_turn("run it", thread_id="thread-a")
        assert memory.record_actions(turn, [attempt]) == ("verify-0",)


def test_a_request_with_no_result_is_a_failure_not_a_silent_drop() -> None:
    result = {"messages": [_Msg(tool_calls=[{"id": "c1", "name": "bash", "args": {}}])]}
    (attempt,) = extract_tool_attempts(result)
    assert not attempt.ok


def test_a_turn_with_no_tools_extracts_nothing() -> None:
    assert extract_tool_attempts({"messages": [_Msg(content="just an answer")]}) == ()


def test_nonzero_command_cannot_support_the_completed_outcome(seam_http) -> None:
    messages = [
        _Msg(tool_calls=[{"id": "c1", "name": "run_command", "args": {}}]),
        _Msg(
            tool_call_id="c1",
            name="run_command",
            content="exit=3 duration_ms=4\n",
            status="success",
            artifact=CommandResult(exit_code=3, duration_ms=4.5).to_artifact(),
        ),
        _Msg(content="The command failed with exit code 3."),
    ]

    class Graph:
        def invoke(self, input, *, context, config):
            return {"messages": messages}

    class RecordingMemory:
        def __init__(self, wrapped: SeamMemory) -> None:
            self.wrapped = wrapped
            self.passed_ids: tuple[str, ...] | None = None
            self.completion_support: tuple[str, ...] | None = None

        def begin_turn(self, user_input: str, *, thread_id: str) -> SeamTurn:
            return self.wrapped.begin_turn(user_input, thread_id=thread_id)

        def record_actions(
            self, turn: SeamTurn, attempts: tuple[ToolAttempt, ...]
        ) -> tuple[str, ...]:
            self.passed_ids = self.wrapped.record_actions(turn, attempts)
            return self.passed_ids

        def complete_turn(self, turn: SeamTurn, **kwargs: Any) -> tuple[str, ...]:
            self.completion_support = tuple(kwargs["verification_ids"])
            return self.wrapped.complete_turn(turn, **kwargs)

        def fail_turn(self, turn: SeamTurn, **kwargs: Any) -> None:
            self.wrapped.fail_turn(turn, **kwargs)

        def close(self) -> None:
            self.wrapped.close()

    with SeamMemory(_settings(), client=seam_http) as wrapped:
        memory = RecordingMemory(wrapped)
        answer = run_turn(
            memory=memory,
            graph=Graph(),
            user_input="run the check",
            thread_id="thread-a",
            extract_attempts=extract_tool_attempts,
        )

    assert answer == "The command failed with exit code 3."
    assert memory.passed_ids == ()
    assert memory.completion_support == ()
    path, payload = next(
        (path, payload)
        for path, payload in seam_http.calls
        if path == "/v1/agent/turns/actions"
    )
    assert path == "/v1/agent/turns/actions"
    assert payload["attempts"] == [
        {
            "name": "run_command",
            "request": "{}",
            "output": "exit=3 duration_ms=4\n",
            "ok": False,
            "exit_code": 3,
            "duration_ms": 4.5,
        }
    ]


@pytest.mark.parametrize(
    "content",
    [
        "the operator declined to run the command",
        "command exceeded 1s and was killed",
    ],
)
def test_refused_or_timed_out_command_returns_no_passed_support(
    seam_http, content: str
) -> None:
    result = {
        "messages": [
            _Msg(tool_calls=[{"id": "c1", "name": "run_command", "args": {}}]),
            _Msg(
                tool_call_id="c1",
                name="run_command",
                content=content,
                status="error",
                artifact=None,
            ),
        ]
    }
    (attempt,) = extract_tool_attempts(result)
    assert attempt.ok is False
    assert attempt.exit_code is None
    with SeamMemory(_settings(), client=seam_http) as memory:
        turn = memory.begin_turn("run it", thread_id="thread-a")
        assert memory.record_actions(turn, [attempt]) == ()
