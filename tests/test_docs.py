from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def _markdown_files() -> list[Path]:
    return [ROOT / "README.md", *sorted(DOCS.rglob("*.md"))]


def test_every_document_is_routed_from_index() -> None:
    index = (DOCS / "INDEX.md").read_text(encoding="utf-8")
    missing = []
    for document in sorted(DOCS.rglob("*.md")):
        if document.name == "INDEX.md":
            continue
        relative = document.relative_to(DOCS).as_posix()
        if relative not in index:
            missing.append(relative)
    assert not missing, f"docs missing from docs/INDEX.md: {missing}"


def test_relative_markdown_links_resolve_inside_repository() -> None:
    failures = []
    root = ROOT.resolve()
    for document in _markdown_files():
        text = document.read_text(encoding="utf-8")
        for raw_target in MARKDOWN_LINK.findall(text):
            target = raw_target.strip().split("#", 1)[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            resolved = (document.parent / target).resolve()
            if not resolved.is_relative_to(root):
                failures.append(f"{document.relative_to(ROOT)} escapes repository: {target}")
            elif not resolved.exists():
                failures.append(f"{document.relative_to(ROOT)} missing: {target}")
    assert not failures, "\n".join(failures)
