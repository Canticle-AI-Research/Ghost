"""Regenerate ``HISTORY_INDEX.md`` from canonical ``HISTORY.md``."""

from __future__ import annotations

from .model import HISTORY_PATH, INDEX_PATH, history_sha256, load_history


def render_index() -> str:
    entries = load_history()
    latest = entries[-1]
    lines = [
        "# Ghost History Index",
        "",
        "> Derived from `HISTORY.md`; do not edit by hand. Regenerate with",
        "> `uv run python -m tools.history.rebuild_index`.",
        "",
        f"- Source SHA-256: `{history_sha256()}`",
        f"- Entries: `{len(entries)}`",
        f"- Latest: `{latest.label}`",
        "",
        "| ID | Date | Status | Commit | Topics | Supersedes | Event |",
        "|---:|---|---|---|---|---|---|",
    ]
    for entry in reversed(entries):
        commit = entry.commits[0][:12] if entry.commits else "working-tree"
        topics = ", ".join(entry.topics)
        supersedes = ", ".join(f"#{value:03d}" for value in entry.supersedes) or "—"
        title = entry.title.replace("|", "\\|")
        lines.append(
            f"| {entry.id:03d} | {entry.date.date().isoformat()} | {entry.status} | "
            f"`{commit}` | {topics} | {supersedes} | {title} |"
        )
    lines.extend(
        [
            "",
            "## Bounded retrieval",
            "",
            "Use `uv run python -m tools.history.build_context_pack --latest 5` or select",
            "topics/entry IDs. Do not load the full history during routine startup.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    INDEX_PATH.write_text(render_index(), encoding="utf-8")
    print(f"rebuilt {INDEX_PATH.relative_to(HISTORY_PATH.parent)}")


if __name__ == "__main__":
    main()
