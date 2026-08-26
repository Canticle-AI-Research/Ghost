"""Provider-free contracts for future bounded Ghost specialists.

This module does not activate a specialist topology. It defines the authority,
budget, provenance, and terminal-state boundary that any future framework
adapter must satisfy before a delegated run can support a root outcome.
"""

from __future__ import annotations

from collections.abc import Callable
from contextlib import suppress
from dataclasses import dataclass, field, replace
from pathlib import PurePath
from time import monotonic
from typing import Literal, Protocol

from .config import validate_dimension

SpecialistStatus = Literal["succeeded", "failed", "cancelled", "timed_out", "refused"]


@dataclass(frozen=True, slots=True)
class SpecialistBudget:
    """Hard ceilings carried with one delegation."""

    max_steps: int = 12
    timeout_seconds: float = 120.0
    max_output_chars: int = 20_000

    def __post_init__(self) -> None:
        if not 1 <= self.max_steps <= 100:
            raise ValueError("max_steps must be between 1 and 100")
        if not 0 < self.timeout_seconds <= 3600:
            raise ValueError("timeout_seconds must be greater than 0 and at most 3600")
        if not 1 <= self.max_output_chars <= 1_000_000:
            raise ValueError("max_output_chars must be between 1 and 1000000")


@dataclass(frozen=True, slots=True)
class SpecialistScope:
    """The complete authority visible to one specialist.

    Empty tools and roots mean no tool and filesystem authority. A scope can be
    narrowed by the caller, but never inferred from the root agent.
    """

    tools: frozenset[str] = field(default_factory=frozenset)
    roots: tuple[str, ...] = ()
    namespace: str = "ghost.default"
    workspace: str = "default"
    project: str = "default"

    def __post_init__(self) -> None:
        for tool in self.tools:
            allowed = "abcdefghijklmnopqrstuvwxyz0123456789_-"
            if not tool or any(char not in allowed for char in tool):
                raise ValueError("specialist tool names must be non-empty lowercase identifiers")
        for root in self.roots:
            path = PurePath(root)
            if not path.is_absolute() or ".." in path.parts:
                raise ValueError("specialist roots must be absolute and traversal-free")
        validate_dimension(self.namespace, "namespace")
        validate_dimension(self.workspace, "workspace")
        validate_dimension(self.project, "project")


@dataclass(frozen=True, slots=True)
class DelegationEnvelope:
    """One auditable request from a root turn to a named specialist role."""

    delegation_id: str
    parent_turn_id: str
    role: str
    objective: str
    budget: SpecialistBudget
    scope: SpecialistScope

    def __post_init__(self) -> None:
        validate_dimension(self.delegation_id, "delegation_id")
        validate_dimension(self.parent_turn_id, "parent_turn_id")
        validate_dimension(self.role, "role")
        if not self.objective.strip() or len(self.objective) > 4000:
            raise ValueError("objective must contain 1 to 4000 characters")


@dataclass(frozen=True, slots=True)
class SpecialistEvidence:
    """Opaque provenance supporting a specialist outcome."""

    ref: str
    kind: str

    def __post_init__(self) -> None:
        if not self.ref.strip() or len(self.ref) > 512:
            raise ValueError("evidence ref must contain 1 to 512 characters")
        validate_dimension(self.kind, "evidence kind")


@dataclass(frozen=True, slots=True)
class SpecialistOutcome:
    """Terminal result returned to the root without raw exception details."""

    status: SpecialistStatus
    summary: str
    steps_used: int = 0
    evidence: tuple[SpecialistEvidence, ...] = ()
    duration_ms: float = 0.0
    error_type: str | None = None

    def __post_init__(self) -> None:
        if self.status not in {"succeeded", "failed", "cancelled", "timed_out", "refused"}:
            raise ValueError("invalid specialist status")
        if self.steps_used < 0:
            raise ValueError("steps_used cannot be negative")
        if self.duration_ms < 0:
            raise ValueError("duration_ms cannot be negative")


@dataclass(frozen=True, slots=True)
class SpecialistEvent:
    """Content-free telemetry safe for an operational event stream."""

    kind: str
    delegation_id: str
    parent_turn_id: str
    role: str
    attributes: dict[str, str | int]


class SpecialistRunner(Protocol):
    def __call__(self, envelope: DelegationEnvelope) -> SpecialistOutcome: ...


class SpecialistCancelled(RuntimeError):
    """Raised by an adapter when root or operator cancellation is observed."""


Observer = Callable[[SpecialistEvent], None]


def _terminal(
    status: SpecialistStatus,
    error_type: str,
    duration_ms: float,
) -> SpecialistOutcome:
    return SpecialistOutcome(
        status=status,
        summary="specialist outcome rejected",
        duration_ms=duration_ms,
        error_type=error_type,
    )


def execute_delegation(
    envelope: DelegationEnvelope,
    runner: SpecialistRunner,
    *,
    observe: Observer | None = None,
) -> SpecialistOutcome:
    """Execute one adapter under an explicit envelope and normalize failures.

    Timeout enforcement belongs in the framework adapter because this
    synchronous boundary cannot safely kill an arbitrary worker. A runner must
    raise ``TimeoutError`` when its deadline fires; returned elapsed time is
    also checked so a late success cannot pass the budget gate.
    """

    def emit(event: SpecialistEvent) -> None:
        if observe is None:
            return
        # Telemetry must never change the delegated operation's outcome.
        with suppress(Exception):
            observe(event)

    emit(
        SpecialistEvent(
            "specialist.started",
            envelope.delegation_id,
            envelope.parent_turn_id,
            envelope.role,
            {},
        )
    )
    started = monotonic()
    try:
        outcome = runner(envelope)
        duration_ms = (monotonic() - started) * 1000
        if outcome.steps_used > envelope.budget.max_steps:
            outcome = _terminal("failed", "BudgetExceeded", duration_ms)
        elif len(outcome.summary) > envelope.budget.max_output_chars:
            outcome = _terminal("failed", "OutputLimitExceeded", duration_ms)
        elif duration_ms > envelope.budget.timeout_seconds * 1000:
            outcome = _terminal("timed_out", "DeadlineExceeded", duration_ms)
        elif outcome.status != "succeeded":
            outcome = _terminal(
                outcome.status,
                {
                    "cancelled": "SpecialistCancelled",
                    "failed": "SpecialistFailed",
                    "refused": "SpecialistRefused",
                    "timed_out": "SpecialistTimedOut",
                }[outcome.status],
                duration_ms,
            )
        else:
            outcome = replace(outcome, duration_ms=duration_ms, error_type=None)
    except SpecialistCancelled:
        outcome = _terminal(
            "cancelled",
            "SpecialistCancelled",
            (monotonic() - started) * 1000,
        )
    except TimeoutError:
        outcome = _terminal(
            "timed_out",
            "TimeoutError",
            (monotonic() - started) * 1000,
        )
    except PermissionError:
        outcome = _terminal(
            "refused",
            "PermissionError",
            (monotonic() - started) * 1000,
        )
    except Exception:
        outcome = _terminal(
            "failed",
            "RunnerError",
            (monotonic() - started) * 1000,
        )
    emit(
        SpecialistEvent(
            "specialist.finished",
            envelope.delegation_id,
            envelope.parent_turn_id,
            envelope.role,
            {"status": outcome.status, "steps_used": outcome.steps_used},
        )
    )
    return outcome


__all__ = [
    "DelegationEnvelope",
    "Observer",
    "SpecialistBudget",
    "SpecialistCancelled",
    "SpecialistEvent",
    "SpecialistEvidence",
    "SpecialistOutcome",
    "SpecialistRunner",
    "SpecialistScope",
    "SpecialistStatus",
    "execute_delegation",
]
