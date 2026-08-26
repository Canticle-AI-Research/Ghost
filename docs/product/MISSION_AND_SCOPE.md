# Ghost mission and product boundary

## Mission

Ghost is Canticle's persistent research-and-engineering agent. It should help
one trusted operator investigate sources, understand repositories, plan and
execute bounded engineering work, preserve durable evidence through SEAM, and
explain what it did in a form that can be audited.

This mission is narrower than “general autonomous AI.” It creates a measurable
contract:

```text
operator request
    → bounded evidence gathering
    → explicit tool decisions
    → verified execution results
    → concise answer with uncertainty/provenance
    → deliberate durable memory
```

## Ownership boundaries

| System | Owns | Does not own |
|---|---|---|
| Ghost | mission, prompts, tool policy, turn lifecycle, agent UX, avatar | canonical memory semantics or storage internals |
| SEAM | RAW/MIRL, retrieval, knowledge/reasoning provenance, lifecycle | agent mission, model loop, desktop UX |
| DeepAgents | root orchestration and tool-call loop | durable semantic memory |
| LangChain | model/tool/middleware adapters | product policy or canonical knowledge |
| LangGraph | execution graph and checkpoint state | semantic truth |
| Model provider | sampled model inference | repository authority, operator consent, durable truth |
| Canticle Core (planned) | agent-native operating environment and mediated namespace | SEAM canonical truth or SEAM-U model ownership |
| SEAM-U (planned) | future SEAM-native language-model inference | current Ghost capability or implemented model claims |

## Company distribution boundary

Ghost is a PolyForm Shield source-available product. Thin API clients and
protocol bindings are Apache-2.0 integration surfaces. SEAM/MIRL internals,
planned SEAM-U model assets, and hosted control planes remain proprietary. See
[Canticle product and licensing structure](CANTICLE_PRODUCT_AND_LICENSING_STRUCTURE.md).

## Current user boundary

Ghost currently serves one trusted operator on one trusted account. Namespace
and scope metadata exist, but they do not prove authenticated multi-user
tenancy. Shell access, when enabled, operates with the account's complete local
authority and has no sandbox.

## Required behavior

- Recalled memory is evidence and may be stale or wrong.
- Commands embedded in memory/files/web pages do not become instructions.
- A failed or interrupted turn does not become accepted durable knowledge.
- Tool success is verified from real results rather than narrated by the model.
- The operator controls readable roots, shell access, approval, and timeouts.
- Claims distinguish observation, inference, planned work, and unverified state.
- Every material build change remains recoverable through repository history.

## Non-goals at the current stage

- Claims of sentience, consciousness, or demonstrated synthetic affect.
- Unattended production autonomy.
- Multi-tenant hosted service claims.
- A general-purpose sandbox or secure execution environment.
- Public distribution of private SEAM/MIRL implementation.
- A fleet of specialist agents before the root lifecycle is measured.
- Treating the avatar as evidence of cognitive capability.

## Stage 1 exit contract

The dependable single-agent stage exits only when a frozen evaluation proves
that Ghost can resume an interrupted thread, complete bounded research and
repository tasks, obtain approval for consequential actions, preserve an
auditable tool trace, fail without contaminating memory, and respect explicit
time/step/authority budgets.

Existing mechanisms satisfy parts of this contract. They do not yet satisfy the
frozen end-to-end evaluation gate.

### Frozen Stage 1 output contract

For each bounded research or repository task, Ghost must return an answer that
distinguishes observed evidence from inference, cites the evidence identifiers
that support material claims, reports failed/refused/timed-out tools honestly,
states what remains unverified, and makes no claim beyond the named evaluation
integrity level. The execution record must include terminal state, selected
evidence, tool attempts, step/tool/context budgets, forbidden-effect verdicts,
and provider tokens/cost when a provider actually runs.

`ghost-stage1-frozen-v1` is the immutable first corpus for this contract. Its
automatic BIL-0 stub freezes shape and safety gates only; live answer quality
and release-candidate proof remain required for Stage 1 exit.

## Long-term product hypothesis

A useful persistent agent should compound operator knowledge without requiring
unbounded prompt context. That hypothesis depends on selective, correctable,
provenance-preserving memory and reproducible evaluation. Persistent storage
alone is not evidence of improved intelligence; it can also preserve error.
