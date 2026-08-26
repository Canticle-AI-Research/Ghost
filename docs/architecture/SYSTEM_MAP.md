# Ghost system map

## System boundary

Ghost is an agent application built on DeepAgents, LangChain, LangGraph, and
the private SEAM runtime. Each layer has a separate responsibility.

```mermaid
flowchart TB
    UI[CLI or future API/UI]
    APP[Ghost application policy]
    DA[DeepAgents agent and future specialists]
    LC[LangChain model and middleware]
    LG[LangGraph execution and checkpoints]
    ADAPTER[Ghost SEAM adapter]
    SDK[Private SeamSDK]
    MIRL[(RAW and MIRL canonical store)]
    IDX[Lexical vector and graph projections]
    MODEL[OpenAI Responses API or configured model]

    UI --> APP
    APP --> ADAPTER
    ADAPTER --> SDK
    SDK --> MIRL
    MIRL --> IDX
    IDX --> SDK
    APP --> DA
    DA --> LC
    DA --> LG
    LC --> MODEL
    SDK --> APP
```

## Ownership matrix

| Layer | Owns | Must not become |
|---|---|---|
| Ghost | mission, turn policy, tools, memory admission, user experience | a copy of the SEAM runtime |
| DeepAgents | agent loop, planning, working files, delegation | canonical long-term memory |
| LangChain | model adapters and middleware | an authorization or truth layer |
| LangGraph | execution state, checkpoints, interrupts, resumability | the knowledge graph |
| SEAM SDK | memory operations and typed reasoning sessions | Ghost-specific product policy |
| MIRL/RAW | canonical meaning and source evidence | disposable prompt context |
| Knowledge/vector indexes | retrieval acceleration and topology | a second source of truth |
| Model provider | inference | durable memory or final authority |

## Current pre-turn path

```mermaid
sequenceDiagram
    participant U as User
    participant G as GhostAgent
    participant S as SeamMemory
    participant SDK as SeamSDK
    participant M as Model

    U->>G: user input
    G->>S: begin_turn(input)
    S->>SDK: start_reasoning(namespace, scope)
    S->>SDK: retrieve(mode=mix, graph_hops=N)
    SDK-->>S: selected MIRL records + evidence ids
    S-->>G: transient JSONL memory
    G->>M: invoke with untrusted memory context
    M-->>G: assistant result
```

## Current post-turn path

```mermaid
sequenceDiagram
    participant G as GhostAgent
    participant S as SeamMemory
    participant SDK as SeamSDK
    participant DB as Canonical store

    G->>S: complete_turn(user, answer, ids)
    S->>SDK: ingest(completed turn)
    SDK->>DB: RAW + compiled MIRL + projections
    DB-->>SDK: stored record ids
    S->>SDK: finalize reasoning run
    SDK->>DB: outcome + evidence and knowledge refs
```

## Current versus planned

| Capability | Status | Evidence or destination |
|---|---|---|
| Synchronous root-agent turn | Current | `src/ghost/application.py` |
| Private SDK recall and MIRL ingest | Current | `src/ghost/seam_memory.py` |
| Verified action graph (decision → tool check → verified outcome) | Current | `SeamMemory.record_actions` |
| Injection-resistant transient recall | Current | `src/ghost/middleware.py` |
| Persistent LangGraph checkpoint | Current | `SqliteSaver` in `src/ghost/application.py` |
| Persistent checkpoint | Current | SQLite LangGraph checkpoint in `application.py` |
| Read-first tools | Current | memory recall, bounded file read and literal search |
| Opt-in shell control | Current | unsandboxed, approval/timeout/verification bounded |
| Frozen Stage 1 task qualification | Planned next | roadmap G1 exit gate |
| Selective memory admission | Planned | roadmap stage 2 |
| Correction and forgetting UX | Planned | roadmap stage 2 |
| Custom research/coding/verifier subagents | Planned | roadmap stage 3 |
| Authenticated service and UI | Planned | roadmap stage 4 |

## Dependency boundary

The private SEAM SDK stays in the SEAM repository. Ghost pins an exact private
SEAM revision and imports `SeamSDK`; Ghost contains only the adapter that maps
agent turns into SDK operations. This keeps MIRL migrations, retrieval, graph
projection, and storage contracts versioned with SEAM while allowing Ghost's
agent policy to evolve independently.

See [ADR-0001](../decisions/0001-seam-memory-boundary.md) for the durable
decision.
