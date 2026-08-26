# Ghost desktop avatar (v1)

Desktop AI: a layered-2D Canticle ghost-bunny that floats on the real desktop.
Asked work drives him into the matching app; the task finishing pops him back
out. Idle motion is visual only. The door/room/library is out of scope.

## Character

Round blob, curl on top, arm nubs. Translucent fill, drawn rim, Canticle
tokens (pink `#ff6090`, cyan `#7dcfff`, mint `#9ece6a`). Billboard card in the
existing Three.js overlay. No girl, no cone/halo mesh, no hologram windows,
no crystal folder pedestals.

## Faces

One face at a time. `❯ █` is awake (spawn/un-stealth) and done (task finished).

| Face | Glyph | When |
|---|---|---|
| awake / done | ❯ █ | presence |
| happy | ^ ^ | pleased |
| blissful | ‿ ‿ | delighted |
| wink | ^ █ | ack |
| excited | ✧ ✧ | discovery |
| focused | ▪ ▪ | working / going in |
| blank | ・ ・ | idle float |
| curious | ? ・ | asking |
| surprised | o o | unexpected |
| sleepy | ⌒ ⌒ | stealth / dormant |
| error | x x | failed |
| confused | @ @ | does not follow (new; not `> <`) |
| angry | ▼ ▼ | blocked |
| nervous | ; ; | unsure |

Reaction FX (sweat, `?` pop, vein) are a later art pass.

## Motion

- Asked + idle random in v1. He-decides and the room later.
- Web search → dash to the browser window → go in. Stay until the turn ends.
- Open a named desktop item → emit `avatar_action` with `enter` plus the named
  target; an operator click may separately send the bridge an `open_item`
  request after the visual movement.
- No desktop target → focused in place.
- Task complete or fail → pop out somewhere on the desktop with done/error.
- Idle: float, peek, wink, sleepy. Never enter apps. Never open files.

## Plumbing

- `ghost.avatar.director` maps user text + desktop snapshot → commands.
- Overlay consumes `avatar_action` (`enter`, `pop_out`, `face`, `idle`, `hide`,
  `appear`) plus target fields and `face`; `open_item` is a distinct
  overlay-to-bridge request, not an avatar action.
- `ghost` CLI pushes commands to `ws://127.0.0.1:8765` when the avatar is running.
- Click-through of empty overlay is a known v1 compositor limit.
