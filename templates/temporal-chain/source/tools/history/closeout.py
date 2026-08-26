"""Run the canonical Temporal Chain closeout."""

import argparse
import subprocess
import sys

from .model import ROOT


def _run(*args: str) -> None:
    subprocess.run([sys.executable, *args], cwd=ROOT, check=True)  # noqa: S603


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", required=True)
    args = parser.parse_args()
    _run("-m", "tools.history.rebuild_index")
    _run("-m", "tools.history.verify_handoffs")
    _run("-m", "tools.history.write_snapshot", "--agent", args.agent)
    _run("-m", "tools.history.verify_continuity", "--require-snapshot")


if __name__ == "__main__":
    main()
