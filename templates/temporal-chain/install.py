"""Install the Temporal Chain starter without overwriting existing files."""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

SOURCE = Path(__file__).resolve().parent / "source"


def _render(text: str, *, project_name: str, project_slug: str) -> str:
    now = datetime.now(UTC)
    return (
        text.replace("{{PROJECT_NAME}}", project_name)
        .replace("{{PROJECT_SLUG}}", project_slug)
        .replace("{{TIMESTAMP}}", now.isoformat())
        .replace("{{DATE}}", now.date().isoformat())
    )


def _target_path(repo: Path, relative: Path) -> Path:
    name = relative.name.removesuffix(".tmpl")
    return repo / relative.with_name(name)


def install(repo: Path, *, project_name: str, project_slug: str) -> list[Path]:
    if not (repo / ".git").exists():
        raise ValueError(f"target is not a Git repository: {repo}")
    sources = sorted(
        path
        for path in SOURCE.rglob("*")
        if path.is_file()
        and "__pycache__" not in path.parts
        and path.suffix not in {".pyc", ".pyo"}
    )
    targets = [
        _target_path(repo, path.relative_to(SOURCE))
        for path in sources
        if path.name != ".gitignore.fragment.tmpl"
    ]
    collisions = [path for path in targets if path.exists()]
    if collisions:
        listed = "\n".join(f"- {path.relative_to(repo)}" for path in collisions)
        raise ValueError(f"refusing to overwrite existing files:\n{listed}")

    written: list[Path] = []
    for source, target in zip(
        (path for path in sources if path.name != ".gitignore.fragment.tmpl"),
        targets,
        strict=True,
    ):
        target.parent.mkdir(parents=True, exist_ok=True)
        rendered = _render(
            source.read_text(encoding="utf-8"),
            project_name=project_name,
            project_slug=project_slug,
        )
        target.write_text(rendered, encoding="utf-8")
        written.append(target)

    fragment = (SOURCE / ".gitignore.fragment.tmpl").read_text(encoding="utf-8")
    ignore = repo / ".gitignore"
    existing = ignore.read_text(encoding="utf-8") if ignore.exists() else ""
    if ".continuity/" not in existing.splitlines():
        separator = "" if not existing or existing.endswith("\n") else "\n"
        ignore.write_text(existing + separator + fragment, encoding="utf-8")
        written.append(ignore)

    subprocess.run(
        [sys.executable, "-m", "tools.history.rebuild_index"],
        cwd=repo,
        check=True,
    )
    subprocess.run(
        [sys.executable, "-m", "tools.history.verify_continuity"],
        cwd=repo,
        check=True,
    )
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--project-name", required=True)
    parser.add_argument("--project-slug")
    args = parser.parse_args()
    repo = args.repo.resolve()
    slug = args.project_slug or "-".join(args.project_name.lower().split())
    written = install(repo, project_name=args.project_name, project_slug=slug)
    print(f"installed temporal chain: {len(written)} files in {repo}")


if __name__ == "__main__":
    main()
