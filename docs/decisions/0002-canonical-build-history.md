# ADR-0002: Canonical append-only build history

- Status: accepted
- Date: 2026-08-25
- Governing history: HISTORY#023

## Context

Ghost had dated implementation reports but no complete repository chronology,
small current-state router, stable decision ledger, bounded history index,
single handoff head, or continuity verifier. Status answers required rebuilding
state from Git, local notes, and memory of earlier sessions.

## Decision

Ghost adopts:

- root `PROJECT_STATUS.md` for current state;
- root `REPO_LEDGER.md` for stable decisions;
- append-only root `HISTORY.md` as the event authority;
- generated `HISTORY_INDEX.md` for bounded startup;
- `docs/handoffs/INDEX.md` with exactly one linear current head;
- ignored `.ghost/snapshots/` for local recovery state;
- standard-library `tools/history/` for parsing, indexing, bounded packs,
  snapshots, handoff verification, continuity, and closeout; and
- CI tests for schema, chronology, docs reachability, and derived index drift.

## Consequences

- Material changes have an explicit closeout cost.
- Incorrect historical entries are corrected by successors, not edited.
- Routine agent startup remains bounded as history grows.
- Local/remote/merged/released/deployed state becomes auditable.
- Snapshots remain local to avoid publishing workstation paths/dirty state.
- Git remains the byte-level source diff authority; history provides intent,
  verification, boundary, and temporal routing.

## Rejected alternatives

- Git log alone: lacks verification boundaries, failures, and unresolved state.
- Dated files without a registry: permits multiple ambiguous “latest” notes.
- One ever-growing status file: makes current-state reads scale with history.
- Rewriting old reports: destroys the correction trail.
- Copying SEAM's full multi-stream machinery immediately: unnecessary for
  Ghost's current repository size and would increase maintenance surface before
  the simpler protocol is exercised.
