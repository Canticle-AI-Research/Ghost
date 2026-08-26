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


def test_environment_variables_match_the_configuration_page() -> None:
    """Every knob the code reads is documented, and nothing documented is dead.

    Configuration drift is the quietest kind: an operator follows a page that
    describes a variable the code stopped reading, and the system silently uses
    a default instead.
    """
    env_pattern = re.compile(r"GHOST_[A-Z0-9_]+")
    in_code: set[str] = set()
    for module in sorted((ROOT / "src" / "ghost").rglob("*.py")):
        in_code |= set(env_pattern.findall(module.read_text(encoding="utf-8")))
    documented = set(
        env_pattern.findall((DOCS / "operations" / "CONFIGURATION.md").read_text(encoding="utf-8"))
    )
    undocumented = sorted(in_code - documented)
    stale = sorted(documented - in_code)
    assert not undocumented, (
        f"variables read by code but absent from CONFIGURATION.md: {undocumented}"
    )
    assert not stale, f"variables documented but no longer read by code: {stale}"


def test_console_scripts_are_documented() -> None:
    """A shipped entry point an operator cannot find in the reference is unusable."""
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    scripts_block = pyproject.split("[project.scripts]", 1)[1].split("\n[", 1)[0]
    scripts = re.findall(r"^([a-z0-9-]+)\s*=", scripts_block, re.MULTILINE)
    assert scripts, "no console scripts found; the parser or pyproject changed"
    reference = (DOCS / "operations" / "COMMAND_REFERENCE.md").read_text(encoding="utf-8")
    missing = sorted(script for script in scripts if script not in reference)
    assert not missing, f"console scripts absent from the command reference: {missing}"


def test_roadmap_uses_the_controlled_status_vocabulary() -> None:
    """A roadmap status outside the declared vocabulary cannot be gated on."""
    roadmap = (DOCS / "roadmap" / "SECOND_BRAIN_ROADMAP.md").read_text(encoding="utf-8")
    vocabulary = set(re.findall(r"^- \*\*(.+?)\*\* —", roadmap, re.MULTILINE))
    assert vocabulary, "roadmap status vocabulary is missing"
    declared = re.findall(r"^\*\*Status: (.+?)\*\*$", roadmap, re.MULTILINE)
    assert declared, "no track statuses found; the roadmap format changed"
    unknown = sorted(
        status
        for status in declared
        if not any(term in status for term in vocabulary)
    )
    assert not unknown, f"roadmap statuses outside the vocabulary: {unknown}"
