# Avatar assets

Only the sprites the runtime actually loads are tracked here.

| File | Loaded by |
|---|---|
| `ghost_blob_sprite.png` | `avatar/desktop_pet.py` — the GTK pet's sprite sheet |
| `ghost_B2_opaque.png` | `avatar/desktop_pet.py` — opaque fallback |
| `ghost_B2_sprite.png` | `avatar/visual.py` — default composition source |

## What is deliberately not tracked

The generation run that produced these also produced roughly 28MB of candidate
iterations — `ghost_opt_a/b/c_*`, `ghost_blob_0000*`, `ghost_bunny_front_*`,
the Meshy GLB intermediates. They are selection artifacts: the inputs to a
choice that has already been made, in favour of the B2 direction.

This repository is public, and anything committed here is in its history
permanently. Those files carry no runtime benefit, so `.gitignore` excludes
them. They remain on the originating machine, and the toolchain in `tools/`
regenerates them.

The overlay front-end (`src/ghost/avatar/overlay/`) ships inside the package
and is resolved package-relative, so the installed `ghost-avatar` entry point
does not depend on this directory. The paths here are repo-root relative and
are therefore a source-checkout convenience, used by the GTK pet and the
composition tooling.
