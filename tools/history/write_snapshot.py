"""Write an ignored, bounded Ghost continuity snapshot."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import UTC, datetime

from .handoffs import load_handoffs
from .model import ROOT, history_sha256, load_history

SNAPSHOT_DIR = ROOT / ".ghost" / "snapshots"


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, check=True, text=True
    ).stdout.strip()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", required=True)
    parser.add_argument("--entries", type=int, default=5)
    args = parser.parse_args()
    if args.entries < 1:
        raise SystemExit("--entries must be positive")

    entries = load_history()
    latest_handoff, _handoffs = load_handoffs()
    created = datetime.now(UTC)
    payload = {
        "schema": "ghost-snapshot/1",
        "created_at": created.isoformat(),
        "agent": args.agent,
        "branch": _git("branch", "--show-current"),
        "head": _git("rev-parse", "HEAD"),
        "origin_main": _git("rev-parse", "origin/main"),
        "history_sha256": history_sha256(),
        "latest_history": entries[-1].label,
        "latest_handoff": latest_handoff,
        "entries": [entry.label for entry in entries[-args.entries :]],
        "dirty_paths": _git("status", "--short").splitlines(),
    }
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    path = SNAPSHOT_DIR / created.strftime("%Y%m%dT%H%M%SZ.json")
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
