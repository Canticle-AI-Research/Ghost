"""Optional push from the `ghost` CLI into a running desktop overlay.

Off unless ``GHOST_AVATAR=1`` (or ``GHOST_AVATAR_WS`` is set). Connection
failures are silent: a turn must not die because the overlay is not up.
"""

from __future__ import annotations

import json
import os
from typing import Any

from .director import plan_turn_end, plan_turn_start
from .sensor import DesktopItem, DesktopState, WindowInfo

_TRUTHY = {"1", "true", "yes", "on"}
_DEFAULT_WS = "ws://127.0.0.1:8765"


def avatar_ws_url() -> str | None:
    explicit = os.environ.get("GHOST_AVATAR_WS", "").strip()
    if explicit:
        return explicit
    flag = os.environ.get("GHOST_AVATAR", "").strip().lower()
    if flag in _TRUTHY:
        return _DEFAULT_WS
    return None


def desktop_from_payload(state: dict[str, Any]) -> DesktopState:
    windows = [WindowInfo(**row) for row in state.get("windows") or []]
    items = [DesktopItem(**row) for row in state.get("items") or []]
    return DesktopState(
        screen_width=int(state.get("screen_width") or 1920),
        screen_height=int(state.get("screen_height") or 1080),
        windows=windows,
        items=items,
    )


def _push(url: str, messages: list[dict[str, Any]]) -> None:
    try:
        from websockets.sync.client import connect
    except ImportError:
        return
    try:
        with connect(url, open_timeout=0.4, close_timeout=0.4) as ws:
            raw = ws.recv()
            first = json.loads(raw)
            desktop = None
            if first.get("type") == "desktop_sync" and isinstance(first.get("state"), dict):
                desktop = desktop_from_payload(first["state"])
            for message in messages:
                if message.get("_plan") == "start":
                    text = str(message.get("text") or "")
                    for cmd in plan_turn_start(text, desktop):
                        ws.send(json.dumps(cmd.to_message()))
                    ws.send(json.dumps({"type": "agent_state", "state": "thinking"}))
                    continue
                if message.get("_plan") == "end":
                    ok = bool(message.get("ok", True))
                    for cmd in plan_turn_end(ok=ok):
                        ws.send(json.dumps(cmd.to_message()))
                    ws.send(
                        json.dumps(
                            {
                                "type": "agent_state",
                                "state": "idle" if ok else "error",
                            }
                        )
                    )
                    continue
                ws.send(json.dumps(message))
    except Exception:
        return


def notify_turn_start(user_input: str) -> None:
    url = avatar_ws_url()
    if url is None:
        return
    _push(url, [{"_plan": "start", "text": user_input}])


def notify_turn_end(*, ok: bool) -> None:
    url = avatar_ws_url()
    if url is None:
        return
    _push(url, [{"_plan": "end", "ok": ok}])
