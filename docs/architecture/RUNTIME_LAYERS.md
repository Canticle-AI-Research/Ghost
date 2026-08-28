# Runtime layers and replaceable boundaries

Ghost separates memory semantics, turn policy, framework integration, and user
interface so a framework upgrade cannot silently redefine durable behavior.

## Four layers

```text
Layer 4  interface       cli.py / future API / avatar hooks
                         operator I/O, exit codes, display
            │
Layer 3  agent adapter   application.py / middleware.py
                         DeepAgents, LangChain, LangGraph, provider messages
            │
Layer 2  turn contract   lifecycle.py
                         framework-free sequencing and failure rules
            │
Layer 1  memory adapter  seam_memory.py
                         bounded opaque HTTP operations
            │
Layer 0  SEAM service    canonical RAW/MIRL/retrieval/provenance implementation
```

## Layer 1: memory adapter

`SeamMemory` owns one `httpx.Client` and exposes only the operations a Ghost turn
needs:

- `begin_turn` — open reasoning and retrieve;
- `record_actions` — add decisions and tool verifications;
- `complete_turn` — ingest and finalize;
- `fail_turn` — reject without ingest;
- `query_knowledge` — read-only tool lookup; and
- `close` — release the owned HTTP client.

This file must not import agent frameworks or private SEAM modules. The service
returns bounded text and opaque handles; it derives evidence and accepted
verification IDs server-side. If the public HTTP contract changes, this is the
primary adaptation point.

## Layer 2: turn contract

`run_turn` depends on plain protocols and dataclasses. It does not know about
LangChain messages, DeepAgents middleware, or provider payloads.

Invariants:

1. non-empty normalized input;
2. reasoning begins before model execution;
3. recall precedes ingest;
4. every open run closes on completion or failure;
5. failures do not ingest;
6. tool attempts are translated before verification; and
7. only passed verification IDs support a verified outcome.

## Layer 3: framework adapter

`GhostAgent` constructs:

- the configured model;
- Responses API mode for OpenAI providers;
- the allowed tool set;
- `SeamRecallMiddleware`;
- a persistent `SqliteSaver`; and
- the DeepAgent graph.

`extract_tool_attempts` is intentionally here because provider/framework
message shapes are adapter details. `run_command` returns bounded model-facing
text plus a `ghost.command_result/v1` artifact. LangChain's `ToolMessage.status`
only describes tool transport and may remain `success` for a process that exits
nonzero; the adapter therefore validates the artifact and carries its real
`ok`, `exit_code`, and `duration_ms` into the framework-free `ToolAttempt`.
Absent, malformed, contradictory, or nonzero command artifacts fail closed.

Every lifecycle invocation assigns the current human message the client turn
ID. The adapter requires exactly one matching `HumanMessage`, scans only the
messages after it, and uses mutually exclusive concrete `AIMessage` and
`ToolMessage` roles. This prevents a persistent checkpoint from replaying an
older tool result and prevents an assistant message with result-shaped extra
fields from forging success. The framework-free SEAM adapter performs a second
exact-type, fail-closed validation before transport.

This boundary does not make completed actions crash-atomic. If a tool changes
the machine and a later graph/model/checkpoint step raises before `invoke`
returns, the lifecycle still lacks a returned attempt to submit. GPROV-001
tracks the required durable idempotent journal and reconciliation protocol.

## Layer 4: interfaces

The landed interface is `ghost.cli`. It owns argument parsing, interactive
terminal behavior, command approval prompts, exit codes, and resource cleanup.

The current working tree adds avatar turn notifications, but those calls are
local WIP and not a mainline contract.

## Replacement tests

| Change | Files expected to change | Files expected to remain stable |
|---|---|---|
| Change model provider | config/application | lifecycle/seam_memory |
| Replace DeepAgents | application/middleware | lifecycle/seam_memory |
| Replace LangGraph checkpoint saver | application | lifecycle/seam_memory |
| Advance SEAM API contract | seam_memory + tests | lifecycle/CLI where possible |
| Add interface | new interface adapter | memory/lifecycle invariants |
| Add tool | tools + application + trust docs/tests | memory ownership |

`tests/test_layering.py` and `tests/test_memory_boundary.py` enforce the most
important directions of this table.
