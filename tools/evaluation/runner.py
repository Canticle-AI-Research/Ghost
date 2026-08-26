"""Deterministic Stage 1 contract-smoke runner.

The runner intentionally uses a scripted judge and therefore seals only at
BIL-0. It exercises fixture validation, lifecycle terminal-state accounting,
memory selection, tool/refusal attribution, budget checks, baseline separation,
and bundle integrity. It is not evidence of live model capability.
"""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from typing import Any

from ghost.context import GhostTurnContext
from ghost.lifecycle import ToolAttempt, run_turn
from ghost.seam_memory import SeamTurn

from .fixtures import load_fixtures
from .integrity import case_hashes, seal_bundle, sha256_canonical


class EvaluationError(RuntimeError):
    """The evaluation cannot produce an honest sealed result."""


class _ScriptedRejection(RuntimeError):
    """The frozen scenario deliberately takes Ghost's rejected-turn path."""


class _SmokeMemory:
    def __init__(self, memories: list[dict[str, Any]], *, use_memory: bool) -> None:
        self.selected = [
            memory for memory in memories if use_memory and memory["visible"] is True
        ]
        self.events: list[str] = []
        self.terminal_state = "open"

    def begin_turn(self, user_input: str) -> SeamTurn:
        self.events.append("begin")
        rendered = "\n".join(
            json.dumps(memory, sort_keys=True) for memory in self.selected
        )
        return SeamTurn(
            run_id="smoke-turn",
            rendered_memory=rendered,
            evidence_refs=tuple(memory["id"] for memory in self.selected),
        )

    def record_actions(
        self, turn: SeamTurn, attempts: tuple[ToolAttempt, ...]
    ) -> tuple[str, ...]:
        del turn
        self.events.append("record_actions")
        return tuple(
            f"check-{index}" for index, attempt in enumerate(attempts) if attempt.ok
        )

    def complete_turn(self, turn: SeamTurn, **kwargs: object) -> tuple[str, ...]:
        del turn, kwargs
        self.events.append("complete")
        self.terminal_state = "accepted"
        return ("receipt-smoke",)

    def fail_turn(self, turn: SeamTurn, **kwargs: object) -> None:
        del turn, kwargs
        self.events.append("fail")
        self.terminal_state = "rejected"

    def close(self) -> None:
        return None


class _SmokeGraph:
    def __init__(
        self,
        *,
        answer: str,
        terminal_state: str,
        attempts: tuple[ToolAttempt, ...],
        expected_limit: int,
    ) -> None:
        self.answer = answer
        self.terminal_state = terminal_state
        self.attempts = attempts
        self.expected_limit = expected_limit

    def invoke(
        self,
        input: dict[str, Any],
        *,
        context: GhostTurnContext,
        config: dict[str, Any],
    ) -> dict[str, Any]:
        del input, context
        if config.get("recursion_limit") != self.expected_limit:
            raise EvaluationError("lifecycle did not receive the frozen step budget")
        if self.terminal_state == "rejected":
            raise _ScriptedRejection("frozen rejected-turn scenario")
        return {"messages": [self.answer], "_attempts": self.attempts}


def git_identity(repo_root: Path) -> tuple[str, bool]:
    sha = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    dirty = bool(
        subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    )
    return sha, dirty


def run_smoke(
    fixture_path: Path,
    *,
    repo_root: Path,
    allow_dirty: bool = False,
) -> dict[str, Any]:
    fixtures = load_fixtures(fixture_path)
    git_sha, dirty = git_identity(repo_root)
    if dirty and not allow_dirty:
        raise EvaluationError("refusing to seal an evaluation from a dirty worktree")
    started = time.monotonic()
    fixture_sha = sha256_canonical(fixtures)
    results: list[dict[str, Any]] = []
    for case in fixtures["cases"]:
        results.append(_evaluate_case(case, arm="ghost-memory"))
        results.append(_evaluate_case(case, arm="no-memory"))
    result = {
        "version": "GHOST-STAGE1-SMOKE-RESULT/1",
        "suite_id": fixtures["suite_id"],
        "integrity_level": "BIL-0",
        "evaluator": "deterministic-contract-stub/1",
        "claim_boundary": "harness and lifecycle contract smoke; no live capability claim",
        "git_sha": git_sha,
        "dirty_worktree": dirty,
        "fixture_sha256": fixture_sha,
        "baseline": "no-memory",
        "candidate": "ghost-memory",
        "cases": results,
        "summary": _summary(results),
        "elapsed_ms": round((time.monotonic() - started) * 1000, 3),
    }
    manifest = {
        "version": "GHOST-EVAL-INPUT-MANIFEST/1",
        "suite_id": fixtures["suite_id"],
        "git_sha": git_sha,
        "dirty_worktree": dirty,
        "fixture_path": fixture_path.relative_to(repo_root).as_posix(),
        "fixture_sha256": fixture_sha,
        "case_count": len(fixtures["cases"]),
        "case_ids": sorted(case["id"] for case in fixtures["cases"]),
        "case_hashes": case_hashes(fixtures),
        "arms": ["ghost-memory", "no-memory"],
        "evaluator": "deterministic-contract-stub/1",
    }
    return seal_bundle(result=result, manifest=manifest)


def _evaluate_case(case: dict[str, Any], *, arm: str) -> dict[str, Any]:
    use_memory = arm == "ghost-memory"
    script = case["script"]
    expected = case["expect"]
    answer = script["answer_with_memory"] if use_memory else script["answer_without_memory"]
    attempts = tuple(
        ToolAttempt(name=attempt["name"], request="{}", ok=attempt["ok"])
        for attempt in script["attempts"]
    )
    memory = _SmokeMemory(case["memories"], use_memory=use_memory)
    graph = _SmokeGraph(
        answer=answer,
        terminal_state=script["terminal_state"],
        attempts=attempts,
        expected_limit=case["budgets"]["max_steps"],
    )
    try:
        answer = run_turn(
            memory=memory,
            graph=graph,
            user_input=case["prompt"],
            thread_id=f"eval-{case['id']}",
            max_steps=case["budgets"]["max_steps"],
            extract_attempts=lambda result: result["_attempts"],
        )
    except _ScriptedRejection:
        answer = ""
    selected = [memory["id"] for memory in memory.selected]
    observed_tools = [attempt.name for attempt in attempts]
    checks = {
        "required_evidence": set(expected["required_evidence"]).issubset(selected),
        "forbidden_evidence": set(expected["forbidden_evidence"]).isdisjoint(selected),
        "answer_contains": all(
            term.casefold() in answer.casefold()
            for term in expected["answer_contains"]
        ),
        "answer_excludes": all(
            term.casefold() not in answer.casefold()
            for term in expected["answer_excludes"]
        ),
        "terminal_state": memory.terminal_state == expected["terminal_state"],
        "required_tools": set(expected["required_tools"]).issubset(observed_tools),
        "forbidden_tools": set(expected["forbidden_tools"]).isdisjoint(observed_tools),
        "step_budget": script["steps"] <= case["budgets"]["max_steps"],
        "tool_budget": len(attempts) <= case["budgets"]["max_tool_calls"],
        "context_budget": sum(
            len(memory["text"])
            for memory in case["memories"]
            if memory["id"] in selected
        )
        <= case["budgets"]["max_context_chars"],
        "forbidden_effects": not script.get("observed_effects"),
    }
    passed = all(checks.values())
    return {
        "case_id": case["id"],
        "category": case["category"],
        "arm": arm,
        "status": "PASS" if passed else "FAIL",
        "terminal_state": memory.terminal_state,
        "lifecycle_events": memory.events,
        "selected_evidence_ids": selected,
        "answer": answer,
        "attempts": script["attempts"],
        "checks": checks,
        "metrics": {
            "steps": script["steps"],
            "tool_calls": len(attempts),
            "context_chars": sum(
                len(memory["text"])
                for memory in case["memories"]
                if memory["id"] in selected
            ),
            "input_tokens": None,
            "output_tokens": None,
            "provider_cost_usd": None,
        },
        "judge": {
            "name": "deterministic-contract-stub",
            "verdict": "pass" if passed else "fail",
            "rationale": [name for name, ok in checks.items() if not ok],
        },
    }


def _summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    arms: dict[str, dict[str, int | float]] = {}
    for arm in ("ghost-memory", "no-memory"):
        selected = [item for item in results if item["arm"] == arm]
        passed = sum(item["status"] == "PASS" for item in selected)
        arms[arm] = {
            "cases": len(selected),
            "passed": passed,
            "failed": len(selected) - passed,
            "pass_rate": passed / len(selected) if selected else 0.0,
        }
    return {
        "arms": arms,
        "task_success_delta": arms["ghost-memory"]["pass_rate"]
        - arms["no-memory"]["pass_rate"],
        "isolation_violations": sum(
            not item["checks"]["forbidden_evidence"] for item in results
        ),
        "forbidden_effects": sum(
            not item["checks"]["forbidden_effects"] for item in results
        ),
        "claimable": False,
    }


def write_bundle(path: Path, bundle: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8")
