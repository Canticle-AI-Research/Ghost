"""Run Ghost's canonical documentation/continuity closeout sequence."""

from __future__ import annotations

import argparse
import subprocess
import sys

from .model import ROOT


def _run(*args: str) -> None:
    subprocess.run([sys.executable, *args], cwd=ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", required=True)
    parser.add_argument("--snapshot-entries", type=int, default=5)
    args = parser.parse_args()
    _run("-m", "tools.history.rebuild_index")
    _run("-m", "tools.history.verify_handoffs")
    _run(
        "-m",
        "tools.history.write_snapshot",
        "--agent",
        args.agent,
        "--entries",
        str(args.snapshot_entries),
    )
    _run("-m", "tools.history.verify_continuity", "--require-snapshot")
    _run(
        "-m",
        "pytest",
        "tests/test_docs.py",
        "tests/test_history_tools.py",
        "tests/test_licensing.py",
        # The closeout must not be quieter than the gate that blocks a PR.
        "tests/test_recorded_facts.py",
        "tests/test_local_gates.py",
        "-q",
    )


if __name__ == "__main__":
    main()
