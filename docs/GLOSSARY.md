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
currently ingests every successful root turn; selective admission is planned.

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

