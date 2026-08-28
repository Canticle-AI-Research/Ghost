# Current state: 2026-08-27

This report separates landed source, local work, remote state, verification,
and roadmap maturity. `PROJECT_STATUS.md` is the compact router to this page.

## Repository state

| Plane | Observed state |
|---|---|
| Default branch | protected `main`; use live Git reconciliation for its moving head |
| GTOOL-001 implementation merge | `ba68c3852a1787efd568d3e221c2935f5a9af4b7` through PR #21 |
| GTOOL-002 implementation merge | `783964699d93c12725c7f91bdccf2bb1ecfcd008` through PR #24 |
| Publication record | GTOOL-002 closeout merged through PR #25; protected `main@9abbff12e722f88b42347791e8dc8c261c35f28f` |
| Stage 1 evaluation substrate | merged through PR #10: 20 frozen cases, real-lifecycle BIL-0 smoke/verifier/gate, step ceiling, final clean baseline |
| Public transport | merged through PR #8; public install and opaque transport source published |
| Primary working branch | `agent/avatar-u1-temporal-integration`, preserving avatar-only WIP on its earlier reviewed base |
| Canonical foundation | merged through PRs #6 and #7 |
| Preserved local work | avatar source/tests/assets/tools plus CLI/package/lock changes in the primary checkout |
| Remote visibility | public |
| Relevant current merges | GTOOL-001 PR #21 and GTOOL-002 PR #24 |
| Open PRs | Dependabot #2, #4, and #16 through #20 |
| Exact GTOOL-002 CI | source run `33125003964` and merge-head run `33125085772` green; all six required jobs passed |
| Final publication CI | exact `main@9abbff1` run `33125372170` green; all six required jobs passed |
| Action-provenance implementation | PR #26 exact source `21782f5024897e89dfb4d8f25369a2cc59999ea8`; implementation merge `2a85aab6e0696ef64844e80ade70fe75628e9634` |
| Exact action-provenance CI | source run `33133873076` and merge-head run `33133921906` green; all six required jobs passed |
| Structural audit | remediation ledger merged through PR #21 |
| GTOOL-001 | search containment merged through PR #21; exact PR and merge-head CI passed |
| GTOOL-002 | typed shell-result truth merged through PR #24; exact PR and merge-head CI passed |
| GitHub security automation | secret scanning/push protection enabled; dependency security updates disabled; no code-scanning analysis |
| Public transport proof | 200 provider-free tests, Ruff, build, clean wheel install, real `ghost --help`, and protected PR/main CI passed; 8 live tests deselected |

This is a status snapshot, not authorization to delete or combine local files.

## Landed capability through implementation merge `7839646`

- DeepAgents root agent with provider routing through LangChain.
- OpenAI reasoning-model use through the Responses API.
- Independently authored `httpx` adapter for the opaque public SEAM lifecycle;
  no private package or Git source is installed.
- Framework-free lifecycle and framework-specific adapter separation.
- Pre-turn mixed SEAM recall with graph expansion.
- Transient, escaped, bounded MIRL context injection.
- Completed-turn ingest and evidence/knowledge-linked reasoning outcomes.
- Failed-turn rejection without ingest.
- Persistent SQLite LangGraph checkpoints separate from SEAM memory.
- Always-on memory recall tool.
- Operator-scoped file read and repository search.
- Repository search rejects absolute/traversal globs and verifies every opened
  descriptor remains inside its originating configured root.
- Opt-in unsandboxed shell with approval and timeout controls.
- Versioned, framework-free command result with real exit/duration/truncation
  truth; failed, invalid, mismatched, or unpairable command evidence cannot
  become passed SEAM support.
- Unique current-turn message markers, concrete request/result roles, and
  strict SEAM egress prevent prior checkpoint actions or coerced fields from
  becoming current support.
- Tool decisions and SEAM verifications supporting accepted outcomes.
- CLI one-shot and interactive surfaces.
- Reproducible brand toolkit and expression assets.
- Hosted automatic Public CI separated from manual-only Private CI.
- Required protected-main checks, external-contributor approval, secret
  scanning/push protection, and zero assigned repository runners.
- Canonical wiki, complete build blueprint, command/how-to/install docs,
  append-only history, Temporal Chain gates/template, licensing/company
  foundation, and multi-harness launcher tooling.
- Full provider-free suite on hosted Python 3.11 and 3.13, clean wheel install,
  and real command smoke, all required by protected main.
- Coordinated deliberate-memory SEAM server source through protected PR #233 at
  `main@0b07244`; this is not a hosted deployment claim.
- `ghost-stage1-frozen-v1` 20-case corpus and immutable manifest.
- Deterministic two-arm BIL-0 bundle, verifier, and safety gate.
- Tracked non-claimable baseline bound to clean source `bc18555` and bundle
  hash `6b16ad74`.
- Lifecycle-executing successor bound to clean source `78a5035` and bundle
  hash `9ce3f9d8`; preserved as the pre-CodeRabbit lifecycle baseline.
- Final post-review artifact bound to clean source `ee4f63b` and bundle hash
  `57ca22ea`; this supersedes earlier artifacts for current comparisons.
- `GHOST_MAX_STEPS` runtime superstep ceiling and explicit non-streaming policy.
- Deterministic admit/reject/review policy that cannot promote model output.
- Explicit remember, current/history recall, additive correction, and
  confirmed soft-forgetting commands over opaque IDs.
- Workspace/project/thread durable-memory isolation and lifecycle status.
- Frozen 10-case Stage 2 memory-governance mechanism fixture.
- Provider-free specialist envelopes, budgets, scopes, evidence, terminal
  normalization, and content-free lifecycle events; no live specialist adapter.
- SQLite-consistent checkpoint backup, digest/integrity verification,
  non-overwriting restore commands, and redacted fail-closed health types.

## Local-only capability

- `ghost-avatar` WebSocket/HTTP/browser overlay runner.
- GTK desktop pet using the selected B2 art direction.
- CLI notifications from agent-turn start/end to the avatar bridge.
- Desktop sensing, movement direction, expressions, and avatar tests.
- Generated image and GLB intermediary assets.

The local avatar is not present on `origin/main`. Documentation must not call it
shipped.

## Licensing and company boundary

- Ghost now carries merged PolyForm Shield 1.0.0 package metadata with required
  notice and separated trademark/brand assets.
- The adjacent clean SEAM SDK checkout carries a local BUSL-to-PolyForm Shield
  candidate; it is not committed or published.
- The thin client remains Apache-2.0.
- Canticle Core and SEAM Node scaffolds carry PolyForm Shield placement; the
  private runtime scaffold carries an All Rights Reserved boundary.
- SEAM-U is named as the planned first SEAM-native language model. No model
  repository, weights, tokenizer, training corpus, checkpoint, or qualified
  evaluation was located.
- Nicholas Thomas remains the identified copyright holder. No Canticle legal
  entity or founder-to-company IP assignment is evidenced by this repository.

The cross-product matrix is an architecture decision, not counsel approval,
company formation, IP assignment, release, or evidence that adjacent private
runtime repositories have already been relicensed.

## Verification boundary

The earlier audit-only tree passed 270 provider-free tests with eight live
tests deselected; that evidence remains in HISTORY#051 and the structural
ledger. GTOOL-001 repair evidence is recorded in HISTORY#052: Ruff passed; 281
provider-free tests passed with eight live tests deselected; build and diff
hygiene passed; and the final CodeRabbit delta review returned no findings.
Exact PR source run `33120765857` and merge-head run `33120850903` each passed
all six protected jobs. Paid/provider-live work was not run.

The earlier recorded `184 passed` predated the continuity, licensing, and
Temporal Chain slices that added tests; see HISTORY#031.

GTOOL-002 qualification passed 306 provider-free tests with eight live tests
deselected and focused command/lifecycle/layering checks. Exact source run
`33125003964` and merge-head run `33125085772` passed all six protected jobs.
The repair preserves a real nonzero exit through SEAM action evidence and
withholds failed support.

The provider-live lane was not run. The full current documentation/continuity
closeout is recorded in the latest history entry after completion.

## Known defects and blockers

1. GTOOL-001 and GTOOL-002 are closed on protected main. Six P0 defects still
   block unattended shell use or artifact publication; GPROV-001 requires
   durable action journaling after the local replay/role repair publishes.
2. Resource ownership, SQLite cleanup, checkpoint permissions/defaults,
   transport/request bounds, and controlled CLI failure surfaces remain open.
3. A tracked repository-root `checkpoints.db` is generated execution state and
   enters the sdist; remove it in a dedicated reviewed cleanup with history.
4. Status/roadmap/blueprint facts drifted without failing the current
   recorded-fact gate; the structural ledger is authoritative for remediation.
5. Private integration CI remains unavailable without a deliberately assigned,
   reviewed runner; public exact-head CI is green.
6. Stage 1 provider-live and exact release-candidate qualification remain open;
   the deterministic artifact is explicitly non-claimable.
7. Deliberate-memory mechanisms are protected-main, but the sealed Q3
   equal-budget memory-quality comparison is absent.
8. Dependabot security updates are disabled, no code-scanning analysis exists,
   and seven dependency update PRs require deliberate review.
9. Desktop-avatar work remains local and isolated on its older branch.
10. The license structure needs counsel review and a written founder IP
    assignment after the company is legally formed.

## Next issue

Specify and close GPROV-001 with coordinated SEAM idempotency and
crash-reconciliation tests. GTOOL-003 follows. Keep the avatar checkout
untouched and keep shell use off until the P0 tool/config/provenance lane
closes.
