# Configuration reference

Ghost loads `.env.local` with `override=False`, so an already-exported process
variable wins. `.env.example` is a template, not a credential store.

```text
process environment  highest precedence
       │
       └─ .env.local fills only missing names
              │
              └─ GhostSettings code defaults
```

## Core variables

| Variable | Default | Bounds / meaning |
|---|---|---|
| `OPENAI_API_KEY` | unset | provider credential; required for OpenAI calls |
| `GHOST_MODEL` | `openai:gpt-5.6-terra` | `provider:model`; provider controls adapter options |
| `GHOST_SEAM_DB` | `~/.local/share/ghost/seam.db` | canonical Ghost semantic memory store |
| `GHOST_CHECKPOINT_DB` | `~/.local/share/ghost/checkpoints.db` | LangGraph execution state only |
| `GHOST_SEAM_NAMESPACE` | `ghost.default` | logical SEAM namespace |
| `GHOST_SEAM_SCOPE` | `thread` | SEAM scope label; not automatic thread-ID isolation |
| `GHOST_RECALL_BUDGET` | `8` | integer 1–64 selected records/budget control |
| `GHOST_GRAPH_HOPS` | `2` | integer 0–3 graph expansion |

## Read-tool variables

| Variable | Default | Meaning |
|---|---|---|
| `GHOST_TOOL_ROOTS` | empty | colon-separated readable directories |

Each root is expanded and resolved at startup. A missing/non-directory root is
an error. With no roots, `read_file` and `search_repo` do not exist in the
agent's tool list.

Example:

```bash
export GHOST_TOOL_ROOTS="/path/to/repo:/path/to/notes"
uv run ghost "Find every reference to the release boundary in the repository."
```

## Shell variables

| Variable | Default | Bounds / meaning |
|---|---|---|
| `GHOST_ENABLE_SHELL` | false | adds the real `run_command` tool |
| `GHOST_SHELL_APPROVAL` | true | ask on `/dev/tty` before every command |
| `GHOST_SHELL_TIMEOUT` | `120` | integer 1–3600 seconds; model may narrow, not widen |
| `GHOST_SHELL_WORKDIR` | current directory | resolved command working directory |

Truth values recognized as enabled are `1`, `true`, `yes`, and `on`. Unknown
values fall back to the setting's conservative default. An unset shell flag is
never enabled.

Example with approval:

```bash
export GHOST_ENABLE_SHELL=1
export GHOST_SHELL_WORKDIR="/path/to/repo"
uv run ghost "Run the narrow provider-free test for the CLI and report the result."
```

`GHOST_SHELL_APPROVAL=0` is appropriate only for a separately isolated,
deliberate unattended environment. It does not create a sandbox.

## SEAM-owned variables

Ghost passes `allow_pgvector_env=True` when it constructs the SDK. An existing
SEAM pgvector environment configuration may therefore affect the derived
retrieval adapter. Those variables are governed by the SEAM runtime, not
redefined here. Use an isolated SQLite path and clear external DSNs when a test
must be provider/service-free.

## Local avatar variables

These exist only in the unmerged avatar working tree:

| Variable | Meaning |
|---|---|
| `GHOST_AVATAR` | set to `1` to send CLI turn events to default `ws://127.0.0.1:8765` |
| `GHOST_AVATAR_WS` | explicit WebSocket URL; also enables the hook |
| `GHOST_SPRITE` | direct GTK pet sprite override |
| `GHOST_PET_X` | direct GTK pet initial X coordinate |
| `GHOST_PET_Y` | direct GTK pet initial Y coordinate |
| `DISPLAY` | X11 display used by GTK and desktop sensor commands |

The hook suppresses connection failure so an absent avatar does not fail an
agent turn.

## Safe configuration practices

- Keep `.env.local` mode 0600 and ignored.
- Never copy actual values into docs, history, snapshots, issues, or PR text.
- Prefer explicit isolated database paths for tests.
- Use separate namespaces/stores for destructive experiments.
- Do not infer multi-user isolation from namespace/scope strings.
- Record configuration names and bounds in evidence; redact values.
