"""Composite the cute blob with a translucent galaxy core — Ghost mark rules.

Dim volume, drawn rim, constellation clipped inside the body. Face stays.
"""

from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

ROOT = Path("/mnt/data/projects/Github-Repositories/Canticle-Research/Ghost")
SRC = ROOT / "assets/avatar/ghost_blob_sprite.png"
OPAQUE = ROOT / "assets/avatar/ghost_blob_sprite_opaque.png"
OUT = ROOT / "assets/avatar/ghost_blob_sprite.png"
PICTURES = Path("/home/terrabyte/Pictures/canticle/ghost-avatar/ghost_blob_sprite.png")

# Canticle / Tokyo-night stops from the mark
STOPS = [
    (247, 118, 142),  # #f7768e
    (255, 158, 100),  # #ff9e64
    (224, 175, 104),  # #e0af68
    (158, 206, 106),  # #9ece6a
    (125, 207, 255),  # #7dcfff
    (122, 162, 247),  # #7aa2f7
    (196, 167, 231),  # #c4a7e7
]


def _lerp(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return (
        int(a[0] + (b[0] - a[0]) * t),
        int(a[1] + (b[1] - a[1]) * t),
        int(a[2] + (b[2] - a[2]) * t),
    )


def nebula(size: tuple[int, int], rng: random.Random) -> Image.Image:
    w, h = size
    layer = Image.new("RGB", size, (10, 12, 22))
    draw = ImageDraw.Draw(layer, "RGBA")
    for _ in range(28):
        color = rng.choice(STOPS)
        cx = rng.randint(-w // 6, w + w // 6)
        cy = rng.randint(-h // 6, h + h // 6)
        rw = rng.randint(w // 8, w // 2)
        rh = rng.randint(h // 8, h // 2)
        draw.ellipse(
            (cx - rw, cy - rh, cx + rw, cy + rh),
            fill=(*color, rng.randint(40, 95)),
        )
    layer = layer.filter(ImageFilter.GaussianBlur(radius=max(18, w // 28)))
    # second pass of smaller blooms
    bloom = Image.new("RGBA", size, (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(bloom)
    for _ in range(16):
        color = rng.choice(STOPS)
        cx = rng.randint(0, w)
        cy = rng.randint(int(h * 0.15), int(h * 0.85))
        r = rng.randint(w // 16, w // 5)
        bdraw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(*color, rng.randint(50, 110)))
    bloom = bloom.filter(ImageFilter.GaussianBlur(radius=max(10, w // 40)))
    layer = Image.alpha_composite(layer.convert("RGBA"), bloom)
    return layer


def constellation(size: tuple[int, int], rng: random.Random) -> Image.Image:
    w, h = size
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # field of faint stars
    for _ in range(180):
        x = rng.randint(0, w - 1)
        y = rng.randint(0, h - 1)
        s = rng.choice((1, 1, 1, 2))
        a = rng.randint(80, 220)
        c = rng.choice(STOPS)
        draw.ellipse((x, y, x + s, y + s), fill=(*c, a))
    # core nodes — neural constellation, clipped later by the body
    nodes: list[tuple[int, int]] = []
    cx, cy = w // 2, int(h * 0.55)
    for _ in range(11):
        ang = rng.random() * math.tau
        rad = rng.uniform(0.08, 0.28) * min(w, h)
        nx = int(cx + math.cos(ang) * rad)
        ny = int(cy + math.sin(ang) * rad * 0.85)
        nodes.append((nx, ny))
    for i, (x1, y1) in enumerate(nodes):
        for j, (x2, y2) in enumerate(nodes):
            if j <= i:
                continue
            dist = math.hypot(x1 - x2, y1 - y2)
            if dist < min(w, h) * 0.22:
                c = rng.choice(STOPS)
                draw.line((x1, y1, x2, y2), fill=(*c, 70), width=1)
    for x, y in nodes:
        c = rng.choice(STOPS)
        r = rng.randint(2, 4)
        draw.ellipse((x - r * 3, y - r * 3, x + r * 3, y + r * 3), fill=(*c, 50))
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, 230))
    return img.filter(ImageFilter.GaussianBlur(radius=0.6))


def compose(src: Image.Image) -> Image.Image:
    src = src.convert("RGBA")
    w, h = src.size
    # Fixed seed for reproducible sprite art, not for secrets.
    rng = random.Random(20260821)  # noqa: S311
    galaxy = nebula((w, h), rng)
    stars = constellation((w, h), rng)
    galaxy = Image.alpha_composite(galaxy, stars)

    px = src.load()
    gx = galaxy.load()
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ox = out.load()

    def lum(r: int, g: int, b: int) -> int:
        return (r * 3 + g * 6 + b) // 10

    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 8:
                continue
            edge = False
            if x == 0 or y == 0 or x == w - 1 or y == h - 1:
                edge = True
            else:
                for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2), (-3, -3), (3, 3)):
                    if px[max(0, min(w - 1, x + dx)), max(0, min(h - 1, y + dy))][3] < 20:
                        edge = True
                        break
            gr, gg, gb, _ga = gx[x, y]
            L = lum(r, g, b)
            # black eyes / dark face marks stay
            is_eye = L < 55 and a > 180
            # blush / tongue / high-chroma face bits
            is_face = (r > 180 and g < 160 and b > 140 and L > 70) or (
                r > 200 and g > 80 and b > 140 and y < h * 0.48
            )
            if is_eye:
                ox[x, y] = (r, g, b, 240)
            elif is_face:
                mix = 0.55
                ox[x, y] = (
                    int(r * mix + gr * (1 - mix)),
                    int(g * mix + gg * (1 - mix)),
                    int(b * mix + gb * (1 - mix)),
                    200,
                )
            elif edge:
                # drawn rim over bloom — mark spec
                rim = _lerp((r, g, b), (125, 207, 255), 0.35)
                ox[x, y] = (*rim, 210)
            else:
                # dim volume: galaxy reads through, original is a whisper
                mix = 0.18
                ox[x, y] = (
                    int(r * mix + gr * (1 - mix)),
                    int(g * mix + gg * (1 - mix)),
                    int(b * mix + gb * (1 - mix)),
                    128,
                )
    # soft outer bloom
    glow = out.filter(ImageFilter.GaussianBlur(radius=6))
    glow = ImageEnhance.Brightness(glow).enhance(1.25)
    glow.putalpha(glow.getchannel("A").point(lambda v: int(v * 0.35)))
    return Image.alpha_composite(glow, out)


def main() -> None:
    if not OPAQUE.exists():
        Image.open(SRC).save(OPAQUE)
    result = compose(Image.open(OPAQUE))
    result.save(OUT)
    PICTURES.parent.mkdir(parents=True, exist_ok=True)
    result.save(PICTURES)
    print(f"wrote {OUT} {result.size}")


if __name__ == "__main__":
    main()
