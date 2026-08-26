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
PUBLIC_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "public-ci.yml"
TESTS_DIR = REPO_ROOT / "tests"

# Jobs that must never resolve the private SEAM dependency. They live in the
# PUBLIC workflow: Ghost is public, so hosted minutes are free, and running them
# on every push and pull request is strictly better than gating them behind a
# manual dispatch that needs a registered self-hosted runner to move at all.
CREDENTIAL_FREE_JOBS = ("repo-hygiene", "brand-assets", "package-smoke")
# The job that installs the project and runs everything, in the PRIVATE workflow.
PRIVATE_TIER_JOB = "tests"

_GHOST_IMPORT = re.compile(r"^\s*(?:from|import)\s+ghost\b", re.MULTILINE)
# Split so this file never matches itself.
_LIVE_MARKER = "pytest" ".mark.live"


@pytest.fixture(scope="module")
def workflow() -> dict:
    assert CI_WORKFLOW.exists(), f"missing CI workflow at {CI_WORKFLOW}"
    return yaml.safe_load(CI_WORKFLOW.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def public_workflow() -> dict:
    assert PUBLIC_WORKFLOW.exists(), (
        f"missing public workflow at {PUBLIC_WORKFLOW}"
    )
    return yaml.safe_load(PUBLIC_WORKFLOW.read_text(encoding="utf-8"))


def _triggers(workflow: dict) -> dict:
    # PyYAML 1.1 parses the unquoted YAML key `on` as boolean true.
    return workflow.get("on") or workflow.get(True) or {}


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


def test_credential_free_tests_also_run_without_the_private_sdk(public_workflow) -> None:
    """The load-bearing invariant.

    Every test file that does not import `ghost` must be named by a job that
    never syncs the project. Otherwise CI's only meaningful signal depends on
    two private repositories being reachable -- and, since the private workflow
    needs a registered self-hosted runner, on that runner existing at all.
    """
    credential_free_commands = " ".join(
        _job_commands(public_workflow, job) for job in CREDENTIAL_FREE_JOBS
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


def test_live_marked_tests_actually_run_in_a_job(workflow) -> None:
    """`-m "not live"` in pyproject DESELECTS rather than skips, which strict
    no-skip cannot see. Without this invariant a live test could sit in the
    tree running in no lane at all -- and the live tests are the only ones that
    prove Ghost works, so that failure would be silent and total.
    """
    this_file = Path(__file__).resolve()
    live_files = sorted(
        path.relative_to(REPO_ROOT).as_posix()
        for path in _test_files()
        if path.resolve() != this_file and _LIVE_MARKER in path.read_text(encoding="utf-8")
    )
    assert live_files, "no live-marked test files found; the detector is wrong"

    commands = _job_commands(workflow, "live")
    assert "-m live" in commands, (
        "the `live` job no longer selects the live tests back, so they run nowhere"
    )
    # The job runs the whole marker set, so naming the marker is enough; but a
    # path filter would silently narrow it.
    narrowed = [f for f in live_files if "tests/" in commands and f not in commands]
    assert not narrowed or "-m live" in commands, (
        f"the live job filters by path and omits: {narrowed}"
    )


def test_live_tests_require_explicit_manual_selection(workflow) -> None:
    """A private manual run must not silently spend provider credit."""
    condition = str(workflow["jobs"]["live"].get("if", ""))
    assert "inputs.run_live" in condition, "the live job has no explicit paid-run input"


def test_live_job_degrades_to_skipped_without_a_key(workflow) -> None:
    """An unconfigured repository must show `live` as skipped, not failed."""
    assert "live-key-present" in (workflow["jobs"]["live"].get("needs") or [])
    condition = str(workflow["jobs"]["live"].get("if", ""))
    assert "live-key-present" in condition and "available" in condition


def test_credential_free_jobs_never_sync_the_project(public_workflow) -> None:
    """`uv sync` resolves the private git dependency. A job claiming to be
    credential-free must not do it, or the claim silently stops being true."""
    for job in CREDENTIAL_FREE_JOBS:
        commands = _job_commands(public_workflow, job)
        assert "uv sync" not in commands, f"`{job}` runs `uv sync` and is no longer credential-free"
        assert "uv run --no-project" in commands or "uv build" in commands, (
            f"`{job}` neither builds nor uses --no-project; check it stays project-free"
        )


def test_fast_gates_run_automatically_rather_than_gating_the_private_tier(
    public_workflow,
) -> None:
    """The fast gates must report without anyone dispatching anything.

    They used to be `needs:` of the private tier, which is impossible across
    workflows and was worse anyway: it made lint and docs results depend on a
    manual dispatch reaching a registered runner. Running them automatically on
    hosted infrastructure is the stronger guarantee, so this asserts that rather
    than a cross-workflow dependency that cannot exist.
    """
    triggers = _triggers(public_workflow)
    assert "pull_request" in triggers and "push" in triggers
    for job in CREDENTIAL_FREE_JOBS:
        assert job in public_workflow["jobs"], f"fast gate `{job}` is not in the public workflow"
        assert public_workflow["jobs"][job]["runs-on"] == "ubuntu-latest", (
            f"fast gate `{job}` left hosted infrastructure and now needs a runner to exist"
        )


def test_linter_runs_over_the_whole_tree_in_a_required_job(public_workflow) -> None:
    """pyproject configures ruff; CI must run it over everything.

    A narrowed scope is how a finding in an unlisted path stays green forever.
    """
    commands = _job_commands(public_workflow, "repo-hygiene")
    assert "ruff check ." in commands, "the lint step no longer covers the whole tree"


def test_canonical_docs_and_history_run_in_the_credential_free_gate(public_workflow) -> None:
    """Code, blueprint, history index, and handoff chain must move together."""
    commands = _job_commands(public_workflow, "repo-hygiene")
    assert "tests/test_docs.py" in commands
    assert "tests/test_history_tools.py" in commands
    assert "tests/test_licensing.py" in commands
    assert "tools.history.verify_continuity" in commands


def test_secret_scanning_runs(public_workflow) -> None:
    """Ghost is public and documents private infrastructure."""
    assert "gitleaks" in _job_commands(public_workflow, "repo-hygiene")


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


def test_all_private_jobs_target_the_self_hosted_runner(workflow) -> None:
    """Only work that genuinely needs the private SDK may remain on the runner.

    Anything else belongs on hosted infrastructure, where it runs without a
    registered runner existing.
    """
    for name, job in workflow["jobs"].items():
        assert job.get("runs-on") == ["self-hosted", "seam-box"], (
            f"job `{name}` does not target seam-box: {job.get('runs-on')}"
        )


def test_privileged_workflow_is_manual_only(workflow) -> None:
    """Public PR code must never receive an automatic seam-box assignment."""
    triggers = _triggers(workflow)
    assert set(triggers) == {"workflow_dispatch"}
    assert "pull_request" not in triggers
    assert "push" not in triggers


def test_public_continuity_runs_on_hosted_infrastructure(public_workflow) -> None:
    """Fork-safe continuity is automatic and cannot resolve private dependencies."""
    triggers = _triggers(public_workflow)
    assert "pull_request" in triggers
    assert "push" in triggers
    job = public_workflow["jobs"]["repo-hygiene"]
    assert job["runs-on"] == "ubuntu-latest"
    commands = _job_commands(public_workflow, "repo-hygiene")
    assert "uv sync" not in commands
    assert "tools.history.verify_append_only" in commands
    assert "tools.history.verify_continuity" in commands
    assert "tests/test_history_tools.py" in commands
    assert "tests/test_licensing.py" in commands
    assert "gitleaks" in commands


def test_public_diff_hygiene_checks_the_event_range(public_workflow) -> None:
    commands = _job_commands(public_workflow, "repo-hygiene")
    assert "git diff --check" in commands
    assert "BASE_SHA" in commands and "HEAD_SHA" in commands
    checkout = public_workflow["jobs"]["repo-hygiene"]["steps"][0]
    assert checkout.get("with", {}).get("fetch-depth") == 0


def test_superseded_runs_are_cancelled(workflow) -> None:
    """One runner, one job at a time: stale runs must not queue ahead of fresh."""
    assert workflow["concurrency"]["cancel-in-progress"] is True
