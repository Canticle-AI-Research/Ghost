"""Truthful operational states shared by every Ghost avatar renderer."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class AvatarState(StrEnum):
    """Observable agent/runtime states, not claims about inner emotion."""

    IDLE = "idle"
    RETRIEVING = "retrieving"
    REASONING = "reasoning"
    WAITING_APPROVAL = "waiting_approval"
    ACTING = "acting"
    SUCCESS = "success"
    ERROR = "error"
    DEGRADED = "degraded"
    DISCONNECTED = "disconnected"


@dataclass(frozen=True, slots=True)
class AvatarVisualState:
    """Renderer-neutral expression and light contract for one state."""

    face: str
    primary: tuple[int, int, int]
    secondary: tuple[int, int, int]
    energy: float


VISUAL_STATES: dict[AvatarState, AvatarVisualState] = {
    AvatarState.IDLE: AvatarVisualState("awake", (125, 207, 255), (196, 167, 231), 0.35),
    AvatarState.RETRIEVING: AvatarVisualState(
        "curious", (125, 207, 255), (122, 162, 247), 0.62
    ),
    AvatarState.REASONING: AvatarVisualState(
        "focused", (122, 162, 247), (228, 120, 208), 0.82
    ),
    AvatarState.WAITING_APPROVAL: AvatarVisualState(
        "curious", (224, 175, 104), (255, 158, 200), 0.48
    ),
    AvatarState.ACTING: AvatarVisualState(
        "focused", (158, 206, 106), (125, 207, 255), 1.0
    ),
    AvatarState.SUCCESS: AvatarVisualState(
        "happy", (158, 206, 106), (125, 207, 255), 0.72
    ),
    AvatarState.ERROR: AvatarVisualState("error", (247, 118, 142), (255, 158, 100), 0.78),
    AvatarState.DEGRADED: AvatarVisualState(
        "nervous", (224, 175, 104), (247, 118, 142), 0.35
    ),
    AvatarState.DISCONNECTED: AvatarVisualState(
        "sleepy", (112, 122, 150), (88, 96, 120), 0.15
    ),
}

_ALIASES = {
    "thinking": AvatarState.REASONING,
    "speaking": AvatarState.ACTING,
    "done": AvatarState.SUCCESS,
    "failed": AvatarState.ERROR,
    "offline": AvatarState.DISCONNECTED,
}


def coerce_avatar_state(value: str | AvatarState) -> AvatarState:
    """Normalize legacy names while rejecting invented or ambiguous states."""

    if isinstance(value, AvatarState):
        return value
    normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
    if normalized in _ALIASES:
        return _ALIASES[normalized]
    try:
        return AvatarState(normalized)
    except ValueError as exc:
        raise ValueError(f"unknown avatar state: {value!r}") from exc


def state_message(state: str | AvatarState, *, detail: str = "") -> dict[str, str]:
    """Build the versioned wire message used by hooks and renderers."""

    normalized = coerce_avatar_state(state)
    return {
        "type": "agent_state",
        "schema": "ghost-avatar-state/1",
        "state": normalized.value,
        "detail": detail[:240],
    }
