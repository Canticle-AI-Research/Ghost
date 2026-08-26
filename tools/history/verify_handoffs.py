"""Verify Ghost's registered handoffs form one chronological chain."""

from __future__ import annotations

from datetime import datetime

from .handoffs import load_handoffs
from .model import load_history


def verify() -> None:
    latest, handoffs = load_handoffs()
    history = {entry.id: entry for entry in load_history()}
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
        datetime.fromisoformat(handoff.created_at)
        if position + 1 < len(handoffs):
            older = handoffs[position + 1]
            if handoff.history_id <= older.history_id:
                raise ValueError("handoff history IDs are not strictly newest-first")
            if history[handoff.history_id].date < history[older.history_id].date:
                raise ValueError("handoff history timestamps regress")


def main() -> None:
    verify()
    print("handoff continuity verified")


if __name__ == "__main__":
    main()
