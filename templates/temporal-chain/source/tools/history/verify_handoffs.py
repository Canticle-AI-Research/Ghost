"""Verify one chronological, single-head handoff chain."""

from datetime import datetime

from .handoffs import load_handoffs
from .model import load_history


def verify() -> None:
    latest, handoffs = load_handoffs()
    history = {entry.id: entry for entry in load_history()}
    if latest != handoffs[0].path or handoffs[0].status != "current":
        raise ValueError("newest handoff is not the declared current head")
    if sum(item.status == "current" for item in handoffs) != 1:
        raise ValueError("handoff registry needs exactly one current head")
    for position, handoff in enumerate(handoffs):
        if handoff.history_id not in history:
            raise ValueError(f"{handoff.path} references missing history")
        expected = handoffs[position + 1].handoff_id if position + 1 < len(handoffs) else None
        if handoff.supersedes != expected:
            raise ValueError(f"{handoff.path} breaks the supersession chain")
        datetime.fromisoformat(handoff.created_at)


if __name__ == "__main__":
    verify()
    print("handoff continuity verified")
