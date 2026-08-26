"""Read the registered single-head handoff chain."""

import re
from dataclasses import dataclass

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


def load_handoffs() -> tuple[str, list[Handoff]]:
    text = INDEX.read_text(encoding="utf-8")
    latest = LATEST.search(text)
    if not latest:
        raise ValueError("handoff index has no latest field")
    handoffs = []
    for row in ROW.finditer(text):
        path = row.group("path")
        document = (ROOT / path).read_text(encoding="utf-8")
        fields = {
            match.group("key"): match.group("value").strip()
            for match in FIELD.finditer(document)
        }
        if set(fields) != {"handoff_id", "supersedes", "handoff_status", "history", "created_at"}:
            raise ValueError(f"invalid handoff metadata: {path}")
        handoffs.append(Handoff(
            path, fields["handoff_id"], fields["handoff_status"],
            int(fields["history"].removeprefix("HISTORY#")),
            None if fields["supersedes"] == "none" else fields["supersedes"],
            fields["created_at"],
        ))
    if not handoffs:
        raise ValueError("handoff index has no rows")
    return latest.group(1), handoffs
