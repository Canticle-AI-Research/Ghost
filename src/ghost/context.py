"""Per-invocation context passed through the DeepAgents runtime."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GhostTurnContext:
    """Transient SEAM context that is not written into graph state."""

    seam_memory: str = ""

