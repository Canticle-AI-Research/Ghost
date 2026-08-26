# Stage 1 lifecycle smoke repaired after review

handoff_id: `ghost-stage1-lifecycle-smoke-repaired-20260825`
supersedes: `ghost-stage1-baseline-frozen-20260825`
handoff_status: `current`
history: `HISTORY#041`
created_at: `2026-08-25T22:15:15-05:00`

## Review findings repaired

The initial runner scored scripted records without invoking Ghost's real
lifecycle. It was honestly BIL-0/non-claimable, but its lifecycle claim was too
weak. The repaired runner now drives `run_turn` with deterministic graph and
memory doubles and pins accepted `begin → record_actions → complete` and
rejected `begin → fail` event sequences.

Fixture validation now rejects unknown, hidden-required, or visible-forbidden
evidence and any scripted step/tool/context use outside its declared budget.
Bundle verification fails closed on malformed case count/ID types instead of
raising. The CLI gate also fails closed on malformed arm summaries. Hosted CI
now installs the locked project before invoking the lifecycle-aware smoke.

Focused evaluation, CI-contract, and layering tests pass after repair. The
first clean-source baseline remains preserved as historical BIL-0 evidence; it
must not be relabeled as lifecycle-execution proof.

## Review boundary and next

CodeRabbit CLI 0.7.5 was authenticated, but the repository is not connected to
the accessible organization and the free CLI allowance returned a five-minute
rate-limit error before analysis. The valid issues above came from manual
review and reproduction, not CodeRabbit findings.

Commit this repair, generate a new clean-source lifecycle baseline under a new
artifact name, seal/verify/gate it, and advance the handoff again before push.
