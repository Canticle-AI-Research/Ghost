# Action-provenance boundaries qualified

handoff_id: `ghost-action-provenance-boundaries-qualified-20260827`
supersedes: `ghost-gtool-002-shell-result-truth-published-20260827`
handoff_status: `current`
history: `HISTORY#057`
created_at: `2026-08-27T20:38:40-05:00`

## Qualified local result

The focused candidate is based on protected
`main@9abbff12e722f88b42347791e8dc8c261c35f28f`. It scopes action extraction
to exactly one current-turn human-message ID, accepts request/result evidence
only from concrete `AIMessage`/`ToolMessage` roles, validates call identity and
transport fields without coercion, and revalidates framework-free attempts at
the SEAM egress. Non-UTF-8 command output now produces replacement characters
and retains a typed terminal result.

Tracked regressions use a real LangGraph `StateGraph`, `ToolNode`, and
`SqliteSaver`. They prove a nonzero command artifact survives checkpoint
persistence and that a later answer-only turn cannot resubmit the older action.
Role-confused messages, missing/duplicate markers, malformed booleans and exit
codes, contradictory command evidence, and non-finite durations fail closed.
Continuity closeout, Ruff, 317 provider-free tests with eight live tests
deselected, build, and diff hygiene passed locally.

The registered report is
`docs/audits/2026-08-27-action-provenance-boundaries.md`.

This does not close GPROV-001. A completed tool followed by a graph/model/
checkpoint failure can still escape without a durable action batch because the
graph invocation raises before returning messages. Exactly-once action
provenance therefore remains unclaimed and is the next P0 architecture issue.

This is local source qualification, not protected-main publication, package
publication, release, deployment, live provider/SEAM qualification, or avatar
publication. The three pre-existing dirty WIP worktrees remain preserved.

## Resume order

1. Publish this exact candidate by feature PR; require all six protected checks
   on the exact source, merge, and verify the immutable merge head.
2. Write the GPROV-001 Ghost/SEAM idempotency contract before implementation:
   stable turn/tool identity, durable start/terminal journal, outbox delivery,
   retry/restart reconciliation, and exactly-once server semantics.
3. Inject post-tool model, recursion, checkpoint-write, delivery-loss, and
   restart failures; require exactly one action record and no false support.
4. Continue with GTOOL-003 whole-process-tree timeout termination, then
   GTOOL-004 streaming output bounds.
5. Keep shell use off for normal operation and preserve the isolated avatar,
   repository-guidelines, and runner-safety WIP until the operator chooses a
   separate preservation or discard action.
