"""Parse and validate the repository's append-only history stream."""

from __future__ import annotations

import hashlib
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HISTORY_PATH = ROOT / "HISTORY.md"
INDEX_PATH = ROOT / "HISTORY_INDEX.md"
PATH_MOVES_PATH = ROOT / "docs" / "history" / "PATH_MOVES.md"
MOVE_ROW = re.compile(
    r"^\|\s*`(?P<old>[^`|]+)`\s*\|\s*(?:`(?P<new>[^`|]+)`|(?P<removed>removed))\s*\|"
    r"\s*HISTORY#(?P<entry>\d{3})\s*\|",
    re.MULTILINE,
)
ENTRY_HEADING = re.compile(r"^## HISTORY#(?P<id>\d{3}) — (?P<title>.+)$", re.MULTILINE)
METADATA = re.compile(r"^- (?P<key>[A-Za-z][A-Za-z -]+):\s*(?P<value>.*)$", re.MULTILINE)
REQUIRED_FIELDS = {
    "date", "agent", "status", "topics", "commits", "refs", "supersedes", "verification"
}
VALID_STATUSES = {"planned", "in-progress", "done", "changed", "deferred", "abandoned"}
FORBIDDEN = (
    re.compile(r"https?://(?:chatgpt\.com|chat\.openai\.com|claude\.ai)/share/", re.I),
    re.compile(r"\b(?:sk-proj-|ghp_|github_pat_)[A-Za-z0-9_-]{12,}"),
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"),
)


@dataclass(frozen=True, slots=True)
class HistoryEntry:
    id: int
    title: str
    date: datetime
    status: str
    topics: tuple[str, ...]
    commits: tuple[str, ...]
    refs: tuple[str, ...]
    supersedes: tuple[int, ...]
    raw: str

    @property
    def label(self) -> str:
        return f"HISTORY#{self.id:03d}"


def _csv(value: str) -> tuple[str, ...]:
    value = value.strip().strip("`")
    if value.lower() in {"", "none", "n/a"}:
        return ()
    return tuple(part.strip().strip("`") for part in value.split(",") if part.strip())


def parse_history(text: str) -> list[HistoryEntry]:
    headings = list(ENTRY_HEADING.finditer(text))
    if not headings:
        raise ValueError("HISTORY.md has no entries")
    entries = []
    for position, heading in enumerate(headings):
        end = headings[position + 1].start() if position + 1 < len(headings) else len(text)
        raw = text[heading.start():end].rstrip() + "\n"
        metadata = {
            match.group("key").strip().lower(): match.group("value").strip()
            for match in METADATA.finditer(raw)
        }
        missing = REQUIRED_FIELDS - metadata.keys()
        if missing:
            raise ValueError(f"HISTORY#{heading.group('id')} missing {sorted(missing)}")
        date = datetime.fromisoformat(metadata["date"].strip("`"))
        if date.tzinfo is None:
            raise ValueError("history dates require a timezone")
        status = metadata["status"].strip("`").lower()
        if status not in VALID_STATUSES:
            raise ValueError(f"invalid history status: {status}")
        supersedes = []
        for value in _csv(metadata["supersedes"]):
            match = re.fullmatch(r"(?:HISTORY#)?(\d{1,3})", value, re.I)
            if not match:
                raise ValueError(f"invalid supersedes value: {value}")
            supersedes.append(int(match.group(1)))
        entries.append(HistoryEntry(
            id=int(heading.group("id")), title=heading.group("title").strip(), date=date,
            status=status, topics=_csv(metadata["topics"]), commits=_csv(metadata["commits"]),
            refs=_csv(metadata["refs"]), supersedes=tuple(supersedes), raw=raw,
        ))
    return entries


def load_path_moves(path: Path = PATH_MOVES_PATH) -> dict[str, str | None]:
    """Keep immutable history refs resolvable after a path moves or is removed."""

    if not path.exists():
        return {}
    moves: dict[str, str | None] = {}
    for match in MOVE_ROW.finditer(path.read_text(encoding="utf-8")):
        old = match.group("old").strip()
        if old in moves:
            raise ValueError(f"path-move ledger lists {old} more than once")
        moves[old] = None if match.group("removed") else match.group("new").strip()
    return moves


def resolve_ref(ref: str, moves: dict[str, str | None]) -> str | None:
    """Follow the move chain to the current path, or ``None`` when removed."""

    seen: set[str] = set()
    current = ref
    while current in moves:
        if current in seen:
            raise ValueError(f"path-move ledger has a cycle at {current}")
        seen.add(current)
        target = moves[current]
        if target is None:
            return None
        current = target
    return current


def validate_entries(entries: list[HistoryEntry], *, check_refs: bool = True) -> None:
    if [entry.id for entry in entries] != list(range(1, len(entries) + 1)):
        raise ValueError("history ids must be contiguous from 001")
    moves = load_path_moves() if check_refs else {}
    known: set[int] = set()
    previous: datetime | None = None
    for entry in entries:
        if previous and entry.date < previous:
            raise ValueError(f"{entry.label} has a regressing timestamp")
        previous = entry.date
        if any(prior not in known for prior in entry.supersedes):
            raise ValueError(f"{entry.label} supersedes a missing or later entry")
        known.add(entry.id)
        for ref in entry.refs:
            if not check_refs or "://" in ref or ref.startswith("HISTORY#"):
                continue
            target = resolve_ref(ref, moves)
            if target is None:
                continue
            if not (ROOT / target).exists():
                detail = ref if target == ref else f"{ref}, moved to {target},"
                raise ValueError(f"{entry.label} references missing path {detail}")
        for pattern in FORBIDDEN:
            if pattern.search(entry.raw):
                raise ValueError(f"{entry.label} contains forbidden material")


def load_history(*, check_refs: bool = True) -> list[HistoryEntry]:
    entries = parse_history(HISTORY_PATH.read_text(encoding="utf-8"))
    validate_entries(entries, check_refs=check_refs)
    return entries


def history_sha256() -> str:
    return hashlib.sha256(HISTORY_PATH.read_bytes()).hexdigest()


def history_at(ref: str) -> str | None:
    commit = subprocess.run(  # noqa: S603
        ["git", "cat-file", "-e", f"{ref}^{{commit}}"],  # noqa: S607
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    if commit.returncode != 0:
        raise ValueError(f"base revision does not exist: {ref}")
    result = subprocess.run(  # noqa: S603
        ["git", "show", f"{ref}:HISTORY.md"],  # noqa: S607
        cwd=ROOT,
        capture_output=True,
        check=False,
        text=True,
    )
    return result.stdout if result.returncode == 0 else None
