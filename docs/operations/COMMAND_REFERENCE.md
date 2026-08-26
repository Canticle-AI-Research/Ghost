# Complete command reference

Commands are grouped by authority. Examples assume the repository root and use
`uv run` so they work on systems without a bare `python` command.

## `ghost`: run the agent

```text
uv run ghost [-h] [--thread-id THREAD_ID] [prompt ...]
```

| Argument | Meaning |
|---|---|
| `prompt ...` | one-shot prompt; words are joined with spaces |
| `--thread-id ID` | LangGraph checkpoint thread, default `default` |
| no prompt | interactive terminal loop |
| `-h`, `--help` | print usage without constructing the agent |

Examples:

```bash
uv run ghost "Summarize the current project boundary."
uv run ghost --thread-id research-a "Continue the source audit."
uv run ghost --thread-id research-a
```

Interactive commands are `/exit` and `/quit`. EOF exits zero. Ctrl-C exits 130.

## Environment/install commands

### `uv lock --check`

Confirms `pyproject.toml` agrees with committed `uv.lock` without changing it.

```bash
uv lock --check
```

### `uv sync --frozen`

Installs the exact locked public project and development dependencies. It does
not contact a SEAM service or require private source access.

```bash
uv sync --frozen
uv sync --frozen --python 3.11
```

### `uv build`

Builds wheel and source distribution under ignored `dist/`. It does not upload.

```bash
uv build
```

## Verification commands

### Provider-free default suite

```bash
uv run pytest
uv run python -m pytest
```

Both are supported. Project configuration deselects `live` tests.

### Focused tests

```bash
uv run pytest tests/test_cli.py -q
uv run pytest tests/test_memory_boundary.py tests/test_layering.py -q
uv run pytest tests/test_docs.py tests/test_history_tools.py -q
```

### Live provider tests

Costs provider credit and needs a key. Run only with explicit approval:

```bash
uv run pytest -m live tests/test_live_agent.py -q
```

### Ruff

```bash
uv run ruff check .
uv run ruff check path/to/file.py
```

Do not use `--fix` without reviewing changes, especially public re-exports,
test monkeypatch targets, security suppressions, and local WIP.

### Diff hygiene

```bash
git diff --check
```

## Frozen evaluation commands

All commands below are credential-free. They exercise the deterministic BIL-0
contract runner, not a live model.

### Validate Stage 1 fixtures

```bash
uv run python -m tools.evaluation validate-fixtures
```

Options: `--fixtures PATH` selects a successor or experimental corpus. The
default is `evals/stage1/fixtures.json`.

### Seal the Stage 1 smoke bundle

```bash
uv run python -m tools.evaluation smoke \
  --output /tmp/ghost-stage1-smoke.json
```

Required: `--output PATH`. Optional: `--fixtures PATH`. The command refuses a
dirty worktree. `--allow-dirty` is for harness development only and records the
dirty state, making the artifact unsuitable as a baseline.

### Verify an evaluation bundle

```bash
uv run python -m tools.evaluation verify /tmp/ghost-stage1-smoke.json
```

Exit 0 means the bundle version, integrity block, shapes, manifest/result/bundle
hashes, and cross-payload suite/Git/fixture/case identities agree. It does not
mean the result is live-model evidence.

### Gate the Stage 1 smoke

```bash
uv run python -m tools.evaluation gate /tmp/ghost-stage1-smoke.json
```

The gate includes verification and requires zero candidate contract failures,
zero isolation violations, and zero forbidden effects. It preserves the BIL-0
claim boundary.

## Canonical continuity commands

### Rebuild history index

```bash
uv run python -m tools.history.rebuild_index
```

No options. Parses/validates `HISTORY.md` and rewrites the derived index.

### Build a bounded context pack

```text
uv run python -m tools.history.build_context_pack
  [--latest N]
  [--topics TOPIC ...]
  [--entries ID ...]
  [--token-budget N]
```

Examples:

```bash
uv run python -m tools.history.build_context_pack --latest 5
uv run python -m tools.history.build_context_pack --topics avatar docs --latest 4
uv run python -m tools.history.build_context_pack --entries 18 19 --latest 2
uv run python -m tools.history.build_context_pack --latest 8 --token-budget 3000
```

Topic matching is “any named topic”; exact entries and topics combine as
filters. `--latest` applies after filtering.

### Verify handoffs

```bash
uv run python -m tools.history.verify_handoffs
```

No options. Enforces one current head, document/index metadata agreement, one
linear chain, and increasing history chronology.

### Verify append-only history against Git

```bash
uv run python -m tools.history.verify_append_only --base-ref origin/main
```

This rejects any changed, removed, or reordered byte already present in the
base revision. The hosted pull-request workflow supplies the exact base commit.

### Write local snapshot

```text
uv run python -m tools.history.write_snapshot --agent NAME [--entries N]
```

Example:

```bash
uv run python -m tools.history.write_snapshot --agent codex --entries 5
```

Writes ignored `.ghost/snapshots/<UTC>.json` with bounded history and git state.

### Verify continuity

```bash
uv run python -m tools.history.verify_continuity
uv run python -m tools.history.verify_continuity --require-snapshot
```

The second form is the local closeout gate; CI may omit the ignored snapshot.

### Full history closeout

```bash
uv run python -m tools.history.closeout --agent codex
uv run python -m tools.history.closeout --agent operator --snapshot-entries 8
```

### Install the commit gate

```bash
bash tools/git-hooks/install.sh
```

Symlinks `tools/git-hooks/pre-commit` into `.git/hooks/`, falling back to a copy
on filesystems without symlink support. Run once per clone.

### Audit recorded facts

```bash
uv run python -m tools.history.recorded_fact_audit
```

Checks test-count claims, cited module lengths, and handoff pointers in active
docs and the latest history entry. Also runs inside `verify_continuity`, with no
flag to disable it.

### Install the Ghost agent launchers

```bash
uv run python tools/launchers/install.py --dry-run
uv run python tools/launchers/install.py
uv run python tools/launchers/install.py --harness grok --harness agy
```

Installs `ghost-claude`, `ghost-codex`, `ghost-grok`, and `ghost-agy` into
`~/.local/bin` (override with `--bin-dir`). It renders the Grok and Antigravity
`canticle-ghost` definitions from the shared persona body. The Claude agent file
and Codex `[profiles.ghost]` configuration are maintained separately and must
already exist for those two launchers. See
[agent harnesses](AGENT_HARNESSES.md).

### Install the Temporal Chain in another repository

```bash
uv run python templates/temporal-chain/install.py \
  --repo /absolute/path/to/repository \
  --project-name "Project Name"
```

The installer is standard-library-only and refuses to overwrite existing
targets. Merge collisions deliberately in established repositories.

It rebuilds the index, verifies handoffs, writes a snapshot, verifies
continuity, and runs documentation/history tests. It does not run Ruff, full
pytest, build, live tests, or GitHub CI.

## Brand asset commands

Entrypoint:

```bash
uv run python -m tools.branding.assets <subcommand> ...
```

### `fonts`

Report whether every declared primary brand face resolves through fontconfig.

```bash
uv run python -m tools.branding.assets fonts
```

### `css`

Print tokens as CSS variables or write them to a file.

```bash
uv run python -m tools.branding.assets css
uv run python -m tools.branding.assets css --out /tmp/ghost-tokens.css
```

### `png`

Rasterize SVG or HTML through headless Chrome.

```bash
uv run python -m tools.branding.assets png branding/ghost.svg /tmp/ghost.png
uv run python -m tools.branding.assets png branding/ghost.svg /tmp/ghost-512.png --width 512 --height 512
uv run python -m tools.branding.assets png branding/ghost.svg /tmp/ghost-opaque.png --opaque
```

### `pdf`

Render HTML to PDF.

```bash
uv run python -m tools.branding.assets pdf page.html /tmp/page.pdf
uv run python -m tools.branding.assets pdf page.html /tmp/page.pdf --landscape
```

### `ico`

Create the multi-resolution favicon from a rasterizable source.

```bash
uv run python -m tools.branding.assets ico branding/ghost-mark.svg /tmp/ghost.ico
```

### `video`

Encode a PNG sequence with ffmpeg. MP4 selects H.264; `.webm` selects VP9.

```bash
uv run python -m tools.branding.assets video frames/ /tmp/ghost.mp4
uv run python -m tools.branding.assets video frames/ /tmp/ghost.webm --fps 24 --pattern 'ghost_%04d.png'
```

## Local avatar commands

These commands describe unmerged working-tree code.

### Browser/bridge avatar

```text
uv run ghost-avatar [--ws-port PORT] [--http-port PORT] [--no-launch]
```

```bash
uv run ghost-avatar
uv run ghost-avatar --ws-port 8875 --http-port 8876 --no-launch
GHOST_AVATAR=1 uv run ghost "Search the web for the project documentation."
GHOST_AVATAR_WS=ws://127.0.0.1:8875 uv run ghost "Inspect the repository."
```

### Direct GTK desktop pet

```bash
DISPLAY=<x11-display> /usr/bin/python3 src/ghost/avatar/desktop_pet.py
GHOST_PET_X=<x> GHOST_PET_Y=<y> DISPLAY=<x11-display> \
  /usr/bin/python3 src/ghost/avatar/desktop_pet.py
```

This uses system Python because GTK bindings are not part of the uv project.

### Galaxy/neural sprite experiment

```bash
uv run python tools/make_galaxy_sprite.py
```

Current script paths are workstation-specific; repair them before treating the
command as portable.

### Blender GLB card export

```bash
blender --background --python tools/export_ghost_glb.py
```

The script currently exports a textured card of the older sprite and contains
workstation-specific paths. It is not the selected B2 3D production pipeline.

## Git/GitHub reconciliation commands

```bash
git status --short --branch
git fetch --prune origin
git rev-parse HEAD origin/main
git worktree list --porcelain
git log --oneline --decorate -12
gh repo view Canticle-AI-Research/Ghost --json visibility,isPrivate,defaultBranchRef,url
gh pr list --repo Canticle-AI-Research/Ghost --state all --limit 20
gh run list --repo Canticle-AI-Research/Ghost --branch main --limit 10
```

These are read-only reconciliation commands. A status report should run them
before asserting remote, merged, CI, or visibility state.
