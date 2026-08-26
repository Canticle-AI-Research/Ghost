# ADR-0001: SEAM owns memory; Ghost owns agent policy

- Status: Accepted; transport amended by ADR-0005
- Date: 2026-08-14

## Context

Ghost needs durable semantic memory, graph-assisted retrieval, provenance, and
future correction/lifecycle behavior. DeepAgents also provides working-file and
store abstractions, while LangGraph provides checkpoints. Treating any one of
these as interchangeable would blur canonical knowledge, execution state, and
temporary agent workspace.

The private SEAM SDK already owns MIRL compilation, canonical storage,
retrieval, graph projection, lifecycle contracts, and reasoning records. Ghost
needs a product-specific policy for when to recall, what to inject, what to
remember, which tools may act, and how users interact with the agent.

## Decision

1. The canonical private SDK remains in the SEAM repository.
2. Ghost consumes SEAM through the transport selected by the current boundary ADR.
3. Ghost owns a thin `SeamMemory` adapter that maps agent turns to that boundary.
4. RAW and MIRL are canonical memory truth.
5. Knowledge graph, vector, lexical, PACK, and lens data are derived or bounded
   projections and must remain traceable to canonical records.
6. LangGraph checkpoints store execution state, not long-term semantic truth.
7. DeepAgents working files and future stores do not replace SEAM memory.
8. Ghost owns memory-admission and tool policies but implements them through
   supported SEAM HTTP API operations rather than direct storage mutation.

## Consequences

Positive:

- one source of truth for MIRL and migrations;
- independent Ghost and SEAM release decisions;
- exact dependency qualification;
- clearer tests and failure boundaries; and
- no copied private runtime code in the agent repository.

Costs:

- SEAM service availability is a runtime dependency;
- contract upgrades require explicit cross-repository compatibility tests; and
- coordinated server/client changes must land without copying private code.

## Rejected alternatives

### Copy the SDK into Ghost

Rejected because it creates duplicate MIRL, migration, retrieval, and lifecycle
implementations that can drift.

### Use LangGraph checkpoints as long-term memory

Rejected because checkpoints preserve execution state and message history, not
canonical semantic meaning, provenance, correction, or graph projections.

### Make the knowledge graph the canonical store

Rejected because graph topology cannot by itself preserve exact RAW evidence,
all MIRL semantics, or safe rebuild/versioning behavior.

### Put Ghost policy inside SEAM

Rejected because agent mission, tools, UI, and admission policy are
application-specific and should not redefine the general memory runtime.
