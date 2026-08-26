"""Write an ignored bounded continuity snapshot."""

import argparse
import json
import subprocess
from datetime import UTC, datetime

from .handoffs import load_handoffs
from .model import ROOT, history_sha256, load_history

SNAPSHOT_DIR = ROOT / ".continuity" / "snapshots"


def _git(*args: str) -> str:
    result = subprocess.run(  # noqa: S603
        ["git", *args],  # noqa: S607
        cwd=ROOT,
        capture_output=True,
        check=False,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else "unavailable"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", required=True)
    parser.add_argument("--entries", type=int, default=5)
    args = parser.parse_args()
    entries = load_history()
    latest_handoff, _ = load_handoffs()
    now = datetime.now(UTC)
    payload = {
        "schema": "repo-continuity-snapshot/1", "created_at": now.isoformat(),
        "agent": args.agent, "branch": _git("branch", "--show-current"),
        "head": _git("rev-parse", "HEAD"), "origin_main": _git("rev-parse", "origin/main"),
        "history_sha256": history_sha256(), "latest_history": entries[-1].label,
        "latest_handoff": latest_handoff,
        "entries": [entry.label for entry in entries[-args.entries:]],
        "dirty_paths": _git("status", "--short").splitlines(),
    }
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    path = SNAPSHOT_DIR / now.strftime("%Y%m%dT%H%M%SZ.json")
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
