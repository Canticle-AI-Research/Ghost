# Recovery, health, and observability

## Current status and boundary

Ghost now has provider-free checkpoint backup, verification, non-overwriting
restore, redacted component-health types, and content-free specialist lifecycle
events. It does not have a hosted API, scheduler, dashboard, alert manager,
multi-tenant control plane, or deployed disaster-recovery proof.

Two stores must never be confused:

```text
LangGraph checkpoint SQLite                 SEAM durable memory service
conversation execution position             semantic memory + provenance
        │                                             │
        ├─ Ghost can back up/restore this file         └─ governed by SEAM backup,
        │                                                 projection, and recovery
        └─ does not reconstruct semantic truth              procedures
```

A checkpoint backup can resume execution state. It cannot rebuild SEAM, and a
SEAM backup cannot replace the checkpoint conversation state.

## Checkpoint commands

### Create a consistent backup

```bash
uv run ghost checkpoint backup /secure/backups/ghost-checkpoints-20260826.db
```

The source is `GHOST_CHECKPOINT_DB` (or its documented default). The command
uses SQLite's online backup API, runs `PRAGMA quick_check`, refuses an existing
destination, and emits a JSON manifest containing absolute path, bytes, and
SHA-256. Store the manifest beside—but not inside—the backup database.

### Verify before depending on a backup

```bash
uv run ghost checkpoint verify /secure/backups/ghost-checkpoints-20260826.db
uv run ghost checkpoint verify /secure/backups/ghost-checkpoints-20260826.db \
  --sha256 EXPECTED_64_HEX_DIGEST
```

Without `--sha256`, verification proves current SQLite integrity and reports
the current digest. With it, a digest mismatch fails before SQLite validation.
Production recovery should always use a digest retained outside the recovered
host.

### Restore to a new path

```bash
uv run ghost checkpoint restore \
  /secure/backups/ghost-checkpoints-20260826.db \
  /srv/ghost/recovery/checkpoints.db \
  --sha256 EXPECTED_64_HEX_DIGEST
```

Restore is deliberately non-destructive: the destination parent must exist and
the destination itself must not. Bytes are copied to a same-directory
temporary file, flushed, digest-checked, SQLite-checked, and atomically linked
to the new name. An existing path is never replaced.

To adopt a restored database:

1. stop or drain the Ghost process that owns the old checkpoint connection;
2. verify the backup using an independently retained digest;
3. restore to a new path;
4. point `GHOST_CHECKPOINT_DB` at that new path;
5. start one isolated process and resume a non-sensitive test thread;
6. separately verify the configured SEAM principal and memory boundary;
7. record artifact digest, operator, time, old/new paths, and outcome; and
8. retain the old database until the rollback window closes.

The command does not delete the old database, rotate backups, encrypt files,
upload them, or change configuration.

## Backup schedule and retention contract

A hosted operator must define, outside this repository:

- recovery point objective and recovery time objective;
- checkpoint and SEAM schedules appropriate to their different stores;
- encryption at rest and in transit;
- off-host/off-region copies and key custody;
- retention, legal hold, tenant deletion, and secure disposal;
- restore-drill cadence and evidence retention;
- schema/version compatibility; and
- who may authorize restore, rollback, and destructive retirement.

The local primitive is necessary but insufficient for any disaster-recovery or
production-readiness claim.

## Health model

`probe_components` evaluates named, side-effect-free probes in stable sorted
order. Every successful component is `ready` with the fixed code `ok`; probe
return values are discarded so they cannot accidentally become telemetry. A failure is
`unavailable` with only the fixed code `probe_failed`. Readiness is fail-closed: an empty
probe set or any unavailable component makes the snapshot unavailable.

```text
checkpoint probe ─┐
SEAM probe ───────┼─► redacted HealthSnapshot ─► future /ready endpoint
provider probe ───┘       state, ready, UTC time,
                          component name/state/code
```

Probe return values are ignored and must not be used to carry diagnostics. The
health function is implemented; no network endpoint exposes it today.

## Observability data contract

Allowed operational dimensions include:

- stable component, operation, role, model, and deployment identifiers;
- terminal status and fixed reviewed error code;
- duration, step, tool-call, token, and cost counters;
- bounded queue depth and rate-limit state;
- opaque turn, delegation, receipt, verification, and bundle references; and
- candidate/release/deployment revision.

Forbidden by default:

- user prompts and assistant answers;
- recalled memory text;
- tool arguments and raw tool output;
- exception messages and stack locals;
- bearer tokens, cookies, keys, headers, environment values, and URLs carrying
  credentials; and
- personal data used merely because it was convenient as a metric label.

Content debugging requires a separate, access-controlled, time-bounded consent
path with redaction and retention policy. It must never be enabled by changing
the meaning of the safe operational stream.

## Incident and recovery sequence

```text
detect ─► classify ─► contain ─► preserve evidence ─► recover to new path
  │          │             │             │                    │
 alert    stable code   drain/disable  hashes + revisions   verify + smoke
  └──────────────────────────────► communicate ─► post-incident actions
```

Minimum evidence for a future incident record: exact deployed artifact,
configuration names without values, first/last observed time, affected
principals/namespaces, status codes, containment action, backup digest, restored
path identity, SEAM recovery evidence, smoke result, rollback decision, and
follow-up owner. This repository currently supplies no hosted incident system.

## Provider-free verification

```bash
uv run pytest tests/test_operations.py tests/test_specialists.py -q
uv run ruff check src/ghost/operations.py src/ghost/specialists.py
```

The tests inject corruption, an existing restore target, component failure,
specialist budget overrun, exception text, and cancellation. They make no live
provider or SEAM request and cannot qualify a deployment.
