"""Runner for Ghost 3D Desktop Avatar System.

Starts the local WebSocket Bridge, serves the 3D anime overlay frontend,
and launches the transparent desktop viewport.
"""

from __future__ import annotations

import argparse
import asyncio
import http.server
import logging
import shutil
import socketserver
import subprocess
import threading
from pathlib import Path

from .bridge import AvatarBridge
from .sensor import DesktopSensor

logger = logging.getLogger("ghost.avatar")

OVERLAY_DIR = Path(__file__).parent / "overlay"


class QuietHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """Serve static overlay files quietly without cluttering agent logs."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(OVERLAY_DIR), **kwargs)

    def log_message(self, fmt: str, *args) -> None:
        pass


def start_http_server(port: int = 8766) -> socketserver.TCPServer:
    """Start local HTTP server for the 3D overlay assets."""
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("127.0.0.1", port), QuietHTTPHandler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    logger.info("Overlay HTTP server running on http://127.0.0.1:%d", port)
    return httpd


def launch_browser_overlay(url: str, transparent: bool = True) -> subprocess.Popen | None:
    """Launch Chrome / Chromium in transparent app mode or default browser."""
    chrome_bin = (
        shutil.which("google-chrome")
        or shutil.which("chromium")
        or shutil.which("chromium-browser")
    )
    if chrome_bin:
        flags = [
            chrome_bin,
            f"--app={url}",
            "--user-data-dir=/tmp/ghost_avatar_profile",
            "--window-size=1920,1080",
            "--window-position=0,0",
            "--class=GhostAvatar",
            "--disable-infobars",
            "--enable-features=OverlayScrollbar",
            "--no-first-run",
            "--no-default-browser-check",
        ]
        if transparent:
            flags.extend([
                "--enable-transparent-visuals",
                "--transparent",
            ])
        try:
            return subprocess.Popen(flags, start_new_session=True)
        except Exception as e:
            logger.warning("Could not launch chrome app mode: %s", e)

    # Fallback to standard xdg-open
    if shutil.which("xdg-open"):
        subprocess.Popen(["xdg-open", url], start_new_session=True)
    return None


async def run_avatar_system(
    ws_port: int = 8765,
    http_port: int = 8766,
    auto_launch: bool = True,
) -> None:
    """Main async entry point for the 3D Desktop Avatar system."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    print("\n" + "=" * 60)
    print(" 👻 GHOST 3D DESKTOP AVATAR ENVIRONMENT")
    print("=" * 60)

    # 1. Start HTTP Server for Overlay Assets
    httpd = start_http_server(http_port)
    overlay_url = f"http://127.0.0.1:{http_port}"
    print(f" ▸ Overlay Web Viewport: {overlay_url}")

    # 2. Start Desktop Sensor & WebSocket Bridge
    sensor = DesktopSensor()
    state = sensor.get_state()
    print(f" ▸ Display: {state.screen_width}x{state.screen_height}")
    print(f" ▸ Desktop Folders & Items Detected: {len(state.items)}")
    print(f" ▸ Active Application Windows: {len(state.windows)}")

    bridge = AvatarBridge(sensor=sensor, port=ws_port)
    await bridge.start()
    print(f" ▸ WebSocket IPC Bridge: ws://127.0.0.1:{ws_port}")
    print(" ▸ Drive from `ghost` with GHOST_AVATAR=1")

    # 3. Launch Overlay Viewport
    if auto_launch:
        print(" ▸ Launching transparent 3D desktop overlay...")
        launch_browser_overlay(overlay_url)

    print("\n✨ Ghost 3D Desktop is running! Press Ctrl+C to stop.\n")

    try:
        while True:
            await asyncio.sleep(3600)
    except (asyncio.CancelledError, KeyboardInterrupt):
        print("\nShutting down Ghost Avatar system...")
    finally:
        await bridge.stop()
        httpd.shutdown()


def main() -> None:
    parser = argparse.ArgumentParser(description="Ghost 3D Desktop Avatar System")
    parser.add_argument("--ws-port", type=int, default=8765, help="WebSocket IPC port")
    parser.add_argument("--http-port", type=int, default=8766, help="HTTP overlay port")
    parser.add_argument(
        "--no-launch",
        action="store_true",
        help="Do not automatically launch browser overlay",
    )
    args = parser.parse_args()

    asyncio.run(run_avatar_system(
        ws_port=args.ws_port,
        http_port=args.http_port,
        auto_launch=not args.no_launch,
    ))


if __name__ == "__main__":
    main()
