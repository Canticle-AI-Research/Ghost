"""Fail closed on Ghost history, index, handoff, and snapshot drift."""

from __future__ import annotations

import argparse
import json

from .handoffs import load_handoffs
from .model import INDEX_PATH, ROOT, history_sha256, load_history
from .rebuild_index import render_index
from .recorded_fact_audit import audit_latest_entry, audit_recorded_facts
from .verify_handoffs import verify as verify_handoffs
from .write_snapshot import SNAPSHOT_DIR


def _verify_snapshot(*, required: bool) -> None:
    snapshots = sorted(SNAPSHOT_DIR.glob("*.json"))
    if not snapshots:
        if required:
            raise ValueError("no continuity snapshot exists")
        return
    payload = json.loads(snapshots[-1].read_text(encoding="utf-8"))
    if payload.get("schema") != "ghost-snapshot/1":
        raise ValueError("latest snapshot has an unknown schema")
    if payload.get("history_sha256") != history_sha256():
        raise ValueError("latest snapshot does not cover current HISTORY.md")
    if payload.get("latest_history") != load_history()[-1].label:
        raise ValueError("latest snapshot points to stale history")
    latest_handoff, _handoffs = load_handoffs()
    if payload.get("latest_handoff") != latest_handoff:
        raise ValueError("latest snapshot points to a stale handoff")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-snapshot", action="store_true")
    args = parser.parse_args()
    entries = load_history()
    expected = render_index()
    if not INDEX_PATH.exists() or INDEX_PATH.read_text(encoding="utf-8") != expected:
        raise ValueError(
            "HISTORY_INDEX.md is stale; run "
            "uv run python -m tools.history.rebuild_index"
        )
    verify_handoffs()
    _verify_snapshot(required=args.require_snapshot)
    # Deliberately not suppressible. A gate that can be quietened converts
    # "unverified" into "verified", which is the state the next agent acts on.
    issues = audit_recorded_facts() + audit_latest_entry()
    if issues:
        listed = "\n".join(f"- {issue.format()}" for issue in issues)
        raise ValueError(f"recorded-fact audit found stale claims:\n{listed}")
    print(
        f"continuity verified: {len(entries)} entries, "
        f"latest={entries[-1].label}, facts audited, root={ROOT.name}"
    )


if __name__ == "__main__":
    # A gate should report what failed, not a stack trace. The traceback tells
    # the operator about this file; the message tells them about their repo.
    try:
        main()
    except ValueError as failure:
        raise SystemExit(f"continuity gate failed: {failure}") from None
