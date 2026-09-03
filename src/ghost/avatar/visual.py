"""Deterministic B2 renderer: stable silhouette, neon gas, and neural light."""

from __future__ import annotations

import argparse
import math
import random
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

from .state import VISUAL_STATES, AvatarState, coerce_avatar_state

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SOURCE = REPO_ROOT / "assets" / "avatar" / "ghost_B2_sprite.png"
SIZE = 160
PAD = 28
CANVAS_SIZE = SIZE + (PAD * 2)
SEED = 20260821


@dataclass(frozen=True, slots=True)
class Particle:
    x: float
    y: float
    phase: float
    radius: int
    mix: float


@dataclass(frozen=True, slots=True)
class NeuralNode:
    x: float
    y: float
    phase: float


def _remove_squiggle(image: Image.Image) -> Image.Image:
    """Remove the rejected hot-pink crown line while preserving B2's body."""

    image = image.copy()
    pixels = image.load()
    bbox = image.getbbox() or (0, 0, image.width, image.height)
    y_cut = bbox[1] + int((bbox[3] - bbox[1]) * 0.42)
    for y in range(bbox[1], y_cut):
        for x in range(bbox[0], bbox[2]):
            red, green, blue, alpha = pixels[x, y]
            if alpha >= 20 and red > 175 and green < 165 and blue > 130 and red > green + 25:
                pixels[x, y] = (
                    int(90 + green * 0.35),
                    int(180 + green * 0.15),
                    int(210 + blue * 0.08),
                    alpha,
                )
    return image.filter(ImageFilter.SMOOTH)


def _inside(mask: Image.Image, x: float, y: float, threshold: int = 80) -> bool:
    px = min(mask.width - 1, max(0, int(x)))
    py = min(mask.height - 1, max(0, int(y)))
    return mask.getpixel((px, py)) >= threshold


def _sample_points(
    mask: Image.Image,
    rng: random.Random,
    count: int,
    *,
    top: float = 0.12,
    bottom: float = 0.84,
) -> list[tuple[float, float]]:
    bbox = mask.getbbox() or (0, 0, mask.width, mask.height)
    y0 = bbox[1] + (bbox[3] - bbox[1]) * top
    y1 = bbox[1] + (bbox[3] - bbox[1]) * bottom
    points: list[tuple[float, float]] = []
    attempts = 0
    while len(points) < count and attempts < count * 100:
        attempts += 1
        x = rng.uniform(bbox[0], bbox[2] - 1)
        y = rng.uniform(y0, y1)
        if _inside(mask, x, y):
            points.append((x, y))
    return points


def _mix(
    left: tuple[int, int, int],
    right: tuple[int, int, int],
    amount: float,
) -> tuple[int, int, int]:
    return tuple(int(a + (b - a) * amount) for a, b in zip(left, right, strict=True))


class GhostVisualRenderer:
    """Render B2 from explicit operational state without changing its outline."""

    def __init__(self, source: Path = DEFAULT_SOURCE, *, size: int = SIZE) -> None:
        if not source.exists():
            raise FileNotFoundError(f"missing approved B2 source: {source}")
        self.size = size
        body = Image.open(source).convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)
        self.body = _remove_squiggle(body)
        self.mask = self.body.getchannel("A")
        rng = random.Random(SEED)  # noqa: S311 - deterministic visual provenance
        particle_points = _sample_points(self.mask, rng, 260)
        self.particles = [
            Particle(x, y, rng.uniform(0, math.tau), rng.choice((1, 1, 1, 2)), rng.random())
            for x, y in particle_points
        ]
        node_points = _sample_points(self.mask, rng, 11, top=0.42, bottom=0.82)
        self.nodes = [NeuralNode(x, y, rng.uniform(0, math.tau)) for x, y in node_points]
        self.edges = self._build_edges()

    def _build_edges(self) -> tuple[tuple[int, int], ...]:
        edges: set[tuple[int, int]] = set()
        for index, node in enumerate(self.nodes):
            nearest = sorted(
                (
                    ((node.x - other.x) ** 2 + (node.y - other.y) ** 2, other_index)
                    for other_index, other in enumerate(self.nodes)
                    if other_index != index
                ),
                key=lambda item: item[0],
            )[:2]
            for _distance, other_index in nearest:
                edges.add(tuple(sorted((index, other_index))))
        return tuple(sorted(edges))

    def _gas_layer(self, t: float, state: AvatarState) -> Image.Image:
        spec = VISUAL_STATES[state]
        layer = Image.new("RGBA", (self.size, self.size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)
        for particle in self.particles:
            drift = 2.0 + 2.0 * spec.energy
            x = particle.x + drift * math.cos(t * (0.55 + spec.energy * 0.3) + particle.phase)
            y = particle.y + drift * math.sin(
                t * (0.68 + spec.energy * 0.25) + particle.phase * 1.3
            )
            if not _inside(self.mask, x, y, threshold=55):
                continue
            pulse = 0.5 + 0.5 * math.sin(t * (1.4 + spec.energy) + particle.phase)
            color = _mix(spec.primary, spec.secondary, particle.mix)
            alpha = int(38 + 112 * (0.3 + 0.7 * pulse) * (0.45 + spec.energy * 0.55))
            radius = particle.radius
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*color, alpha))
        layer.putalpha(
            Image.composite(layer.getchannel("A"), Image.new("L", layer.size), self.mask)
        )
        return layer.filter(ImageFilter.GaussianBlur(radius=0.55))

    def _neural_layer(self, t: float, state: AvatarState) -> Image.Image:
        spec = VISUAL_STATES[state]
        layer = Image.new("RGBA", (self.size, self.size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)
        positions = []
        for node in self.nodes:
            positions.append(
                (
                    node.x + math.cos(t * 0.4 + node.phase) * 1.4,
                    node.y + math.sin(t * 0.5 + node.phase) * 1.4,
                )
            )
        line_alpha = int(35 + 75 * spec.energy)
        for left, right in self.edges:
            draw.line(
                (*positions[left], *positions[right]),
                fill=(*spec.primary, line_alpha),
                width=1,
            )
        for index, (x, y) in enumerate(positions):
            pulse = 0.5 + 0.5 * math.sin(t * (1.8 + spec.energy) + self.nodes[index].phase)
            radius = 1.2 + pulse * (1.0 + spec.energy)
            color = _mix(spec.primary, spec.secondary, pulse)
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*color, 180))
            if pulse > 0.76:
                draw.point((x, y), fill=(255, 255, 255, 240))
        layer.putalpha(
            Image.composite(layer.getchannel("A"), Image.new("L", layer.size), self.mask)
        )
        return layer

    def _face_layer(self, t: float, state: AvatarState) -> Image.Image:
        spec = VISUAL_STATES[state]
        layer = Image.new("RGBA", (self.size, self.size), (0, 0, 0, 0))
        bbox = self.mask.getbbox() or (0, 0, self.size, self.size)
        width, height = bbox[2] - bbox[0], bbox[3] - bbox[1]
        center_x = bbox[0] + width * 0.5
        eye_y = bbox[1] + height * 0.36
        eye_dx = width * 0.105
        mouth_y = bbox[1] + height * 0.49
        blink = (t % 5.1) < 0.13 or spec.face == "sleepy"
        plate = (
            center_x - width * 0.22,
            eye_y - height * 0.10,
            center_x + width * 0.22,
            mouth_y + height * 0.08,
        )
        face_glow = Image.new("RGBA", layer.size, (0, 0, 0, 0))
        ImageDraw.Draw(face_glow).ellipse(plate, fill=(215, 238, 245, 165))
        layer = Image.alpha_composite(
            layer,
            face_glow.filter(ImageFilter.GaussianBlur(radius=4.2)),
        )
        draw = ImageDraw.Draw(layer)
        ink = (20, 18, 30, 235)
        highlight = (*spec.primary, 220)
        if blink:
            for eye_x in (center_x - eye_dx, center_x + eye_dx):
                draw.arc((eye_x - 5, eye_y - 1, eye_x + 5, eye_y + 5), 8, 172, fill=ink, width=2)
        elif spec.face == "error":
            for eye_x in (center_x - eye_dx, center_x + eye_dx):
                draw.line((eye_x - 4, eye_y - 4, eye_x + 4, eye_y + 4), fill=ink, width=2)
                draw.line((eye_x + 4, eye_y - 4, eye_x - 4, eye_y + 4), fill=ink, width=2)
        elif spec.face == "nervous":
            for eye_x in (center_x - eye_dx, center_x + eye_dx):
                draw.ellipse((eye_x - 3, eye_y - 6, eye_x + 3, eye_y + 5), fill=ink)
                draw.point((eye_x, eye_y - 3), fill=highlight)
        else:
            for eye_x in (center_x - eye_dx, center_x + eye_dx):
                eye_height = 10 if spec.face in {"focused", "curious"} else 12
                draw.ellipse(
                    (eye_x - 4, eye_y - eye_height / 2, eye_x + 4, eye_y + eye_height / 2),
                    fill=ink,
                )
                draw.ellipse(
                    (eye_x - 1.5, eye_y - eye_height / 3, eye_x + 1, eye_y - 1),
                    fill=highlight,
                )
        if spec.face == "happy":
            draw.arc(
                (center_x - 7, mouth_y - 5, center_x + 7, mouth_y + 5),
                5,
                175,
                fill=ink,
                width=2,
            )
        elif spec.face in {"error", "nervous"}:
            draw.arc(
                (center_x - 6, mouth_y - 1, center_x + 6, mouth_y + 7),
                190,
                350,
                fill=ink,
                width=2,
            )
        elif spec.face == "focused":
            draw.line((center_x - 4, mouth_y, center_x + 4, mouth_y), fill=ink, width=2)
        else:
            draw.ellipse((center_x - 3, mouth_y - 2, center_x + 3, mouth_y + 4), fill=ink)
        return layer

    def render(self, t: float, state: str | AvatarState = AvatarState.IDLE) -> Image.Image:
        state = coerce_avatar_state(state)
        spec = VISUAL_STATES[state]
        red, green, blue, alpha = self.body.split()
        wash = Image.merge(
            "RGBA",
            (
                red.point(lambda value: int(value * 0.85)),
                green.point(lambda value: int(value * 0.92)),
                blue,
                alpha.point(
                    lambda value: int(value * (0.58 + spec.energy * 0.12)) if value else 0
                ),
            ),
        )
        character = Image.alpha_composite(wash, self._gas_layer(t, state))
        character = Image.alpha_composite(character, self._neural_layer(t, state))
        character = Image.alpha_composite(character, self._face_layer(t, state))
        canvas = Image.new("RGBA", (CANVAS_SIZE, CANVAS_SIZE), (0, 0, 0, 0))
        canvas.paste(character, (PAD, PAD), character)
        glow = canvas.filter(ImageFilter.GaussianBlur(radius=7 + spec.energy * 2))
        glow = ImageEnhance.Brightness(glow).enhance(1.2 + spec.energy * 0.25)
        glow.putalpha(glow.getchannel("A").point(lambda value: int(value * 0.42)))
        return Image.alpha_composite(glow, canvas)


def render_contact_sheet(renderer: GhostVisualRenderer, *, t: float = 1.75) -> Image.Image:
    """Render every operational state for one deterministic review artifact."""

    states = list(AvatarState)
    tile_width, tile_height = CANVAS_SIZE + 16, CANVAS_SIZE + 42
    columns = 3
    rows = math.ceil(len(states) / columns)
    sheet = Image.new("RGB", (columns * tile_width, rows * tile_height), (26, 27, 38))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for index, state in enumerate(states):
        x = (index % columns) * tile_width
        y = (index // columns) * tile_height
        frame = renderer.render(t + index * 0.31, state)
        sheet.paste(frame, (x + 8, y + 6), frame)
        draw.text((x + 12, y + CANVAS_SIZE + 12), state.value, fill=(225, 230, 245), font=font)
    return sheet


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--state", default=AvatarState.IDLE.value)
    parser.add_argument("--time", type=float, default=1.75)
    parser.add_argument("--contact-sheet", action="store_true")
    args = parser.parse_args()
    renderer = GhostVisualRenderer(args.source)
    image = (
        render_contact_sheet(renderer, t=args.time)
        if args.contact_sheet
        else renderer.render(args.time, args.state)
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.output)
    print(args.output)


if __name__ == "__main__":
    main()
