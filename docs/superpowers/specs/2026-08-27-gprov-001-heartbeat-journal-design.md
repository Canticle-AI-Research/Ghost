# GPROV-001 heartbeat action journal design

Status: operator-approved architecture; implementation and coordinated SEAM
service support remain incomplete.

## Purpose

Ghost currently records actions only after `graph.invoke` returns. A tool can
change the machine and return successfully, then a later model call, recursion
limit, checkpoint write, or graph step can raise. The lifecycle rejects the
SEAM turn, but the completed action never reaches the canonical action record.

GPROV-001 closes that crash window with two cooperating mechanisms:

1. Ghost durably journals tool intent and terminal state around the actual tool
   call; and
2. an in-process reconciliation heartbeat synchronizes the journal with an
   idempotent SEAM action endpoint until every record has a durable receipt.

The journal provides safety across graph and process failure. The heartbeat
provides eventual convergence. Neither mechanism makes arbitrary external side
effects universally exactly-once.

## Decision

Use a hybrid Ghost execution journal plus SEAM-owned canonical action ledger.
Ghost stores only the minimum bounded execution metadata required to recover
and deduplicate delivery. SEAM remains the authority for canonical action
identity, result verification, accepted-outcome support, and durable reasoning
records.

```text
                 local durability                 canonical provenance

tool request -> Ghost SQLite journal -> heartbeat -> SEAM action ledger
                    |                                  |
                    | STARTED                          | one action per key
                    | terminal state                   | verification receipt
                    | delivery receipt                 | support decision
                    v                                  v
             restart reconciliation             accepted or rejected turn
```

Rejected alternatives:

- A SEAM-only two-phase journal would make every tool effect depend on current
  network availability.
- A Ghost-only journal cannot resolve accepted-response loss or become the
  canonical verification authority without violating the opaque SEAM boundary.

## Required invariants

1. Ghost commits `STARTED` before it invokes a consequential tool.
2. The action key is the exact `(SEAM turn_id, tool_call_id)` pair.
3. One key names one immutable tool name and request fingerprint.
4. A terminal state is immutable after first durable commit.
5. Same key plus same content is an idempotent replay; same key plus different
   immutable or terminal content is a conflict.
6. A completed or indeterminate action is never automatically re-executed.
7. Graph, model, recursion, checkpoint, delivery, and process failures cannot
   erase the local action record.
8. A rejected turn remains rejected. Late action reconciliation cannot create
   accepted support or ingest the failed exchange.
9. Only SEAM-issued passed verification IDs may support an accepted outcome.
10. The heartbeat may stop indefinitely without corrupting the journal. When
    it resumes, synchronization continues from durable cursors and receipts.
11. The design guarantees exactly one canonical provenance record per action
    key. It does not claim exactly-once effects in arbitrary external systems.

## Ghost components

### Action journal

Create a separate operator-private SQLite database at
`~/.local/share/ghost/action-journal.db`. It is execution recovery state, not
semantic memory and not a LangGraph checkpoint. The first implementation uses
this fixed production path and constructor injection for isolated tests; adding
an operator path override waits for the authority-configuration repair.

SQLite uses WAL mode, foreign keys, busy timeouts, and transactionally assigned
monotonic journal sequence numbers. Directory and database permissions are
operator-private. A unique constraint on `(seam_turn_id, tool_call_id)` is the
local idempotency boundary.

Each record contains only:

- journal sequence;
- client turn UUID and opaque SEAM turn ID;
- exact nonblank tool-call ID and tool name;
- keyed request fingerprint, never raw arguments;
- `STARTED`, `SUCCEEDED`, `FAILED`, or `INDETERMINATE` state;
- exact typed success, exit code, duration, truncation state, output length,
  and keyed output fingerprint when available;
- bounded safe failure code, never an exception message or traceback;
- delivery state, SEAM receipt ID, verification IDs, server cursor, and
  timestamps; and
- the process instance ID that first claimed execution.

Raw tool arguments, raw command output, model text, memory text, credentials,
and exception detail are never stored in the journal. Request and output
fingerprints use an installation-local random key so low-entropy secret-shaped
values cannot be tested against an unsalted public digest. That key is stored
at `~/.local/share/ghost/action-journal.key` with operator-private permissions.

The startup maintenance transaction removes acknowledged records older than
seven days.
Pending, conflicting, `STARTED`, and `INDETERMINATE` records are never removed
automatically.

### Tool-call interception

Add an `ActionJournalMiddleware` at the existing LangChain middleware layer.
Its synchronous `wrap_tool_call` hook receives `ToolCallRequest`, including the
framework tool-call ID, before `ToolNode` invokes the actual tool.

The middleware performs this sequence:

```text
validate turn and call identity
        |
        v
commit STARTED
        |
        v
invoke the tool exactly once
        |
        +-- terminal ToolMessage/result -> commit SUCCEEDED or FAILED
        |
        `-- exception/unknown result ----> commit FAILED when known,
                                           otherwise leave STARTED
```

Failure to commit `STARTED` refuses execution. Failure to commit a terminal
state after an effect leaves `STARTED`; restart reconciliation converts it to
`INDETERMINATE` rather than re-running it. Existing typed command-result
validation remains authoritative for `run_command` success and exit status.

### Turn context

The lifecycle binds the client turn UUID, opaque SEAM turn ID, dimensions, and
journal handle into the framework turn context before graph execution. Missing,
blank, duplicated, or mismatched identity fails before tool execution.

Existing current-turn message scoping remains as a second verification path
for normally returned graph results. It must not become the durability source.

### Reconciliation heartbeat

The heartbeat is in-process for this slice. It runs:

- immediately after the journal opens;
- immediately after a terminal journal commit;
- every five seconds while any row is unacknowledged;
- with exponential retry from one second to sixty seconds plus bounded jitter
  after transport failure; and
- once during graceful shutdown under a bounded two-second best-effort flush.

No network heartbeat is emitted while the journal has no pending or unresolved
records. Startup reconciliation runs before Ghost accepts a tool-enabled turn.
If SEAM is unavailable, Ghost preserves the journal and refuses new
tool-enabled work; it does not enter an unrecorded degraded mode.

The heartbeat is a synchronization scheduler, not a lock, lease, or source of
truth:

```text
durable journal + idempotent SEAM contract = safety
periodic heartbeat                         = liveness
```

## Additive SEAM contract

The public `/v1` contract gains two additive fields and two routes. Private
SEAM/MIRL schemas remain outside Ghost.

### Idempotent turn begin

`POST /v1/agent/turns/begin` accepts required `client_turn_id` for the new
protocol. Replaying the same authenticated dimensions and client turn ID
returns the same opaque `turn_id`. Reusing the client turn ID with different
dimensions or immutable input returns `409`.

The response advertises `action_sync_version: "ghost.action_sync/v1"`.
Ghost refuses consequential tools when the capability is absent. No-tool turns
may retain the legacy contract during migration.

### Action synchronization

Add `POST /v1/agent/turns/actions/sync`.

Heartbeat request:

```json
{
  "namespace": "ghost.default",
  "scope": "thread",
  "workspace": "default",
  "project": "default",
  "session_id": "thread-42",
  "turn_id": "opaque-turn-handle",
  "client_turn_id": "018f...uuid",
  "journal_id": "018f...uuid",
  "instance_id": "018f...uuid",
  "after_server_cursor": 103,
  "actions": [
    {
      "sequence": 104,
      "tool_call_id": "call_7",
      "name": "run_command",
      "state": "SUCCEEDED",
      "request_fingerprint": "hmac-sha256:...",
      "result_fingerprint": "hmac-sha256:...",
      "ok": true,
      "exit_code": 0,
      "duration_ms": 14.2,
      "truncated": false,
      "output_length": 28,
      "evidence_level": "journal_recovered"
    }
  ]
}
```

Heartbeat response:

```json
{
  "turn_state": "REJECTED",
  "server_cursor": 104,
  "actions": [
    {
      "tool_call_id": "call_7",
      "status": "ACKNOWLEDGED",
      "receipt_id": "act_opaque-handle",
      "verification_ids": [],
      "passed_verification_ids": []
    }
  ]
}
```

The route is simultaneously delivery, lookup, and reconciliation. SEAM applies
these rules:

- same action key and same immutable/terminal content returns the original
  receipt;
- conflicting content returns `409` without overwriting either record;
- `STARTED` may transition once to one terminal state;
- a recovered digest-only terminal record is canonical provenance but cannot
  receive a passed verification ID;
- a terminal record with full bounded evidence delivered through the normal
  action path may receive verification under the existing server policy;
- late action synchronization is accepted for `REJECTED` turns but can never
  change their terminal state or support an accepted outcome; and
- `complete` fails closed while any known action is `STARTED`, conflicting, or
  otherwise unresolved.

### Full-evidence terminal delivery

Add `POST /v1/agent/turns/actions/terminal` for the normal path where the
bounded request and tool result are still available in process memory. It
carries the same action key, immutable fingerprints, exact typed terminal
fields, and the bounded raw evidence required by the existing SEAM verifier.
It returns the same per-action receipt and verification shape as the sync
route.

This route is idempotent under the same rules. If SEAM commits the terminal
record but the response is lost, the next metadata-only heartbeat retrieves
the original receipt. Raw evidence is never written to the Ghost journal and
is never copied into a heartbeat. If Ghost crashes before full-evidence
delivery, the recovered digest-only record is retained as non-supporting
provenance.

The existing `/v1/agent/turns/actions` route remains during migration. New
Ghost clients do not fall back to it for tool-enabled turns.

## Normal and failure flows

### Normal turn

```text
begin idempotent SEAM turn
  -> bind journal context
  -> commit STARTED
  -> execute tool
  -> commit terminal result
  -> immediate heartbeat/sync
  -> graph returns
  -> normal full-evidence action verification
  -> require no unresolved journal rows
  -> complete turn
  -> retain receipt for bounded recovery window
```

### Post-tool graph failure

```text
commit STARTED
  -> execute tool
  -> commit terminal result
  -> later graph/model/checkpoint step raises
  -> reject SEAM turn
  -> heartbeat synchronizes the terminal record
  -> SEAM stores one non-supporting action receipt on the rejected turn
```

### Response loss and restart

```text
Ghost sends sync -> SEAM commits -> response is lost
  -> local row stays pending
  -> Ghost restarts
  -> startup heartbeat replays the same key/content
  -> SEAM returns the original receipt
  -> Ghost marks the row acknowledged
  -> tool is not re-executed
```

### Unknown terminal outcome

```text
commit STARTED -> process/effect boundary is interrupted -> restart
  -> convert stale STARTED to INDETERMINATE
  -> never re-execute automatically
  -> synchronize one non-supporting provenance record
  -> require operator inspection before any deliberate retry
```

## Failure policy

| Failure | Required behavior |
|---|---|
| journal unavailable before tool | refuse tool; no effect |
| duplicate terminal row | replay same result or conflict; never execute |
| tool raises before known effect | commit `FAILED`; synchronize non-supporting record |
| terminal journal commit fails after effect | preserve `STARTED`; recover as `INDETERMINATE` |
| model or recursion fails after tool | reject turn; synchronize terminal record |
| checkpoint write fails | journal remains independent; reject and reconcile |
| SEAM unavailable | retain pending rows; refuse new tool-enabled turns |
| SEAM response lost after commit | query through heartbeat; receive original receipt |
| local/server content conflict | quarantine row, fail turn, require operator review |
| malformed heartbeat response | preserve local state and fail closed |
| heartbeat worker crashes | tool journal remains durable; restart worker with backoff |

## Concurrency and ownership

One journal database permits one active writer process. A process obtains an
exclusive writer lease recorded with a random instance ID, renews it every
five seconds, and gives it a thirty-second expiry. A second writer refuses tool
execution rather than sharing authority. After expiry, a successor may claim
the lease and reconcile the prior writer's rows. The heartbeat may read and
acknowledge rows through the owning process only.

The tool wrapper must handle parallel framework calls. SQLite transactions and
the unique action key serialize each individual start/terminal transition
without imposing a global tool execution order.

## Compatibility boundary

- The design is additive under `/v1` but requires coordinated Ghost and SEAM
  publication before tool-enabled activation.
- Frozen Stage 1 fixtures, manifests, runners, result schemas, and historical
  BIL-0 bundles remain byte-compatible.
- The current post-return action extractor stays green as a normal-path
  validation layer.
- No private SEAM/MIRL implementation, schema, graph, or tenant identity enters
  Ghost.
- GTOOL-003, GTOOL-004, GTOOL-005, authority configuration, package cleanup,
  provider-live qualification, and hosting remain separate workstreams.

## Acceptance evidence

Provider-free tests must begin red and prove:

1. post-tool model failure yields one terminal local row and one rejected-turn
   SEAM action receipt;
2. recursion failure yields the same without re-execution;
3. checkpoint-write failure cannot erase the journaled result;
4. accepted-response loss plus retry returns one canonical receipt;
5. restart drains pending rows without re-running the tool;
6. stale `STARTED` becomes `INDETERMINATE` and never passed support;
7. failed, nonzero, malformed, refused, and timed-out actions never receive
   passed verification support;
8. same key plus different content fails with a stable conflict;
9. heartbeat backoff, restart, and idle behavior are deterministic under an
   injected clock and random source;
10. raw request/output/exception text is absent from the SQLite journal and
    heartbeat payload;
11. missing action-sync capability blocks consequential tools before effect;
12. current-turn scoping and typed command-result regressions remain green; and
13. every tracked Stage 1 BIL-0 bundle still verifies byte-for-byte.

The complete closeout also requires Ruff, the full provider-free suite on the
supported protected matrix, package build, diff hygiene, continuity gates,
exact pushed-head CI, and independent review. Paid providers and a live SEAM
deployment require separate operator approval.

## Claim boundary

Completion of this design would establish durable, restart-reconcilable,
idempotent action provenance across the named Ghost failure modes. It would not
establish universally exactly-once external effects, unattended-shell safety,
tenant isolation, provider quality, package release fitness, deployment, or
production readiness.
