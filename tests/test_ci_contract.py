"""Invariants for public automatic CI and explicitly paid live validation."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
LIVE_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"
PUBLIC_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "public-ci.yml"
HOSTED_PUBLIC_JOBS = ("repo-hygiene", "brand-assets", "tests", "package-smoke")
_LIVE_MARKER = "pytest" ".mark.live"


@pytest.fixture(scope="module")
def live_workflow() -> dict:
    return yaml.safe_load(LIVE_WORKFLOW.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def public_workflow() -> dict:
    return yaml.safe_load(PUBLIC_WORKFLOW.read_text(encoding="utf-8"))


def _triggers(workflow: dict) -> dict:
    # PyYAML 1.1 parses an unquoted `on` key as boolean true.
    return workflow.get("on") or workflow.get(True) or {}


def _job_commands(workflow: dict, job: str) -> str:
    assert job in workflow["jobs"], f"CI has no `{job}` job"
    return " ".join(step.get("run", "") for step in workflow["jobs"][job]["steps"])


def test_full_provider_free_suite_runs_automatically(public_workflow) -> None:
    triggers = _triggers(public_workflow)
    assert "pull_request" in triggers and "push" in triggers
    commands = _job_commands(public_workflow, "tests")
    assert re.search(r"pytest(?!\s+\S*tests/)", commands)
    assert "-m live" not in commands
    checkout = public_workflow["jobs"]["tests"]["steps"][0]
    assert checkout.get("with", {}).get("fetch-depth") == 0


def test_every_automatic_job_uses_disposable_hosted_infrastructure(public_workflow) -> None:
    for name in HOSTED_PUBLIC_JOBS:
        assert public_workflow["jobs"][name]["runs-on"] == "ubuntu-latest"
    assert "self-hosted" not in PUBLIC_WORKFLOW.read_text(encoding="utf-8")


def test_public_install_never_resolves_a_private_source() -> None:
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    lock = (REPO_ROOT / "uv.lock").read_text(encoding="utf-8")
    forbidden = ("git+ssh", "seam-sdk", "Seam_SDK.git", "seam-runtime")
    for marker in forbidden:
        assert marker not in pyproject
        assert marker not in lock


def test_wheel_is_clean_installed_and_command_is_smoked(public_workflow) -> None:
    commands = _job_commands(public_workflow, "package-smoke")
    assert "uv build" in commands
    assert "uv pip install" in commands
    assert 'bin/ghost" --help' in commands


def test_lock_file_is_verified_before_public_install(public_workflow) -> None:
    commands = _job_commands(public_workflow, "tests")
    assert "uv lock --check" in commands
    assert "uv sync --frozen" in commands


def test_python_floor_is_exercised(public_workflow) -> None:
    versions = public_workflow["jobs"]["tests"]["strategy"]["matrix"]["python-version"]
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    floor = re.search(r'requires-python\s*=\s*">=(\d+\.\d+)', pyproject)
    assert floor
    assert floor.group(1) in versions


def test_live_tests_have_one_explicit_manual_paid_lane(live_workflow) -> None:
    triggers = _triggers(live_workflow)
    assert set(triggers) == {"workflow_dispatch"}
    condition = str(live_workflow["jobs"]["live"].get("if", ""))
    assert "inputs.run_live" in condition
    commands = _job_commands(live_workflow, "live")
    assert "-m live" in commands
    assert live_workflow["jobs"]["live"]["runs-on"] == "ubuntu-latest"


def test_live_lane_requires_provider_and_seam_credentials(live_workflow) -> None:
    gate = _job_commands(live_workflow, "live-config-present")
    raw = LIVE_WORKFLOW.read_text(encoding="utf-8")
    assert "PROVIDER_KEY" in gate and "SEAM_URL" in gate and "SEAM_TOKEN" in gate
    assert "SEAM_BASE_URL" in raw and "SEAM_API_TOKEN" in raw
    assert "live-config-present" in (live_workflow["jobs"]["live"].get("needs") or [])


def test_every_live_marked_file_is_selected_by_the_live_lane(live_workflow) -> None:
    live_files = [
        path
        for path in (REPO_ROOT / "tests").glob("test_*.py")
        if _LIVE_MARKER in path.read_text(encoding="utf-8")
    ]
    assert live_files
    assert "-m live" in _job_commands(live_workflow, "live")


def test_strict_no_skip_is_never_disabled() -> None:
    raw = PUBLIC_WORKFLOW.read_text(encoding="utf-8") + LIVE_WORKFLOW.read_text(
        encoding="utf-8"
    )
    assert not re.search(
        r"GHOST_STRICT_NO_SKIP\s*[:=]\s*[\"']?(0|false|no|off)", raw, re.I
    )


def test_public_continuity_and_secret_scan_remain_automatic(public_workflow) -> None:
    commands = _job_commands(public_workflow, "repo-hygiene")
    for marker in (
        "tools.history.verify_append_only",
        "tools.history.verify_continuity",
        "tests/test_history_tools.py",
        "tests/test_licensing.py",
        "git diff --check",
        "gitleaks",
    ):
        assert marker in commands
    checkout = public_workflow["jobs"]["repo-hygiene"]["steps"][0]
    assert checkout.get("with", {}).get("fetch-depth") == 0
    assert "httpx" in commands


def test_brand_lane_installs_the_shared_test_fake_dependency(public_workflow) -> None:
    commands = _job_commands(public_workflow, "brand-assets")
    assert "pillow" in commands
    assert "httpx" in commands


def test_linter_covers_the_whole_tree(public_workflow) -> None:
    assert "ruff check ." in _job_commands(public_workflow, "repo-hygiene")


def test_superseded_runs_are_cancelled(public_workflow, live_workflow) -> None:
    assert public_workflow["concurrency"]["cancel-in-progress"] is True
    assert live_workflow["concurrency"]["cancel-in-progress"] is True
