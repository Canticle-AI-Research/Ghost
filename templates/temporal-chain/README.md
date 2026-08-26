# Temporal Chain

The **Temporal Chain** is the repository-neutral protocol, proven in SEAM and
adopted by Ghost, for two things a long-running project cannot afford to lose:

1. **How build history is recorded** — an append-only chronology whose
   corrections never rewrite the past; and
2. **The git protocol around it** — how a session starts, what it must
   reconcile before claiming status, how a change is closed out, and what
   separates committed from merged from released from deployed.

It is called a chain because every link is ordered and verified: each history
entry follows the last, each handoff supersedes exactly one predecessor, and
the derived index is rebuilt from the chain rather than maintained beside it.
Breaking a link fails a test rather than passing silently.

## What a repository gets

| Artifact | Role |
|---|---|
| `HISTORY.md` | append-only chronological authority; the chain itself |
| `HISTORY_INDEX.md` | generated bounded map; never hand-edited |
| `PROJECT_STATUS.md` | current headline and routes; not an archive |
| `REPO_LEDGER.md` | stable decisions and invariants |
| `docs/handoffs/INDEX.md` | one current head, one linear supersession chain |
| `AGENTS.md` | the git and session protocol every agent/operator follows |
| `.continuity/` snapshots | ignored local recovery state |
| `tools/history/` | standard-library verification and closeout commands |
| `.github/workflows/continuity.yml` | fork-safe hosted enforcement |

## Install into a repository

Run from this template directory:

```bash
python install.py --repo /absolute/path/to/repository --project-name "Project Name"
```

The installer is fail-closed: it refuses to overwrite any existing target. In
an established repository, review collisions and merge the policy text rather
than adding a force flag. After installation:

```bash
python -m tools.history.rebuild_index
python -m tools.history.verify_continuity
python -m tools.history.closeout --agent operator
```

The template uses only the Python standard library. Repositories may wrap the
commands with `uv run`, Poetry, Hatch, or another environment manager without
changing the protocol.

## The chain's integrity rules

- `HISTORY.md` is append-only. Existing bytes must remain an exact prefix of
  any candidate; parsing a valid rewritten file is not enough.
- A correction is a **new** entry naming what it `Supersedes`. Nothing earlier
  is edited to look cleaner in hindsight.
- The index is derived. Delete it and it rebuilds; delete the history and
  nothing rebuilds it, because the index omits event bodies on purpose.
- Exactly one handoff is current. A folder of dated notes is not a recovery
  protocol.
- Snapshots stay local and ignored: even filenames and workstation paths can be
  inappropriate to publish.

## Layers

| Layer | Include when | Components |
|---|---|---|
| Core | every maintained repository | status, ledger, history, derived index, bounded packs, snapshots, CI |
| Handoffs | work may cross sessions or agents | single current head, linear supersession, recovery boundary |
| Routing | durable topic branches become hard to find | classification manifest and topic ledgers |
| Streams | roadmap, experience, or library timelines grow independently | per-stream logs/indexes and a derived cross-index |

The core and handoff layers install by default. SEAM's routing manifests, topic
ledgers, roadmap/experience streams, and global cross-index are intentionally
optional — add them when a repository has enough history or parallel
workstreams to justify the coordination cost, and port them with their full
verification gates rather than copying isolated stream files.
