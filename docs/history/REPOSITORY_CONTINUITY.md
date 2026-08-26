# Repository continuity and build-history protocol

Ghost preserves complete chronology without requiring every session to load it.
This protocol is the **Temporal Chain**: the SEAM-derived contract covering both
how build history is recorded and how git work is conducted around it. It keeps
current state, stable facts, chronology, bounded indexes, handoffs, and local
snapshots separated so that no single layer has to carry all of them.

The git half of the protocol — session reconciliation, branch/PR discipline, and
the committed/merged/released/deployed distinction — lives in `AGENTS.md`. This
page specifies the history half and the commands that verify both.

## Data model

```text
                    stable decisions
                         │
                         ▼
                  REPO_LEDGER.md

live checkout ──► PROJECT_STATUS.md ──► current task routes
      │
      ├─────────► HISTORY.md ─────────► HISTORY_INDEX.md
      │               │                       │
      │               │                       └─ bounded context packs
      │               │
      │               ├──────────────► docs/handoffs/INDEX.md
      │               │                       │
      │               │                       └─ one current recovery head
      │               │
      │               └──────────────► .ghost/snapshots/*.json
      │                                       local + ignored
      └─────────► git / GitHub / package / deployment evidence
```

`HISTORY.md` is the event authority. The index and snapshots are derived. A
handoff references its own history event and belongs to one linear
supersession chain.

The public continuity workflow also compares the candidate history with the
exact base revision. Existing bytes must be an exact prefix of the candidate;
parsing a valid rewritten file is not enough.

## Why the layers are separate

- Current status changes frequently and should remain small.
- Stable architectural decisions should not be rediscovered from session logs.
- Chronology must remain immutable enough to audit later corrections.
- An exhaustive history eventually exceeds a useful agent context window.
- Handoffs need a single current head; a folder full of dated notes is not a
  recovery protocol.
- Local snapshots may contain workstation paths and dirty-tree state, so they
  are useful for recovery but unsafe as public tracked artifacts.

## Normal startup

```bash
sed -n '1,220p' PROJECT_STATUS.md
sed -n '1,260p' REPO_LEDGER.md
sed -n '1,220p' HISTORY_INDEX.md
sed -n '1,240p' docs/INDEX.md
sed -n '1,160p' docs/handoffs/INDEX.md
uv run python -m tools.history.build_context_pack --latest 5 --token-budget 2000
```

Add `--topics`, `--entries`, or a larger bounded budget only when the task
requires more history.

## Recording an event

Append one entry using the schema in `AGENTS.md`. The entry records:

- what changed and why;
- whether it is local, committed, pushed, merged, released, or deployed;
- exact verification commands and exclusions;
- failures and skipped checks;
- relevant paths, commits, PRs, and durable public evidence;
- the prior event it corrects or supersedes; and
- unresolved next work.

Do not store raw model reasoning, provider payloads, secrets, local environment
values, session URLs, or private conversation links.

## Closeout

```bash
uv run python -m tools.history.closeout --agent codex
```

Expanded sequence:

```bash
uv run python -m tools.history.rebuild_index
uv run python -m tools.history.verify_handoffs
uv run python -m tools.history.verify_append_only --base-ref origin/main
uv run python -m tools.history.write_snapshot --agent codex --entries 5
uv run python -m tools.history.verify_continuity --require-snapshot
uv run pytest tests/test_docs.py tests/test_history_tools.py -q
```

Then run the code checks appropriate to the change. The history closeout does
not replace Ruff, the full test suite, package build, live qualification, or
exact-head CI.

## Correction rule

An incorrect merged entry remains immutable. Append a correction:

```text
## HISTORY#024 — Correct HISTORY#020 release claim
...
- Supersedes: HISTORY#020
...
```

The correction states exactly which claim was wrong, what evidence changed the
conclusion, and which later state is authoritative.

## Moving a referenced path

`HISTORY.md` is append-only, so a merged entry's `Refs` cannot be corrected when
a file is renamed or deleted. Record the move in
[`docs/history/PATH_MOVES.md`](PATH_MOVES.md) in the same change:

```text
| `old/path.md` | `new/path.md` | HISTORY#NNN |
| `deleted/path.md` | removed | HISTORY#NNN |
```

Continuity verification follows that chain before checking existence, so
documentation and source can be reorganized as Ghost upgrades without a dangling
historical reference and without rewriting the past. Chains resolve
transitively; a cycle or a move to a still-missing path fails the gate.

## Snapshot boundary

Snapshots contain only bounded history labels, git identity, handoff identity,
and dirty-path names. They do not copy file contents, environment variables,
credentials, or tool output. `.ghost/` is ignored because even filenames and
workstation paths can be inappropriate for a public repository.

## Rebuilding continuity tooling

All tooling uses the Python standard library and lives in `tools/history/`.
There is no database. To reconstruct it:

1. restore the files in `tools/history/`;
2. restore `HISTORY.md` and `docs/handoffs/`;
3. run `uv run python -m tools.history.rebuild_index`;
4. run `uv run python -m tools.history.verify_continuity`;
5. run `uv run pytest tests/test_history_tools.py -q`.

`HISTORY_INDEX.md` may be deleted and regenerated. `HISTORY.md` may not be
regenerated from the index because the index intentionally omits event bodies.

## The Temporal Chain template

The standalone [Temporal Chain template](../../templates/temporal-chain/README.md)
packages the core and handoff layers without Ghost or SEAM names, dependencies,
or machine paths. Install it into a new Git repository with:

```bash
python templates/temporal-chain/install.py \
  --repo /absolute/path/to/repository \
  --project-name "Project Name"
```

The installer refuses to overwrite collisions and verifies the generated
index and handoff chain. Its GitHub-hosted workflow enforces append-only base
comparison and current-tree continuity using only the standard library.

SEAM's classification routing, durable topic ledgers, roadmap/experience
streams, and derived cross-index are the optional mature-repository layer.
Promote those as a complete verified layer when scale requires them; do not
copy isolated stream files without their parsers and integrity gates.
