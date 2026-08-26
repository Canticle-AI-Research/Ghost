# Current state: 2026-08-25

This report separates landed source, local work, remote state, verification,
and roadmap maturity. `PROJECT_STATUS.md` is the compact router to this page.

## Repository state

| Plane | Observed state |
|---|---|
| Default branch | `main@a5997c616e946496875a3ba4772ab9759b46f2d7` |
| Primary working branch | `agent/avatar-u1-temporal-integration`, fast-forwarded to main and preserving avatar-only WIP |
| Canonical foundation | merged through PR #6 |
| Preserved local work | avatar source/tests/assets/tools plus CLI/package/lock changes in the primary checkout |
| Remote visibility | public |
| Merged PRs | PR #1, PR #5, and PR #6 |
| Open PRs | Dependabot #2 and #4 |
| Exact-head public CI | run `32918733013` green on `a5997c6`; all three required jobs passed |
| Private integration CI | not run; Ghost has no assigned self-hosted runner |

This is a status snapshot, not authorization to delete or combine local files.

## Landed capability at `main@a5997c6`

- DeepAgents root agent with provider routing through LangChain.
- OpenAI reasoning-model use through the Responses API.
- Private exact-revision `seam-sdk[pgvector]` dependency.
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
4. The current wheel depends on private Git-over-SSH sources and is not fit for
   public PyPI.
5. Stage 1 lacks frozen task/memory exit qualification.
6. Selective memory admission, correction, forgetting, and principal isolation
   remain absent.
7. The API/client path needed for a publicly installable Ghost is planned, not
   implemented; current Ghost still imports the in-process SDK.
8. The license structure needs counsel review and a written founder IP
    assignment after the company is legally formed.

## Next issue

Design and qualify the public API/client distribution boundary while preserving
the avatar candidate in its isolated primary working branch.
