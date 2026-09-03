"""Avatar Event & Communication Bridge.

Runs a lightweight WebSocket server connecting Ghost's agent reasoning loop,
the desktop sensor, and the 3D anime overlay renderer.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
from collections.abc import Callable
from typing import Any

import websockets
from websockets.asyncio.server import ServerConnection, serve

from .sensor import DesktopSensor

logger = logging.getLogger("ghost.avatar.bridge")


class AvatarBridge:
    """Coordinates IPC between Python Ghost agent and the 3D Desktop overlay."""

    def __init__(
        self,
        sensor: DesktopSensor | None = None,
        host: str = "127.0.0.1",
        port: int = 8765,
    ) -> None:
        self.sensor = sensor or DesktopSensor()
        self.host = host
        self.port = port
        self.clients: set[ServerConnection] = set()
        self.server: Any = None
        self._running = False
        self._sync_task: asyncio.Task[None] | None = None
        self._action_callbacks: list[Callable[[dict[str, Any]], None]] = []

    async def register(self, websocket: ServerConnection) -> None:
        """Register a new overlay client connection."""
        self.clients.add(websocket)
        logger.info("Avatar overlay connected (%d clients)", len(self.clients))
        # Send immediate initial desktop state
        await self.send_desktop_sync(websocket)

    async def unregister(self, websocket: ServerConnection) -> None:
        """Unregister an overlay client."""
        self.clients.discard(websocket)
        logger.info("Avatar overlay disconnected (%d clients)", len(self.clients))

    async def broadcast(self, message: dict[str, Any]) -> None:
        """Broadcast a JSON message to all connected overlay clients."""
        if not self.clients:
            return
        payload = json.dumps(message)
        to_remove = set()
        for client in self.clients:
            try:
                await client.send(payload)
            except websockets.ConnectionClosed:
                to_remove.add(client)
        for client in to_remove:
            self.clients.discard(client)

    async def send_desktop_sync(self, websocket: ServerConnection | None = None) -> None:
        """Send current desktop window geometry and folder coordinates."""
        state = self.sensor.get_state()
        msg = {
            "type": "desktop_sync",
            "state": state.to_dict(),
        }
        if websocket:
            with contextlib.suppress(websockets.ConnectionClosed):
                await websocket.send(json.dumps(msg))
        else:
            await self.broadcast(msg)

    # --- Agent Interaction Triggers ---

    async def command_avatar(
        self,
        action: str,
        *,
        target_name: str | None = None,
        target_x: int | None = None,
        target_y: int | None = None,
        text: str | None = None,
        emotion: str = "normal",
        duration: float = 2.0,
        face: str | None = None,
        target_kind: str | None = None,
    ) -> None:
        """Dispatch a visual movement or action to the desktop avatar."""
        msg = {
            "type": "avatar_action",
            "action": action,
            "target_name": target_name,
            "target_kind": target_kind,
            "target_x": target_x,
            "target_y": target_y,
            "text": text,
            "emotion": emotion,
            "face": face,
            "duration": duration,
        }
        await self.broadcast(msg)

    async def report_agent_state(
        self,
        state: str,  # 'idle', 'thinking', 'acting', 'speaking', 'error'
        detail: str = "",
        emotion: str = "normal",
    ) -> None:
        """Notify the avatar of Ghost's internal cognitive state."""
        msg = {
            "type": "agent_state",
            "state": state,
            "detail": detail,
            "emotion": emotion,
        }
        await self.broadcast(msg)

    # --- Incoming Client Messages ---

    async def handle_client_message(self, data: str) -> None:
        """Process messages and events received from the 3D overlay."""
        try:
            payload = json.loads(data)
        except Exception:
            return

        msg_type = payload.get("type")

        # Overlay clicked a desktop folder/icon
        if msg_type == "open_item":
            path = payload.get("path")
            if path:
                self.sensor.open_item(path)

        # Overlay launched an app
        elif msg_type == "launch_app":
            target = payload.get("target")
            if target:
                self.sensor.launch_app(target)

        # Custom interaction callback for external listeners
        for cb in self._action_callbacks:
            try:
                cb(payload)
            except Exception as e:
                logger.error("Error in action callback: %s", e)

    def on_action(self, callback: Callable[[dict[str, Any]], None]) -> None:
        """Register a callback for overlay-generated user interactions."""
        self._action_callbacks.append(callback)

    # --- Server Lifecycle & Periodic Sync ---

    async def _ws_handler(self, websocket: ServerConnection) -> None:
        await self.register(websocket)
        try:
            async for message in websocket:
                await self.handle_client_message(str(message))
        except websockets.ConnectionClosed:
            pass
        finally:
            await self.unregister(websocket)

    async def _periodic_desktop_sync(self, interval: float = 1.0) -> None:
        """Periodically scan and sync desktop windows & folders."""
        while self._running:
            try:
                await self.send_desktop_sync()
            except Exception as e:
                logger.error("Error in periodic sync: %s", e)
            await asyncio.sleep(interval)

    async def start(self) -> None:
        """Start the WebSocket server and periodic sync loop."""
        self._running = True
        self.server = await serve(self._ws_handler, self.host, self.port)
        logger.info("Ghost Avatar Bridge listening on ws://%s:%d", self.host, self.port)
        self._sync_task = asyncio.create_task(self._periodic_desktop_sync(1.0))

    async def stop(self) -> None:
        """Stop the WebSocket server."""
        self._running = False
        if self._sync_task:
            self._sync_task.cancel()
            self._sync_task = None
        if self.server:
            self.server.close()
            await self.server.wait_closed()
