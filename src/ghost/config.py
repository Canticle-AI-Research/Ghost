"""Environment-backed configuration for Ghost."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
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


def _bounded_float(name: str, default: float, *, minimum: float, maximum: float) -> float:
    raw = os.environ.get(name, str(default))
    try:
        value = float(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be a number") from exc
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}")
    return value


def _flag(name: str, *, default: bool) -> bool:
    """Read a boolean switch.

    Anything unrecognised is the default rather than an error, EXCEPT that an
    unset shell flag must never read as enabled -- so the default is passed in
    by the caller rather than inferred from the string.
    """

    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _choice(name: str, default: str, allowed: frozenset[str]) -> str:
    value = os.environ.get(name, default).strip().lower()
    if value not in allowed:
        raise ValueError(f"{name} must be one of: {', '.join(sorted(allowed))}")
    return value


def validate_dimension(value: str, name: str) -> str:
    """Validate one caller-visible SEAM boundary label."""

    value = value.strip()
    if not value or len(value) > 128:
        raise ValueError(f"{name} must contain 1 to 128 characters")
    if not value[0].isascii() or not value[0].isalnum():
        raise ValueError(f"{name} must start with an ASCII letter or number")
    if any(not (char.isascii() and (char.isalnum() or char in "._-")) for char in value):
        raise ValueError(
            f"{name} must use ASCII letters, numbers, dots, underscores, or hyphens"
        )
    return value


def _dimension(name: str, default: str) -> str:
    return validate_dimension(os.environ.get(name, default), name)


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
    workspace: str = "default"
    project: str = "default"
    memory_admission: str = "explicit"
    seam_base_url: str = "http://127.0.0.1:8765"
    seam_api_token: str | None = field(default=None, repr=False)
    seam_timeout: float = 30.0
    recall_budget: int = 8
    graph_hops: int = 2
    # LangGraph recursion/superstep ceiling. This is the hard model/tool-loop
    # budget for one turn; a provider timeout is a separate transport bound.
    max_steps: int = 25
    agent_id: str = "ghost"
    # Directories the filesystem tools may read. Empty by default: Ghost should
    # not be able to read arbitrary files just because it was started, so the
    # operator opts in per deployment with GHOST_TOOL_ROOTS.
    tool_roots: tuple[Path, ...] = ()
    # Execution state only (ADR-0001 item 6), never semantic truth. Defaults
    # beside the SEAM store rather than inside it, so the distinction between
    # "where the conversation got to" and "what is remembered" stays physical.
    checkpoint_db: Path | None = None
    # Shell access. Off unless the operator turns it on, so importing Ghost or
    # running it with defaults can never reach a shell.
    enable_shell: bool = False
    # Ask before each command. On whenever the shell is on, because the shell's
    # blast radius is the whole account; an operator running unattended turns
    # it off deliberately with GHOST_SHELL_APPROVAL=0.
    shell_approval: bool = True
    shell_timeout: int = 120
    shell_workdir: Path | None = None

    @classmethod
    def from_env(cls) -> GhostSettings:
        default_root = Path.home() / ".local" / "share" / "ghost"
        default_db = default_root / "seam.db"
        default_checkpoints = default_root / "checkpoints.db"
        return cls(
            model=os.environ.get("GHOST_MODEL", "openai:gpt-5.6-terra"),
            seam_db=Path(os.environ.get("GHOST_SEAM_DB", str(default_db))).expanduser(),
            checkpoint_db=Path(
                os.environ.get("GHOST_CHECKPOINT_DB", str(default_checkpoints))
            ).expanduser(),
            namespace=_dimension("GHOST_SEAM_NAMESPACE", "ghost.default"),
            scope=_choice(
                "GHOST_SEAM_SCOPE",
                "thread",
                frozenset({"ephemeral", "global", "org", "project", "thread", "user"}),
            ),
            workspace=_dimension("GHOST_WORKSPACE", "default"),
            project=_dimension("GHOST_PROJECT", "default"),
            memory_admission=_choice(
                "GHOST_MEMORY_ADMISSION",
                "explicit",
                frozenset({"all", "explicit", "off"}),
            ),
            seam_base_url=os.environ.get(
                "SEAM_BASE_URL", "http://127.0.0.1:8765"
            ).rstrip("/"),
            seam_api_token=os.environ.get("SEAM_API_TOKEN") or None,
            seam_timeout=_bounded_float(
                "GHOST_SEAM_TIMEOUT", 30.0, minimum=0.1, maximum=300.0
            ),
            recall_budget=_bounded_int(
                "GHOST_RECALL_BUDGET", 8, minimum=1, maximum=50
            ),
            graph_hops=_bounded_int("GHOST_GRAPH_HOPS", 2, minimum=0, maximum=3),
            max_steps=_bounded_int("GHOST_MAX_STEPS", 25, minimum=2, maximum=100),
            tool_roots=_tool_roots(),
            enable_shell=_flag("GHOST_ENABLE_SHELL", default=False),
            shell_approval=_flag("GHOST_SHELL_APPROVAL", default=True),
            shell_timeout=_bounded_int(
                "GHOST_SHELL_TIMEOUT", 120, minimum=1, maximum=3600
            ),
            shell_workdir=(
                Path(os.environ["GHOST_SHELL_WORKDIR"]).expanduser().resolve()
                if os.environ.get("GHOST_SHELL_WORKDIR", "").strip()
                else None
            ),
        )

    @property
    def checkpoints(self) -> Path:
        """Resolved checkpoint path, defaulting beside ``seam_db``."""

        if self.checkpoint_db is not None:
            return self.checkpoint_db
        return self.seam_db.with_name("checkpoints.db")

    @property
    def provider(self) -> str | None:
        provider, separator, _model = self.model.partition(":")
        return provider if separator else None

    @property
    def model_name(self) -> str:
        _provider, separator, model = self.model.partition(":")
        return model if separator else self.model
