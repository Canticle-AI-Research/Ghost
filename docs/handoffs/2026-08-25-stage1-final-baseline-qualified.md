# Stage 1 post-review baseline locally qualified

handoff_id: `ghost-stage1-final-baseline-qualified-20260825`
supersedes: `ghost-stage1-review-repaired-20260825`
handoff_status: `superseded`
history: `HISTORY#044`
created_at: `2026-08-25T22:24:57-05:00`

## Final local candidate

All eight CodeRabbit findings are repaired in clean source
`ee4f63b5b2be5ac1272caf1d33ff29f09701ad3a`. The final artifact is
`evals/runs/stage1/ghost-stage1-frozen-v1-bil0-final-baseline.json`.

- bundle hash: `57ca22ea5706f78e8513b92c8569fb8641e3e58c43cfedf3df0e39d81512a959`;
- manifest dirty flag: false;
- 20 cases and exact two-arm coverage;
- all eleven bundle-level verifier integrity checks: pass (per-case checks
  still record expected no-memory-arm failures);
- coverage, candidate outcome, and safety gates: pass;
- zero candidate contract failures, isolation violations, and forbidden
  effects; and
- claimable: false.

Earlier artifacts remain preserved as historical evidence. This final artifact
is the current BIL-0 comparison baseline.

## Next

Run the final successor-tree suite/build/continuity checks, re-review the exact
candidate if quota permits, push, open the PR, add `stage1-evals` to protected
main after the context exists, and merge only on green exact-head CI. No paid or
provider-live work is authorized by this artifact.
