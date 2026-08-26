# Ghost documentation index

This is the exhaustive active-document registry and authority map. The human
learning surface is [the Ghost engineering wiki](README.md).

## Authority order

1. Current code plus reproducible verification define implemented behavior.
2. `REPO_LEDGER.md` defines stable repository and architecture decisions.
3. ADRs define durable design decisions and their consequences.
4. `PROJECT_STATUS.md` and `status/CURRENT_STATE.md` define current state.
5. `HISTORY.md` defines immutable chronology; `HISTORY_INDEX.md` is derived.
6. This documentation explains and reconstructs those authorities without
   promoting plans into implementation claims.

## Core routes

| Document | Role | Status |
|---|---|---|
| [README.md](README.md) | wiki home and human learning routes | current |
| [GLOSSARY.md](GLOSSARY.md) | controlled project terminology | current |
| [product/MISSION_AND_SCOPE.md](product/MISSION_AND_SCOPE.md) | product identity and success boundary | governing |
| [product/CANTICLE_PRODUCT_AND_LICENSING_STRUCTURE.md](product/CANTICLE_PRODUCT_AND_LICENSING_STRUCTURE.md) | Ghost/SEAM/Canticle Core/SEAM-U product and license architecture | governing candidate |
| [product/REBUILD_BLUEPRINT.md](product/REBUILD_BLUEPRINT.md) | zero-to-working-system reconstruction | current |
| [status/CURRENT_STATE.md](status/CURRENT_STATE.md) | detailed checkout/remote/maturity state | current |
| [roadmap/SECOND_BRAIN_ROADMAP.md](roadmap/SECOND_BRAIN_ROADMAP.md) | dependency-ordered roadmap and gates | current |

## Architecture

| Document | Covers |
|---|---|
| [architecture/COMPLETE_SYSTEM_BLUEPRINT.md](architecture/COMPLETE_SYSTEM_BLUEPRINT.md) | every major component and end-to-end ASCII flows |
| [architecture/RUNTIME_LAYERS.md](architecture/RUNTIME_LAYERS.md) | service, lifecycle, adapter, interface separation |
| [architecture/SEAM_HTTP_CONTRACT.md](architecture/SEAM_HTTP_CONTRACT.md) | exact opaque turn/recall routes, payloads, errors, and proof split |
| [architecture/SYSTEM_MAP.md](architecture/SYSTEM_MAP.md) | framework and data-flow map |
| [architecture/MEMORY_LAYERS.md](architecture/MEMORY_LAYERS.md) | RAW/MIRL/derived/checkpoint ownership |
| [architecture/KNOWLEDGE_GRAPH.md](architecture/KNOWLEDGE_GRAPH.md) | knowledge, reasoning, and execution graphs |
| [architecture/AVATAR_SYSTEM.md](architecture/AVATAR_SYSTEM.md) | local desktop-avatar architecture and status |
| [concepts/SECOND_BRAIN.md](concepts/SECOND_BRAIN.md) | second-brain definition and limits |

## Operations and commands

| Document | Covers |
|---|---|
| [operations/INSTALLATION.md](operations/INSTALLATION.md) | prerequisites, public install, service setup, smoke tests, troubleshooting |
| [operations/COMMAND_REFERENCE.md](operations/COMMAND_REFERENCE.md) | every runtime, verification, continuity, brand, and local-avatar command |
| [operations/HOW_TO.md](operations/HOW_TO.md) | task-oriented operator recipes |
| [operations/CONFIGURATION.md](operations/CONFIGURATION.md) | every environment variable and precedence rule |
| [operations/MEMORY_LIFECYCLE.md](operations/MEMORY_LIFECYCLE.md) | recall, execution, ingest, verified outcome, failure |
| [operations/NAMESPACE_AND_SCOPE.md](operations/NAMESPACE_AND_SCOPE.md) | boundaries and non-tenancy caveat |
| [operations/DEVELOPMENT_WORKFLOW.md](operations/DEVELOPMENT_WORKFLOW.md) | code/docs/history workflow that prevents drift |
| [operations/AGENT_HARNESSES.md](operations/AGENT_HARNESSES.md) | running Ghost's persona across Claude, Codex, Grok, and Antigravity |
| [operations/RELEASE_AND_DEPLOYMENT.md](operations/RELEASE_AND_DEPLOYMENT.md) | build, package, release, runner, deployment gates |

## Security and trust

| Document | Covers |
|---|---|
| [security/TRUST_BOUNDARIES.md](security/TRUST_BOUNDARIES.md) | model, memory, filesystem, tool, provider, output boundaries |
| [security/PUBLIC_REPOSITORY_AND_RUNNER.md](security/PUBLIC_REPOSITORY_AND_RUNNER.md) | enforced public/private runner boundary and evidence |
| [decisions/0001-seam-memory-boundary.md](decisions/0001-seam-memory-boundary.md) | SEAM is the only semantic memory owner |
| [decisions/0002-canonical-build-history.md](decisions/0002-canonical-build-history.md) | append-only repository continuity decision |
| [decisions/0003-documentation-is-the-blueprint.md](decisions/0003-documentation-is-the-blueprint.md) | code/documentation co-change contract |
| [decisions/0004-open-edge-shielded-product-proprietary-core.md](decisions/0004-open-edge-shielded-product-proprietary-core.md) | Apache edge, PolyForm products, proprietary core decision |
| [decisions/0005-opaque-seam-service-boundary.md](decisions/0005-opaque-seam-service-boundary.md) | public Ghost transport with server-owned reasoning and opaque IDs |

## Legal and company readiness

| Document | Covers |
|---|---|
| [legal/README.md](legal/README.md) | legal/company documentation router and limitation |
| [legal/LICENSING_STRUCTURE.md](legal/LICENSING_STRUCTURE.md) | repository-by-repository placement and license mechanics |
| [legal/COMPANY_IP_READINESS.md](legal/COMPANY_IP_READINESS.md) | founder IP assignment, contributors, trademarks, models, provenance |
| [legal/COMMERCIAL_TERMS_CHECKLIST.md](legal/COMMERCIAL_TERMS_CHECKLIST.md) | product, API, enterprise, and research contracts to prepare |

## Evaluation

| Document | Covers |
|---|---|
| [evaluation/MEMORY_EVALS.md](evaluation/MEMORY_EVALS.md) | planned memory-quality fixtures and measures |
| [evaluation/STAGE1_FROZEN_SUITE.md](evaluation/STAGE1_FROZEN_SUITE.md) | frozen 20-case corpus, BIL-0 bundle/verifier/gate, commands, and live successor boundary |
| [evaluation/TESTING_AND_QUALIFICATION.md](evaluation/TESTING_AND_QUALIFICATION.md) | test lanes, exact commands, evidence meanings, release gates |

## Continuity and evidence

| Document | Covers |
|---|---|
| [history/REPOSITORY_CONTINUITY.md](history/REPOSITORY_CONTINUITY.md) | Temporal Chain history/index/snapshot/handoff model and commands |
| [history/PATH_MOVES.md](history/PATH_MOVES.md) | ledger that keeps immutable history refs resolvable after a rename |
| [Temporal Chain template](../templates/temporal-chain/README.md) | reusable standard-library history + git protocol starter for other repositories |
| [handoffs/INDEX.md](handoffs/INDEX.md) | canonical single-head handoff registry |
| [handoffs/2026-08-25-stage1-candidate-ready.md](handoffs/2026-08-25-stage1-candidate-ready.md) | current exact-head CI publication boundary for Stage 1 evaluation |
| [handoffs/2026-08-25-stage1-final-baseline-qualified.md](handoffs/2026-08-25-stage1-final-baseline-qualified.md) | superseded post-review clean-source Stage 1 baseline boundary |
| [handoffs/2026-08-25-stage1-review-repaired.md](handoffs/2026-08-25-stage1-review-repaired.md) | superseded Stage 1 evaluation review-repair boundary |
| [handoffs/2026-08-25-stage1-lifecycle-baseline-qualified.md](handoffs/2026-08-25-stage1-lifecycle-baseline-qualified.md) | superseded clean-source lifecycle-executing BIL-0 baseline boundary |
| [handoffs/2026-08-25-stage1-lifecycle-smoke-repaired.md](handoffs/2026-08-25-stage1-lifecycle-smoke-repaired.md) | superseded real-lifecycle BIL-0 smoke repair boundary |
| [handoffs/2026-08-25-stage1-baseline-frozen.md](handoffs/2026-08-25-stage1-baseline-frozen.md) | superseded initial clean-source BIL-0 baseline boundary |
| [handoffs/2026-08-25-stage1-frozen-evals-qualified.md](handoffs/2026-08-25-stage1-frozen-evals-qualified.md) | superseded locally qualified Stage 1 frozen-evaluation boundary |
| [handoffs/2026-08-25-public-seam-transport-published.md](handoffs/2026-08-25-public-seam-transport-published.md) | superseded protected-main public-transport boundary |
| [handoffs/2026-08-25-public-seam-transport-ci-repaired.md](handoffs/2026-08-25-public-seam-transport-ci-repaired.md) | superseded exact-head public-CI repair boundary |
| [handoffs/2026-08-25-public-seam-transport-qualified.md](handoffs/2026-08-25-public-seam-transport-qualified.md) | superseded locally qualified public-transport boundary |
| [handoffs/2026-08-25-canonical-foundation-merged.md](handoffs/2026-08-25-canonical-foundation-merged.md) | superseded merged-foundation and public-API resume boundary |
| [handoffs/2026-08-25-canonical-foundation-candidate.md](handoffs/2026-08-25-canonical-foundation-candidate.md) | superseded isolated canonical-foundation publication boundary |
| [handoffs/2026-08-25-public-runner-closed.md](handoffs/2026-08-25-public-runner-closed.md) | superseded safety closure and foundation-publication boundary |
| [handoffs/2026-08-25-temporal-chain-named.md](handoffs/2026-08-25-temporal-chain-named.md) | superseded Temporal Chain naming and documentation-gate candidate |
| [handoffs/2026-08-25-company-licensing-foundation.md](handoffs/2026-08-25-company-licensing-foundation.md) | superseded company licensing and product-boundary candidate |
| [handoffs/2026-08-25-continuity-template-integrated.md](handoffs/2026-08-25-continuity-template-integrated.md) | superseded reusable-continuity and workflow safety candidate boundary |
| [handoffs/2026-08-25-public-runner-next.md](handoffs/2026-08-25-public-runner-next.md) | superseded runner-safety predecessor |
| [handoffs/2026-08-25-documentation-foundation.md](handoffs/2026-08-25-documentation-foundation.md) | locally qualified documentation predecessor |
| [handoffs/2026-08-21-desktop-pet.md](handoffs/2026-08-21-desktop-pet.md) | registered predecessor avatar boundary |
| [audits/INDEX.md](audits/INDEX.md) | dated audit registry |
| [audits/2026-08-25-public-runner-safety-closure.md](audits/2026-08-25-public-runner-safety-closure.md) | exact merge, hosted-run, settings, and runner-boundary evidence |
| [audits/2026-08-25-company-licensing-architecture.md](audits/2026-08-25-company-licensing-architecture.md) | placement, ownership, and adjacent-product licensing evidence |
| [audits/2026-08-25-repository-documentation-reconciliation.md](audits/2026-08-25-repository-documentation-reconciliation.md) | current repository/documentation evidence |
| [updates/README.md](updates/README.md) | landed-change report policy |
| [updates/2026-08-19-ci-and-test-coverage.md](updates/2026-08-19-ci-and-test-coverage.md) | CI and initial defect report |
| [updates/2026-08-19-verified-action-graph.md](updates/2026-08-19-verified-action-graph.md) | verified action graph report |
| [updates/2026-08-19-operating-system-control.md](updates/2026-08-19-operating-system-control.md) | shell-control report |
| [updates/2026-08-21-desktop-pet-handoff.md](updates/2026-08-21-desktop-pet-handoff.md) | detailed local avatar handoff |
| [updates/2026-08-25-canonical-foundation.md](updates/2026-08-25-canonical-foundation.md) | merged wiki, history, Temporal Chain, licensing, and launcher foundation |
| [updates/2026-08-25-public-runner-safety.md](updates/2026-08-25-public-runner-safety.md) | merged public/private CI safety change |
| [updates/2026-08-25-stage1-status-correction.md](updates/2026-08-25-stage1-status-correction.md) | append-only correction of Stage 1 completion claim |

## Local avatar specification

| Document | Covers | State |
|---|---|---|
| [superpowers/specs/2026-08-21-desktop-avatar.md](superpowers/specs/2026-08-21-desktop-avatar.md) | v1 face/motion/IPC behavior | local design, not merged |

## Maintenance rule

No Markdown page under `docs/` is allowed to float unregistered. Every new page
must appear in this file and every relative link must resolve. This index is the
sole self-evident exception because it is the registry itself. Run:

```bash
uv run pytest tests/test_docs.py -q
uv run python -m tools.history.verify_continuity
```
