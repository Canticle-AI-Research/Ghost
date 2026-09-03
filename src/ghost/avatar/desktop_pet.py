"""Desktop-layer Ghost: a body of light-dust, not a sticker full of marbles."""

from __future__ import annotations

import math
import os
import random
from pathlib import Path

import gi
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
# PyGObject requires require_version() to run before the namespace import.
from gi.repository import Gdk, GdkPixbuf, GLib, Gtk  # noqa: E402

SPRITE = (
    Path(__file__).resolve().parents[3]
    / "assets"
    / "avatar"
    / "ghost_blob_sprite.png"
)
OPAQUE = (
    Path(__file__).resolve().parents[3] / "assets" / "avatar" / "ghost_B2_opaque.png"
)
SIZE = 160
PAD = 28
WIN = SIZE + PAD * 2
STOPS = [
    (125, 207, 255),
    (122, 162, 247),
    (158, 206, 106),
    (196, 167, 231),
    (255, 158, 200),
    (180, 230, 255),
]


def _pil_to_pixbuf(im: Image.Image) -> tuple[GdkPixbuf.Pixbuf, bytes]:
    im = im.convert("RGBA")
    raw = im.tobytes()
    pb = GdkPixbuf.Pixbuf.new_from_data(
        raw,
        GdkPixbuf.Colorspace.RGB,
        True,
        8,
        im.width,
        im.height,
        im.width * 4,
    )
    return pb, raw


def _remove_squiggle(img: Image.Image) -> Image.Image:
    """Paint out the hot-pink drip line on B2's crown."""
    img = img.copy()
    px = img.load()
    w, h = img.size
    bbox = img.getbbox() or (0, 0, w, h)
    y_cut = bbox[1] + int((bbox[3] - bbox[1]) * 0.42)
    for y in range(bbox[1], y_cut):
        for x in range(bbox[0], bbox[2]):
            r, g, b, a = px[x, y]
            if a < 20:
                continue
            if r > 175 and g < 165 and b > 130 and r > g + 25:
                px[x, y] = (
                    int(90 + g * 0.35),
                    int(180 + g * 0.15),
                    int(210 + b * 0.08),
                    a,
                )
    return img.filter(ImageFilter.SMOOTH)


def _eye_layer(src: Image.Image) -> Image.Image:
    """Keep the original oval eyes; nothing redrawn."""
    out = Image.new("RGBA", src.size, (0, 0, 0, 0))
    sp, op = src.load(), out.load()
    w, h = src.size
    bbox = src.getbbox() or (0, 0, w, h)
    y0 = bbox[1] + int((bbox[3] - bbox[1]) * 0.22)
    y1 = bbox[1] + int((bbox[3] - bbox[1]) * 0.52)
    x0 = bbox[0] + int((bbox[2] - bbox[0]) * 0.18)
    x1 = bbox[0] + int((bbox[2] - bbox[0]) * 0.82)
    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, b, a = sp[x, y]
            if a < 40:
                continue
            if (r * 3 + g * 6 + b) // 10 < 48:
                op[x, y] = (12, 10, 16, 255)
    return out


def _seed_dust(mask: Image.Image, rng: random.Random) -> list[tuple]:
    """Gas/dust samples that *are* the body."""
    w, h = mask.size
    px = mask.load()
    dust: list[tuple] = []
    for y in range(h):
        for x in range(w):
            if px[x, y] < 70:
                continue
            edge = False
            for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
                nx, ny = x + dx, y + dy
                if not (0 <= nx < w and 0 <= ny < h) or px[nx, ny] < 40:
                    edge = True
                    break
            keep = rng.random() < (0.55 if edge else 0.18)
            if not keep:
                continue
            dust.append(
                (
                    x - w / 2,
                    y - h / 2,
                    edge,
                    rng.choice(STOPS),
                    rng.uniform(0, math.tau),
                    1 if edge or rng.random() < 0.12 else 0,
                )
            )
    return dust


class GhostPet(Gtk.Window):
    def __init__(self, sprite: Path) -> None:
        super().__init__()
        self.set_title("")
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_app_paintable(True)
        self.set_resizable(False)
        self.set_default_size(WIN, WIN)

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual is not None:
            self.set_visual(visual)

        body_path = OPAQUE if OPAQUE.exists() else sprite
        body = Image.open(body_path).convert("RGBA").resize((SIZE, SIZE), Image.Resampling.LANCZOS)
        body = _remove_squiggle(body)
        self._mask = body.getchannel("A")
        self._wash = body
        self._eyes = _eye_layer(body)
        # Fixed seed for reproducible visual jitter, not for secrets.
        rng = random.Random(20260821)  # noqa: S311
        self._dust = _seed_dust(self._mask, rng)

        self._image = Gtk.Image()
        box = Gtk.EventBox()
        box.set_visible_window(False)
        box.add(self._image)
        box.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK
            | Gdk.EventMask.BUTTON_RELEASE_MASK
            | Gdk.EventMask.BUTTON1_MOTION_MASK
            | Gdk.EventMask.POINTER_MOTION_MASK
        )
        box.connect("button-press-event", self._on_press)
        box.connect("button-release-event", self._on_release)
        box.connect("motion-notify-event", self._on_motion)
        self.add(box)

        self._t = 0.0
        self._base_x = 0
        self._base_y = 0
        self._dragging = False
        self._grab_dx = 0.0
        self._grab_dy = 0.0
        self._keep_bytes = b""
        self.connect("realize", self._on_realize)
        GLib.timeout_add(33, self._tick)

    def _on_realize(self, *_args: object) -> None:
        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor() if display is not None else None
        geo = monitor.get_geometry() if monitor is not None else None
        env_x, env_y = os.environ.get("GHOST_PET_X"), os.environ.get("GHOST_PET_Y")
        if env_x and env_y:
            self._base_x, self._base_y = int(env_x), int(env_y)
        elif geo is not None:
            self._base_x = geo.x + geo.width - WIN - 80
            self._base_y = geo.y + geo.height // 3
        else:
            self._base_x, self._base_y = 1400, 300
        self.move(self._base_x, self._base_y)
        gdk_win = self.get_window()
        if gdk_win is not None:
            gdk_win.set_override_redirect(True)

    def _frame(self) -> Image.Image:
        t = self._t
        gas = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        draw = ImageDraw.Draw(gas)
        mask_px = self._mask.load()
        blink = (t % 4.8) < 0.12
        for dx, dy, edge, color, phase, _rad in self._dust:
            # Silhouette stays put. Only interior gas drifts in place.
            if edge:
                x = int(SIZE / 2 + dx)
                y = int(SIZE / 2 + dy)
            else:
                drift = 3.5
                x = int(SIZE / 2 + dx + drift * math.cos(t * 0.9 + phase))
                y = int(SIZE / 2 + dy + drift * math.sin(t * 1.05 + phase * 1.3))
            if not (0 <= x < SIZE and 0 <= y < SIZE):
                continue
            if mask_px[x, y] < 50:
                continue
            tw = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(t * 2.4 + phase))
            if edge:
                a = int(170 + 70 * tw)
                c = (min(255, color[0] + 40), min(255, color[1] + 40), min(255, color[2] + 50))
            else:
                a = int(80 + 120 * tw)
                c = color
            draw.point((x, y), fill=(*c, a))
            if tw > 0.78:
                draw.point((x, y), fill=(255, 255, 255, min(255, a + 40)))
        # faint original jelly as a ghost of form, not a sticker
        wash = self._wash.copy()
        wr, wg, wb, wa = wash.split()
        wr = wr.point(lambda v: int(v * 0.55))
        wg = wg.point(lambda v: int(v * 0.7))
        wb = wb.point(lambda v: int(v * 0.85))
        wa = wa.point(lambda v: int(v * 0.38) if v else 0)
        wash = Image.merge("RGBA", (wr, wg, wb, wa))
        char = Image.alpha_composite(wash, gas)
        eyes = self._eyes.copy()
        if blink:
            eyes.putalpha(eyes.getchannel("A").point(lambda v: int(v * 0.15)))
        char = Image.alpha_composite(char, eyes)
        # outer bloom — made of light
        canvas = Image.new("RGBA", (WIN, WIN), (0, 0, 0, 0))
        canvas.paste(char, (PAD, PAD), char)
        glow = canvas.filter(ImageFilter.GaussianBlur(radius=7))
        glow = ImageEnhance.Brightness(glow).enhance(1.35)
        glow.putalpha(glow.getchannel("A").point(lambda v: int(v * 0.45)))
        return Image.alpha_composite(glow, canvas)

    def _show(self) -> None:
        pb, raw = _pil_to_pixbuf(self._frame())
        self._keep_bytes = raw
        self._image.set_from_pixbuf(pb)

    def _on_press(self, _widget: Gtk.Widget, event: Gdk.EventButton) -> bool:
        if event.button != 1:
            return False
        wx, wy = self.get_position()
        self._dragging = True
        self._grab_dx = event.x_root - wx
        self._grab_dy = event.y_root - wy
        Gdk.pointer_grab(
            event.window,
            False,
            Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.BUTTON1_MOTION_MASK,
            None,
            None,
            event.time,
        )
        return True

    def _on_motion(self, _widget: Gtk.Widget, event: Gdk.EventMotion) -> bool:
        if not self._dragging:
            return False
        self._base_x = int(event.x_root - self._grab_dx)
        self._base_y = int(event.y_root - self._grab_dy)
        self.move(self._base_x, self._base_y)
        return True

    def _on_release(self, _widget: Gtk.Widget, event: Gdk.EventButton) -> bool:
        if event.button != 1:
            return False
        self._dragging = False
        Gdk.pointer_ungrab(event.time)
        return True

    def _tick(self) -> bool:
        self._t += 0.033
        self._show()
        if not self._dragging:
            dx = int(2.5 * math.sin(self._t * 0.85))
            dy = int(3.5 * math.sin(self._t * 1.15))
            self.move(self._base_x + dx, self._base_y + dy)
        return True


def main() -> None:
    sprite = Path(os.environ.get("GHOST_SPRITE", str(SPRITE)))
    if not sprite.exists():
        raise SystemExit(f"missing sprite: {sprite}")
    Gtk.init([])
    pet = GhostPet(sprite)
    pet.connect("destroy", Gtk.main_quit)
    pet.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
