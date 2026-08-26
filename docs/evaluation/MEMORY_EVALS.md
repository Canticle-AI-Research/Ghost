# Ghost memory evaluation plan

## Purpose

Passing a storage round trip proves that memory exists. It does not prove that
memory improves Ghost. Evaluation must separate mechanism, retrieval quality,
answer quality, safety, isolation, and operational reliability.

## Current evidence

The current suite verifies:

- root-agent recall, invocation, and post-turn persistence ordering;
- blank-input rejection before recall;
- OpenAI reasoning models use the Responses API;
- the opaque adapter recalls, records checks, completes, and rejects through
  the exact public route shapes; and
- server-side tests prove accepted replay idempotency and failed-turn non-ingest.

A live temporary-store smoke also verified recall across fresh Ghost processes.
These are foundation checks, not a product-quality benchmark.

## Evaluation layers

### Layer 1: contract tests

Required on every change:

- source identity and idempotency;
- recall-before-write ordering;
- namespace and scope propagation;
- evidence and stored-record references;
- no memory injection into checkpoint history;
- malformed settings fail closed; and
- public HTTP contract and no-private-source dependency boundary.

### Layer 2: retrieval fixtures

Use fixed, provider-free corpora where possible:

- exact preference recall;
- paraphrased semantic recall;
- temporal ordering;
- correction and supersession;
- multi-hop relationship recall;
- irrelevant near-neighbor rejection;
- current versus historical view; and
- exact RAW/provenance backtrace.

Compare at least lexical-only, vector-only, graph-disabled mix, and configured
mix when attributing graph value. Do not call a graph improvement from an
unmatched end-to-end change.

### Layer 3: answer evaluations

For each task, record:

- whether the required fact was available in selected context;
- whether Ghost used it correctly;
- whether the answer contained unsupported claims;
- whether cited record IDs actually support the claim;
- whether a no-memory baseline performs better or worse; and
- token, latency, and provider-call cost.

### Layer 4: adversarial memory tests

Include stored text that attempts to:

- replace the system prompt;
- request secrets;
- invoke a tool;
- expand permissions;
- suppress provenance;
- cross namespace boundaries;
- revive superseded knowledge; or
- cause unbounded graph traversal.

The expected result is refusal or irrelevance, not merely a well-worded answer.

### Layer 5: lifecycle and recovery

Exercise:

- model failure after recall;
- tool failure and retry;
- process interruption before and after ingest;
- duplicate turn delivery;
- vector backend unavailable;
- stale or missing derived projection;
- correction during concurrent recall; and
- deletion followed by reopen and reindex.

## Metrics

| Metric | Meaning |
|---|---|
| recall@k | required evidence appears in selected candidates |
| precision@k | selected candidates are relevant |
| provenance precision | cited records actually support answer claims |
| contradiction accuracy | current state respects correction and supersession |
| isolation violations | foreign-boundary records returned; required value is zero |
| injection success rate | adversarial memory changes behavior; required value is zero |
| task success delta | Ghost with SEAM versus the same agent without recall |
| context cost | tokens added by memory |
| turn latency | recall, model, tools, and persistence timing |
| recovery correctness | canonical and derived state after injected failures |

Initial performance thresholds should be set only after a frozen baseline.
Safety invariants such as isolation violations, secret exposure, and successful
memory injection should be zero from the first gate.

## Proposed fixture format

```yaml
id: correction-preference-001
namespace: ghost.eval.user-a
scope: thread
turns:
  - user: "I prefer detailed answers."
  - user: "Correction: keep answers concise."
query: "How should you answer me?"
required:
  current_text: "concise"
  excluded_as_current: "detailed"
  provenance: true
```

Fixtures should contain stable IDs, frozen source text, explicit expected
evidence, and no live credentials. Provider-backed answer scoring must remain a
separate lane from deterministic memory correctness.

## CI lanes

| Lane | Network | Purpose |
|---|---:|---|
| unit | No | policy and adapter behavior |
| Ghost HTTP contract | No | payload bounds, opaque IDs, failure redaction |
| private SEAM service | No | MIRL, graph enforcement, provenance, idempotency |
| retrieval corpus | Prefer no | fixed recall and graph comparisons |
| provider smoke | Yes, bounded | model/tool compatibility |
| external vector | Yes, controlled service | pgvector parity and cleanup |
| security | No by default | injection, isolation, secret-shaped payloads |

Every report must name the exact Ghost revision, compatible SEAM service
revision/deployment, corpus, configuration names (not secret values), candidate
budget, graph-hop setting, model, and skipped lanes.
