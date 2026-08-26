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
                         exact private SeamSDK operations
            │
Layer 0  SEAM            canonical RAW/MIRL/retrieval/provenance implementation
```

## Layer 1: memory adapter

`SeamMemory` owns one SDK instance and exposes only the operations a Ghost turn
needs:

- `begin_turn` — open reasoning and retrieve;
- `record_actions` — add decisions and tool verifications;
- `complete_turn` — ingest and finalize;
- `fail_turn` — reject without ingest;
- `query_knowledge` — read-only tool lookup; and
- `close` — release the owned SDK.

This file must not import agent frameworks. If the SDK changes, this is the
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
message shapes are adapter details.

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
| Advance SEAM SDK contract | seam_memory + tests | lifecycle/CLI where possible |
| Add interface | new interface adapter | memory/lifecycle invariants |
| Add tool | tools + application + trust docs/tests | memory ownership |

`tests/test_layering.py` and `tests/test_memory_boundary.py` enforce the most
important directions of this table.
