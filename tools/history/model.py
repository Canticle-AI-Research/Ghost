"""Parse and validate Ghost's append-only ``HISTORY.md`` stream."""

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
    "date",
    "agent",
    "status",
    "topics",
    "commits",
    "refs",
    "supersedes",
    "verification",
}
VALID_STATUSES = {"planned", "in-progress", "done", "changed", "deferred", "abandoned"}
FORBIDDEN_PATTERNS = (
    re.compile(r"https?://(?:chatgpt\.com|chat\.openai\.com)/share/", re.I),
    re.compile(r"https?://claude\.ai/share/", re.I),
    re.compile(r"\b(?:sk-proj-|ghp_|github_pat_)[A-Za-z0-9_-]{12,}"),
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"),
)


class HistoryError(ValueError):
    """The canonical history stream violates its schema or chronology."""


@dataclass(frozen=True, slots=True)
class HistoryEntry:
    """One immutable repository event."""

    id: int
    title: str
    date: datetime
    agent: str
    status: str
    topics: tuple[str, ...]
    commits: tuple[str, ...]
    refs: tuple[str, ...]
    supersedes: tuple[int, ...]
    verification: str
    body: str
    raw: str

    @property
    def label(self) -> str:
        return f"HISTORY#{self.id:03d}"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def history_sha256(path: Path = HISTORY_PATH) -> str:
    return sha256_text(path.read_text(encoding="utf-8"))


def _csv(value: str) -> tuple[str, ...]:
    normalized = value.strip().strip("`")
    if normalized.lower() in {"", "none", "n/a"}:
        return ()
    return tuple(part.strip().strip("`") for part in normalized.split(",") if part.strip())


def _supersedes(value: str) -> tuple[int, ...]:
    values = _csv(value)
    parsed = []
    for item in values:
        match = re.fullmatch(r"(?:HISTORY#)?(\d{1,3})", item, re.I)
        if not match:
            raise HistoryError(f"invalid supersedes reference: {item}")
        parsed.append(int(match.group(1)))
    return tuple(parsed)


def parse_history(text: str) -> list[HistoryEntry]:
    """Parse the stream without consulting git or the filesystem."""

    headings = list(ENTRY_HEADING.finditer(text))
    if not headings:
        raise HistoryError("HISTORY.md has no entries")

    entries: list[HistoryEntry] = []
    for position, heading in enumerate(headings):
        start = heading.start()
        end = headings[position + 1].start() if position + 1 < len(headings) else len(text)
        raw = text[start:end].rstrip() + "\n"
        metadata = {
            match.group("key").strip().lower(): match.group("value").strip()
            for match in METADATA.finditer(raw)
        }
        missing = sorted(REQUIRED_FIELDS - metadata.keys())
        if missing:
            raise HistoryError(f"HISTORY#{heading.group('id')} missing fields: {missing}")
        try:
            date = datetime.fromisoformat(metadata["date"].strip("`"))
        except ValueError as exc:
            raise HistoryError(f"HISTORY#{heading.group('id')} has invalid ISO date") from exc
        if date.tzinfo is None:
            raise HistoryError(f"HISTORY#{heading.group('id')} date needs a timezone")
        status = metadata["status"].strip("`").lower()
        if status not in VALID_STATUSES:
            raise HistoryError(f"HISTORY#{heading.group('id')} has invalid status: {status}")
        body_start = max((match.end() for match in METADATA.finditer(raw)), default=0)
        entries.append(
            HistoryEntry(
                id=int(heading.group("id")),
                title=heading.group("title").strip(),
                date=date,
                agent=metadata["agent"].strip("`"),
                status=status,
                topics=_csv(metadata["topics"]),
                commits=_csv(metadata["commits"]),
                refs=_csv(metadata["refs"]),
                supersedes=_supersedes(metadata["supersedes"]),
                verification=metadata["verification"].strip(),
                body=raw[body_start:].strip(),
                raw=raw,
            )
        )
    return entries


def load_path_moves(path: Path = PATH_MOVES_PATH) -> dict[str, str | None]:
    """Read the ledger that keeps immutable history refs resolvable after a move.

    History is append-only, so a renamed or deleted path can never be corrected
    in place. Each row records where an old path went; ``removed`` marks a
    deliberate deletion. The value is ``None`` for a removal.
    """

    if not path.exists():
        return {}
    moves: dict[str, str | None] = {}
    for match in MOVE_ROW.finditer(path.read_text(encoding="utf-8")):
        old = match.group("old").strip()
        if old in moves:
            raise HistoryError(f"path-move ledger lists {old} more than once")
        moves[old] = None if match.group("removed") else match.group("new").strip()
    return moves


def resolve_ref(ref: str, moves: dict[str, str | None]) -> str | None:
    """Follow the move chain to the current path, or ``None`` when removed."""

    seen: set[str] = set()
    current = ref
    while current in moves:
        if current in seen:
            raise HistoryError(f"path-move ledger has a cycle at {current}")
        seen.add(current)
        target = moves[current]
        if target is None:
            return None
        current = target
    return current


def _git_object_exists(commit: str) -> bool:
    if commit in {"working-tree", "none"}:
        return True
    result = subprocess.run(
        ["git", "cat-file", "-e", f"{commit}^{{commit}}"],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def validate_entries(entries: list[HistoryEntry], *, check_refs: bool = True) -> None:
    expected_ids = list(range(1, len(entries) + 1))
    actual_ids = [entry.id for entry in entries]
    if actual_ids != expected_ids:
        raise HistoryError(f"history ids must be contiguous from 001: {actual_ids}")

    moves = load_path_moves() if check_refs else {}
    known: set[int] = set()
    previous_date: datetime | None = None
    for entry in entries:
        if previous_date is not None and entry.date < previous_date:
            raise HistoryError(f"{entry.label} predates the preceding entry")
        previous_date = entry.date
        for prior in entry.supersedes:
            if prior not in known:
                raise HistoryError(f"{entry.label} supersedes missing or later HISTORY#{prior:03d}")
        known.add(entry.id)
        for commit in entry.commits:
            if not _git_object_exists(commit):
                raise HistoryError(f"{entry.label} references missing commit {commit}")
        if check_refs:
            for ref in entry.refs:
                if "://" in ref or ref.startswith("HISTORY#"):
                    continue
                target = resolve_ref(ref, moves)
                if target is None:
                    continue
                path = (ROOT / target).resolve()
                if not path.is_relative_to(ROOT.resolve()) or not path.exists():
                    detail = ref if target == ref else f"{ref}, moved to {target},"
                    raise HistoryError(f"{entry.label} references missing path {detail}")
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.search(entry.raw):
                raise HistoryError(
                    f"{entry.label} contains forbidden secret or private-session material"
                )


def load_history(path: Path = HISTORY_PATH, *, check_refs: bool = True) -> list[HistoryEntry]:
    entries = parse_history(path.read_text(encoding="utf-8"))
    validate_entries(entries, check_refs=check_refs)
    return entries
