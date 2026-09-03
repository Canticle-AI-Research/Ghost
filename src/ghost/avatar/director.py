"""Map Ghost's turn into desktop-avatar commands.

The overlay animates; this module decides. Pure functions so a turn can be
tested without a compositor, a browser, or a live agent.
"""

from __future__ import annotations

from dataclasses import dataclass

from .sensor import DesktopItem, DesktopState, WindowInfo

FACE_GLYPHS: dict[str, str] = {
    "awake": "❯ █",  # noqa: RUF001  # lockup prompt, not ASCII >
    "done": "❯ █",  # noqa: RUF001
    "happy": "^ ^",
    "blissful": "‿ ‿",
    "wink": "^ █",
    "excited": "✧ ✧",
    "focused": "▪ ▪",
    "blank": "・ ・",
    "curious": "? ・",
    "surprised": "o o",
    "sleepy": "⌒ ⌒",
    "error": "x x",
    "confused": "@ @",
    "angry": "▼ ▼",
    "nervous": "; ;",
}

IDLE_FACES: tuple[str, ...] = ("blank", "curious", "sleepy", "wink")

_WEB_HINTS: tuple[str, ...] = (
    "search the web",
    "google ",
    "look up",
    "look it up",
    "internet",
    "browser",
    "https://",
    "http://",
    "search online",
)

_BROWSER_MARKERS: tuple[str, ...] = (
    "chrome",
    "chromium",
    "firefox",
    "brave",
    "navigator",
)


@dataclass(frozen=True, slots=True)
class AvatarCommand:
    """One instruction the overlay can play."""

    action: str
    face: str
    target_kind: str | None = None
    target_name: str | None = None
    text: str | None = None

    def to_message(self) -> dict[str, str | None]:
        return {
            "type": "avatar_action",
            "action": self.action,
            "face": self.face,
            "target_kind": self.target_kind,
            "target_name": self.target_name,
            "text": self.text,
        }


def looks_like_web_search(text: str) -> bool:
    lowered = text.lower()
    return any(hint in lowered for hint in _WEB_HINTS)


def find_browser_window(windows: list[WindowInfo]) -> WindowInfo | None:
    for window in windows:
        haystack = f"{window.wm_class} {window.title}".lower()
        if any(marker in haystack for marker in _BROWSER_MARKERS):
            return window
    return None


def match_desktop_item(text: str, items: list[DesktopItem]) -> DesktopItem | None:
    lowered = text.lower()
    for item in items:
        if item.name.lower() in lowered:
            return item
    return None


def plan_spawn() -> AvatarCommand:
    return AvatarCommand(action="appear", face="awake")


def plan_turn_start(
    user_input: str, desktop: DesktopState | None = None
) -> tuple[AvatarCommand, ...]:
    text = user_input.strip()
    if not text:
        return ()
    items = desktop.items if desktop is not None else []
    windows = desktop.windows if desktop is not None else []

    if looks_like_web_search(text):
        browser = find_browser_window(windows)
        return (
            AvatarCommand(
                action="enter",
                face="focused",
                target_kind="browser",
                target_name=browser.title if browser is not None else "browser",
            ),
        )

    item = match_desktop_item(text, items)
    if item is not None:
        return (
            AvatarCommand(
                action="enter",
                face="focused",
                target_kind="item",
                target_name=item.name,
            ),
        )

    return (AvatarCommand(action="face", face="focused"),)


def plan_turn_end(*, ok: bool = True, mood: str | None = None) -> tuple[AvatarCommand, ...]:
    if mood is not None:
        face = mood
    elif ok:
        face = "done"
    else:
        face = "error"
    return (AvatarCommand(action="pop_out", face=face),)


def plan_idle(choice: int) -> AvatarCommand:
    """Visual-only idle. `choice` is the caller's RNG so tests stay deterministic."""
    return AvatarCommand(action="idle", face=IDLE_FACES[choice % len(IDLE_FACES)])
