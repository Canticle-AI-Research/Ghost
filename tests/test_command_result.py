"""Strict, framework-free command-result contract tests."""

from __future__ import annotations

import pytest

from ghost.command_result import CommandResult, InvalidCommandResult


def test_command_result_round_trips_without_coercion() -> None:
    original = CommandResult(exit_code=7, duration_ms=12.5, truncated=True)

    restored = CommandResult.from_artifact(original.to_artifact())

    assert restored == original
    assert restored.ok is False
    assert restored.status == "failed"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("schema", "ghost.command_result/v0"),
        ("exit_code", True),
        ("duration_ms", float("nan")),
        ("duration_ms", float("inf")),
        ("duration_ms", -0.1),
        ("truncated", 0),
        ("ok", False),
        ("status", "failed"),
    ],
)
def test_command_result_rejects_malformed_or_contradictory_fields(
    field: str, value: object
) -> None:
    artifact = CommandResult(exit_code=0, duration_ms=1.0).to_artifact()
    artifact[field] = value

    with pytest.raises(InvalidCommandResult):
        CommandResult.from_artifact(artifact)
