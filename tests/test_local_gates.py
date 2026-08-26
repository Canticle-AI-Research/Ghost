"""The local commit gate must never be quieter than the checks that block a PR.

A local gate that passes where CI will fail is worse than having no local gate:
it converts "unverified" into "verified", and "verified" is the state the next
agent acts on. Ghost's continuity gates were previously enforced only by an
agent remembering to run closeout, which is not enforcement at all.

These tests fail if the commit hook drops a gate, if any gate gains a
suppression flag, or if the hook stops blocking the paths that must never be
committed.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "tools" / "git-hooks" / "pre-commit"
INSTALLER = ROOT / "tools" / "git-hooks" / "install.sh"
PUBLIC_WORKFLOW = ROOT / ".github" / "workflows" / "public-ci.yml"

# The hook must run at least these. verify_append_only is deliberately absent:
# it needs a base revision to diff against, which a pre-commit hook has no
# reliable way to resolve, so CI owns that one.
REQUIRED_GATES = {
    "tools.history.verify_continuity",
    "tools.history.verify_handoffs",
    "tools.history.recorded_fact_audit",
}

SUPPRESSION = re.compile(r"--(?:no|skip|disable)-[\w-]+")


def _hook_text() -> str:
    return HOOK.read_text(encoding="utf-8")


def test_commit_hook_and_installer_exist_and_are_executable() -> None:
    for script in (HOOK, INSTALLER):
        assert script.exists(), f"missing {script.relative_to(ROOT)}"
        assert script.stat().st_mode & 0o111, f"{script.relative_to(ROOT)} is not executable"


def test_commit_hook_runs_every_required_gate() -> None:
    text = _hook_text()
    missing = sorted(gate for gate in REQUIRED_GATES if gate not in text)
    assert not missing, f"pre-commit hook does not run: {missing}"


def test_no_local_gate_passes_a_suppression_flag() -> None:
    """A gate that can be quietened is a false-negative generator."""
    gate_lines = [
        line for line in _hook_text().splitlines() if line.strip().startswith("run_gate")
    ]
    assert gate_lines, "no run_gate lines found; the hook format changed"
    suppressed = [line.strip() for line in gate_lines if SUPPRESSION.search(line)]
    assert not suppressed, f"local gates carry suppression flags: {suppressed}"


def test_recorded_fact_audit_cannot_be_disabled() -> None:
    """verify_continuity must expose no flag that skips the fact audit."""
    source = (ROOT / "tools" / "history" / "verify_continuity.py").read_text(encoding="utf-8")
    assert "audit_recorded_facts" in source, "continuity no longer audits recorded facts"
    flags = set(re.findall(r'add_argument\(\s*"(--[\w-]+)"', source))
    disabling = sorted(flag for flag in flags if SUPPRESSION.match(flag))
    assert not disabling, f"continuity gained a suppression flag: {disabling}"


def test_hook_blocks_agent_local_and_generated_paths() -> None:
    text = _hook_text()
    for pattern in (r"\.claude/", r"\.ghost/", r"checkpoints\\?\.db"):
        assert re.search(pattern, text), f"hook no longer scope-blocks {pattern}"


def test_hook_gates_are_also_reachable_from_ci() -> None:
    """Every gate the hook runs must exist as a real module CI can run too."""
    workflow = PUBLIC_WORKFLOW.read_text(encoding="utf-8")
    assert "tools.history.verify_continuity" in workflow, (
        "the continuity workflow no longer runs verify_continuity; "
        "the local hook would then be stricter than CI, which hides drift on PRs"
    )
    for gate in sorted(REQUIRED_GATES):
        module = ROOT / Path(gate.replace(".", "/") + ".py")
        assert module.exists(), f"hook runs {gate}, but {module.name} does not exist"
