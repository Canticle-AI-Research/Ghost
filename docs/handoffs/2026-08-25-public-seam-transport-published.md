# Public SEAM transport published to protected main

handoff_id: `ghost-public-seam-transport-published-20260825`
supersedes: `ghost-public-seam-transport-ci-repaired-20260825`
handoff_status: `current`
history: `HISTORY#038`
created_at: `2026-08-25T21:49:58-05:00`

## Protected-main result

- Ghost PR #8 merged as `66841fc3450b93a275b5e13e4fa82e9531be93b7`.
- Exact source head `7a8228a7de823881a26644973a2c225e0f8a252b`
  passed `repo-hygiene`, `brand-assets`, `tests (3.11)`, `tests (3.13)`, and
  `package-smoke` before merge.
- Exact merge-head run `32924125667` passed the same five jobs.
- Protected main now requires all five contexts with strict up-to-date checks;
  administrator enforcement, conversation resolution, and force-push/deletion
  blocks remain enabled.
- SEAM PR #231 is protected-main server source at merge `9d29c24`.

## Published boundary

Ghost now installs from public dependencies only and preserves begin, action,
completion, failure, and recall semantics through an independently authored
opaque HTTP adapter. SEAM owns private MIRL, reasoning, verification, evidence,
and persistence internals. The wheel build and clean install are proven; no
wheel, sdist, tag, GitHub Release, or hosted service was published.

## Preserved work and next gate

The primary `agent/avatar-u1-temporal-integration` checkout remains untouched
with avatar-only WIP. The next product gate is the frozen Stage 1 task/memory
evaluation baseline. Do not begin deliberate memory policy or specialist work
until that baseline is reproducible and sealed. No provider/live test or paid
benchmark was run.
