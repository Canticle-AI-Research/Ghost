"""Verify Ghost's registered handoffs form one chronological chain."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .handoffs import load_handoffs
from .model import ROOT, load_history


def verify(*, root: Path = ROOT) -> None:
    latest, handoffs = load_handoffs(root=root)
    history = {
        entry.id: entry
        for entry in load_history(root / "HISTORY.md", check_refs=False)
    }
    if latest != handoffs[0].path:
        raise ValueError("latest does not match the first handoff row")
    if handoffs[0].status != "current":
        raise ValueError("newest handoff is not current")
    if sum(item.status == "current" for item in handoffs) != 1:
        raise ValueError("handoff registry must have exactly one current head")

    ids = {item.handoff_id for item in handoffs}
    if len(ids) != len(handoffs):
        raise ValueError("duplicate handoff_id")
    for position, handoff in enumerate(handoffs):
        if handoff.history_id not in history:
            raise ValueError(f"{handoff.path} references missing history")
        expected = handoffs[position + 1].handoff_id if position + 1 < len(handoffs) else None
        if handoff.supersedes != expected:
            raise ValueError(f"{handoff.path} breaks the supersession chain")
        created_at = datetime.fromisoformat(handoff.created_at)
        if position + 1 < len(handoffs):
            older = handoffs[position + 1]
            older_created_at = datetime.fromisoformat(older.created_at)
            if created_at <= older_created_at:
                raise ValueError("handoff created_at values are not strictly newest-first")
            if handoff.history_id <= older.history_id:
                raise ValueError("handoff history IDs are not strictly newest-first")
            if history[handoff.history_id].date < history[older.history_id].date:
                raise ValueError("handoff history timestamps regress")


def main() -> None:
    verify()
    print("handoff continuity verified")


if __name__ == "__main__":
    main()
