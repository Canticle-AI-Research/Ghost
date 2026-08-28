# GPROV-001 heartbeat action-journal design protected-main publication

handoff_id: `ghost-gprov-001-heartbeat-design-published-20260828`
supersedes: `ghost-gprov-001-heartbeat-design-20260827`
handoff_status: `current`
history: `HISTORY#060`
created_at: `2026-08-28T00:10:12-05:00`

## Protected-main evidence

The approved GPROV-001 design is protected-main source. PR #28 merged exact
source `4a354918c784b82ffb788f7dc26bff469a6b70de` as
`16542118476edb1f4f68263f88b23276562e372b`. The exact-source Public CI run
`33143820536` and exact merge-head Public CI run `33143873137` each passed the
six required provider-free jobs: `repo-hygiene`, `brand-assets`, `tests (3.11)`,
`tests (3.13)`, `package-smoke`, and `stage1-evals`.

The committed specification is
`docs/superpowers/specs/2026-08-27-gprov-001-heartbeat-journal-design.md`.
It preserves the approved split: the Ghost SQLite journal and SEAM idempotency
provide safety, while the in-process heartbeat provides liveness.

## Current boundary

This publication records architecture and continuity only. It does not
implement the journal, middleware, heartbeat, opaque client contract, or SEAM
service routes. No private SEAM/MIRL code, runtime code, tests, dependencies,
provider-live operation, package publication, release, deployment, or avatar
state changed in this publication boundary.

The design does not establish universally exactly-once external effects,
production readiness, or a provider/live qualification. The frozen Stage 1
BIL-0 artifacts remain untouched and non-claimable.

## Next boundary

The operator must review the committed specification before any implementation
plan or runtime work begins. No implementation plan is written by this
publication. After explicit operator approval, a separate planning task may
use the repository's planning protocol and must keep coordinated live SEAM
support as a separately evidenced dependency.
