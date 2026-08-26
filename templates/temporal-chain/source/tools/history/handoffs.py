"""Read the registered single-head handoff chain."""

import re
from dataclasses import dataclass
from pathlib import Path

from .model import ROOT

INDEX = ROOT / "docs" / "handoffs" / "INDEX.md"
LATEST = re.compile(r"^latest:\s*`?([^`\s]+)`?\s*$", re.MULTILINE)
ROW = re.compile(
    r"^\|\s*`(?P<path>docs/handoffs/[^`]+\.md)`\s*\|\s*(?P<id>[^|]+?)\s*\|"
    r"\s*(?P<status>[^|]+?)\s*\|\s*(?P<history>HISTORY#\d{3})\s*\|"
    r"\s*(?P<supersedes>[^|]+?)\s*\|\s*$", re.MULTILINE,
)
FIELD = re.compile(
    r"^(?P<key>handoff_id|supersedes|handoff_status|history|created_at):"
    r"\s*`?(?P<value>[^`\n]+)`?\s*$", re.MULTILINE,
)


@dataclass(frozen=True, slots=True)
class Handoff:
    path: str
    handoff_id: str
    status: str
    history_id: int
    supersedes: str | None
    created_at: str


def load_handoffs(*, root: Path = ROOT) -> tuple[str, list[Handoff]]:
    text = (root / "docs" / "handoffs" / "INDEX.md").read_text(encoding="utf-8")
    latest = LATEST.search(text)
    if not latest:
        raise ValueError("handoff index has no latest field")
    rows = list(ROW.finditer(text))
    paths = [row.group("path") for row in rows]
    documents = {
        path.relative_to(root).as_posix()
        for path in (root / "docs" / "handoffs").glob("*.md")
        if path.name != "INDEX.md"
    }
    if not rows or len(paths) != len(set(paths)) or set(paths) != documents:
        raise ValueError("handoff index has invalid registered documents")
    handoffs = []
    for row in rows:
        path = row.group("path")
        document = (root / path).read_text(encoding="utf-8")
        fields = {
            match.group("key"): match.group("value").strip()
            for match in FIELD.finditer(document)
        }
        if set(fields) != {"handoff_id", "supersedes", "handoff_status", "history", "created_at"}:
            raise ValueError(f"invalid handoff metadata: {path}")
        handoff = Handoff(
            path, fields["handoff_id"], fields["handoff_status"],
            int(fields["history"].removeprefix("HISTORY#")),
            None if fields["supersedes"] == "none" else fields["supersedes"],
            fields["created_at"],
        )
        row_supersedes = row.group("supersedes").strip().strip("`")
        row_values = (
            row.group("id").strip().strip("`"),
            row.group("status").strip().strip("`"),
            int(row.group("history").removeprefix("HISTORY#")),
            None if row_supersedes == "none" else row_supersedes,
        )
        if row_values != (
            handoff.handoff_id, handoff.status, handoff.history_id, handoff.supersedes
        ):
            raise ValueError(f"invalid handoff metadata: {path}")
        handoffs.append(handoff)
    return latest.group(1), handoffs
