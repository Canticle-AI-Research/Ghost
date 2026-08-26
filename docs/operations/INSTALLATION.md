# Installation and first run

Ghost currently requires private SEAM repository access. A clone without that
authorization can read the public code/docs and run credential-free doc/brand/
package checks, but it cannot install the complete runtime dependency graph.

These commands install the current internal/developer topology. Ghost's local
PolyForm Shield candidate does not grant private-repository credentials. A
public installation path requires the planned thin client/API or a licensed
local SEAM Node.

## Supported development range

- Python `>=3.11,<3.15`;
- `uv` package/environment manager;
- Git with SSH access to GitHub;
- Linux is the primary tested operator environment;
- an OpenAI key is required only when invoking the default model or live tests.

## 1. Install system prerequisites

Required commands:

```bash
git --version
ssh -V
uv --version
```

Optional asset checks:

```bash
command -v google-chrome || command -v chromium
command -v fc-match
command -v ffmpeg
```

The avatar's direct GTK path is local WIP and additionally needs system Python,
GTK 3 GObject bindings, and Pillow visible to that system interpreter. It is
not required for the landed Ghost agent.

## 2. Verify private Git access

Do not print keys or tokens. Verify the GitHub identity:

```bash
ssh -T git@github.com
```

Then verify read access without cloning another copy:

```bash
git ls-remote git@github.com:Canticle-AI-Research/Seam_SDK.git HEAD
```

The SDK resolves its own exact private runtime dependency. An authorization
failure here is not a Python packaging defect.

## 3. Clone and reconcile

```bash
git clone git@github.com:Canticle-AI-Research/Ghost.git
cd Ghost
git status --short --branch
git fetch --prune origin
git rev-parse HEAD origin/main
```

Read the repository protocol before changing files:

```bash
sed -n '1,260p' AGENTS.md
sed -n '1,220p' PROJECT_STATUS.md
sed -n '1,260p' REPO_LEDGER.md
sed -n '1,220p' HISTORY_INDEX.md
```

## 4. Install the frozen environment

```bash
uv lock --check
uv sync --frozen
```

`--frozen` refuses to rewrite `uv.lock`. That matters because the lock records
reviewed private Git revisions; a silent re-resolution changes the memory
substrate under the agent.

Smoke the import and console entry:

```bash
uv run ghost --help
```

## 5. Configure local state

Create an ignored configuration file:

```bash
cp .env.example .env.local
chmod 600 .env.local
```

Edit `.env.local` without committing it. Minimum model-backed configuration:

```text
OPENAI_API_KEY=<set locally>
GHOST_MODEL=openai:gpt-5.6-terra
GHOST_SEAM_DB=~/.local/share/ghost/seam.db
GHOST_CHECKPOINT_DB=~/.local/share/ghost/checkpoints.db
```

Keep the two databases separate. The first is semantic memory; the second is
conversation execution state.

## 6. Run provider-free verification

```bash
uv run ruff check .
uv run pytest
uv build
uv run pytest tests/test_docs.py tests/test_history_tools.py -q
uv run python -m tools.history.verify_continuity
```

The default pytest configuration deselects tests marked `live`. Record that
boundary when reporting results.

## 7. First model-backed turn

This uses provider credit:

```bash
uv run ghost "State your role and explain which system owns your durable memory."
```

Interactive mode:

```bash
uv run ghost --thread-id first-install
```

Type `/exit` or `/quit` to stop.

## 8. Prove checkpoint restart

```bash
uv run ghost --thread-id restart-proof "Remember that the rebuild marker is cobalt."
uv run ghost --thread-id restart-proof "What marker did I give you?"
```

This test touches both checkpoint and semantic memory. A response alone is not
a formal memory-quality evaluation; use isolated paths and inspect the named
test suite for qualification.

## Clean-room install notes

- Do not install from the repository root with pip and assume the lock was
  honored; use uv's frozen environment.
- Do not replace the SDK with `seam-client` to make installation public.
- Do not describe PolyForm Shield as access to private SEAM runtime source;
  repository access and software licensing are separate controls.
- Do not point first-run tests at an operator's existing canonical SEAM store.
- Do not run the live test marker without explicit spend approval.
- Do not treat a successful wheel build as permission to upload to PyPI.

## Troubleshooting

### Private dependency authentication fails

```bash
ssh -T git@github.com
git ls-remote git@github.com:Canticle-AI-Research/Seam_SDK.git HEAD
```

Repair SSH authorization; do not rewrite `pyproject.toml` to a local absolute
path in a commit.

### `python: command not found`

Ghost's documented commands use `uv run python`. A bare `python` executable is
not required on this machine.

### OpenAI function tools fail through Chat Completions

Ghost sets `use_responses_api=True` for OpenAI models. Verify the provider is
parsed from a `provider:model` string and do not bypass `_init_model`.

### PgVector dependency error

The package uses `seam-sdk[pgvector]`. Verify `uv lock --check` and
`uv sync --frozen`; do not silently remove the extra.

### GTK avatar import fails

The direct desktop pet uses system GTK bindings, not the normal uv environment.
This is an unmerged optional lane. The core agent install is still valid when
the avatar is absent.
