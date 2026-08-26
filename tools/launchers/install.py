"""Install the Ghost launchers and per-harness agent definitions.

Ghost runs inside several agent harnesses. Each one carries the same charter but
discovers agents in its own directory and with its own frontmatter schema, so
the persona is assembled here from one shared body rather than maintained as
four drifting copies.

    tools/launchers/agents/_body.md   shared, harness-neutral persona
    tools/launchers/agents/<h>.md     harness frontmatter only
    tools/launchers/ghost-<h>         credential-scoping launcher

The launcher exists because an exported API key otherwise takes precedence over
the cached subscription login; each script unsets only its own provider's
variables, and only in the child process.
"""

from __future__ import annotations

import argparse
import shutil
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
AGENTS = HERE / "agents"
CHARTER = Path.home() / ".config" / "canticle-agents" / "ghost.md"


@dataclass(frozen=True, slots=True)
class Harness:
    """One agent client: where it finds agents, and what to call it."""

    label: str
    agent_dir: Path | None = None
    definition: Path | None = None


# A harness with no definition selects its persona another way: Claude's agent
# file is managed outside this installer, and Codex uses a config profile.
HARNESSES: dict[str, Harness] = {
    "claude": Harness("Claude Code", Path.home() / ".claude" / "agents"),
    "codex": Harness("Codex"),
    "grok": Harness("Grok", Path.home() / ".grok" / "agents", AGENTS / "grok.md"),
    "agy": Harness(
        "Antigravity",
        Path.home() / ".gemini" / "config" / "agents",
        AGENTS / "agy.md",
    ),
}


def render_definition(harness: str) -> str:
    """Join harness frontmatter with the shared persona body."""

    spec = HARNESSES[harness]
    if spec.definition is None:
        raise ValueError(f"{harness} has no rendered agent definition")
    body = (AGENTS / "_body.md").read_text(encoding="utf-8")
    body = body.replace("{{CHARTER}}", str(CHARTER)).replace("{{HARNESS}}", spec.label)
    return spec.definition.read_text(encoding="utf-8") + body


def install(harness: str, *, bin_dir: Path, dry_run: bool) -> list[str]:
    actions: list[str] = []
    spec = HARNESSES[harness]

    launcher = HERE / f"ghost-{harness}"
    if launcher.exists():
        target = bin_dir / launcher.name
        actions.append(f"launcher  {target}")
        if not dry_run:
            bin_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(launcher, target)
            target.chmod(0o755)

    if spec.definition is not None and spec.agent_dir is not None:
        target = spec.agent_dir / "canticle-ghost.md"
        actions.append(f"agent     {target}")
        if not dry_run:
            spec.agent_dir.mkdir(parents=True, exist_ok=True)
            target.write_text(render_definition(harness), encoding="utf-8")

    return actions


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--harness",
        action="append",
        choices=sorted(HARNESSES),
        help="install only this harness; repeatable (default: all)",
    )
    parser.add_argument("--bin-dir", type=Path, default=Path.home() / ".local" / "bin")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not CHARTER.exists():
        print(f"warning: shared charter is missing at {CHARTER}")

    for harness in args.harness or sorted(HARNESSES):
        for action in install(harness, bin_dir=args.bin_dir, dry_run=args.dry_run):
            print(f"{'would write' if args.dry_run else 'wrote'}  {action}")


if __name__ == "__main__":
    main()
