# Current state: 2026-08-26

This report separates landed source, local work, remote state, verification,
and roadmap maturity. `PROJECT_STATUS.md` is the compact router to this page.

## Repository state

| Plane | Observed state |
|---|---|
| Default branch | `main@2a23fdcd730c051a83bab26622154df993431980` |
| Stage 1 evaluation substrate | merged through PR #10: 20 frozen cases, real-lifecycle BIL-0 smoke/verifier/gate, step ceiling, final clean baseline |
| Public transport | merged through PR #8; public install and opaque transport source published |
| Primary working branch | `agent/avatar-u1-temporal-integration`, preserving avatar-only WIP on its earlier reviewed base |
| Canonical foundation | merged through PRs #6 and #7 |
| Preserved local work | avatar source/tests/assets/tools plus CLI/package/lock changes in the primary checkout |
| Remote visibility | public |
| Merged PRs | PR #1 and PRs #5 through #12 |
| Open PRs | Dependabot #2 and #4 |
| Exact-head public CI | run `32933109326` green on `2a23fdc`; all six required jobs passed |
| Public transport proof | 200 provider-free tests, Ruff, build, clean wheel install, real `ghost --help`, and protected PR/main CI passed; 8 live tests deselected |

This is a status snapshot, not authorization to delete or combine local files.

## Landed capability at `main@2a23fdc`

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
- Opt-in unsandboxed shell with approval and timeout controls.
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

Current-tree evidence, each claim naming the command that produced it:

```text
See the latest history entry and handoff for commands and exact results for the
current publication slice. Paid/provider-live work was not run.
```

The earlier recorded `184 passed` predated the continuity, licensing, and
Temporal Chain slices that added tests; see HISTORY#031.

The provider-live lane was not run. The full current documentation/continuity
closeout is recorded in the latest history entry after completion.

## Known defects and blockers

1. Private integration CI remains unavailable without a deliberately assigned,
   reviewed runner; public exact-head CI is green.
2. Desktop-avatar work remains local and must stay isolated from the
   documentation/history foundation.
3. A tracked repository-root `checkpoints.db` is generated execution state and
   should be removed in a dedicated reviewed cleanup.
4. Stage 1 provider-live and exact release-candidate qualification remain open;
   the frozen deterministic artifact is explicitly non-claimable.
5. Both repository halves of deliberate-memory governance are protected-main,
   but a sealed Q3 memory-quality comparison remains absent.
6. The license structure needs counsel review and a written founder IP
    assignment after the company is legally formed.

## Next issue

Build the sealed Q3 memory-quality comparison against a named baseline without
touching the isolated avatar branch.
