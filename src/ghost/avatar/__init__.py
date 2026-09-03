"""Ghost desktop avatar: a 2D ghost-bunny that lives on the real desktop."""

from .bridge import AvatarBridge
from .director import AvatarCommand, plan_idle, plan_spawn, plan_turn_end, plan_turn_start
from .sensor import DesktopItem, DesktopSensor, DesktopState, WindowInfo

__all__ = [
    "AvatarBridge",
    "AvatarCommand",
    "DesktopItem",
    "DesktopSensor",
    "DesktopState",
    "WindowInfo",
    "plan_idle",
    "plan_spawn",
    "plan_turn_end",
    "plan_turn_start",
]
