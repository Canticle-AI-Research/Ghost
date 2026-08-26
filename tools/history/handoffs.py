"""Parse Ghost's single-head tracked handoff chain."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .model import ROOT

INDEX = ROOT / "docs" / "handoffs" / "INDEX.md"
LATEST = re.compile(r"^latest:\s*`?([^`\s]+)`?\s*$", re.MULTILINE)
ROW = re.compile(
    r"^\|\s*`(?P<path>docs/handoffs/[^`]+\.md)`\s*\|\s*(?P<id>[^|]+?)\s*\|"
    r"\s*(?P<status>[^|]+?)\s*\|\s*(?P<history>HISTORY#\d{3})\s*\|"
    r"\s*(?P<supersedes>[^|]+?)\s*\|\s*$",
    re.MULTILINE,
)
FIELD = re.compile(
    r"^(?P<key>handoff_id|supersedes|handoff_status|history|created_at):"
    r"\s*`?(?P<value>[^`\n]+)`?\s*$",
    re.MULTILINE,
)


@dataclass(frozen=True, slots=True)
class Handoff:
    path: str
    handoff_id: str
    status: str
    history_id: int
    supersedes: str | None
    created_at: str


def _read_document(path: str) -> Handoff:
    text = (ROOT / path).read_text(encoding="utf-8")
    fields = {
        match.group("key"): match.group("value").strip()
        for match in FIELD.finditer(text)
    }
    required = {"handoff_id", "supersedes", "handoff_status", "history", "created_at"}
    missing = required - fields.keys()
    if missing:
        raise ValueError(f"{path} missing handoff metadata: {sorted(missing)}")
    supersedes = None if fields["supersedes"].lower() == "none" else fields["supersedes"]
    history = re.fullmatch(r"HISTORY#(\d{3})", fields["history"])
    if not history:
        raise ValueError(f"{path} has invalid history metadata")
    return Handoff(
        path=path,
        handoff_id=fields["handoff_id"],
        status=fields["handoff_status"],
        history_id=int(history.group(1)),
        supersedes=supersedes,
        created_at=fields["created_at"],
    )


def load_handoffs() -> tuple[str, list[Handoff]]:
    text = INDEX.read_text(encoding="utf-8")
    latest_match = LATEST.search(text)
    if not latest_match:
        raise ValueError("handoff index has no latest field")
    paths = [match.group("path") for match in ROW.finditer(text)]
    if not paths:
        raise ValueError("handoff index has no registered documents")
    return latest_match.group(1), [_read_document(path) for path in paths]
