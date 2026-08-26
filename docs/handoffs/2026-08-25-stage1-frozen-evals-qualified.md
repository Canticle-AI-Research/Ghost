# Stage 1 frozen evaluation substrate locally qualified

handoff_id: `ghost-stage1-frozen-evals-qualified-20260825`
supersedes: `ghost-public-seam-transport-published-20260825`
handoff_status: `current`
history: `HISTORY#039`
created_at: `2026-08-25T22:08:42-05:00`

## Locally qualified candidate

- `ghost-stage1-frozen-v1` freezes 20 cases across all ten G1 categories.
- Every case names evidence, answer, tool, terminal, budget, and forbidden-
  effect contracts.
- The deterministic runner records Ghost-memory and no-memory arms, per-case
  full results, null provider usage/cost, and `claimable: false`.
- BIL-0 bundles carry exact Git/fixture/case identities and canonical manifest,
  stable-result, and whole-bundle hashes.
- Public `verify` and `gate` commands reject tampering, identity drift,
  candidate failures, isolation violations, and forbidden effects.
- `GHOST_MAX_STEPS` bounds LangGraph supersteps at 25 by default (2–100), and
  invalid programmatic values fail before recall.
- Hosted CI gains a credential-free `stage1-evals` job.

## Verification

- fixture validation: 20 cases passed;
- development smoke bundle sealed, verified, and gated at BIL-0;
- Ruff passed the entire repository;
- complete provider-free suite: 212 passed, 8 live tests deselected; and
- `git diff --check` passed.

The development smoke used `--allow-dirty` and is not a baseline. It proves the
candidate before commit, not an exact source identity.

## Next

Commit the infrastructure, run the smoke from that clean exact commit, track
the resulting baseline bundle in a successor commit, rerun full qualification,
push, require the new hosted job, and merge only after exact-head CI. A BIL-0
stub is never a live capability claim; provider-backed and release-candidate
qualification remain later G1 exits and require explicit spend approval.
