"""Desktop Spatial Sensor & Interaction Controller.

Monitors X11 window tree, screen dimensions, and ~/Desktop items to map the OS
desktop into 3D spatial coordinates that Ghost's avatar can traverse and interact with.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class WindowInfo:
    """Represents a visible desktop application window."""

    window_id: str
    title: str
    wm_class: str
    x: int
    y: int
    width: int
    height: int
    is_active: bool = False
    z_index: int = 0


@dataclass(frozen=True)
class DesktopItem:
    """Represents an icon or folder located on the user's desktop."""

    name: str
    path: str
    item_type: str  # 'folder', 'app', 'file'
    grid_col: int
    grid_row: int
    x: int
    y: int


@dataclass
class DesktopState:
    """Complete snapshot of the desktop spatial environment."""

    screen_width: int
    screen_height: int
    windows: list[WindowInfo] = field(default_factory=list)
    items: list[DesktopItem] = field(default_factory=list)
    timestamp: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class DesktopSensor:
    """Inspects X11 desktop geometry, open windows, and Desktop folder contents."""

    def __init__(self, desktop_dir: Path | None = None) -> None:
        self.desktop_dir = desktop_dir or Path.home() / "Desktop"
        self._screen_width = 1920
        self._screen_height = 1080
        self.update_screen_resolution()

    def update_screen_resolution(self) -> tuple[int, int]:
        """Detect primary monitor resolution using xrandr or xwininfo."""
        try:
            res = subprocess.run(
                ["xrandr", "--query"],
                capture_output=True,
                text=True,
                check=False,
                timeout=2,
            )
            primary_match = re.search(r"connected\s+primary\s+(\d+)x(\d+)", res.stdout)
            if not primary_match:
                primary_match = re.search(r"connected\s+(\d+)x(\d+)", res.stdout)
            if primary_match:
                self._screen_width = int(primary_match.group(1))
                self._screen_height = int(primary_match.group(2))
                return self._screen_width, self._screen_height
        except Exception:
            pass

        # Fallback to root window size via xwininfo
        try:
            res = subprocess.run(
                ["xwininfo", "-root"],
                capture_output=True,
                text=True,
                check=False,
                timeout=2,
            )
            w_match = re.search(r"Width:\s+(\d+)", res.stdout)
            h_match = re.search(r"Height:\s+(\d+)", res.stdout)
            if w_match and h_match:
                self._screen_width = int(w_match.group(1))
                self._screen_height = int(h_match.group(2))
        except Exception:
            pass

        return self._screen_width, self._screen_height

    def scan_windows(self) -> list[WindowInfo]:
        """Query top-level X11 windows and extract bounding boxes and names."""
        windows: list[WindowInfo] = []
        try:
            res = subprocess.run(
                ["xwininfo", "-root", "-tree"],
                capture_output=True,
                text=True,
                check=False,
                timeout=3,
            )
        except Exception:
            return windows

        # Match lines: 0x340001c "Chrome": ("google-chrome" "Google-chrome") 1920x999+0+32 +0+32
        line_re = re.compile(
            r'^\s*(0x[0-9a-fA-F]+)\s+"([^"]*)":\s+\("([^"]*)"\s+"([^"]*)"\)\s+'
            r"(\d+)x(\d+)\+(-?\d+)\+(-?\d+)"
        )

        ignored_classes = {
            "gnome-shell",
            "Desktop",
            "ibus-ui-gtk3",
            "GhostAvatar",
            "ghost-avatar",
        }

        for line in res.stdout.splitlines():
            match = line_re.match(line)
            if not match:
                continue

            wid, title, wm_name, wm_class, w_str, h_str, x_str, y_str = match.groups()
            width = int(w_str)
            height = int(h_str)
            x = int(x_str)
            y = int(y_str)

            if width < 150 or height < 100:
                continue
            if wm_class in ignored_classes or wm_name in ignored_classes:
                continue
            if not title and not wm_name:
                continue

            display_title = title if title else wm_class
            windows.append(
                WindowInfo(
                    window_id=wid,
                    title=display_title,
                    wm_class=wm_class,
                    x=x,
                    y=y,
                    width=width,
                    height=height,
                    is_active=False,
                    z_index=len(windows),
                )
            )

        return windows

    def scan_desktop_items(self) -> list[DesktopItem]:
        """Scan ~/Desktop and calculate 2D grid coordinates for folders and apps."""
        items: list[DesktopItem] = []
        if not self.desktop_dir.exists():
            return items

        col_width = 120
        row_height = 110
        start_x = 40
        start_y = 50
        max_rows = max(1, (self._screen_height - 100) // row_height)

        entries = sorted(
            [e for e in self.desktop_dir.iterdir() if not e.name.startswith(".")],
            key=lambda p: (not p.is_dir(), p.name.lower()),
        )

        for idx, entry in enumerate(entries):
            col = idx // max_rows
            row = idx % max_rows

            x = start_x + (col * col_width)
            y = start_y + (row * row_height)

            if entry.is_dir():
                item_type = "folder"
            elif entry.suffix == ".desktop":
                item_type = "app"
            else:
                item_type = "file"

            name = entry.name
            if item_type == "app" and name.endswith(".desktop"):
                name = name[:-8].replace("-", " ").replace("_", " ").title()

            items.append(
                DesktopItem(
                    name=name,
                    path=str(entry.resolve()),
                    item_type=item_type,
                    grid_col=col,
                    grid_row=row,
                    x=x,
                    y=y,
                )
            )

        return items

    def get_state(self) -> DesktopState:
        """Capture the full current desktop state."""
        import time

        w, h = self.update_screen_resolution()
        windows = self.scan_windows()
        items = self.scan_desktop_items()
        return DesktopState(
            screen_width=w,
            screen_height=h,
            windows=windows,
            items=items,
            timestamp=time.time(),
        )

    # --- Interactive Desktop Actions ---

    def open_item(self, target_path: str | Path) -> bool:
        """Open a desktop folder or file in the default OS file manager/app."""
        path = Path(target_path).resolve()
        if not path.exists():
            return False

        try:
            if shutil.which("xdg-open"):
                subprocess.Popen(["xdg-open", str(path)], start_new_session=True)
                return True
            if path.is_dir() and shutil.which("nautilus"):
                subprocess.Popen(["nautilus", str(path)], start_new_session=True)
                return True
        except Exception:
            return False
        return False

    def launch_app(self, desktop_file_or_command: str) -> bool:
        """Launch a desktop application or command."""
        try:
            if desktop_file_or_command.endswith(".desktop") and shutil.which("gtk-launch"):
                app_id = Path(desktop_file_or_command).stem
                subprocess.Popen(["gtk-launch", app_id], start_new_session=True)
                return True
            if shutil.which("xdg-open"):
                subprocess.Popen(["xdg-open", desktop_file_or_command], start_new_session=True)
                return True
        except Exception:
            return False
        return False
