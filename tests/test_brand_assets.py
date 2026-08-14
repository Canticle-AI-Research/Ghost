"""Regressions for the vendored brand asset toolkit.

Two classes of defect are pinned here, both found while building it:

* ``color.semantic.*`` entries hold token *paths*, not literals. Flattening
  without resolving them emits CSS like ``--semantic-canvas: color.base.bg``,
  which renders as nothing and fails silently.
* Pillow's ICO writer downscales from the base image, so passing the smallest
  render as base clamps every requested size down to it. The first cut produced
  a 337-byte 16x16-only favicon that looked like a success.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from tools.branding.assets import (
    BrandError,
    _flatten_colors,
    check_fonts,
    html_shell,
    load_tokens,
    render_ico,
    render_pdf,
    render_png,
    tokens_to_css,
)

MARK = Path(__file__).resolve().parents[1] / "branding" / "ghost-mark.svg"


@pytest.fixture(scope="module")
def tokens():
    return load_tokens()


def test_semantic_aliases_resolve_to_literal_colors(tokens):
    assert tokens.color("semantic.canvas") == tokens.color("base.bg")
    assert tokens.color("semantic.brand_live") == tokens.color("accent.pink")
    for name, value in tokens.colors.items():
        assert not value.startswith("color."), f"{name} left unresolved as {value}"


def test_unresolvable_alias_is_dropped_not_passed_through():
    flat = _flatten_colors({
        "base": {"bg": "#111111"},
        "semantic": {"good": "color.base.bg", "bad": "color.base.nope"},
    })
    assert flat["semantic.good"] == "#111111"
    assert "semantic.bad" not in flat


def test_unknown_color_token_raises(tokens):
    with pytest.raises(BrandError):
        tokens.color("accent.chartreuse")


def test_css_emits_every_color_and_font(tokens):
    css = tokens_to_css(tokens)
    assert "--accent-pink: #ff6090;" in css
    assert "--font-mono:" in css and "--font-sans:" in css
    assert "color." not in css.split(":root")[1], "an unresolved alias leaked into CSS"


def test_html_shell_carries_brand_ground(tokens):
    doc = html_shell("<p>x</p>", tokens, width=800, height=400)
    assert "--base-bg" in doc and "width:800px" in doc
    assert doc.startswith("<!doctype html>")


def test_font_stack_quotes_multiword_families(tokens):
    assert "'Fira Code'" in tokens.font_stack("mono")
    with pytest.raises(BrandError):
        tokens.font_stack("cursive")


def test_check_fonts_ignores_fallbacks(tokens):
    """Only the first face in a stack is the brand face; the rest are fallbacks."""
    status = check_fonts(tokens)
    if not status:
        pytest.fail("fc-match unavailable; the toolkit cannot verify brand faces")
    assert "Cascadia Mono" not in status, "a fallback face was treated as required"
    assert "Fira Code" in status


def test_render_png_produces_a_real_image(tmp_path, tokens):
    from PIL import Image

    out = render_png(MARK, tmp_path / "m.png", width=400, height=100)
    im = Image.open(out)
    assert im.format == "PNG" and im.size == (400, 100)
    assert im.getbbox() is not None, "rendered a blank canvas"


def test_render_ico_contains_every_requested_size(tmp_path):
    from PIL import Image

    out = render_ico(MARK, tmp_path / "f.ico", sizes=(16, 32, 64))
    got = sorted(Image.open(out).info.get("sizes", []))
    assert got == [(16, 16), (32, 32), (64, 64)]


def test_render_pdf_writes_a_pdf(tmp_path, tokens):
    src = tmp_path / "r.html"
    src.write_text(html_shell("<h1>Report</h1>", tokens, width=816, height=1056))
    out = render_pdf(src, tmp_path / "r.pdf")
    assert out.read_bytes().startswith(b"%PDF-")


def test_missing_source_raises(tmp_path):
    with pytest.raises(BrandError):
        render_png(tmp_path / "nope.svg", tmp_path / "o.png")
