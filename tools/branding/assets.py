"""Produce brand-correct assets from the vendored token contract.

TEMPORARY VENDOR. The brand toolkit is being extracted into its own repository
and this copy exists only so Ghost can regenerate its identity in the meantime.
Treat it as a bridge, not as the canonical source:

  - do not fix bugs here alone; fix them where the toolkit is being extracted to
  - when the toolkit ships as a package, delete this directory and depend on it
  - branding/tokens.json is likewise a copy of the Canticle contract, which
    upstream owns; a palette or motion change there is copied down deliberately

Kept deliberately small and dependency-light so the swap is a one-line change.

Every asset this company ships -- a logo, an avatar, a favicon, an ad card, a
report, a video frame -- should derive its colors, type, and lockup geometry
from one place. In this repo that place is ``branding/tokens.json``, which
already records the palette, font stacks, lockup geometry, and motion timing.

This module is the consumer side of that contract. It resolves the tokens
(including the ``color.semantic.*`` aliases, which point at other token paths
rather than at literal colors), emits them as CSS custom properties, and
rasterizes SVG or HTML into whatever format the surface needs.

Renderers are deliberately ones already present on this machine, so the
pipeline needs no new system packages:

    headless Chrome   SVG/HTML -> PNG at any scale, HTML -> PDF
    ffmpeg            PNG frame sequence -> MP4/WebM
    Pillow            multi-resolution ICO

The brand faces (Fira Code, Outfit, Press Start 2P) are not bundled with the
kit by design. They are the FIRST entry in each stack in tokens.json; the rest
(JetBrains Mono, Cascadia Mono, system-ui) are fallbacks, and their absence on
a given machine is not a defect. ``check_fonts()`` reports which are missing,
because a render that silently falls back to a generic face is off-brand in a
way nobody notices until it is printed.

Usage:
    python -m tools.branding.assets fonts
    python -m tools.branding.assets css --out build/brand.css
    python -m tools.branding.assets png  logo.svg out.png --width 1024
    python -m tools.branding.assets pdf  report.html out.pdf
    python -m tools.branding.assets ico  mark.svg favicon.ico
    python -m tools.branding.assets video frames/ out.mp4 --fps 30
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TOKENS_PATH = REPO_ROOT / "branding" / "tokens.json"

# Ordered by preference; the first one present wins.
CHROME_CANDIDATES: tuple[str, ...] = (
    "google-chrome", "chromium", "chromium-browser", "google-chrome-stable",
)
ICO_SIZES: tuple[int, ...] = (16, 32, 48, 64, 128, 256)


class BrandError(RuntimeError):
    """Raised when the toolkit cannot produce a correct asset."""


@dataclass(frozen=True)
class Tokens:
    raw: dict
    colors: dict[str, str]
    typography: dict
    lockup: dict
    motion: dict

    def color(self, path: str) -> str:
        """Look up a color by dotted path, e.g. 'accent.mint' or 'semantic.brand_live'."""
        if path not in self.colors:
            raise BrandError(f"unknown color token {path!r}; have {sorted(self.colors)[:8]}...")
        return self.colors[path]

    def font_stack(self, family: str) -> str:
        fams = self.typography.get("families", {}).get(family)
        if not fams:
            raise BrandError(f"unknown font family {family!r}")
        return ", ".join(f"'{f}'" if " " in f else f for f in fams)


def _flatten_colors(color_block: dict) -> dict[str, str]:
    """Flatten color.* to dotted keys, then resolve semantic aliases.

    A semantic entry holds a token *path* ("color.base.bg"), not a literal, so
    it must be resolved after the literal groups are flattened. Unresolvable
    aliases are dropped rather than passed through, so a typo surfaces as a
    missing token instead of a CSS value of the literal string.
    """
    flat: dict[str, str] = {}
    for group, entries in color_block.items():
        if not isinstance(entries, dict):
            continue
        for name, value in entries.items():
            if isinstance(value, str):
                flat[f"{group}.{name}"] = value

    resolved = dict(flat)
    for key, value in flat.items():
        if not value.startswith("color."):
            continue
        target = value[len("color."):]
        if target in flat and not flat[target].startswith("color."):
            resolved[key] = flat[target]
        else:
            resolved.pop(key, None)
    return resolved


def load_tokens(path: Path | None = None) -> Tokens:
    src = path or TOKENS_PATH
    if not src.exists():
        raise BrandError(f"token contract not found at {src}")
    raw = json.loads(src.read_text(encoding="utf-8"))
    return Tokens(
        raw=raw,
        colors=_flatten_colors(raw.get("color", {})),
        typography=raw.get("typography", {}),
        lockup=raw.get("lockup", {}),
        motion=raw.get("motion", {}),
    )


def check_fonts(tokens: Tokens) -> dict[str, bool]:
    """Report which declared brand faces fontconfig can actually resolve.

    fc-match always returns *something*, so presence is confirmed by comparing
    the resolved family against the requested one -- otherwise a missing face
    reports as available and renders in DejaVu Sans.
    """
    results: dict[str, bool] = {}
    if not shutil.which("fc-match"):
        return results
    for names in tokens.typography.get("families", {}).values():
        # Only the first entry is the brand face. The rest of the stack is
        # fallback -- present so the asset degrades gracefully elsewhere -- and
        # its absence on this machine is not a defect.
        for name in names[:1]:
            if name in {"monospace", "sans-serif", "system-ui"} or name in results:
                continue
            try:
                out = subprocess.run(
                    ["fc-match", name], capture_output=True, text=True, timeout=10, check=False
                ).stdout
            except (OSError, subprocess.SubprocessError):
                results[name] = False
                continue
            resolved = out.split('"')[1] if '"' in out else ""
            results[name] = resolved.strip().lower() == name.strip().lower()
    return results


def tokens_to_css(tokens: Tokens) -> str:
    """CSS custom properties, so an HTML asset is on-brand by construction."""
    lines = [
        "/* Generated from branding/tokens.json by tools/branding/assets.py.",
        f"   kit={tokens.raw.get('kit_id')} schema={tokens.raw.get('schema_version')}",
        "   Do not hand-edit; regenerate instead. */",
        ":root {",
    ]
    for key in sorted(tokens.colors):
        lines.append(f"  --{key.replace('.', '-')}: {tokens.colors[key]};")
    for family in tokens.typography.get("families", {}):
        lines.append(f"  --font-{family}: {tokens.font_stack(family)};")
    square = tokens.lockup.get("square", {})
    for name, value in square.items():
        if isinstance(value, str) and not value.startswith("color."):
            lines.append(f"  --lockup-square-{name.replace('_', '-')}: {value};")
    lines.append("}")
    return "\n".join(lines) + "\n"


def html_shell(body: str, tokens: Tokens, *, width: int, height: int) -> str:
    """Wrap markup in the brand ground so every HTML asset starts on-brand."""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
{tokens_to_css(tokens)}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html,body {{ width:{width}px; height:{height}px; overflow:hidden; }}
body {{
  background: var(--base-bg);
  color: var(--text_chrome-text);
  font-family: var(--font-mono);
  -webkit-font-smoothing: antialiased;
}}
</style></head><body>{body}</body></html>"""


def _chrome() -> str:
    for name in CHROME_CANDIDATES:
        found = shutil.which(name)
        if found:
            return found
    raise BrandError(
        "no Chrome/Chromium found; it is the rasterizer for SVG and HTML. "
        f"Looked for: {', '.join(CHROME_CANDIDATES)}"
    )


def _run_chrome(args: list[str], *, timeout: int = 120) -> None:
    cmd = [
        _chrome(), "--headless=new", "--no-sandbox", "--disable-gpu",
        "--disable-dev-shm-usage", "--hide-scrollbars",
        "--allow-file-access-from-files", *args,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
    if proc.returncode != 0:
        raise BrandError(f"chrome failed ({proc.returncode}): {proc.stderr.strip()[:400]}")


def render_png(
    source: Path, out: Path, *, width: int = 1024, height: int | None = None,
    transparent: bool = True,
) -> Path:
    """Rasterize an SVG or HTML file to PNG at an exact pixel size.

    An SVG carrying intrinsic ``width``/``height`` attributes renders at that
    size and sits in the corner of a larger viewport, so an SVG source is
    wrapped in a page that scales it to fill. ``object-fit: contain`` preserves
    the aspect ratio, which matters for a mark that must not be stretched when
    the requested box is not square.
    """
    if not source.exists():
        raise BrandError(f"source not found: {source}")
    out.parent.mkdir(parents=True, exist_ok=True)
    h = height or width
    args = [f"--screenshot={out}", f"--window-size={width},{h}"]
    if transparent:
        args.append("--default-background-color=00000000")

    with tempfile.TemporaryDirectory() as tmp:
        target = source
        if source.suffix.lower() == ".svg":
            wrapper = Path(tmp) / "wrap.html"
            wrapper.write_text(
                "<!doctype html><style>html,body{margin:0;padding:0;"
                f"width:{width}px;height:{h}px;overflow:hidden}}"
                "img{width:100%;height:100%;object-fit:contain;display:block}</style>"
                f'<img src="{source.resolve().as_uri()}">',
                encoding="utf-8",
            )
            target = wrapper
        args.append(target.resolve().as_uri())
        _run_chrome(args)

    if not out.exists():
        raise BrandError(f"chrome reported success but wrote no file at {out}")
    return out


def render_pdf(source: Path, out: Path, *, landscape: bool = False) -> Path:
    """Render an HTML document to PDF -- the path for reports and one-pagers."""
    if not source.exists():
        raise BrandError(f"source not found: {source}")
    out.parent.mkdir(parents=True, exist_ok=True)
    args = [f"--print-to-pdf={out}", "--no-pdf-header-footer"]
    if landscape:
        args.append("--print-to-pdf-landscape")
    args.append(source.resolve().as_uri())
    _run_chrome(args)
    if not out.exists():
        raise BrandError(f"chrome wrote no PDF at {out}")
    return out


def render_ico(source: Path, out: Path, sizes: tuple[int, ...] = ICO_SIZES) -> Path:
    """Multi-resolution ICO, rendered per size rather than downscaled once.

    Rendering each size from the vector keeps 16px legible; a single 256px
    render scaled down turns thin strokes to mush at favicon scale.
    """
    try:
        from PIL import Image
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise BrandError("Pillow is required for ICO output") from exc
    out.parent.mkdir(parents=True, exist_ok=True)
    ordered = sorted(sizes, reverse=True)
    with tempfile.TemporaryDirectory() as tmp:
        frames = []
        for size in ordered:
            png = Path(tmp) / f"{size}.png"
            render_png(source, png, width=size, height=size, transparent=True)
            frames.append(Image.open(png).convert("RGBA"))
        # Pillow downscales from the base image, so the base must be the
        # largest or every requested size is clamped down to it. append_images
        # supplies the independently rendered smaller frames, which is the
        # point: a 16px frame drawn from the vector stays legible where one
        # downscaled from 256px turns to mush.
        frames[0].save(
            out, format="ICO",
            sizes=[(s, s) for s in ordered],
            append_images=frames[1:],
        )
    return out


def render_video(
    frames_dir: Path, out: Path, *, fps: int = 30, pattern: str = "frame_%04d.png",
    crf: int = 18,
) -> Path:
    """Encode a PNG frame sequence to MP4 (H.264) or WebM (VP9) by extension."""
    if not shutil.which("ffmpeg"):
        raise BrandError("ffmpeg not found; it is required for video output")
    if not frames_dir.is_dir():
        raise BrandError(f"frames directory not found: {frames_dir}")
    out.parent.mkdir(parents=True, exist_ok=True)
    codec = ["-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p"] if out.suffix == ".webm" else [
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
    ]
    cmd = [
        "ffmpeg", "-y", "-framerate", str(fps), "-i", str(frames_dir / pattern),
        *codec, "-crf", str(crf), str(out),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=900, check=False)
    if proc.returncode != 0:
        raise BrandError(f"ffmpeg failed: {proc.stderr.strip()[-400:]}")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("fonts", help="Report which brand faces fontconfig resolves.")
    p_css = sub.add_parser("css", help="Emit tokens as CSS custom properties.")
    p_css.add_argument("--out", type=Path)

    p_png = sub.add_parser("png", help="Rasterize SVG/HTML to PNG.")
    p_png.add_argument("source", type=Path)
    p_png.add_argument("out", type=Path)
    p_png.add_argument("--width", type=int, default=1024)
    p_png.add_argument("--height", type=int)
    p_png.add_argument("--opaque", action="store_true")

    p_pdf = sub.add_parser("pdf", help="Render HTML to PDF.")
    p_pdf.add_argument("source", type=Path)
    p_pdf.add_argument("out", type=Path)
    p_pdf.add_argument("--landscape", action="store_true")

    p_ico = sub.add_parser("ico", help="Multi-resolution favicon.")
    p_ico.add_argument("source", type=Path)
    p_ico.add_argument("out", type=Path)

    p_vid = sub.add_parser("video", help="Encode a PNG frame sequence.")
    p_vid.add_argument("frames", type=Path)
    p_vid.add_argument("out", type=Path)
    p_vid.add_argument("--fps", type=int, default=30)
    p_vid.add_argument("--pattern", default="frame_%04d.png")

    args = parser.parse_args(argv)
    tokens = load_tokens()

    try:
        if args.cmd == "fonts":
            status = check_fonts(tokens)
            missing = [n for n, ok in status.items() if not ok]
            for name, ok in sorted(status.items()):
                print(f"  {'OK  ' if ok else 'MISS'}  {name}")
            if missing:
                print(f"\n{len(missing)} brand face(s) missing -- renders will "
                      f"silently fall back and be off-brand: {', '.join(missing)}")
                return 1
            print("\nAll declared brand faces resolve.")
            return 0

        if args.cmd == "css":
            css = tokens_to_css(tokens)
            if args.out:
                args.out.parent.mkdir(parents=True, exist_ok=True)
                args.out.write_text(css, encoding="utf-8")
                print(f"wrote {args.out}")
            else:
                print(css, end="")
            return 0

        if args.cmd == "png":
            out = render_png(args.source, args.out, width=args.width,
                             height=args.height, transparent=not args.opaque)
        elif args.cmd == "pdf":
            out = render_pdf(args.source, args.out, landscape=args.landscape)
        elif args.cmd == "ico":
            out = render_ico(args.source, args.out)
        else:
            out = render_video(args.frames, args.out, fps=args.fps, pattern=args.pattern)
        print(f"wrote {out} ({out.stat().st_size:,} bytes)")
        return 0
    except BrandError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
