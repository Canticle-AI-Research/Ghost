# Ghost and SEAM glossary

## Agent and orchestration terms

### Ghost

The Canticle research-and-engineering DeepAgent in this repository. Ghost owns
agent policy, tool selection, user interaction, and the turn lifecycle. It does
not own the SEAM memory implementation.

### DeepAgents

The higher-level agent framework used to construct Ghost. It provides an agent
loop, planning support, working-file behavior, and a route to specialist
subagents.

### LangChain

The model and middleware integration layer. Ghost uses it to initialize the
configured model and to inject recalled SEAM evidence into model requests.

### LangGraph

The execution graph underneath Ghost. It controls state transitions, tool
loops, checkpoints, interruption, and resumption. LangGraph state is execution
state, not durable semantic knowledge.

### Checkpoint

A snapshot of agent execution state used to resume a thread or interrupted
workflow. A checkpoint may contain messages and graph state. It should not be
treated as the long-term second brain.

### Subagent

A specialist agent delegated a bounded multi-step task. Subagents are planned;
Ghost currently has no custom specialist definitions.

## Memory terms

### Second brain

The complete system that captures experience, preserves evidence, organizes
meaning, retrieves relevant context, reconciles corrections, and helps an agent
act. A second brain may use a knowledge graph, but it is not only a graph.

### SEAM

Semantic Encoding for Agent Memory. The private memory runtime and language
used by Ghost for canonical memory, retrieval, provenance, graph projection,
and bounded context.

### MIRL

SEAM's canonical memory intermediate representation. MIRL records preserve
semantic meaning, typed relationships, time, status, and routes back to source
evidence.

### RAW

Verbatim source material such as a conversation turn or document. RAW preserves
phrasing and exact evidence.

### IR

Canonical semantic intermediate representation. In Ghost's SEAM integration,
MIRL is the working IR that preserves normalized meaning.

### PACK

A bounded, task-relevant context projection derived from canonical memory.
PACK is disposable and regenerable; it is not durable truth.

### LENS

A task-specific view over memory, such as a project, user-preference, temporal,
or debugging view. A lens shapes retrieval and packing without becoming a new
truth store.

### Canonical truth

The durable record against which derived indexes and views are rebuilt. For
Ghost's memory system, RAW and MIRL are canonical. The knowledge graph and
vector indexes are derived projections.

### Memory admission

The policy that decides whether an observation should become durable memory,
what kind of memory it is, and what evidence and trust state it carries. Ghost
implements deterministic `admit`, `reject`, and `review` decisions; only admit
causes SEAM ingest.

### Recall

Retrieval of bounded, relevant memory for a task. Recall is not the same as
loading a full conversation transcript.

### Provenance

The route from a remembered claim or state back to the source records and
evidence that support it.

### Reconciliation

The process of preserving corrections, contradictions, supersession, and
resolved current state without silently overwriting history.

## Graph terms

### Knowledge graph

A derived network of entities, claims, events, states, values, sources, and
typed relationships projected from canonical MIRL. It answers questions about
what is known and how facts relate.

### Reasoning graph

A bounded, auditable graph of objectives, evidence references, decisions,
verifications, and outcomes. It records public justification, never hidden
chain-of-thought, and cannot promote itself into MIRL.

### Execution graph

The LangGraph control flow that runs Ghost. It answers what the agent should do
next, not what the world contains.

### Vector index

A derived semantic-search index over canonical memory units. It improves
similarity retrieval but is not a canonical store.

## Repository and evidence terms

### Implemented

Present in source code. This does not imply the change is committed, pushed,
merged, released, deployed, or qualified.

### Landed

Reachable from the default `main` branch at a named commit. Landed behavior may
still lack a green exact-head CI run or release qualification.

### Exact-head verification

Verification whose recorded source SHA exactly matches the candidate being
judged. A result from an ancestor or a dirty descendant is not exact-head.

### Temporal chain

The SEAM-derived protocol that governs how a repository records build history
and how git work is conducted around it. The chain is the ordered, verified
sequence of history entries and handoffs: each entry follows the last, each
handoff supersedes exactly one predecessor, and the derived index is rebuilt
from the chain rather than maintained beside it. Ghost runs the chain natively
and ships it as the repository-neutral
[Temporal Chain template](../templates/temporal-chain/README.md).

### Canonical build history

Ghost's append-only `HISTORY.md` event stream: intent, state boundary,
verification, failures, refs, and supersession. Git remains the byte-level diff
authority; history is the temporal and operational authority.

### History index

The generated `HISTORY_INDEX.md` route map. It is derived from canonical
history and can be regenerated. It intentionally omits full event bodies.

### Handoff

A tracked recovery document registered in `docs/handoffs/INDEX.md`. Ghost has
one current handoff head and one linear supersession chain; an unregistered
dated note is not a canonical handoff.

### Snapshot

An ignored, bounded local recovery JSON containing Git identity, dirty-path
names, recent history labels, and current handoff. It is not a source archive
or public evidence artifact.

### Blueprint

The code-coupled documentation required to reconstruct and operate Ghost:
architecture, installation, commands, configuration, how-tos, trust,
evaluation, roadmap, history, and current state.

### Qualification

Evidence that a named implementation satisfies a declared gate under exact
fixtures, commands, dependencies, models, budgets, and boundaries. A demo is
not qualification.

## Company and distribution terms

### Canticle Core

The planned agent-native operating environment on Linux using Ghost mediation
and SEAM truth. It is an architecture scaffold, not an implemented OS.

### SEAM-U

The approved name for the planned first SEAM-native language model. No
implemented or qualified model is currently recorded.

### Open integration edge

Apache-2.0 thin clients, protocols, examples, and connectors that contain no
private implementation.

### Source-available product

Source distributed with use restrictions. Ghost, Canticle Core, and
source-distributed SDK/node products use PolyForm Shield.

### PolyForm Shield

A source-available license permitting use, modification, and redistribution for
purposes other than providing competing products under its exact terms. It is
not an OSI-approved open-source license.

### Proprietary core

Undistributed SEAM/MIRL internals, SEAM-U assets, cloud control planes,
confidential data, and other All Rights Reserved material.

### Commercial license

A separate written grant that may authorize rights not provided by PolyForm
Shield, such as competing, OEM, or enterprise delivery.
