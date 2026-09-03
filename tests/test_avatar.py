"""Tests for the Ghost 3D Desktop Avatar system."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import websockets

from ghost.avatar.bridge import AvatarBridge
from ghost.avatar.director import (
    FACE_GLYPHS,
    AvatarCommand,
    find_browser_window,
    plan_idle,
    plan_spawn,
    plan_turn_end,
    plan_turn_start,
)
from ghost.avatar.hook import avatar_ws_url, desktop_from_payload
from ghost.avatar.sensor import DesktopItem, DesktopSensor, DesktopState, WindowInfo


def test_window_info_dataclass() -> None:
    win = WindowInfo(
        window_id="0x340001c",
        title="Mixamo - Google Chrome",
        wm_class="google-chrome",
        x=100,
        y=200,
        width=1200,
        height=800,
        is_active=True,
    )
    assert win.window_id == "0x340001c"
    assert win.title == "Mixamo - Google Chrome"
    assert win.width == 1200
    assert win.height == 800
    assert win.is_active is True


def test_desktop_item_dataclass() -> None:
    item = DesktopItem(
        name="Projects",
        path="/home/user/Desktop/Projects",
        item_type="folder",
        grid_col=0,
        grid_row=1,
        x=40,
        y=160,
    )
    assert item.name == "Projects"
    assert item.item_type == "folder"
    assert item.x == 40
    assert item.y == 160


def test_desktop_state_serialization() -> None:
    state = DesktopState(
        screen_width=1920,
        screen_height=1080,
        windows=[
            WindowInfo("0x1", "Terminal", "gnome-terminal", 0, 0, 800, 600)
        ],
        items=[
            DesktopItem("Folder1", "/Desktop/Folder1", "folder", 0, 0, 40, 50)
        ],
    )
    data = state.to_dict()
    assert data["screen_width"] == 1920
    assert len(data["windows"]) == 1
    assert data["windows"][0]["title"] == "Terminal"
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Folder1"


def test_desktop_sensor_scan_items(tmp_path: Path) -> None:
    desktop = tmp_path / "Desktop"
    desktop.mkdir()
    (desktop / "Work").mkdir()
    (desktop / "app.desktop").write_text("[Desktop Entry]\nName=App", encoding="utf-8")
    (desktop / "notes.txt").write_text("hello", encoding="utf-8")

    sensor = DesktopSensor(desktop_dir=desktop)
    items = sensor.scan_desktop_items()

    assert len(items) == 3
    types = {i.item_type for i in items}
    assert "folder" in types
    assert "app" in types
    assert "file" in types


def test_desktop_sensor_parse_windows() -> None:
    mock_output = (
        'xwininfo: Window id: 0x238 (the root window)\n'
        '  0x340001c "Chrome": ("google-chrome" "Google-chrome") 1920x999+0+32 +0+32\n'
        '  0x2a96db9 "Terminal": ("gnome-terminal" "Gnome-terminal") 867x557+795+286 +795+286\n'
    )
    sensor = DesktopSensor()
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout=mock_output, returncode=0)
        windows = sensor.scan_windows()

    assert len(windows) == 2
    assert windows[0].title == "Chrome"
    assert windows[0].width == 1920
    assert windows[1].title == "Terminal"


def test_avatar_bridge_lifecycle() -> None:
    async def _run() -> None:
        sensor = DesktopSensor()
        bridge = AvatarBridge(sensor=sensor, host="127.0.0.1", port=8799)
        await bridge.start()

        try:
            uri = "ws://127.0.0.1:8799"
            async with websockets.connect(uri) as ws:
                msg = await ws.recv()
                data = json.loads(msg)
                assert data["type"] == "desktop_sync"
                assert "state" in data

                await bridge.command_avatar("touch", target_name="canticle.cc", text="Touching!")
                cmd_msg = await ws.recv()
                cmd_data = json.loads(cmd_msg)
                assert cmd_data["type"] == "avatar_action"
                assert cmd_data["action"] == "touch"
                assert cmd_data["target_name"] == "canticle.cc"
        finally:
            await bridge.stop()

    asyncio.run(_run())


def _desktop() -> DesktopState:
    return DesktopState(
        screen_width=1920,
        screen_height=1080,
        windows=[
            WindowInfo("0x1", "GitHub — Mozilla Firefox", "firefox", 100, 80, 1400, 900),
            WindowInfo("0x2", "Terminal", "gnome-terminal", 800, 200, 700, 500),
        ],
        items=[
            DesktopItem("Projects", "/Desktop/Projects", "folder", 0, 0, 40, 50),
            DesktopItem("notes.txt", "/Desktop/notes.txt", "file", 0, 1, 40, 160),
        ],
    )


def test_awake_and_done_share_the_lockup_glyph() -> None:
    assert FACE_GLYPHS["awake"] == "❯ █"  # noqa: RUF001
    assert FACE_GLYPHS["done"] == FACE_GLYPHS["awake"]
    assert FACE_GLYPHS["confused"] == "@ @"
    assert FACE_GLYPHS["confused"] != "> <"


def test_spawn_uses_the_awake_lockup() -> None:
    cmd = plan_spawn()
    assert cmd.action == "appear"
    assert cmd.face == "awake"


def test_web_search_enters_the_browser() -> None:
    cmds = plan_turn_start("search the web for rust iterators", _desktop())
    assert len(cmds) == 1
    assert cmds[0].action == "enter"
    assert cmds[0].face == "focused"
    assert cmds[0].target_kind == "browser"
    assert "firefox" in cmds[0].target_name.lower() or "mozilla" in cmds[0].target_name.lower()


def test_open_named_folder_enters_that_item() -> None:
    cmds = plan_turn_start("open the Projects folder", _desktop())
    assert cmds[0].action == "enter"
    assert cmds[0].target_kind == "item"
    assert cmds[0].target_name == "Projects"


def test_question_with_no_desktop_target_stays_in_place() -> None:
    cmds = plan_turn_start("what is two plus two?", _desktop())
    assert cmds == (AvatarCommand(action="face", face="focused"),)


def test_finished_task_pops_out_with_done_face() -> None:
    cmds = plan_turn_end(ok=True)
    assert cmds[0].action == "pop_out"
    assert cmds[0].face == "done"


def test_failed_task_pops_out_with_error_face() -> None:
    cmds = plan_turn_end(ok=False)
    assert cmds[0].action == "pop_out"
    assert cmds[0].face == "error"


def test_idle_never_enters_an_app() -> None:
    for choice in range(8):
        cmd = plan_idle(choice)
        assert cmd.action != "enter"
        assert cmd.face in {"blank", "curious", "sleepy", "wink"}


def test_find_browser_window_prefers_a_real_browser() -> None:
    browser = find_browser_window(_desktop().windows)
    assert browser is not None
    assert "firefox" in browser.wm_class.lower()


def test_avatar_ws_url_is_off_by_default(monkeypatch) -> None:
    monkeypatch.delenv("GHOST_AVATAR", raising=False)
    monkeypatch.delenv("GHOST_AVATAR_WS", raising=False)
    assert avatar_ws_url() is None


def test_avatar_ws_url_defaults_when_enabled(monkeypatch) -> None:
    monkeypatch.setenv("GHOST_AVATAR", "1")
    monkeypatch.delenv("GHOST_AVATAR_WS", raising=False)
    assert avatar_ws_url() == "ws://127.0.0.1:8765"


def test_desktop_from_payload_round_trips_sensor_state() -> None:
    restored = desktop_from_payload(_desktop().to_dict())
    assert restored.windows[0].title == "GitHub — Mozilla Firefox"
    assert restored.items[0].name == "Projects"
