# Desktop pet handoff (2026-08-21)

Operator asked to hand off. Live pet is the B2 jelly ghost. Next work is
**interior**: neon gas + neural net that lights by mood — not more body wobble.

## Hard rules (already burned)

- Ghost is **on the desktop**, not in a Chrome `--app` window, not in a spawned terminal.
- Character is an **actual art asset** (ComfyUI / Meshy), not a canvas ellipse + kaomoji.
- B2 was chosen (`ghost_opt_b_00002_.png`): dripping jelly ghost, holographic, cute anime.
- Motion must stay **light** (tiny hover-dance). No squash/fluctuate.
- Face should animate (blink, mouth open/close, anime expressions).
- Interior should be **neural constellation + neon gas**, mood-colored — matching
  `branding/README.md` (“being of light”, constellation seen through him).
- Do not use GitHub MCP; `gh` only. SEAM is pinned; Ghost does not float to latest SEAM.

## What is running

```text
DISPLAY=<x11-display> /usr/bin/python3 src/ghost/avatar/desktop_pet.py
```

GTK 3, skip-taskbar, override-redirect, 160px, click-drag, PIL frames (no cairo —
`cairo.Context` GI converter is missing on this machine). Launch with **system**
python3, not the uv venv (needs GTK).

## Key files

| Path | Role |
|---|---|
| `src/ghost/avatar/desktop_pet.py` | Live pet. Faces + hover + galaxy swirl (not neural-gas yet). |
| `src/ghost/avatar/director.py` | Turn → enter/pop_out/faces. Tests in `tests/test_avatar.py`. |
| `src/ghost/avatar/hook.py` | CLI → overlay WS if `GHOST_AVATAR=1`. Off by default. |
| `src/ghost/cli.py` | `_run_turn` notifies the hook. |
| `assets/avatar/ghost_opt_b_00002_.png` | Chosen look (B2). |
| `assets/avatar/ghost_B2_opaque.png` | Cutout used as body. |
| `assets/avatar/ghost_B2_sprite.png` | Galaxy-composited still. |
| `assets/avatar/ghost_blob_meshy.glb` | Meshy 3D of the **older hooded blob**, not B2. 4.4MB. 30 credits. |
| `tools/make_galaxy_sprite.py` | Static galaxy composite. |
| `tools/export_ghost_glb.py` | Blender card GLB of the old sprite. |
| `docs/superpowers/specs/2026-08-21-desktop-avatar.md` | Behavior spec (enter apps, pop out, faces). |
| `branding/README.md` | Mark spec: translucent, rim, constellation, `❯ █` awake/done. |

Local ComfyUI, Meshy, and animation experiments produced candidate assets.
Provider credentials and machine-specific workflow locations remain outside the
repository and must never be copied into history, handoffs, issues, or logs.

## Operator last requests (not done)

1. Interior like a **neural net** (nodes + synapses), not a photo galaxy.
2. Interior like **neon gas** that **lights up by mood** (happy/confused/angry/idle).
3. Keep anime face animation and light hover.

Wire mood from `director.py` faces when `GHOST_AVATAR=1`; until then cycle or map the pet’s own face state (blink/happy/open) to gas hue.

## How to restart the pet

```bash
pkill -f 'src/ghost/avatar/desktop_pet.py'   # or kill the recorded process ID
DISPLAY=<x11-display> /usr/bin/python3 src/ghost/avatar/desktop_pet.py
```
