"""Ghost: a DeepAgent backed by an opaque SEAM memory service."""

from .application import GhostAgent
from .config import GhostSettings

__all__ = ["GhostAgent", "GhostSettings"]
