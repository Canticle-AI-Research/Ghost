"""Roadmap Stage 1 item 4: a crashed turn must not strand a reasoning run.

`begin_turn` opens a SEAM reasoning run before the agent executes. Every path
out of that window has to close the run, or the store accumulates one dangling
run per crash -- and once Ghost has tools, crashing is the ordinary case rather
than the rare one.

Two properties matter beyond "it did not leak", and both are easy to get wrong:

* a failed turn must NOT be ingested, because a turn that crashed has no
  trustworthy assistant output to compile into MIRL; and
* its outcome must NOT be `accepted`, because `reasoning_promotion` and
  `reasoning_patterns` gate on exactly that status -- an accepted outcome makes
  a crash eligible for promotion into knowledge.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from ghost.application import GhostAgent
from ghost.config import GhostSettings
from ghost.seam_memory import SeamMemory, SeamTurn


def _settings(db: Path) -> GhostSettings:
    return GhostSettings(
        model="openai:test-model",
        seam_db=db,
        namespace="ghost.test",
        scope="thread",
        graph_hops=1,
    )


class _RecordingMemory:
    def __init__(self) -> None:
        self.failed: dict[str, Any] | None = None
        self.completed: dict[str, Any] | None = None
        self.closed = False

    def begin_turn(self, user_input: str) -> SeamTurn:
        return SeamTurn("run-1", "", ("clm:1",))

    def complete_turn(self, turn: SeamTurn, **kwargs: Any) -> tuple[str, ...]:
        self.completed = kwargs
        return ()

    def fail_turn(self, turn: SeamTurn, **kwargs: Any) -> None:
        self.failed = {"turn": turn, **kwargs}

    def close(self) -> None:
        self.closed = True


class _ExplodingGraph:
    def __init__(self, error: BaseException) -> None:
        self.error = error

    def invoke(self, input, *, context, config):
        raise self.error


@pytest.mark.parametrize(
    "error",
    [
        RuntimeError("model provider returned 500"),
        KeyboardInterrupt(),  # BaseException, not Exception
    ],
    ids=["exception", "interrupt"],
)
def test_a_crashed_turn_finalizes_the_run_and_reraises(error) -> None:
    memory = _RecordingMemory()
    ghost = GhostAgent(_settings(Path("unused.db")), memory=memory, graph=_ExplodingGraph(error))

    with pytest.raises(type(error)):
        ghost.invoke("what do you remember?", thread_id="t-1", turn_id="turn-1")

    assert memory.failed is not None, "the reasoning run was left open"
    assert memory.failed["error"] is error
    assert memory.failed["thread_id"] == "t-1"
    assert memory.failed["turn_id"] == "turn-1"
    assert memory.completed is None, "a crashed turn must never be ingested"


def test_an_empty_response_is_a_failure_not_a_silent_success() -> None:
    """`Ghost returned no messages` is raised inside the guarded window, so it
    must finalize like any other failure rather than escaping uncounted."""

    class _EmptyGraph:
        def invoke(self, input, *, context, config):
            return {"messages": []}

    memory = _RecordingMemory()
    ghost = GhostAgent(_settings(Path("unused.db")), memory=memory, graph=_EmptyGraph())

    with pytest.raises(RuntimeError, match="no messages"):
        ghost.invoke("hello")

    assert memory.failed is not None
    assert memory.completed is None


def test_a_successful_turn_does_not_finalize_as_failed() -> None:
    class _Message:
        content = "an answer"

    class _OkGraph:
        def invoke(self, input, *, context, config):
            return {"messages": [_Message()]}

    memory = _RecordingMemory()
    ghost = GhostAgent(_settings(Path("unused.db")), memory=memory, graph=_OkGraph())

    assert ghost.invoke("hello") == "an answer"
    assert memory.failed is None
    assert memory.completed is not None


def test_fail_turn_uses_the_rejected_terminal_route(tmp_path: Path, seam_http) -> None:
    with SeamMemory(_settings(tmp_path / "ghost.db"), client=seam_http) as memory:
        turn = memory.begin_turn("what happened?")
        memory.fail_turn(
            turn,
            error=RuntimeError("tool timed out"),
            thread_id="t-1",
            turn_id="turn-1",
        )
    assert seam_http.turns[turn.run_id] == "rejected"
    assert seam_http.calls[-1][0] == "/v1/agent/turns/fail"


def test_a_failed_turn_writes_no_knowledge(tmp_path: Path, seam_http) -> None:
    """Ghost never sends failed-turn content to the completion/ingest route."""
    with SeamMemory(_settings(tmp_path / "ghost.db"), client=seam_http) as memory:
        first = memory.begin_turn("remember my preferred colour")
        memory.fail_turn(
            first, error=RuntimeError("boom"), thread_id="t-1", turn_id="turn-1"
        )

        # A later turn must not be able to recall anything from the failed one.
        later = memory.begin_turn("what is my preferred colour?")
        assert later.rendered_memory == "", (
            "a crashed turn left recallable memory behind: "
            f"{later.rendered_memory[:200]}"
        )
        assert later.evidence_refs == ()
    assert not any(path.endswith("/complete") for path, _payload in seam_http.calls)
    assert seam_http.memories == []
