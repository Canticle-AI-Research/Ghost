# Specialist and operations foundation published

handoff_id: `ghost-specialist-ops-foundation-published-20260826`
supersedes: `ghost-specialist-ops-foundation-qualified-20260826`
handoff_status: `superseded`
history: `HISTORY#050`
created_at: `2026-08-26T00:41:04-05:00`

## Protected-main result

PR #14 merged exact source `3d2d8b9805ddaaafc784aa186b1d6b3e94e1a24f`
as `main@c9d8a83cbf5585338f9bf5db8b978e70fd2dd398`. Exact PR run
`32934880135` and exact merge-head run `32934944801` passed all six protected
jobs: repository hygiene, brand assets, Python 3.11, Python 3.13, package smoke,
and Stage 1 evaluations.

The published source provides bounded specialist contracts and local
checkpoint recovery/redacted-health primitives. It runs no specialist model,
hosts no endpoint, and establishes no deployment. The full command,
architecture, recovery, observability, blueprint, roadmap, status, ledger,
wiki, and Temporal Chain records are part of the protected merge.

## Remaining gates

- G1 provider-live and release-candidate qualification remains open.
- G2 requires the sealed equal-budget Q3 memory-quality comparison.
- G3 requires G1/G2 exit plus a model-backed adapter and equal-budget Q3
  specialist comparison.
- G4 requires R4/G2 plus authenticated hosting, SEAM recovery, migration,
  tenancy, supervision, dashboards, incident response, rollback, and deployed
  drills.
- Public CI reports a Node 20 action-runtime deprecation warning; jobs pass,
  but workflow action revisions should be updated in a focused maintenance PR.
- The isolated avatar worktree remains untouched.
