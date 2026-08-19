"""Invariants on the CI workflow itself.

Ported from SEAM's `test_github_pr_gates.py`. The required sets here are
DERIVED FROM THE TREE, never hardcoded: a hardcoded list is exactly how a gate
goes on claiming full coverage while the tree grows past it.

The invariant that matters most for Ghost is the credential split. Ghost's only
runtime dependency is a private git+ssh package, so any test that imports
`ghost` can only run where those private repositories are reachable. Tests that
do NOT import it -- docs, brand assets, this file -- must therefore also run in
a job that never syncs the project, so CI keeps saying something true on a fork,
on a Dependabot PR, and on the day the private remote is down.

This file needs no private dependency itself, by design.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
CI_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"
TESTS_DIR = REPO_ROOT / "tests"

# Jobs that must never resolve the private SEAM dependency.
CREDENTIAL_FREE_JOBS = ("repo-hygiene", "brand-assets", "package-smoke")
# The job that installs the project and runs everything.
PRIVATE_TIER_JOB = "tests"

_GHOST_IMPORT = re.compile(r"^\s*(?:from|import)\s+ghost\b", re.MULTILINE)


@pytest.fixture(scope="module")
def workflow() -> dict:
    assert CI_WORKFLOW.exists(), f"missing CI workflow at {CI_WORKFLOW}"
    return yaml.safe_load(CI_WORKFLOW.read_text(encoding="utf-8"))


def _job_commands(workflow: dict, job: str) -> str:
    assert job in workflow["jobs"], f"CI has no `{job}` job"
    return " ".join(step.get("run", "") for step in workflow["jobs"][job]["steps"])


def _test_files() -> list[Path]:
    found = sorted(TESTS_DIR.glob("test_*.py"))
    assert found, "no test files discovered; the glob is wrong"
    return found


def _needs_private_sdk(path: Path) -> bool:
    """`ghost/__init__.py` imports the application, which imports seam_sdk, so
    importing ANY ghost submodule pulls the private dependency in."""
    return bool(_GHOST_IMPORT.search(path.read_text(encoding="utf-8")))


def test_every_test_file_runs_in_the_full_suite(workflow) -> None:
    """The private tier must invoke pytest with no path filter, so a new test
    file is picked up without anyone remembering to register it."""
    commands = _job_commands(workflow, PRIVATE_TIER_JOB)
    assert re.search(r"pytest(?!\s+\S*tests/)", commands), (
        f"the `{PRIVATE_TIER_JOB}` job no longer runs the unfiltered suite; "
        "test files would only run where they are named explicitly"
    )


def test_credential_free_tests_also_run_without_the_private_sdk(workflow) -> None:
    """The load-bearing invariant.

    Every test file that does not import `ghost` must be named by a job that
    never syncs the project. Otherwise CI's only meaningful signal depends on
    two private repositories being reachable.
    """
    credential_free_commands = " ".join(
        _job_commands(workflow, job) for job in CREDENTIAL_FREE_JOBS
    )

    should_run_publicly = [p for p in _test_files() if not _needs_private_sdk(p)]
    assert should_run_publicly, "no credential-free test files found; the detector is wrong"

    missing = sorted(
        p.relative_to(REPO_ROOT).as_posix()
        for p in should_run_publicly
        if p.relative_to(REPO_ROOT).as_posix() not in credential_free_commands
    )
    assert not missing, (
        "these test files need no private dependency but run only in the private "
        f"tier, so CI says nothing when the SEAM remote is unreachable: {missing}"
    )


def test_credential_free_jobs_never_sync_the_project(workflow) -> None:
    """`uv sync` resolves the private git dependency. A job claiming to be
    credential-free must not do it, or the claim silently stops being true."""
    for job in CREDENTIAL_FREE_JOBS:
        commands = _job_commands(workflow, job)
        assert "uv sync" not in commands, f"`{job}` runs `uv sync` and is no longer credential-free"
        assert "uv run --no-project" in commands or "uv build" in commands, (
            f"`{job}` neither builds nor uses --no-project; check it stays project-free"
        )


def test_private_tier_waits_for_the_fast_gates(workflow) -> None:
    """seam-box runs one job at a time; a lint error must not wait on a sync."""
    needs = workflow["jobs"][PRIVATE_TIER_JOB].get("needs") or []
    missing = sorted(set(CREDENTIAL_FREE_JOBS) - set(needs))
    assert not missing, f"`{PRIVATE_TIER_JOB}` does not wait for: {missing}"


def test_linter_runs_in_a_required_job(workflow) -> None:
    """pyproject configures ruff; CI must actually run it."""
    assert "ruff check" in _job_commands(workflow, "repo-hygiene")


def test_secret_scanning_runs(workflow) -> None:
    """Ghost is public and documents private infrastructure."""
    assert "gitleaks" in _job_commands(workflow, "repo-hygiene")


def test_lock_file_is_verified_before_install(workflow) -> None:
    """uv.lock pins two private git revisions; an unlocked pyproject would
    install a different SEAM than the README names as reviewed."""
    commands = _job_commands(workflow, PRIVATE_TIER_JOB)
    assert "uv lock --check" in commands
    assert "--frozen" in commands, "install must not silently re-resolve the lock"


def test_strict_no_skip_is_never_disabled(workflow) -> None:
    """A lane that exports GHOST_STRICT_NO_SKIP=0 would look identical to a
    clean run while tests quietly stopped executing."""
    raw = CI_WORKFLOW.read_text(encoding="utf-8")
    assert not re.search(r"GHOST_STRICT_NO_SKIP\s*[:=]\s*[\"']?(0|false|no|off)", raw, re.I)


def test_python_floor_is_exercised(workflow) -> None:
    """`requires-python` claims a floor; the matrix must prove it."""
    versions = workflow["jobs"][PRIVATE_TIER_JOB]["strategy"]["matrix"]["python-version"]
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    floor = re.search(r'requires-python\s*=\s*">=(\d+\.\d+)', pyproject)
    assert floor, "could not read requires-python from pyproject.toml"
    assert floor.group(1) in versions, (
        f"requires-python claims >={floor.group(1)} but the matrix tests {versions}"
    )


def test_all_jobs_target_the_self_hosted_runner(workflow) -> None:
    """Hosted runners have neither the SSH credentials nor the brand renderers."""
    for name, job in workflow["jobs"].items():
        assert job.get("runs-on") == ["self-hosted", "seam-box"], (
            f"job `{name}` does not target seam-box: {job.get('runs-on')}"
        )


def test_public_repo_tripwire_is_present(workflow) -> None:
    """Ghost is private today and planned to go public once the site is ready.

    A self-hosted runner is a personal desktop holding SSH keys to two private
    repositories, so that flip is the moment the runner must be detached. This
    asserts the tripwire survives -- it is a reminder to the owner, NOT a
    security boundary (a fork PR ships its own workflow file and can delete it).
    """
    steps = workflow["jobs"]["repo-hygiene"]["steps"]
    guard = [s for s in steps if "private == false" in str(s.get("if", ""))]
    assert guard, (
        "the public-repo tripwire is gone from repo-hygiene; going public would "
        "silently expose seam-box to fork pull requests"
    )
    assert guard[0] is steps[1], (
        "the tripwire must run before any other work, not after the repo has "
        "already been checked out and acted on"
    )


def test_superseded_runs_are_cancelled(workflow) -> None:
    """One runner, one job at a time: stale runs must not queue ahead of fresh."""
    assert workflow["concurrency"]["cancel-in-progress"] is True
