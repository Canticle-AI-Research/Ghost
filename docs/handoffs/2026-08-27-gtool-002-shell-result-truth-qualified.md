# GTOOL-002 shell-result truth qualified

handoff_id: `ghost-gtool-002-shell-result-truth-qualified-20260827`
supersedes: `ghost-gtool-001-search-containment-published-20260827`
handoff_status: `superseded`
history: `HISTORY#055`
created_at: `2026-08-27T17:56:55-05:00`

## Current boundary

Protected `origin/main@2e7cd543c55d457f6bc92d75292d866405e9a537`
contains the GTOOL-001 repair and passed all six required provider-free jobs in
exact-head run `33121533122`. The focused local branch
`fix/gtool-002-shell-result-truth` is based on that head and contains the
qualified GTOOL-002 candidate. It is not yet pushed or merged at this
qualification boundary.

The primary checkout remains on
`agent/avatar-u1-temporal-integration@a5997c6` with its pre-existing
avatar/package WIP untouched.

## Qualified repair

- `ghost.command_result/v1` is the authoritative framework-free completed
  command result: real exit code, measured duration, success derived from exit
  zero, and truncation state.
- LangChain `ToolMessage.status` remains transport status; the typed artifact
  supplies process truth.
- The adapter validates request/result order, unique call identity, exact
  `run_command` name, exact transport success, schema, types, finiteness, and
  internal consistency.
- Missing, malformed, stale, duplicated, mismatched, refused, or timed-out
  evidence fails closed without inventing an exit code.
- A real nonzero exit reaches SEAM `/actions` as `ok=false` with its real exit
  code and cannot return a passed verification ID or support completion.
- The registered artifact report is
  `docs/audits/2026-08-27-gtool-002-shell-result-truth.md`.

## Verification

- Focused Ruff and command/lifecycle/layering regressions passed.
- The complete provider-free suite passed 306 tests with eight live tests
  deselected.
- Independent framework-transport review returned no findings. Adversarial
  review found one blank-call-ID evidence-drop path; the path was repaired and
  its end-to-end SEAM regression passes. The second adversarial review returned
  no findings.
- Continuity closeout through HISTORY#055, full Ruff, build, diff hygiene,
  recorded-fact audit, and changed-path secret-shaped scan passed.
- Initial exact-source PR run `33124878342` passed five jobs but failed
  `repo-hygiene`: the status router's volatile exact suite count disagreed with
  collection under that job's narrow dependency set. The count was removed as
  the recorded-fact gate recommends; corrected exact-head CI remains required.
- No provider/model, live SEAM, paid judge, package publication, release,
  deployment, avatar change, or destructive cleanup ran.

## Resume order

1. Push and merge only through a feature PR and all six required exact-head
   checks.
2. Write a successor publication record with exact PR, source, merge, and CI
   evidence.
3. Start GTOOL-003 in a new focused worktree: terminate and reap the entire
   process group on timeout and prove no delayed descendant side effect.
4. Keep shell use off until GTOOL-003/GTOOL-004 and GST-001/GST-002 close; keep
   the avatar workstream separate.
