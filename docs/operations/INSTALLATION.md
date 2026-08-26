# Installation and first run

Ghost installs from its public repository without access to private SEAM
source. Runtime use requires a reachable SEAM service implementing the opaque
`/v1/memories/recall` and `/v1/agent/turns/*` contracts. Repository access,
software licensing, service authorization, and provider credentials are four
separate controls.

## Supported range

- Python `>=3.11,<3.15`;
- `uv` package/environment manager;
- Linux is the primary tested operator environment;
- a SEAM service URL and, outside trusted loopback, a bearer token;
- a model-provider credential only when invoking that provider.

## 1. Install prerequisites

```bash
git --version
uv --version
```

Optional brand/avatar tools:

```bash
command -v google-chrome || command -v chromium
command -v fc-match
command -v ffmpeg
```

The experimental GTK avatar is not part of the landed core-agent install.

## 2. Clone and reconcile

```bash
git clone https://github.com/Canticle-AI-Research/Ghost.git
cd Ghost
git status --short --branch
git fetch --prune origin
git rev-parse HEAD origin/main
```

Before contributing, read:

```bash
sed -n '1,260p' AGENTS.md
sed -n '1,220p' PROJECT_STATUS.md
sed -n '1,260p' REPO_LEDGER.md
sed -n '1,220p' HISTORY_INDEX.md
```

## 3. Install the frozen public environment

```bash
uv lock --check
uv sync --frozen
uv run ghost --help
```

`--frozen` refuses to rewrite the reviewed lock. `pyproject.toml` and `uv.lock`
must contain no `git+ssh`, `seam-sdk`, or private runtime source. Automatic CI
tests that invariant and clean-installs the built wheel on a disposable hosted
runner.

## 4. Configure the SEAM service

Copy the ignored template:

```bash
cp .env.example .env.local
chmod 600 .env.local
```

Minimum service configuration:

```text
SEAM_BASE_URL=http://127.0.0.1:8765
SEAM_API_TOKEN=
GHOST_SEAM_NAMESPACE=ghost.default
GHOST_SEAM_SCOPE=thread
GHOST_WORKSPACE=default
GHOST_PROJECT=default
GHOST_MEMORY_ADMISSION=explicit
GHOST_CHECKPOINT_DB=~/.local/share/ghost/checkpoints.db
```

Use HTTPS and a bearer token for any non-loopback service. Do not put the token
in command history, documentation, issues, logs, or committed environment
files. `GhostSettings` excludes it from `repr`.

The service must provide:

```text
POST /v1/memories/recall
POST /v1/memories
POST /v1/memories/correct
POST /v1/memories/delete
POST /v1/agent/turns/begin
POST /v1/agent/turns/actions
POST /v1/agent/turns/complete
POST /v1/agent/turns/fail
```

Ghost does not open a MIRL database or configure SEAM storage. The legacy
`GHOST_SEAM_DB` variable remains only to derive a default checkpoint path for
older configurations; set `GHOST_CHECKPOINT_DB` directly in new deployments.

## 5. Verify service readiness without provider spend

Do not print the bearer value. This request checks reachability only:

```bash
curl --fail --silent --show-error "${SEAM_BASE_URL%/}/v1/health"
```

For an authenticated contract probe, use a throwaway namespace and send the
token through the header. Do not point experiments at an operator's production
namespace.

## 6. Run provider-free repository verification

```bash
uv run ruff check .
uv run pytest
uv build
uv run python -m tools.history.verify_continuity
```

The default pytest configuration deselects `live` tests. It uses a stateful
HTTP contract fake and contacts neither a provider nor a SEAM deployment.
Record that boundary with any test report.

## 7. Configure and run the model

For the default provider:

```bash
export OPENAI_API_KEY="<set locally>"
export GHOST_MODEL="openai:gpt-5.6-terra"
uv run ghost "State your role and explain which service owns durable memory."
```

Interactive mode:

```bash
uv run ghost --thread-id first-install
```

Type `/exit` or `/quit` to stop.

## 8. Prove checkpoint restart

```bash
uv run ghost --thread-id restart-proof \
  "I will name three fruits: apple, banana, cherry. Reply only with ok."
uv run ghost --thread-id restart-proof \
  "What was the second one I named?"
```

This proves LangGraph conversation execution state survives process teardown.
It is distinct from SEAM semantic recall, which can cross thread IDs within the
same configured namespace and scope.

## 9. Prove durable memory across agent instances

Use a unique, non-secret marker:

```bash
marker="ghost-install-cobalt-$(date +%s)"
uv run ghost "Remember this installation marker exactly: ${marker}"
uv run ghost "What is the installation marker? Answer with the marker."
```

Then use `seam_recall` in the interactive agent or an authorized direct recall
request to confirm the service returns a `mem_...` opaque evidence handle.
Response text alone is not a formal benchmark.

## Clean-room wheel proof

```bash
uv build
tmp_dir="$(mktemp -d)"
uv venv "${tmp_dir}/venv"
uv pip install --python "${tmp_dir}/venv/bin/python" dist/*.whl
"${tmp_dir}/venv/bin/ghost" --help
```

Remove the temporary directory afterward using your normal recoverable cleanup
workflow. A successful build/install proves package reachability, not permission
to publish an artifact or access a SEAM deployment.

## Troubleshooting

### `Connection refused` or timeout

- verify `SEAM_BASE_URL` and `/v1/health`;
- confirm the service is running and reachable from this host;
- keep loopback for local development; and
- increase `GHOST_SEAM_TIMEOUT` only after diagnosing latency.

### HTTP 401 or 403

The service rejected `SEAM_API_TOKEN`. Repair service authorization without
printing or copying the credential. Ghost does not mint service credentials.

### HTTP 404 from an agent-turn route

Either the deployed service predates the additive agent-turn contract or the
opaque turn belongs to another principal/partition. Upgrade the service or
correct namespace/scope; never parse, reuse across tenants, or synthesize turn
handles.

### HTTP 409

The turn is already finalized in an incompatible state, or an action write was
attempted after completion. Treat this as a lifecycle conflict, not a request
to retry with a fabricated handle.

### `python: command not found`

Use `uv run python`; a bare `python` executable is not required.

### OpenAI function tools fail through Chat Completions

Ghost sets `use_responses_api=True` for OpenAI models. Verify the
`provider:model` setting and do not bypass `_init_model`.

### GTK avatar import fails

The avatar uses system GTK bindings and remains a separate experimental lane.
Core Ghost installation is valid without it.
