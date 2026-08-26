"""Regenerate HISTORY_INDEX.md from canonical HISTORY.md."""

from .model import INDEX_PATH, ROOT, history_sha256, load_history


def render_index() -> str:
    entries = load_history()
    lines = [
        f"# {ROOT.name} History Index", "", "> Generated from `HISTORY.md`; do not edit.", "",
        f"- Source SHA-256: `{history_sha256()}`", f"- Entries: `{len(entries)}`",
        f"- Latest: `{entries[-1].label}`", "",
        "| ID | Date | Status | Commit | Topics | Supersedes | Event |",
        "|---:|---|---|---|---|---|---|",
    ]
    for entry in reversed(entries):
        commit = entry.commits[0][:12] if entry.commits else "working-tree"
        supersedes = ", ".join(f"#{value:03d}" for value in entry.supersedes) or "—"
        title = entry.title.replace("|", "\\|")
        lines.append(
            f"| {entry.id:03d} | {entry.date.date()} | {entry.status} | `{commit}` | "
            f"{', '.join(entry.topics)} | {supersedes} | {title} |"
        )
    lines += [
        "",
        "Use `python -m tools.history.build_context_pack --latest 5` for bounded reads.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    INDEX_PATH.write_text(render_index(), encoding="utf-8")
    print(f"rebuilt {INDEX_PATH.name}")


if __name__ == "__main__":
    main()
