"""Audit checkable facts written into Ghost's active docs and latest history.

Continuity already verifies entry hashes, index freshness, supersedes links,
handoff chains, snapshots, and path references. This module covers the other
half: the factual claims an agent *writes in prose*, which nothing else checks.

The failure this prevents is specific. `docs/status/CURRENT_STATE.md` recorded
`184 passed` while `PROJECT_STATUS.md` said 196 and the suite actually ran 196.
Both files are current-state authorities, so a reader routed to either one got a
different answer and neither looked wrong on its own. A stale number is worse
than a missing one, because it reads as verified.

Three fact types are checkable today, and each is checked against ground truth
or against the other claims that must agree with it:

``test_count``
    Test-count claims in the status authorities must agree with each other. A
    disagreement means at least one is stale.
``module_lines``
    A claim of the form ```path/to/file.py` (N lines)`` is checked against the
    file. These drift silently every time the module is edited.
``handoff_pointer``
    A prose claim about the current handoff must match the registry's ``latest``.

Add a new extractor here rather than relying on review when a new kind of
checkable claim starts appearing in Ghost's prose.

There is deliberately **no suppression flag**. A gate that can be quietened
converts "unverified" into "verified", which is the state the next agent acts
on. If an extractor over-matches, fix the pattern.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .handoffs import load_handoffs
from .model import ROOT, load_history

# Only the documents that assert Ghost's *current* state are audited for test
# counts. The roadmap and wiki quote counts as illustrations ("196 tests pass"
# says nothing about...), and auditing those would flag prose that is making the
# opposite point.
STATUS_AUTHORITIES = (
    Path("PROJECT_STATUS.md"),
    Path("docs/status/CURRENT_STATE.md"),
)

# Module-line claims are unambiguous anywhere they appear, because the pattern
# requires a backticked Python path immediately followed by a line count.
MODULE_LINES = re.compile(r"`(?P<path>[\w./-]+\.py)`\s*\((?P<lines>\d+)\s+lines?\)")

# Both word orders occur in Ghost's prose and both are claims: "196 provider-free
# tests pass" and "passes 196 provider-free tests". Matching only one of them
# means a disagreement between two documents cannot be detected at all, because
# only a single claim gets extracted.
TEST_COUNT = re.compile(
    r"\b(?P<count>\d+)\s+(?:[\w-]+\s+)?tests?\s+pass(?:ed|es)?\b"
    r"|\bpass(?:es|ed)\s+(?P<after>\d+)\s+(?:[\w-]+\s+)?tests?\b"
    r"|\b(?P<bare>\d+)\s+passed\b",
    re.IGNORECASE,
)

# Distinguishing a record of the past from a claim about now cannot key on a
# HISTORY#NNN citation: current-state prose cites history entries as evidence
# too. It keys on explicit past-tense language instead, which is the convention
# a superseded count must be written with to stay readable without lying.
SUPERSEDED_FACT = re.compile(
    r"\b(?:earlier|previously|formerly|superseded|predated|no longer)\b",
    re.IGNORECASE,
)

HANDOFF_POINTER = re.compile(
    r"current handoff (?:is|head is)\s+`(?P<path>docs/handoffs/[\w./-]+\.md)`",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class FactIssue:
    """One recorded claim that does not survive checking."""

    kind: str
    location: str
    message: str

    def format(self) -> str:
        return f"{self.kind}: {self.location}: {self.message}"


def _iter_lines(text: str) -> list[tuple[int, str]]:
    return list(enumerate(text.splitlines(), start=1))


def _iter_paragraphs(text: str) -> list[tuple[int, str]]:
    """Blank-line-separated blocks with their starting line number.

    Claims are audited per paragraph rather than per line because a wrapped
    sentence carries its superseding citation on whichever line it lands on.
    """

    paragraphs: list[tuple[int, str]] = []
    start = 1
    buffer: list[str] = []
    for number, line in _iter_lines(text):
        if line.strip():
            if not buffer:
                start = number
            buffer.append(line)
        elif buffer:
            paragraphs.append((start, "\n".join(buffer)))
            buffer = []
    if buffer:
        paragraphs.append((start, "\n".join(buffer)))
    return paragraphs


def _audit_test_counts(repo_root: Path) -> list[FactIssue]:
    """Every current-state test-count claim must name the same number.

    A superseded count stays readable by being written in explicit past tense
    ("the earlier recorded 184 passed predated ..."). That language is how this
    audit tells a *record of the past* from a *claim about now*. It cannot key
    on a ``HISTORY#NNN`` citation, because current-state prose cites history
    entries as supporting evidence.
    """

    claims: list[tuple[str, int]] = []
    for relative in STATUS_AUTHORITIES:
        path = repo_root / relative
        if not path.exists():
            continue
        for number, paragraph in _iter_paragraphs(path.read_text(encoding="utf-8")):
            if SUPERSEDED_FACT.search(paragraph):
                continue
            for match in TEST_COUNT.finditer(paragraph):
                raw = match.group("count") or match.group("after") or match.group("bare")
                claims.append((f"{relative.as_posix()}:{number}", int(raw)))

    distinct = {count for _location, count in claims}
    if len(distinct) <= 1:
        return []
    listed = ", ".join(f"{location} says {count}" for location, count in claims)
    return [
        FactIssue(
            "test_count",
            "status authorities",
            f"current-state test counts disagree ({listed}); at least one is stale",
        )
    ]


def _audit_module_lines(repo_root: Path, documents: list[Path]) -> list[FactIssue]:
    """A cited module length must match the file it names."""

    issues: list[FactIssue] = []
    for document in documents:
        relative = document.relative_to(repo_root).as_posix()
        for number, line in _iter_lines(document.read_text(encoding="utf-8")):
            for match in MODULE_LINES.finditer(line):
                target = repo_root / match.group("path")
                claimed = int(match.group("lines"))
                if not target.exists():
                    issues.append(
                        FactIssue(
                            "module_lines",
                            f"{relative}:{number}",
                            f"cites missing module {match.group('path')}",
                        )
                    )
                    continue
                actual = len(target.read_text(encoding="utf-8").splitlines())
                if actual != claimed:
                    issues.append(
                        FactIssue(
                            "module_lines",
                            f"{relative}:{number}",
                            f"{match.group('path')} is {actual} lines, not {claimed}",
                        )
                    )
    return issues


def _audit_handoff_pointer(repo_root: Path, documents: list[Path]) -> list[FactIssue]:
    """A prose claim about the current handoff must match the registry."""

    claims: list[tuple[str, int, str]] = []
    for document in documents:
        relative = document.relative_to(repo_root).as_posix()
        for number, line in _iter_lines(document.read_text(encoding="utf-8")):
            for match in HANDOFF_POINTER.finditer(line):
                claims.append((relative, number, match.group("path")))
    if not claims:
        return []

    latest, _chain = load_handoffs(root=repo_root)
    issues: list[FactIssue] = []
    for relative, number, claimed in claims:
        if claimed != latest:
            issues.append(
                FactIssue(
                    "handoff_pointer",
                    f"{relative}:{number}",
                    f"names {claimed}; the registry's current head is {latest}",
                )
            )
    return issues


def _audited_documents(repo_root: Path) -> list[Path]:
    """Active prose plus the latest history entry's own file."""

    documents = [repo_root / "PROJECT_STATUS.md", repo_root / "REPO_LEDGER.md"]
    documents.extend(sorted((repo_root / "docs").rglob("*.md")))
    return [path for path in documents if path.exists()]


def audit_recorded_facts(repo_root: Path | None = None) -> list[FactIssue]:
    """Return every recorded claim that fails its check."""

    root = (repo_root or ROOT).resolve()
    documents = _audited_documents(root)
    issues = _audit_test_counts(root)
    issues.extend(_audit_module_lines(root, documents))
    issues.extend(_audit_handoff_pointer(root, documents))
    return issues


def audit_latest_entry(repo_root: Path | None = None) -> list[FactIssue]:
    """Check module-line claims inside the newest history entry.

    History is append-only, so only the latest entry is audited: an older entry
    was true when written, and correcting it would mean rewriting the past.
    """

    root = (repo_root or ROOT).resolve()
    latest = load_history(root / "HISTORY.md")[-1]
    issues: list[FactIssue] = []
    for match in MODULE_LINES.finditer(latest.raw):
        target = root / match.group("path")
        claimed = int(match.group("lines"))
        if not target.exists():
            continue
        actual = len(target.read_text(encoding="utf-8").splitlines())
        if actual != claimed:
            issues.append(
                FactIssue(
                    "module_lines",
                    latest.label,
                    f"{match.group('path')} is {actual} lines, not {claimed}",
                )
            )
    return issues


def main() -> None:
    issues = audit_recorded_facts() + audit_latest_entry()
    if issues:
        listed = "\n".join(f"- {issue.format()}" for issue in issues)
        raise SystemExit(f"recorded-fact audit found stale claims:\n{listed}")
    print("recorded facts verified")


if __name__ == "__main__":
    main()
