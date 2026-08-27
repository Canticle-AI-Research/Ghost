"""Framework-free command-result truth shared by tool and agent adapters.

The shell's model-facing text is not an execution verdict. LangChain can mark
an ordinary tool return successful even when the process exits nonzero, so the
real process result travels separately as a versioned artifact. This module
contains no agent-framework types; adapters may transport the artifact, but
they do not get to reinterpret it.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

COMMAND_RESULT_SCHEMA = "ghost.command_result/v1"


class InvalidCommandResult(ValueError):
    """A command artifact is absent, malformed, or internally inconsistent."""


@dataclass(frozen=True, slots=True)
class CommandResult:
    """The bounded facts Ghost records for one completed shell process."""

    exit_code: int
    duration_ms: float
    truncated: bool = False

    @property
    def ok(self) -> bool:
        return self.exit_code == 0

    @property
    def status(self) -> str:
        return "succeeded" if self.ok else "failed"

    def to_artifact(self) -> dict[str, object]:
        """Return the JSON-compatible LangChain artifact representation."""

        return {
            "schema": COMMAND_RESULT_SCHEMA,
            "status": self.status,
            "ok": self.ok,
            "exit_code": self.exit_code,
            "duration_ms": self.duration_ms,
            "truncated": self.truncated,
        }

    @classmethod
    def from_artifact(cls, artifact: Any) -> CommandResult:
        """Validate and reconstruct an artifact without coercing its fields."""

        if not isinstance(artifact, dict):
            raise InvalidCommandResult("command result artifact is required")
        if artifact.get("schema") != COMMAND_RESULT_SCHEMA:
            raise InvalidCommandResult("command result schema is invalid")

        exit_code = artifact.get("exit_code")
        duration_ms = artifact.get("duration_ms")
        truncated = artifact.get("truncated")
        ok = artifact.get("ok")
        status = artifact.get("status")

        if type(exit_code) is not int:
            raise InvalidCommandResult("command exit code is invalid")
        if type(duration_ms) not in (int, float) or not math.isfinite(duration_ms):
            raise InvalidCommandResult("command duration is invalid")
        if duration_ms < 0:
            raise InvalidCommandResult("command duration is negative")
        if type(truncated) is not bool:
            raise InvalidCommandResult("command truncation flag is invalid")

        result = cls(
            exit_code=exit_code,
            duration_ms=float(duration_ms),
            truncated=truncated,
        )
        if type(ok) is not bool or ok is not result.ok:
            raise InvalidCommandResult("command success flag contradicts exit code")
        if status != result.status:
            raise InvalidCommandResult("command status contradicts exit code")
        return result


__all__ = ["COMMAND_RESULT_SCHEMA", "CommandResult", "InvalidCommandResult"]
