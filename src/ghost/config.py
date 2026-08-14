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
        )

    @property
    def provider(self) -> str | None:
        provider, separator, _model = self.model.partition(":")
        return provider if separator else None

    @property
    def model_name(self) -> str:
        _provider, separator, model = self.model.partition(":")
        return model if separator else self.model
