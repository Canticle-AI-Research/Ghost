# Public SEAM transport CI repaired; exact-head proof pending

handoff_id: `ghost-public-seam-transport-ci-repaired-20260825`
supersedes: `ghost-public-seam-transport-qualified-20260825`
handoff_status: `superseded`
history: `HISTORY#037`
created_at: `2026-08-25T21:46:52-05:00`

## Current boundary

- SEAM PR #231 is merged to protected `main@9d29c24`; this proves server
  source publication, not a compatible hosted deployment.
- Ghost PR #8 remains open at exact source head `e450012` before this repair.
- Package smoke passed, proving the wheel clean-installs from public sources
  and the real `ghost --help` imports.
- The four failures were CI-environment defects, not transport assertions:
  complete-suite jobs used shallow Git history even though continuity tests
  resolve every recorded commit, while two isolated lanes imported the shared
  public-SEAM fake without installing its public `httpx` dependency.

## Repair

- The Python 3.11 and 3.13 jobs now fetch complete Git history.
- Repository-hygiene and brand lanes explicitly install `httpx` alongside
  their isolated test dependencies.
- CI contract tests require full history for the complete suite and the shared
  fake dependency in each isolated lane.
- Focused local CI-contract, history, recorded-fact, and brand tests pass;
  Ruff and diff hygiene pass.

## Preserve and next

The primary avatar checkout remains untouched. Push this repair to PR #8,
observe the new exact-head job contexts, update protected-main requirements
without weakening existing settings, and merge only after all jobs pass. No
provider/live test, paid benchmark, package release, or deployment was run.
