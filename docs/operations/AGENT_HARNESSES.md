# Running Ghost across agent harnesses

Ghost is an operating contract, not a single binary. The same charter can be
carried by several agent harnesses — Claude Code, Codex, Grok, and Antigravity —
so the operator can start Ghost in whichever client is appropriate without
maintaining four drifting personas.

This page covers the *harness* surface. It is unrelated to the Ghost Python
package in `src/ghost/`, which is the DeepAgent runtime; see
[command reference](COMMAND_REFERENCE.md) for that.

## Layers

```text
~/.config/canticle-agents/ghost.md     shared charter, harness-neutral
              │
              ▼
tools/launchers/agents/_body.md        shared persona body (tracked)
              │
              ├── agents/grok.md       harness frontmatter only
              └── agents/agy.md        harness frontmatter only
              │
              ▼
<harness agent directory>/canticle-ghost.md
              ▲
              │
tools/launchers/ghost-<harness>        credential-scoping launcher
```

The charter is the authority. The tracked Grok and Antigravity definitions are
thin adapters that read it and carry the same mission, scope, boundaries, and
return contract. Claude's agent definition and Codex's profile are external
prerequisites in the current slice; the installer warns but does not create
them. The roadmap keeps this track in progress until all four definitions and
the charter are reproducible from tracked sources.

## Why the launcher exists

Every one of these clients prefers an exported API key over the cached
subscription login. If `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` is exported in
the parent shell for a standalone application, the client silently bills the API
instead of using the operator's subscription.

Each launcher unsets **only its own provider's** variables, and only in the child
process, then execs the client with the Ghost persona selected.

## Installed surface

| Launcher | Client | Persona selected by | Agent definition |
|---|---|---|---|
| `ghost-claude` | `claude` | `--agent canticle-ghost` | `~/.claude/agents/canticle-ghost.md` |
| `ghost-codex` | `codex` | `--profile ghost` | `[profiles.ghost]` in `~/.codex/config.toml` |
| `ghost-grok` | `grok` | `--agent canticle-ghost` | `~/.grok/agents/canticle-ghost.md` |
| `ghost-agy` | `agy` | `--agent canticle-ghost` | `~/.gemini/config/agents/canticle-ghost.md` |

Codex is the odd one out: it selects behavior with a config profile rather than
an agent file, so its persona comes from the shared charter plus the project
`AGENTS.md` rather than from a rendered definition.

## Install or refresh

```bash
uv run python tools/launchers/install.py --dry-run
uv run python tools/launchers/install.py
uv run python tools/launchers/install.py --harness grok --harness agy
```

`--bin-dir` overrides the default `~/.local/bin`. The installer copies all four
launchers, renders only the Grok and Antigravity definitions, and warns when the
shared charter is missing. It does not write Claude's agent definition or the
Codex profile.

## Verify discovery

```bash
grok inspect | sed -n '/Agents/,/^$/p'    # canticle-ghost listed as "user"
agy agent | grep canticle-ghost
ls ~/.claude/agents/canticle-ghost.md
grep -n '^\[profiles.ghost\]' ~/.codex/config.toml
```

A launcher that runs but whose agent is not listed means the client did not
discover the definition; check the directory in the table above rather than
assuming the persona loaded.

## Adding another harness

1. Add its frontmatter file to `tools/launchers/agents/<harness>.md` — schema
   only, no persona text.
2. Add an entry to `HARNESSES` in `tools/launchers/install.py` naming the agent
   directory and the client label.
3. Add `tools/launchers/ghost-<harness>` that unsets that provider's key
   variables and execs the client.
4. Record the change in `HISTORY.md` and add the row to the table above.

Never fork the persona body. If a harness needs different wording, the charter
or the shared body is what changes.
