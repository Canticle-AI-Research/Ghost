# Stage 1 lifecycle-executing baseline locally qualified

handoff_id: `ghost-stage1-lifecycle-baseline-qualified-20260825`
supersedes: `ghost-stage1-lifecycle-smoke-repaired-20260825`
handoff_status: `superseded`
history: `HISTORY#042`
created_at: `2026-08-25T22:16:51-05:00`

## Current exact evidence

The repaired source commit is
`78a5035929f03ab94e1f8f5e1cd3cb76829f7e07`. It was clean before generating
`evals/runs/stage1/ghost-stage1-frozen-v1-bil0-lifecycle-baseline.json`.

- bundle hash: `9ce3f9d80ab2a08de3767c0eaf48d84d74e02e73ef64db03891594e6c788cad2`;
- fixture hash: `4f10f3d8022beeb3ac7adbf3b01bd1b727c81d9db48b8388f8e129b84e3ed61d`;
- manifest dirty flag: false;
- accepted lifecycle: begin, record actions, complete;
- rejected lifecycle: begin, fail;
- candidate contract failures: zero;
- isolation violations and forbidden effects: zero; and
- claimable: false.

The initial baseline remains preserved; the lifecycle-executing successor is
the current BIL-0 comparison artifact.

## Publication route

Run final full-suite/build/continuity verification, attempt the delayed review
again if quota permits, push the four-commit candidate, open a focused PR,
require `stage1-evals` in branch protection, and merge only after exact-head
hosted proof. Provider-backed quality and a release-candidate run remain open
G1 work and require explicit spend approval.
