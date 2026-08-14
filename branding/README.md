# Ghost mark

The identity for Ghost, the SEAM agent. Two files, one form, one rule about
which to use where.

| File | Use |
|---|---|
| `ghost.svg` | above 32px — site headers, docs, README, social, anywhere with room |
| `ghost-mark.svg` | 32px and below — favicon, avatar, tab icon, inline chips |
| `ghost.ico` | favicon, six sizes (16 / 32 / 48 / 64 / 128 / 256) |
| `ghost-512.png`, `ghost-mark-512.png` | raster fallbacks for surfaces that cannot take SVG |

## What it is

A being of light. There is no hard outline: the silhouette is a translucent
volume with a drawn rim over a wide bloom, so the edge reads at a glance while
the falloff stays ethereal. A neural constellation fires quietly at his core,
clipped inside the body so it sits within him rather than on him.

The eyes are the SEAM lockup — the `❯` prompt and the `█` block cursor. The
mascot does not sit beside the brand mark; it wears it. That also states the
architecture: Ghost is a DeepAgent whose durable memory is SEAM, so the
constellation is the memory layer, seen through the body.

## Colour

**Everything is RGB.** Every fill and stroke resolves to `currentColor`, and
colour is animated once on the root element, so the entire figure is a single
hue at any instant and sweeps the eight Canticle stops together on an 8 second
linear cycle. Nothing holds a fixed colour, the eyes included.

Two consequences worth knowing before editing either file:

- **`currentColor` inside a gradient stop resolves against the gradient's own
  inherited colour**, not the element referencing the gradient. The animation
  must stay on the root; moving it to an inner group leaves the gradients in
  `defs` inheriting black, and the body renders invisible while the directly
  stroked parts still work.
- **Structure comes from luminance, not hue**, because only one hue exists at a
  time. The body is deliberately dim so the rim, eyes and constellation read
  against it. Brightening the body flattens the whole mark.

To pin a single colour, set `color` on the `<svg>` element and disable the
animation:

```html
<svg style="color:#c4a7e7"> <!-- .rgb { animation: none } -->
```

`prefers-reduced-motion: reduce` already does exactly this, falling back to
lavender `#c4a7e7`.

## Motion

Seven layers, on deliberately unrelated periods so the pattern never visibly
repeats.

| Layer | Period | Effect |
|---|---|---|
| Hue | 8s | full spectrum, whole figure |
| Cursor eye | 0.8s | step-end blink, matching `motion.cursor_blink` |
| Body | 6.5s | breathe |
| Near nodes | 17s | drift |
| Far nodes | 23s | drift, lagging the near layer for parallax |
| Nebula | 19s | bloom |
| Cluster | 80s | rotation |

Node firing runs 4.7s to 8.9s and synapse fades 7.9s to 13.1s, none of them
multiples of each other. Every animation stops under `prefers-reduced-motion`.

## Why there are two files

The reduced mark is drawn for small sizes, not scaled down from the full one.
It carries a heavier rim at lower blur, a flatter body, and eyes that are
larger and further apart, because at 16px their separation is the only thing
that reads as a face. The constellation, nebula, ambient aura and feathered
body layer are removed — below roughly 32px they dissolve into a coloured
smudge and cost the silhouette its clarity without contributing anything
legible.

Verified by rendering each size from the vector and inspecting it magnified,
not by assuming.

## Regenerating

From the Seam repo, using the brand toolkit:

```bash
python -m tools.branding.assets png branding/ghost/ghost.svg out.png --width 512
python -m tools.branding.assets ico branding/ghost/ghost-mark.svg ghost.ico
```

The `ico` path renders every size independently from the vector rather than
downscaling one large render, which is what keeps 16px legible.

## Palette

Every value is a Canticle token; none was invented.

| Stop | Token |
|---|---|
| `#f7768e` | `color.accent.red` |
| `#ff9e64` | `color.accent.orange` |
| `#e0af68` | `color.accent.yellow` |
| `#9ece6a` | `color.accent.mint` |
| `#7dcfff` | `color.accent.cyan` |
| `#7aa2f7` | `color.accent.blue` |
| `#c4a7e7` | `color.accent.lavender` |

Ground is `#0a0b0a`, `color.base.brand_square`. The mark is built for dark
grounds; a light-ground colourway does not exist yet.
