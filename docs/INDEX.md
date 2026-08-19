# Ghost documentation map

This index is the canonical entry point for Ghost documentation. It separates
implemented behavior from intended architecture and future work so a roadmap
idea cannot be mistaken for a shipped capability.

## Status language

- **Current**: present in Ghost code and covered by local verification.
- **Governing**: inherited from the private SEAM/MIRL contracts and treated as
  an architectural invariant.
- **Planned**: an approved direction that is not implemented yet.
- **Exploratory**: a possibility that still needs a decision or evidence.

## Choose a route

| Question | Document |
|---|---|
| Is a second brain the same as a knowledge graph? | [Second brain and knowledge graph](concepts/SECOND_BRAIN.md) |
| What do the core terms mean? | [Glossary](GLOSSARY.md) |
| How do Ghost, DeepAgents, LangChain, LangGraph, and SEAM fit together? | [System map](architecture/SYSTEM_MAP.md) |
| Where does truth live, and what is rebuildable? | [Memory layers](architecture/MEMORY_LAYERS.md) |
| How are the three different graphs separated? | [Knowledge graph](architecture/KNOWLEDGE_GRAPH.md) |
| What happens before, during, and after a turn? | [Memory lifecycle](operations/MEMORY_LIFECYCLE.md) |
| How should users, workspaces, projects, and threads be isolated? | [Namespace and scope](operations/NAMESPACE_AND_SCOPE.md) |
| What must never be trusted or silently promoted? | [Trust boundaries](security/TRUST_BOUNDARIES.md) |
| How will memory quality and safety be measured? | [Memory evaluations](evaluation/MEMORY_EVALS.md) |
| What should be built next, and in what order? | [Second-brain roadmap](roadmap/SECOND_BRAIN_ROADMAP.md) |
| Why does SEAM own memory while Ghost owns policy? | [ADR-0001](decisions/0001-seam-memory-boundary.md) |
| What actually changed, and when? | [Ghost updates](updates/README.md) |
| What landed on 2026-08-19? | [CI, three defects, and the memory boundary](updates/2026-08-19-ci-and-test-coverage.md) |
| How does a turn become a verified graph? | [Verified action graph](updates/2026-08-19-verified-action-graph.md) |

## Current implementation map

| Concern | Current source | Current state |
|---|---|---|
| Turn lifecycle (framework-free) | `src/ghost/lifecycle.py` | Recall, execution, completion and failure finalization |
| Agent adapter | `src/ghost/application.py` | DeepAgents, model wiring, persistent checkpoint |
| Private SEAM adapter | `src/ghost/seam_memory.py` | Reasoning retrieval, MIRL ingest, evidence-linked outcome |
| Transient context injection | `src/ghost/middleware.py` | Retrieved memory is untrusted data and is not checkpointed |
| Runtime settings | `src/ghost/config.py` | Model, database, namespace, scope, recall budget, graph hops |
| Invocation context | `src/ghost/context.py` | Per-turn recalled-memory payload |
| Read-only tools | `src/ghost/tools.py` | Memory recall, bounded file read and search; no write path |
| Operator interface | `src/ghost/cli.py` | One-shot and interactive terminal use |
| Verification | `tests/` | Agent lifecycle, Responses API routing, MIRL round trip, idempotency |

## Authority and conflict handling

1. The private SEAM specification and MIRL contract govern memory semantics.
2. Ghost source code is the evidence for what Ghost currently does.
3. This documentation describes the intended integration and must label
   anything not implemented as planned or exploratory.
4. If code and documentation disagree, report the discrepancy. Do not silently
   reinterpret current behavior to match prose.
5. The knowledge graph, vector indexes, PACK, and views never replace canonical
   RAW/MIRL truth.

## Documentation maintenance

When work lands, record it in [`updates/`](updates/README.md) — that
directory is Ghost's provenance track, and its reports are append-only.

Every new Markdown document under `docs/` must be linked from this index.
Relative links are verified by `tests/test_docs.py`. Architectural changes
should update the relevant concept or architecture document and, when they
change a durable boundary, add or supersede an ADR.

