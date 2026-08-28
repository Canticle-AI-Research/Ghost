"""Ghost's turn lifecycle. Framework-free by construction.

This is layer 2 of three:

    SEAM SDK          durable memory and reasoning records (no LLM dependency)
    turn lifecycle    THIS FILE -- what a turn is, and what a turn owes SEAM
    agent adapter     application.py -- LangChain, DeepAgents, model wiring

Nothing here imports LangChain, LangGraph, or DeepAgents, and
`tests/test_layering.py` fails if that changes. The reason is not tidiness. The
rules a memory-backed turn must obey -- recall before the turn is written so an
answer cannot cite itself, ingest only what completed, close the run on every
path out, and never finalize a crash as an accepted outcome -- are properties
of SEAM's contract, not of any agent framework. Keeping them here means
swapping the harness cannot silently drop one of them.

The agent is reached through the `AgentGraph` protocol, so this file is equally
happy driving DeepAgents, a raw provider loop, or a fake in a test.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol
from uuid import uuid4

from .config import GhostSettings
from .context import GhostTurnContext
from .memory_policy import MemoryAdmission
from .seam_memory import SeamTurn


@dataclass(frozen=True, slots=True)
class ToolAttempt:
    """One tool call and its result, in a form SEAM can check.

    Deliberately a plain dataclass rather than a provider message: the adapter
    translates whatever its framework returns into this, so the lifecycle can
    record an action without knowing what a ``ToolMessage`` is.

    ``output`` is passed to SEAM as a check ``result``, which SEAM fingerprints
    (``result_sha256``, ``result_length``) and does NOT store. That is what
    makes it safe to hand it raw command output: the integrity of the result is
    provable without its contents -- credentials, tokens, environment -- ever
    entering the record.
    """

    name: str
    request: str
    output: str = ""
    ok: bool = True
    exit_code: int | None = None
    duration_ms: float | None = None

    def to_payload(self) -> dict[str, object]:
        """Return a strict, fail-closed payload for the SEAM boundary.

        Adapters are replaceable and therefore cannot be trusted to preserve
        Python types. In particular, ``bool("false")`` is true and ``bool`` is
        an ``int`` subclass. Never let either language quirk turn malformed
        evidence into a passed verification.
        """

        valid_name = isinstance(self.name, str) and bool(self.name.strip())
        valid_request = isinstance(self.request, str)
        valid_output = isinstance(self.output, str)
        valid_ok = type(self.ok) is bool
        valid_exit = self.exit_code is None or type(self.exit_code) is int
        valid_duration = self.duration_ms is None
        if type(self.duration_ms) in (int, float):
            try:
                valid_duration = (
                    math.isfinite(self.duration_ms) and self.duration_ms >= 0
                )
            except OverflowError:
                valid_duration = False
        valid = (
            valid_name
            and valid_request
            and valid_output
            and valid_ok
            and valid_exit
            and valid_duration
        )

        name = self.name if valid_name else "tool"
        request = self.request if valid_request else ""
        output = self.output if valid_output else ""
        exit_code = self.exit_code if valid_exit else None
        duration_ms = self.duration_ms if valid_duration else None
        ok = self.ok if valid else False

        if name == "run_command":
            # A command succeeds only when both independent signals agree.
            ok = ok is True and type(exit_code) is int and exit_code == 0

        return {
            "name": name,
            "request": request,
            "output": output,
            "ok": ok,
            "exit_code": exit_code,
            "duration_ms": duration_ms,
        }


@dataclass(frozen=True, slots=True)
class TurnResult:
    """What a completed turn produced, beyond its text."""

    answer: str
    attempts: tuple[ToolAttempt, ...] = field(default_factory=tuple)


class AgentGraph(Protocol):
    """Anything that can execute one turn. DeepAgents satisfies this."""

    def invoke(
        self,
        input: dict[str, Any],
        *,
        context: GhostTurnContext,
        config: dict[str, Any],
    ) -> dict[str, Any]: ...


class MemoryLayer(Protocol):
    """The SEAM operations a turn needs. `SeamMemory` satisfies this."""

    def begin_turn(self, user_input: str, *, thread_id: str) -> SeamTurn: ...

    def record_actions(
        self, turn: SeamTurn, attempts: Sequence[ToolAttempt]
    ) -> tuple[str, ...]: ...

    def complete_turn(
        self,
        turn: SeamTurn,
        *,
        user_input: str,
        assistant_output: str,
        thread_id: str,
        turn_id: str,
        verification_ids: Sequence[str] = (),
        admission: MemoryAdmission,
    ) -> tuple[str, ...]: ...

    def fail_turn(
        self,
        turn: SeamTurn,
        *,
        error: BaseException,
        thread_id: str,
        turn_id: str,
    ) -> None: ...

    def close(self) -> None: ...


def message_text(message: Any) -> str:
    """Flatten a provider message into the text that gets ingested.

    Providers return either a string or a list of content blocks. Without this,
    a block-returning provider would persist the repr of a list into MIRL.
    """

    content = getattr(message, "content", message)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and isinstance(block.get("text"), str):
                parts.append(block["text"])
        if parts:
            return "\n".join(parts)
    return str(content)


def run_turn(
    *,
    memory: MemoryLayer,
    graph: AgentGraph,
    user_input: str,
    thread_id: str,
    turn_id: str | None = None,
    max_steps: int = 25,
    extract_attempts: Callable[
        [dict[str, Any], str], Sequence[ToolAttempt]
    ]
    | None = None,
    admit_memory: Callable[[str, str], MemoryAdmission] | None = None,
) -> str:
    """Execute one turn under SEAM's contract, and return the answer.

    Recall happens before the turn is ingested, so a response can never cite
    the memory it is about to create.

    Tool calls are not merely logged. Each becomes a `decision` node checked by
    a `tool` verification, and the turn's outcome is finalized against the
    checks that PASSED. That is the whole point of routing actions through
    SEAM rather than a log file: `finalize_verified` refuses an outcome whose
    checks did not pass, so "the action succeeded" is a property the store
    enforces rather than a claim the model makes about itself.

    `extract_attempts` belongs to the adapter, because only the adapter knows
    what its framework's messages look like.
    """

    resolved_input = user_input.strip()
    if not resolved_input:
        raise ValueError("user input is required")
    if not 2 <= max_steps <= 100:
        raise ValueError("max_steps must be between 2 and 100")

    resolved_turn_id = turn_id or uuid4().hex
    seam_turn = memory.begin_turn(resolved_input, thread_id=thread_id)

    # Everything between begin_turn and complete_turn runs inside an open SEAM
    # reasoning run. If it raises -- a model error, a tool timeout, a
    # KeyboardInterrupt mid-answer -- the run must still be closed, or the
    # store accumulates one dangling run per crash. Tools make this the common
    # path rather than the rare one.
    completion_accepted = False
    try:
        result = graph.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": resolved_input,
                        "id": resolved_turn_id,
                    }
                ]
            },
            context=GhostTurnContext(seam_memory=seam_turn.rendered_memory),
            config={
                "configurable": {"thread_id": thread_id},
                "recursion_limit": max_steps,
            },
        )
        messages = result.get("messages") or []
        if not messages:
            raise RuntimeError("Ghost returned no messages")
        answer = message_text(messages[-1])
        attempts = (
            tuple(extract_attempts(result, resolved_turn_id))
            if extract_attempts
            else ()
        )
        verification_ids = (
            memory.record_actions(seam_turn, attempts) if attempts else ()
        )
        admission = (
            admit_memory(resolved_input, answer)
            if admit_memory is not None
            else MemoryAdmission("admit", "conversation", "legacy_auto")
        )
        memory.complete_turn(
            seam_turn,
            user_input=resolved_input,
            assistant_output=answer,
            thread_id=thread_id,
            turn_id=resolved_turn_id,
            verification_ids=verification_ids,
            admission=admission,
        )
        completion_accepted = True
    except BaseException as error:
        # BaseException, not Exception: a cancelled or interrupted turn leaves
        # exactly the same dangling run as a failed one.
        if not completion_accepted:
            try:
                memory.fail_turn(
                    seam_turn,
                    error=error,
                    thread_id=thread_id,
                    turn_id=resolved_turn_id,
                )
            except BaseException as finalization_error:
                error.add_note(
                    "Ghost also failed to finalize the open SEAM turn: "
                    f"{type(finalization_error).__name__}"
                )
        raise
    return answer


__all__ = [
    "AgentGraph",
    "GhostSettings",
    "MemoryLayer",
    "ToolAttempt",
    "TurnResult",
    "message_text",
    "run_turn",
]
