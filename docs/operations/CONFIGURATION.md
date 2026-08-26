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
| `SEAM_BASE_URL` | `http://127.0.0.1:8765` | authenticated SEAM service root; trailing slash ignored |
| `SEAM_API_TOKEN` | unset | SEAM bearer token; never written to logs or settings repr |
| `GHOST_SEAM_TIMEOUT` | `30` | HTTP timeout in seconds; number from 0.1–300 |
| `GHOST_SEAM_DB` | `~/.local/share/ghost/seam.db` | legacy local path used only to place the default checkpoint beside, not semantic storage |
| `GHOST_CHECKPOINT_DB` | `~/.local/share/ghost/checkpoints.db` | LangGraph execution state only |
| `GHOST_SEAM_NAMESPACE` | `ghost.default` | logical SEAM namespace |
| `GHOST_SEAM_SCOPE` | `thread` | semantic scope; thread scope also sends the LangGraph thread ID as `session_id` |
| `GHOST_WORKSPACE` | `default` | validated workspace partition label |
| `GHOST_PROJECT` | `default` | validated project partition label |
| `GHOST_MEMORY_ADMISSION` | `explicit` | `explicit`, `all`, or `off`; completed-turn admission policy |
| `GHOST_RECALL_BUDGET` | `8` | integer 1–50 selected records/public API bound |
| `GHOST_GRAPH_HOPS` | `2` | integer 0–3 graph expansion |
| `GHOST_MAX_STEPS` | `25` | integer 2–100 LangGraph recursion/superstep ceiling per turn |

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

`GHOST_MAX_STEPS` bounds the model/tool graph independently of
`GHOST_SHELL_TIMEOUT`. The first limits how many graph supersteps a turn may
take; the second limits one spawned command. A future provider-wide wall-clock
deadline must be an additional bound, not a replacement for either.

## SEAM service variables

Ghost sends only the public namespace, scope, workspace, project, thread
session, optional bearer token, bounded
turn text, tool-attempt metadata, and raw tool output for server-side hashing.
Storage, pgvector, graph, MIRL, deletion, and lifecycle policy remain
service-owned and are never configured through Ghost. `SEAM_BASE_URL` should
use HTTPS outside trusted loopback. The service must implement the additive
`/v1/agent/turns/*` routes documented in the architecture blueprint.

## Safe configuration practices

- Keep `.env.local` mode 0600 and ignored.
- Never copy actual values into docs, history, snapshots, issues, or PR text.
- Prefer explicit isolated database paths for tests.
- Use separate namespaces/stores for destructive experiments.
- Do not infer multi-user isolation from labels alone; shared hosting also
  requires SEAM principal mode and its authenticated boundary.
- Record configuration names and bounds in evidence; redact values.
