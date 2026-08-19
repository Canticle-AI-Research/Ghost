"""Environment-backed configuration for Ghost."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _bounded_int(name: str, default: int, *, minimum: int, maximum: int) -> int:
    raw = os.environ.get(name, str(default))
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}")
    return value


def _tool_roots() -> tuple[Path, ...]:
    """Readable roots for the filesystem tools, from ``GHOST_TOOL_ROOTS``.

    Colon-separated, like PATH. Each entry is resolved once here so the tools
    compare against a real path rather than re-resolving attacker-supplied
    input, and a root that does not exist is rejected at startup rather than
    silently granting nothing.
    """

    raw = os.environ.get("GHOST_TOOL_ROOTS", "").strip()
    if not raw:
        return ()
    roots: list[Path] = []
    for entry in raw.split(":"):
        candidate = entry.strip()
        if not candidate:
            continue
        resolved = Path(candidate).expanduser().resolve()
        if not resolved.is_dir():
            raise ValueError(f"GHOST_TOOL_ROOTS entry is not a directory: {candidate}")
        roots.append(resolved)
    return tuple(roots)


@dataclass(frozen=True, slots=True)
class GhostSettings:
    """Runtime settings with conservative, bounded memory defaults."""

    model: str
    seam_db: Path
    namespace: str
    scope: str
    recall_budget: int = 8
    graph_hops: int = 2
    agent_id: str = "ghost"
    # Directories the filesystem tools may read. Empty by default: Ghost should
    # not be able to read arbitrary files just because it was started, so the
    # operator opts in per deployment with GHOST_TOOL_ROOTS.
    tool_roots: tuple[Path, ...] = ()

    @classmethod
    def from_env(cls) -> GhostSettings:
        default_db = Path.home() / ".local" / "share" / "ghost" / "seam.db"
        return cls(
            model=os.environ.get("GHOST_MODEL", "openai:gpt-5.6-terra"),
            seam_db=Path(os.environ.get("GHOST_SEAM_DB", str(default_db))).expanduser(),
            namespace=os.environ.get("GHOST_SEAM_NAMESPACE", "ghost.default"),
            scope=os.environ.get("GHOST_SEAM_SCOPE", "thread"),
            recall_budget=_bounded_int(
                "GHOST_RECALL_BUDGET", 8, minimum=1, maximum=64
            ),
            graph_hops=_bounded_int("GHOST_GRAPH_HOPS", 2, minimum=0, maximum=3),
            tool_roots=_tool_roots(),
        )

    @property
    def provider(self) -> str | None:
        provider, separator, _model = self.model.partition(":")
        return provider if separator else None

    @property
    def model_name(self) -> str:
        _provider, separator, model = self.model.partition(":")
        return model if separator else self.model
