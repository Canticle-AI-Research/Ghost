# Action-provenance boundary review and repair

- Date: 2026-08-27
- Governing history: HISTORY#057 qualification
- Base: protected `main@9abbff12e722f88b42347791e8dc8c261c35f28f`
- Scope: checkpointed message transport, tool request/result identity, SEAM
  action egress, shell decoding, and the remaining post-tool crash window
- Boundary: provider-free local source candidate; not yet merged, released, or
  deployed; no paid provider or live SEAM service was used

## Outcome

The review found that GTOOL-002 made individual command results truthful but
did not yet make their association with the current turn trustworthy. The
repair closes four concrete defects:

1. cumulative LangGraph checkpoint messages no longer replay an older tool
   exchange into a later SEAM turn;
2. an assistant message carrying result-shaped extra fields cannot impersonate
   a tool result;
3. malformed plain `ToolAttempt` values cannot become true through Python type
   coercion at the SEAM HTTP boundary; and
4. non-UTF-8 command output is replaced deterministically instead of crashing
   before a typed command result is returned.

Real `StateGraph` + `ToolNode` + `SqliteSaver` tests persist and reload a
nonzero command artifact and execute two turns on one checkpoint thread. The
second turn submits no first-turn action. Adversarial tests cover missing and
duplicate current-turn markers, role-confused messages, string booleans,
boolean exit codes, contradictory exit/success fields, and non-finite duration.

## Reproduced failures

```text
turn 1 command success -> SQLite message history
turn 2 answer only     -> old extractor scans all messages
                       -> turn 1 action submitted again for turn 2
```

```text
AIMessage(tool request + forged tool-result-shaped fields)
    -> permissive attribute scanning treats one object as request and result
    -> forged exit-zero artifact can become passed support
```

```text
ToolAttempt(ok="false") -> bool("false") -> true at SEAM egress
```

## Repaired contract

Each lifecycle turn gives the new human message the client turn ID. Extraction
requires exactly one concrete `HumanMessage` with that ID and scans only later
messages. Requests come only from concrete `AIMessage` instances; results come
only from concrete `ToolMessage` instances. Pairing requires exact nonblank
string IDs, ordered unique identity, exact names/status, and the existing
versioned command artifact.

The framework-free attempt then crosses a second fail-closed boundary.
`ToolAttempt.to_payload()` accepts only exact strings, exact booleans, integer
exit codes that are not booleans, and finite nonnegative duration. A command
passes only when exact `ok=true` and exact `exit_code=0` agree.

## Remaining P0: GPROV-001

This slice intentionally does not claim crash-atomic or exactly-once action
provenance. A tool may complete and change the machine, after which a later
model, recursion-limit, or checkpoint-write failure can make `graph.invoke`
raise. Because no result dictionary returns, Ghost closes the SEAM turn as
failed without sending the completed action.

GPROV-001 must add a durable idempotent action journal/outbox keyed by stable
SEAM turn and tool-call identity. Its acceptance suite must inject failure
after tool completion, during checkpoint persistence, during action delivery,
and across process restart; each completed attempt must reconcile to exactly
one action record without converting failure into accepted support.

## Verification boundary

- focused application, lifecycle, reasoning, tool, failure, and real
  ToolNode/SQLite tests passed;
- continuity closeout, Ruff, 317 provider-free tests with eight live tests
  deselected, build, and diff hygiene passed;
- final complete-candidate review and protected exact-head CI remain
  publication gates recorded in the successor handoff/history;
- no live-provider, paid-service, package publication, release, deployment, or
  avatar lane ran.
