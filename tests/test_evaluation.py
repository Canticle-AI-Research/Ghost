"""Frozen Stage 1 fixture, smoke-runner, and bundle-integrity contracts."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from tools.evaluation.fixtures import REQUIRED_CATEGORIES, load_fixtures
from tools.evaluation.integrity import seal_bundle, sha256_canonical, verify_bundle
from tools.evaluation.runner import EvaluationError, run_smoke

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "evals" / "stage1" / "fixtures.json"
MANIFEST = ROOT / "evals" / "stage1" / "MANIFEST.json"
BASELINE = (
    ROOT / "evals" / "runs" / "stage1" / "ghost-stage1-frozen-v1-bil0-baseline.json"
)


def test_frozen_manifest_matches_the_exact_fixture_corpus() -> None:
    fixtures = load_fixtures(FIXTURES)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    assert manifest["status"] == "frozen"
    assert manifest["suite_id"] == fixtures["suite_id"]
    assert manifest["fixture_sha256"] == sha256_canonical(fixtures)
    assert manifest["case_count"] == len(fixtures["cases"]) == 20
    assert manifest["case_ids"] == sorted(case["id"] for case in fixtures["cases"])
    assert {case["category"] for case in fixtures["cases"]} == REQUIRED_CATEGORIES


def test_smoke_bundle_has_named_baseline_and_zero_safety_violations() -> None:
    bundle = run_smoke(FIXTURES, repo_root=ROOT, allow_dirty=True)
    result = bundle["result"]

    assert verify_bundle(bundle)["status"] == "PASS"
    assert result["integrity_level"] == "BIL-0"
    assert result["baseline"] == "no-memory"
    assert result["candidate"] == "ghost-memory"
    assert result["summary"]["arms"]["ghost-memory"]["failed"] == 0
    assert result["summary"]["arms"]["no-memory"]["failed"] > 0
    assert result["summary"]["isolation_violations"] == 0
    assert result["summary"]["forbidden_effects"] == 0
    assert result["summary"]["claimable"] is False


def test_tracked_baseline_is_clean_source_bound_and_verifiable() -> None:
    bundle = json.loads(BASELINE.read_text(encoding="utf-8"))
    fixtures = load_fixtures(FIXTURES)

    assert verify_bundle(bundle)["status"] == "PASS"
    assert bundle["manifest"]["git_sha"] == "bc18555d364a9ed49ce9be2e6c35378bbad29467"
    assert bundle["manifest"]["dirty_worktree"] is False
    assert bundle["manifest"]["fixture_sha256"] == sha256_canonical(fixtures)
    assert bundle["result"]["summary"]["claimable"] is False


def test_bundle_verification_detects_result_and_manifest_tampering() -> None:
    bundle = run_smoke(FIXTURES, repo_root=ROOT, allow_dirty=True)
    result_tamper = copy.deepcopy(bundle)
    result_tamper["result"]["cases"][0]["status"] = "FAIL"
    assert verify_bundle(result_tamper)["status"] == "FAIL"

    manifest_tamper = copy.deepcopy(bundle)
    manifest_tamper["manifest"]["case_ids"].append("invented-case")
    assert verify_bundle(manifest_tamper)["status"] == "FAIL"


def test_volatile_timing_does_not_change_the_result_hash() -> None:
    bundle = run_smoke(FIXTURES, repo_root=ROOT, allow_dirty=True)
    changed = copy.deepcopy(bundle["result"])
    changed["elapsed_ms"] = 999999
    resealed = seal_bundle(result=changed, manifest=bundle["manifest"])

    assert resealed["hashes"]["result_sha256"] == bundle["hashes"]["result_sha256"]


def test_runner_refuses_a_dirty_source_without_an_explicit_smoke_override(
    monkeypatch,
) -> None:
    monkeypatch.setattr("tools.evaluation.runner.git_identity", lambda root: ("a" * 40, True))
    with pytest.raises(EvaluationError, match="dirty worktree"):
        run_smoke(FIXTURES, repo_root=ROOT)


def test_cli_smoke_verify_and_gate_round_trip(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle.json"
    smoke = subprocess.run(  # noqa: S603 - fixed current interpreter and module
        [
            sys.executable,
            "-m",
            "tools.evaluation",
            "smoke",
            "--allow-dirty",
            "--output",
            str(bundle),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert smoke.returncode == 0, smoke.stderr

    for command in ("verify", "gate"):
        result = subprocess.run(  # noqa: S603 - fixed current interpreter and module
            [sys.executable, "-m", "tools.evaluation", command, str(bundle)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert json.loads(result.stdout)["status"] == "PASS"
