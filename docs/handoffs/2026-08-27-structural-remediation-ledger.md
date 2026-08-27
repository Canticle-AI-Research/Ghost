# Structural remediation ledger handoff

handoff_id: `ghost-structural-remediation-ledger-20260827`
supersedes: `ghost-specialist-ops-foundation-published-20260826`
handoff_status: `superseded`
history: `HISTORY#051`
created_at: `2026-08-27T11:36:21-05:00`

## Current boundary

Protected `origin/main@cccf99ae53dc144c68594ef3cfb67f4aa1471fd0`
contains the specialist/operations source plus its PR #15 publication record.
Exact-head Public CI run `32935194091` passed all six required jobs.

The local branch `docs/structural-audit-20260827` adds only the registered
structural remediation ledger and its continuity/status routing. Nothing in
this branch is pushed, merged, released, or deployed. The separate primary
checkout remains on `agent/avatar-u1-temporal-integration@a5997c6` with its
pre-existing avatar/package WIP untouched.

## What the audit established

- Provider-free Ruff, 270 tests with eight live tests deselected, build, and
  Stage 1 BIL-0 validation/verification/gating pass.
- Seven P0 defects block unattended shell use or release publication.
- Focused probes reproduced a repository-search symlink escape, failed shell
  outcome flattened to success, descendant process survival after timeout,
  fail-open approval typo, and CWD dotenv authority widening.
- The sdist includes the tracked execution-state database and other
  unqualified repository surfaces.
- CodeRabbit's complete `src/ghost` review returned four major and three minor
  findings; all valid findings are routed in the ledger.
- Current status/roadmap truth has drifted, GitHub dependency security updates
  are disabled, no code-scanning analysis exists, and seven dependency PRs are
  open.

## Resume order

1. Read `docs/audits/2026-08-27-structural-remediation-ledger.md`.
2. Start with GTOOL-001 in a new focused branch/worktree from current protected
   main; do not build it on this documentation branch or the avatar checkout.
3. Prove resolved-path containment for every search candidate and reject
   absolute/traversal globs before reading.
4. Add the exact negative tests in the ledger, run closeout/full verification,
   and review the focused diff before publication.
5. Continue one issue at a time in the ledger's course-of-action order.

Keep `GHOST_TOOL_ROOTS` unset for untrusted content until GTOOL-001 closes.
Keep `GHOST_ENABLE_SHELL` off for normal operation until GTOOL-002 through
GTOOL-004 and GST-001/GST-002 close. Do not publish the current sdist until
GPKG-001 closes. Paid/live benchmark execution still requires explicit
operator approval after the provider-free Q3 implementation and cost report.

## Verification boundary

The local audit ran no provider/model, live SEAM, paid judge, package
publication, release, deployment, push, merge, avatar change, or destructive
cleanup. Exact commands and results are recorded in HISTORY#051 and the audit
evidence manifest.
