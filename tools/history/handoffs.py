"""Parse Ghost's single-head tracked handoff chain."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

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


def _read_document(path: str, *, root: Path = ROOT) -> Handoff:
    text = (root / path).read_text(encoding="utf-8")
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


def load_handoffs(*, root: Path = ROOT) -> tuple[str, list[Handoff]]:
    index = root / "docs" / "handoffs" / "INDEX.md"
    text = index.read_text(encoding="utf-8")
    latest_match = LATEST.search(text)
    if not latest_match:
        raise ValueError("handoff index has no latest field")
    rows = list(ROW.finditer(text))
    if not rows:
        raise ValueError("handoff index has no registered documents")
    paths = [row.group("path") for row in rows]
    if len(paths) != len(set(paths)):
        raise ValueError("handoff index registers a document more than once")
    handoff_dir = root / "docs" / "handoffs"
    documents = {
        path.relative_to(root).as_posix()
        for path in handoff_dir.glob("*.md")
        if path.name != "INDEX.md"
    }
    if set(paths) != documents:
        missing = sorted(documents - set(paths))
        stale = sorted(set(paths) - documents)
        raise ValueError(
            f"handoff registry mismatch: unregistered={missing}, missing={stale}"
        )

    handoffs = []
    for row in rows:
        path = row.group("path")
        handoff = _read_document(path, root=root)
        row_supersedes = row.group("supersedes").strip().strip("`")
        row_values = (
            row.group("id").strip().strip("`"),
            row.group("status").strip().strip("`"),
            int(row.group("history").removeprefix("HISTORY#")),
            None if row_supersedes.lower() == "none" else row_supersedes,
        )
        document_values = (
            handoff.handoff_id,
            handoff.status,
            handoff.history_id,
            handoff.supersedes,
        )
        if row_values != document_values:
            raise ValueError(f"invalid handoff metadata: {path}")
        handoffs.append(handoff)
    return latest_match.group(1), handoffs
