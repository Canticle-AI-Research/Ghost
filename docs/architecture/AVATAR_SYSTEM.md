# Desktop avatar architecture

**Status: merged as a presentation lane; not a qualified capability.** The
source, tests, overlay front-end, and the three referenced sprites are tracked.
The avatar never decides whether a turn succeeded, and every entry point is off
unless the operator opts in with `GHOST_AVATAR` or `GHOST_AVATAR_WS`.

The generation intermediates that produced the sprites are deliberately not
tracked; see `assets/avatar/README.md`. The GTK desktop pet additionally needs
PyGObject, which is not a declared dependency, and resolves its sprites
relative to the repository root -- it is a source-checkout tool. The packaged
`ghost-avatar` entry point serves the overlay from inside the package and does
not depend on that path.

## Two local render paths

```text
Path A: browser/Three.js overlay

ghost CLI ── start/end events ─► hook.py ── ws://127.0.0.1:8765 ─► bridge.py
                                                                     │
desktop sensor ◄─────────────────────────────────────────────────────┤
                                                                     ▼
                                                       overlay engine.js
                                                                     │
                                                                     ▼
                                                         Chrome app viewport

Path B: direct GTK desktop pet

system Python + GTK + Pillow ─► desktop_pet.py ─► override-redirect window
                                      │
                                      └─ B2 sprite + animated light dust/face
```

Path A still opens a Chrome app window and therefore does not satisfy the
operator's “actual desktop, not Chrome app” requirement. Path B is the current
direct-desktop experiment.

## Source map

| Path | Responsibility |
|---|---|
| `src/ghost/avatar/bridge.py` | WebSocket command/state bridge |
| `src/ghost/avatar/sensor.py` | X11 screen/window/desktop-item observation |
| `src/ghost/avatar/director.py` | prompt and completion → avatar action/face |
| `src/ghost/avatar/hook.py` | optional CLI notifications; failure-isolated |
| `src/ghost/avatar/runner.py` | HTTP server, WS bridge, browser launch |
| `src/ghost/avatar/desktop_pet.py` | direct GTK desktop pet |
| `src/ghost/avatar/state.py` | renderer-neutral operational-state contract |
| `src/ghost/avatar/visual.py` | deterministic B2 light/particle renderer |
| `src/ghost/avatar/overlay/` | browser overlay HTML/CSS/JS |
| `tests/test_avatar.py` | director, hook, and bridge behavior |
| `assets/avatar/` | candidates, selected B2 source, generated sprites/GLBs |
| `tools/make_galaxy_sprite.py` | local deterministic composite experiment |
| `tools/export_ghost_glb.py` | Blender GLB export experiment |

## Event protocol

```text
user prompt
  └─ notify_turn_start(prompt)
       └─ director selects focused/enter action and face

agent success
  └─ notify_turn_end(ok=True)
       └─ pop_out + done face

agent failure/cancel
  └─ notify_turn_end(ok=False)
       └─ pop_out + error face
```

The hook must never make a Ghost turn fail merely because the avatar is absent.

## Selected art direction

- B2 jelly ghost (`ghost_opt_b_00002_.png`) is the operator-selected form.
- Silhouette motion stays light: tiny hover/dance, no squash or fluctuating
  body geometry.
- The face animates independently.
- Interior should become neural nodes/synapses plus mood-colored neon gas.
- The character is a real authored/generative asset, not a canvas ellipse or
  text glyph pretending to be final art.

## Current defects

- five Ruff findings in avatar/image-tool paths;
- hard-coded workstation paths in local image/Blender tools;
- two competing render paths without one declared production owner;
- browser overlay does not meet the direct-desktop requirement;
- GTK path depends on system Python packages outside the uv environment;
- mood wiring to the neural-gas interior is incomplete;
- generated/candidate assets need a tracked-versus-external manifest decision;
- no branch, PR, CI lane, packaging contract, or rendered approval set exists.

## Qualification gate

Before merge:

1. isolate the avatar work on a feature branch while preserving source assets;
2. remove machine-specific hard-coded paths;
3. choose one v1 render path and mark the other experimental/retired;
4. make Ruff and `tests/test_avatar.py` green;
5. demonstrate CLI operation with avatar absent and present;
6. show actual desktop renders at supported display scales;
7. verify clean wheel membership and optional dependency behavior;
8. document CPU/RAM behavior and process shutdown; and
9. append canonical history and a successor handoff.
