# GPROV-001 heartbeat action-journal design approved

handoff_id: `ghost-gprov-001-heartbeat-design-20260827`
supersedes: `ghost-action-provenance-boundaries-published-20260827`
handoff_status: `superseded`
history: `HISTORY#059`
created_at: `2026-08-27T23:11:59-05:00`

## Design result

The operator approved the hybrid GPROV-001 architecture in
`docs/superpowers/specs/2026-08-27-gprov-001-heartbeat-journal-design.md`.
Ghost will commit tool intent and terminal state to a separate operator-private
SQLite journal around the real `ToolNode` call. An in-process heartbeat will
reconcile pending records with additive idempotent SEAM action routes at
startup, immediately after terminal state, every five seconds while pending,
and during bounded graceful shutdown.

Safety comes from the durable journal and SEAM idempotency. The heartbeat
provides liveness. Recovered digest-only records are non-supporting provenance;
rejected turns remain rejected. The design guarantees one canonical action
record per `(SEAM turn_id, tool_call_id)`, not universally exactly-once
external effects.

## Current boundary

This branch contains documentation and continuity bookkeeping only. No Ghost
runtime, SEAM service, package, provider, release, deployment, or avatar state
changed. The frozen Stage 1 BIL-0 artifacts remain untouched and non-claimable.

The primary avatar checkout and separate repository-guidelines and runner-
safety worktrees remain dirty and preserved. Implementation must occur in this
isolated worktree after the operator reviews the committed specification.

## Resume order

1. Obtain explicit operator approval of the committed specification.
2. Use the writing-plans skill to produce the task-by-task TDD plan.
3. Implement the Ghost journal, middleware, heartbeat, opaque client contract,
   provider-free fake, fault-injection tests, and governing documentation with
   sequential implementer/reviewer subagents.
4. Do not modify private SEAM/MIRL implementation from this repository. Treat
   coordinated live SEAM support as a separately evidenced dependency.
5. Run closeout, Ruff, the complete provider-free suite, Stage 1 verification,
   build, diff hygiene, and independent review.
6. Push the feature branch, open a PR, wait for the six protected checks, merge
   through protected `main`, and publish a successor handoff. Direct push to
   `main` remains prohibited.

## Claim boundary

The approved design is local branch source until protected publication. It is
not implemented, merged, released, deployed, provider-live, or evidence of
production readiness.
