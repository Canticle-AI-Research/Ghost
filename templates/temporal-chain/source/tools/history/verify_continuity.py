"""Verify history, derived index, handoffs, and optional snapshot coverage."""

import argparse
import json

from .handoffs import load_handoffs
from .model import INDEX_PATH, history_sha256, load_history
from .rebuild_index import render_index
from .verify_handoffs import verify as verify_handoffs
from .write_snapshot import SNAPSHOT_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-snapshot", action="store_true")
    args = parser.parse_args()
    entries = load_history()
    if not INDEX_PATH.exists() or INDEX_PATH.read_text(encoding="utf-8") != render_index():
        raise ValueError("HISTORY_INDEX.md is stale; run tools.history.rebuild_index")
    verify_handoffs()
    snapshots = sorted(SNAPSHOT_DIR.glob("*.json"))
    if args.require_snapshot and not snapshots:
        raise ValueError("no continuity snapshot exists")
    if snapshots:
        payload = json.loads(snapshots[-1].read_text(encoding="utf-8"))
        latest_handoff, _ = load_handoffs()
        if payload.get("history_sha256") != history_sha256():
            raise ValueError("latest snapshot does not cover HISTORY.md")
        if payload.get("latest_handoff") != latest_handoff:
            raise ValueError("latest snapshot points to a stale handoff")
    print(f"continuity verified: {len(entries)} entries, latest={entries[-1].label}")


if __name__ == "__main__":
    main()
