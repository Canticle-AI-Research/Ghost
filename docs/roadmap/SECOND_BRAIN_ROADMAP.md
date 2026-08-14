# Ghost second-brain roadmap

This roadmap orders work by dependency. Later stages should not be treated as
complete because a demo exists; each stage has an explicit exit condition.

## Stage 0: verified memory spine

**Status: Current**

Delivered:

- DeepAgents/LangChain/LangGraph root agent;
- private, exact-revision SEAM dependency;
- pre-turn mixed recall with graph expansion;
- transient memory middleware;
- successful-turn MIRL ingest;
- reasoning outcome with evidence and knowledge references;
- CLI, configuration, isolated tests, build, and live smoke.

Boundary: this is a working prototype, not a complete second brain.

## Stage 1: dependable single agent

**Status: Planned next**

Build:

1. one precise Ghost mission and output contract;
2. persistent SQLite LangGraph checkpoints;
3. bounded research, repository/document, and memory-inspection tools;
4. tool permissions, timeouts, retry limits, and maximum steps;
5. explicit failed-run finalization; and
6. streaming and cancellation behavior.

Exit condition: Ghost can resume an interrupted thread and complete a bounded
research task with an auditable tool trace and no unbounded action surface.

## Stage 2: deliberate memory

**Status: Planned**

Build:

1. memory-candidate classification;
2. selective admission instead of storing every successful turn;
3. explicit remember, correct, and forget operations;
4. current/historical retrieval UX;
5. user/workspace/project partitioning; and
6. user-visible provenance references.

Exit condition: fixed evaluations prove relevant recall, corrections,
idempotency, and zero cross-boundary leakage.

## Stage 3: graph-aware specialists

**Status: Planned**

Build only after the root lifecycle is reliable:

- research specialist for source discovery and evidence extraction;
- coding specialist for bounded repository work;
- verifier specialist for tests, citations, and contradiction checks;
- synthesis policy that reconciles specialist outputs; and
- scoped graph inspection tools that resolve every path to MIRL/RAW evidence.

Exit condition: specialists improve frozen task success over the single-agent
baseline without weakening permissions, provenance, or isolation.

## Stage 4: measured product

**Status: Exploratory until earlier gates pass**

Potential work:

- authenticated API and streaming interface;
- operator UI for memory, sources, corrections, and pending admission;
- principal-aware tenancy;
- managed checkpoints, backup, restore, and projection migration;
- tracing, latency, cost, and memory-quality dashboards;
- private dependency and secret management in CI/deployment; and
- release, upgrade, rollback, and incident procedures.

Exit condition: production-readiness review passes security, recovery,
isolation, migration, observability, and rollback gates on the exact release
candidate.

## Recommended immediate slice

The next implementation should remain deliberately small:

1. define Ghost's mission as a Canticle research-and-engineering agent;
2. add a persistent checkpoint;
3. add three read-first tools;
4. add controlled failure finalization;
5. create the first 20 frozen memory and task fixtures; and
6. establish CI for unit, private-SDK integration, docs, and secret scanning.

Do not add a fleet of specialists before this slice is reliable. A subagent is
appropriate for a bounded multi-step capability; a single action remains a
tool, and durable context remains a SEAM memory concern.

