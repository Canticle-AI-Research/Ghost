# Ghost ↔ SEAM opaque HTTP contract

This is Ghost's client-side reconstruction contract. It describes only the
public behavior Ghost depends on; it does not specify MIRL schemas, canonical
IDs, storage, ranking internals, or the private reasoning graph.

## Transport

- Base URL: `SEAM_BASE_URL`, default `http://127.0.0.1:8765`.
- Authentication: `Authorization: Bearer <SEAM_API_TOKEN>` when configured.
- Media type: JSON requests and responses.
- Timeout: `GHOST_SEAM_TIMEOUT`, default 30 seconds, bounded 0.1–300.
- Response allocation: streamed and capped at 8 MiB, including when the server
  omits `Content-Length`.
- Compatibility: `/v1` is additive-only; a breaking shape requires a new URL version.
- Remote deployments use HTTPS. Trusted loopback is the development default.

Ghost treats any network error, non-2xx response, invalid JSON, non-object
body, or malformed required response field as `SeamTransportError`. It does
not continue in memory-degraded mode.

## Shared dimensions

Every turn request includes:

```json
{
  "namespace": "ghost.default",
  "scope": "thread",
  "workspace": "default",
  "project": "default",
  "session_id": "langgraph-thread-id"
}
```

Ghost includes `session_id` whenever scope is `thread`; the exact same thread
value owns checkpoint execution and durable-memory partitioning. These are
public partitions, not proof of identity. The service derives the
principal from authentication and binds opaque handles to that principal and
exact partition. Ghost never sends a private tenant ID.

## State machine

```text
                   actions (0..N batches)
                 ┌─────────────────────────┐
                 │                         ▼
begin ───────► OPEN ───── complete ─────► ACCEPTED
                 │
                 └────── fail ──────────► REJECTED

ACCEPTED + complete again  -> same receipt, replayed
REJECTED + fail again      -> rejected, replayed
terminal + actions         -> 409 conflict
REJECTED + complete        -> 409 conflict
foreign handle             -> content-free 404
```

## Begin

`POST /v1/agent/turns/begin`

```json
{
  "namespace": "ghost.default",
  "scope": "thread",
  "workspace": "default",
  "project": "default",
  "session_id": "thread-42",
  "query": "What does the operator prefer?",
  "limit": 8,
  "graph_hops": 2,
  "agent_id": "ghost",
  "model": "gpt-5.6-terra",
  "provider": "openai"
}
```

Required response subset:

```json
{
  "turn_id": "opaque-turn-handle",
  "memories": [
    {
      "id": "mem_opaque-handle",
      "text": "bounded public memory",
      "score": 0.91,
      "status": "asserted",
      "created_at": "2026-08-25T00:00:00+00:00"
    }
  ]
}
```

Ghost renders each memory as one JSON line with `record_id`, `kind`, `score`,
and bounded `memory` text. Literal angle brackets become Unicode escapes before
the text enters model context. An empty list becomes an empty context string.

## Record actions

`POST /v1/agent/turns/actions`

```json
{
  "namespace": "ghost.default",
  "scope": "thread",
  "workspace": "default",
  "project": "default",
  "session_id": "thread-42",
  "turn_id": "opaque-turn-handle",
  "attempts": [
    {
      "name": "read_file",
      "request": "{\"path\":\"README.md\"}",
      "output": "raw bounded tool result",
      "ok": true,
      "exit_code": 0,
      "duration_ms": 4.5
    }
  ]
}
```

Required response subset:

```json
{
  "verification_ids": ["opaque-check"],
  "passed_verification_ids": ["opaque-check"]
}
```

Ghost returns only passed IDs to its framework-free lifecycle. A failed
attempt is still sent and recorded, but its ID cannot support the accepted
outcome. With no attempts Ghost makes no actions request.

Tool output crosses this authenticated boundary because the server—not the
client—must bind its digest to the verification. The server stores length and
SHA-256 only and never echoes raw output. Service request-body logging must be
disabled or securely redacted.

## Complete

`POST /v1/agent/turns/complete`

```json
{
  "namespace": "ghost.default",
  "scope": "thread",
  "workspace": "default",
  "project": "default",
  "session_id": "thread-42",
  "turn_id": "opaque-turn-handle",
  "user_input": "Remember that I prefer concise evidence.",
  "assistant_output": "I will remember that preference.",
  "memory_admission": {
    "decision": "admit",
    "kind": "preference",
    "reason_code": "explicit_remember"
  }
}
```

Required response subset:

```json
{
  "accepted": true,
  "receipt_id": "rcpt_opaque-handle",
  "memory_count": 1,
  "memory_admission": {
    "decision": "admit",
    "kind": "preference",
    "reason_code": "explicit_remember"
  }
}
```

Ghost deliberately omits its client turn ID, evidence IDs, and verification
IDs. It does send the LangGraph thread ID as the memory `session_id`. The
service owns the authoritative run, retrieval ledger,
passed-check set, deterministic source identity, ingest, and terminal transition.
Only `admit` persists the exchange; `reject` and `review` accept the reasoning
outcome with `memory_count: 0`.

## Fail

`POST /v1/agent/turns/fail`

```json
{
  "namespace": "ghost.default",
  "scope": "thread",
  "workspace": "default",
  "project": "default",
  "session_id": "thread-42",
  "turn_id": "opaque-turn-handle",
  "error_type": "RuntimeError"
}
```

Ghost sends only `type(error).__name__`. It never sends the exception message,
traceback, provider response, partial assistant text, or hidden reasoning. The
service rejects without ingest, then Ghost re-raises the original exception.

## Mid-turn recall tool

`POST /v1/memories/recall`

```json
{
  "query": "release captain",
  "namespace": "ghost.default",
  "scope": "thread",
  "workspace": "default",
  "project": "default",
  "session_id": "thread-42",
  "limit": 5,
  "view": "current"
}
```

The response `memories` list uses the same public item shape as begin. Ghost
adapts it to the existing read-only tool format; the model receives no route
that can complete, fail, delete, correct, promote, or mutate memory.

## Operator memory routes

The CLI, never a model tool, also uses:

```text
POST /v1/memories          explicit remember
POST /v1/memories/recall   current or history view
POST /v1/memories/correct  additive replacement + supersession
POST /v1/memories/delete   auditable soft-delete
```

Every route carries the same dimensions. Correction and deletion additionally
carry an idempotency key and opaque `mem_` handle. Correction accepts exactly
one handle; delete is bounded by the server. A foreign or cross-boundary handle
returns content-free 404. `history` returns lifecycle status but does not
register retired handles for reuse.

## Error handling

| Status | Meaning | Ghost behavior |
|---:|---|---|
| 400 | invalid type, bound, name, or partition | raise `SeamTransportError` |
| 401/403 | missing or invalid authorization | fail; operator repairs credentials |
| 404 | unknown/foreign handle or unsupported route | fail closed without boundary detail |
| 409 | terminal lifecycle conflict | fail; never fabricate/reuse a handle |
| 413 | request body exceeds service bound | fail; reduce bounded input at source |
| 429 | rate limit | fail; supervisor retries only under explicit policy |
| 5xx/network | unavailable service | fail; no silent memory bypass |

Error detail is bounded to 300 characters. The bearer token is excluded from
settings representation and never included in the wrapped error.

## Cross-repository proof split

Ghost tests prove exact payload translation, opaque-handle treatment,
failure-text redaction, injection-resistant rendering, no private imports or
dependency sources, and clean wheel installation.

SEAM tests prove canonical compile/recall, reasoning decisions and outcomes,
raw tool-output non-persistence, server-derived support, terminal idempotency,
failed-turn non-ingest, and cross-principal isolation.

Neither suite may claim the other's proof boundary. End-to-end live evidence
requires named Ghost and SEAM revisions/deployment, explicit provider spend, a
throwaway namespace, and redacted results.
