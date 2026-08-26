"""Execute the frozen Stage 2 memory-governance mechanism fixtures."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from ghost.cli import _operation_key
from ghost.config import GhostSettings
from ghost.memory_policy import classify_memory_candidate
from ghost.seam_memory import SeamMemory
from tools.evaluation.integrity import sha256_canonical

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "evals" / "stage2" / "memory_governance.json"
MANIFEST = ROOT / "evals" / "stage2" / "MANIFEST.json"
REQUIRED_CATEGORIES = {
    "contradiction",
    "idempotency",
    "isolation",
    "relevance",
    "staleness",
}


def _load() -> dict[str, object]:
    return json.loads(FIXTURES.read_text(encoding="utf-8"))


def _settings(**changes: object) -> GhostSettings:
    base = GhostSettings(
        model="openai:test-model",
        seam_db=Path("unused.db"),
        namespace="ghost.eval",
        scope="thread",
        workspace="canticle",
        project="ghost",
    )
    return replace(base, **changes)


def test_frozen_memory_fixture_manifest_is_exact() -> None:
    fixtures = _load()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    cases = fixtures["cases"]
    assert fixtures["version"] == "ghost-memory-governance-fixtures/1"
    assert fixtures["status"] == "frozen"
    assert isinstance(cases, list) and len(cases) == 10
    assert {case["category"] for case in cases} == REQUIRED_CATEGORIES
    assert len({case["id"] for case in cases}) == len(cases)
    assert manifest == {
        "case_count": len(cases),
        "case_ids": sorted(case["id"] for case in cases),
        "fixture_sha256": sha256_canonical(fixtures),
        "status": "frozen",
        "suite_id": fixtures["suite_id"],
    }


def test_frozen_admission_cases_execute_the_real_classifier() -> None:
    for case in _load()["cases"]:
        if case["operation"] not in {"classify", "classify_with_output"}:
            continue
        admission = classify_memory_candidate(
            case["input"], case.get("assistant_output", "")
        )
        assert admission.to_payload() == case["expected"], case["id"]


def test_frozen_correction_staleness_and_forgetting_cases(seam_http) -> None:
    cases = _load()["cases"]
    for case in cases:
        operation = case["operation"]
        if operation not in {"correct", "history_after_correction", "forget"}:
            continue
        thread_id = case["id"]
        with SeamMemory(_settings(), client=seam_http) as memory:
            original = case.get("original") or case["text"]
            memory.remember(original, thread_id=thread_id)
            current = memory.recall(original, thread_id=thread_id)
            memory_id = current["memories"][0]["id"]
            if operation == "forget":
                memory.forget(
                    memory_id,
                    thread_id=thread_id,
                    idempotency_key=f"forget-{case['id']}",
                )
                assert len(memory.recall(original, thread_id=thread_id)["memories"]) == case[
                    "expected_current_count"
                ]
                history = memory.recall(original, thread_id=thread_id, view="history")
                assert history["memories"][0]["status"] == case[
                    "expected_history_status"
                ]
                continue

            memory.correct(
                memory_id,
                case["replacement"],
                thread_id=thread_id,
                idempotency_key=f"correct-{case['id']}",
            )
            current = memory.recall("release deploy", thread_id=thread_id)["memories"]
            history = memory.recall(
                "release deploy", thread_id=thread_id, view="history"
            )["memories"]
            if operation == "correct":
                assert [item["text"] for item in current] == [
                    case["expected_current"]
                ]
                assert any(
                    item["text"] == case["original"]
                    and item["status"] == case["expected_old_status"]
                    for item in history
                )
            else:
                assert any(
                    case["expected_current_contains"] in item["text"]
                    for item in current
                )
                assert any(
                    case["expected_history_contains"] in item["text"]
                    and item["status"] == "deleted_soft"
                    for item in history
                )


def test_frozen_idempotency_case_has_a_stable_operation_key() -> None:
    case = next(
        case for case in _load()["cases"] if case["operation"] == "stable_key"
    )
    first = _operation_key("correct", case["memory_id"], case["replacement"])
    second = _operation_key("correct", case["memory_id"], case["replacement"])
    assert first == second
    assert first.startswith(case["expected_prefix"])


def test_frozen_isolation_cases_have_zero_foreign_recall(seam_http) -> None:
    for case in _load()["cases"]:
        if case["operation"] == "cross_thread":
            with SeamMemory(_settings(), client=seam_http) as memory:
                memory.remember(case["text"], thread_id=case["source_thread"])
                foreign = memory.recall(
                    case["text"], thread_id=case["foreign_thread"]
                )
        elif case["operation"] == "cross_project":
            with SeamMemory(
                _settings(project=case["source_project"]), client=seam_http
            ) as source:
                source.remember(case["text"], thread_id="project-boundary")
            with SeamMemory(
                _settings(project=case["foreign_project"]), client=seam_http
            ) as other:
                foreign = other.recall(case["text"], thread_id="project-boundary")
        else:
            continue
        assert len(foreign["memories"]) == case["expected_foreign_count"], case["id"]
