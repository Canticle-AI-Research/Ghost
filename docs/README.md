# Ghost engineering wiki

This wiki is the rebuildable blueprint for Ghost: what it is, how every layer
fits together, how to install and operate it, how to verify it, and how the
repository preserves a complete canonical build history.

The wiki distinguishes four kinds of claim:

- **landed** — reachable from `main`;
- **local** — present only in a working tree or unmerged branch;
- **planned** — approved direction without an implementation claim; and
- **exploratory** — a possible design that still needs evidence or a decision.

## Start here

| Goal | Route |
|---|---|
| Understand what Ghost is | [Mission and product boundary](product/MISSION_AND_SCOPE.md) |
| Understand company licensing | [Canticle product and licensing structure](product/CANTICLE_PRODUCT_AND_LICENSING_STRUCTURE.md) |
| Prepare the company IP boundary | [Company IP readiness](legal/COMPANY_IP_READINESS.md) |
| See the whole system | [Complete system blueprint](architecture/COMPLETE_SYSTEM_BLUEPRINT.md) |
| Rebuild Ghost from an empty machine | [Installation](operations/INSTALLATION.md) then [rebuild blueprint](product/REBUILD_BLUEPRINT.md) |
| Run Ghost | [Command reference](operations/COMMAND_REFERENCE.md) and [operator how-tos](operations/HOW_TO.md) |
| Launch Ghost in another agent client | [Agent harnesses](operations/AGENT_HARNESSES.md) |
| Configure models, memory, tools, or shell | [Configuration](operations/CONFIGURATION.md) |
| Develop or change Ghost | [Development workflow](operations/DEVELOPMENT_WORKFLOW.md) |
| Reproduce the frozen Stage 1 evaluation | [Stage 1 frozen suite](evaluation/STAGE1_FROZEN_SUITE.md) |
| Understand current state | [Current state](status/CURRENT_STATE.md) |
| See what comes next | [Roadmap](roadmap/SECOND_BRAIN_ROADMAP.md) |
| Recover interrupted work | [Handoff registry](handoffs/INDEX.md) |
| Audit the build history | [History index](../HISTORY_INDEX.md) and [continuity protocol](history/REPOSITORY_CONTINUITY.md) |

## System map

```text
┌────────────────────────────── operator boundary ──────────────────────────────┐
│                                                                               │
│  terminal / future UI / local experimental avatar                             │
│          │                                                                    │
│          ▼                                                                    │
│  ┌─────────────────┐      ┌───────────────────────────────────────────────┐   │
│  │ Ghost interface │─────►│ DeepAgent adapter                            │   │
│  │ CLI; avatar WIP │      │ model + middleware + tools + checkpoints     │   │
│  └─────────────────┘      └──────────────────────┬────────────────────────┘   │
│                                                  │ framework-free turn         │
│                                                  ▼ contract                    │
│                             ┌───────────────────────────────────────────────┐  │
│                             │ recall → execute → verify → ingest/fail      │  │
│                             └──────────────────────┬────────────────────────┘  │
│                                                    │ authenticated HTTP         │
│                                                    ▼                            │
│                             ┌───────────────────────────────────────────────┐  │
│                             │ SEAM                                         │  │
│                             │ RAW/MIRL + retrieval + provenance + graphs   │  │
│                             └───────────────────────────────────────────────┘  │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
```

Ghost owns agent policy and experience. SEAM owns durable knowledge. LangGraph
checkpoints remember where a conversation got to; they are not semantic memory.

## Blueprint domains

### Product and architecture

- [Mission and scope](product/MISSION_AND_SCOPE.md)
- [Rebuild blueprint](product/REBUILD_BLUEPRINT.md)
- [Canticle product and licensing structure](product/CANTICLE_PRODUCT_AND_LICENSING_STRUCTURE.md)
- [Complete system blueprint](architecture/COMPLETE_SYSTEM_BLUEPRINT.md)
- [Runtime layers](architecture/RUNTIME_LAYERS.md)
- [Ghost-SEAM HTTP contract](architecture/SEAM_HTTP_CONTRACT.md)
- [System map](architecture/SYSTEM_MAP.md)
- [Memory layers](architecture/MEMORY_LAYERS.md)
- [Knowledge and reasoning graphs](architecture/KNOWLEDGE_GRAPH.md)
- [Bounded specialist contract](architecture/SPECIALIST_CONTRACT.md)
- [Avatar system](architecture/AVATAR_SYSTEM.md)

### Installation and operation

- [Installation](operations/INSTALLATION.md)
- [Every command](operations/COMMAND_REFERENCE.md)
- [How-to recipes](operations/HOW_TO.md)
- [Configuration](operations/CONFIGURATION.md)
- [Memory lifecycle](operations/MEMORY_LIFECYCLE.md)
- [Namespace and scope](operations/NAMESPACE_AND_SCOPE.md)
- [Agent harnesses and launchers](operations/AGENT_HARNESSES.md)
- [Development and documentation workflow](operations/DEVELOPMENT_WORKFLOW.md)
- [Release and deployment boundaries](operations/RELEASE_AND_DEPLOYMENT.md)
- [Recovery, health, and observability](operations/RECOVERY_AND_OBSERVABILITY.md)

### Safety and evidence

- [Trust boundaries](security/TRUST_BOUNDARIES.md)
- [Public repository and runner](security/PUBLIC_REPOSITORY_AND_RUNNER.md)
- [Opaque SEAM service decision](decisions/0005-opaque-seam-service-boundary.md)
- [Memory evaluations](evaluation/MEMORY_EVALS.md)
- [Testing and qualification](evaluation/TESTING_AND_QUALIFICATION.md)
- [Roadmap](roadmap/SECOND_BRAIN_ROADMAP.md)
- [Licensing structure](legal/LICENSING_STRUCTURE.md)
- [Company IP readiness](legal/COMPANY_IP_READINESS.md)
- [Commercial terms checklist](legal/COMMERCIAL_TERMS_CHECKLIST.md)

### Continuity

- [Repository continuity](history/REPOSITORY_CONTINUITY.md)
- [Temporal Chain template](../templates/temporal-chain/README.md)
- [Current status](../PROJECT_STATUS.md)
- [Stable ledger](../REPO_LEDGER.md)
- [Build history](../HISTORY.md)
- [Bounded history index](../HISTORY_INDEX.md)
- [Handoffs](handoffs/INDEX.md)
- [Audits](audits/INDEX.md)
- [Dated implementation updates](updates/README.md)

## Wiki maintenance contract

Every behavior change must update the relevant blueprint, command reference,
how-to, tests/qualification page, and roadmap/history status in the same pull
request. `tests/test_docs.py` enforces reachability and local links;
`tests/test_history_tools.py` enforces chronology, index, and handoffs. The
repository workflow is specified in [development workflow](operations/DEVELOPMENT_WORKFLOW.md).

The exhaustive file-by-file registry is [`docs/INDEX.md`](INDEX.md). This page
is the human route; the index is the machine-audited inventory.
