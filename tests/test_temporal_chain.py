"""Credential-free proof that the reusable continuity starter remains installable."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "templates" / "temporal-chain" / "install.py"


def _run(*args: str, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603
        list(args),
        cwd=cwd,
        capture_output=True,
        check=check,
        text=True,
    )


def test_template_installs_verifies_and_refuses_overwrite(tmp_path: Path) -> None:
    git = shutil.which("git")
    assert git is not None
    repo = tmp_path / "proof"
    repo.mkdir()
    _run(git, "init", "-q", cwd=repo)

    command = (
        sys.executable,
        str(INSTALLER),
        "--repo",
        str(repo),
        "--project-name",
        "Continuity Proof",
    )
    _run(*command, cwd=ROOT)
    _run(sys.executable, "-m", "tools.history.verify_continuity", cwd=repo)
    _run(
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-p",
        "test_history_tools.py",
        cwd=repo,
    )

    collision = _run(*command, cwd=ROOT, check=False)
    assert collision.returncode != 0
    assert "refusing to overwrite existing files" in collision.stderr
