"""Load and validate immutable Stage 1 evaluation fixtures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

FIXTURE_VERSION = "GHOST-STAGE1-FIXTURES/1"
MINIMUM_CASES = 20
REQUIRED_CATEGORIES = {
    "approval_controlled_action",
    "boundary_isolation",
    "failed_turn_non_admission",
    "memory_restart",
    "refusal_recovery",
    "repository_diagnosis",
    "repository_qa",
    "source_grounded_research",
    "stale_memory",
    "timeout_cancellation_restart",
}


class FixtureError(ValueError):
    """A frozen fixture violates the Stage 1 schema."""


def _require_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FixtureError(f"{label} must be a non-empty string")
    return value


def load_fixtures(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FixtureError(f"cannot load fixture file {path}") from exc
    validate_fixtures(payload)
    return payload


def validate_fixtures(payload: object) -> None:
    if not isinstance(payload, dict):
        raise FixtureError("fixture root must be an object")
    if payload.get("version") != FIXTURE_VERSION:
        raise FixtureError(f"fixture version must be {FIXTURE_VERSION}")
    _require_string(payload.get("suite_id"), "suite_id")
    _require_string(payload.get("frozen_at"), "frozen_at")
    cases = payload.get("cases")
    if not isinstance(cases, list) or len(cases) < MINIMUM_CASES:
        raise FixtureError(f"fixtures require at least {MINIMUM_CASES} cases")

    seen: set[str] = set()
    categories: set[str] = set()
    for index, case in enumerate(cases):
        label = f"cases[{index}]"
        if not isinstance(case, dict):
            raise FixtureError(f"{label} must be an object")
        case_id = _require_string(case.get("id"), f"{label}.id")
        if case_id in seen:
            raise FixtureError(f"duplicate case id: {case_id}")
        seen.add(case_id)
        category = _require_string(case.get("category"), f"{label}.category")
        categories.add(category)
        _require_string(case.get("prompt"), f"{label}.prompt")
        _validate_memories(case.get("memories"), label)
        _validate_script(case.get("script"), label)
        _validate_expectations(case.get("expect"), label)
        _validate_budgets(case.get("budgets"), label)
        _validate_case_consistency(case, label)
        forbidden = case.get("forbidden_effects")
        if not isinstance(forbidden, list) or not all(
            isinstance(item, str) and item for item in forbidden
        ):
            raise FixtureError(f"{label}.forbidden_effects must be a string list")

    missing = sorted(REQUIRED_CATEGORIES - categories)
    if missing:
        raise FixtureError(f"fixtures missing required categories: {missing}")


def _validate_memories(value: object, label: str) -> None:
    if not isinstance(value, list):
        raise FixtureError(f"{label}.memories must be a list")
    ids: set[str] = set()
    for index, memory in enumerate(value):
        if not isinstance(memory, dict):
            raise FixtureError(f"{label}.memories[{index}] must be an object")
        memory_id = _require_string(memory.get("id"), f"{label}.memories[{index}].id")
        if memory_id in ids:
            raise FixtureError(f"{label} repeats memory id {memory_id}")
        ids.add(memory_id)
        _require_string(memory.get("text"), f"{label}.memories[{index}].text")
        if not isinstance(memory.get("visible"), bool):
            raise FixtureError(f"{label}.memories[{index}].visible must be boolean")


def _validate_script(value: object, label: str) -> None:
    if not isinstance(value, dict):
        raise FixtureError(f"{label}.script must be an object")
    terminal = value.get("terminal_state")
    if terminal not in {"accepted", "rejected"}:
        raise FixtureError(f"{label}.script.terminal_state is invalid")
    for key in ("answer_with_memory", "answer_without_memory"):
        if not isinstance(value.get(key), str):
            raise FixtureError(f"{label}.script.{key} must be a string")
    if not isinstance(value.get("steps"), int) or value["steps"] < 1:
        raise FixtureError(f"{label}.script.steps must be a positive integer")
    attempts = value.get("attempts")
    if not isinstance(attempts, list):
        raise FixtureError(f"{label}.script.attempts must be a list")
    for index, attempt in enumerate(attempts):
        if not isinstance(attempt, dict):
            raise FixtureError(f"{label}.script.attempts[{index}] must be an object")
        _require_string(attempt.get("name"), f"{label}.script.attempts[{index}].name")
        if not isinstance(attempt.get("ok"), bool):
            raise FixtureError(f"{label}.script.attempts[{index}].ok must be boolean")
    observed_effects = value.get("observed_effects", [])
    if not isinstance(observed_effects, list) or not all(
        isinstance(item, str) and item for item in observed_effects
    ):
        raise FixtureError(f"{label}.script.observed_effects must be a string list")


def _validate_expectations(value: object, label: str) -> None:
    if not isinstance(value, dict):
        raise FixtureError(f"{label}.expect must be an object")
    if value.get("terminal_state") not in {"accepted", "rejected"}:
        raise FixtureError(f"{label}.expect.terminal_state is invalid")
    for key in (
        "required_evidence",
        "forbidden_evidence",
        "answer_contains",
        "answer_excludes",
        "required_tools",
        "forbidden_tools",
    ):
        entries = value.get(key)
        if not isinstance(entries, list) or not all(
            isinstance(item, str) and item for item in entries
        ):
            raise FixtureError(f"{label}.expect.{key} must be a string list")


def _validate_budgets(value: object, label: str) -> None:
    if not isinstance(value, dict):
        raise FixtureError(f"{label}.budgets must be an object")
    for key in ("max_tool_calls", "max_context_chars"):
        item = value.get(key)
        if not isinstance(item, int) or item < 0:
            raise FixtureError(f"{label}.budgets.{key} must be a non-negative integer")
    max_steps = value.get("max_steps")
    if not isinstance(max_steps, int) or not 2 <= max_steps <= 100:
        raise FixtureError(f"{label}.budgets.max_steps must be between 2 and 100")


def _validate_case_consistency(case: dict[str, Any], label: str) -> None:
    memories = {memory["id"]: memory for memory in case["memories"]}
    expected = case["expect"]
    unknown = (
        set(expected["required_evidence"])
        | set(expected["forbidden_evidence"])
    ) - set(memories)
    if unknown:
        raise FixtureError(f"{label} references unknown evidence: {sorted(unknown)}")
    hidden_required = [
        memory_id
        for memory_id in expected["required_evidence"]
        if memories[memory_id]["visible"] is not True
    ]
    visible_forbidden = [
        memory_id
        for memory_id in expected["forbidden_evidence"]
        if memories[memory_id]["visible"] is not False
    ]
    if hidden_required:
        raise FixtureError(f"{label} requires hidden evidence: {hidden_required}")
    if visible_forbidden:
        raise FixtureError(f"{label} exposes forbidden evidence: {visible_forbidden}")
    script = case["script"]
    budgets = case["budgets"]
    if script["steps"] > budgets["max_steps"]:
        raise FixtureError(f"{label} scripted steps exceed max_steps")
    if len(script["attempts"]) > budgets["max_tool_calls"]:
        raise FixtureError(f"{label} scripted attempts exceed max_tool_calls")
    visible_chars = sum(
        len(memory["text"])
        for memory in case["memories"]
        if memory["visible"] is True
    )
    if visible_chars > budgets["max_context_chars"]:
        raise FixtureError(f"{label} visible memory exceeds max_context_chars")
