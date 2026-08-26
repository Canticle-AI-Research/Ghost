# Deliberate-memory governance locally qualified

handoff_id: `ghost-deliberate-memory-qualified-20260826`
supersedes: `ghost-stage1-frozen-published-20260825`
handoff_status: `superseded`
history: `HISTORY#047`
created_at: `2026-08-26T00:08:48-05:00`

## Candidate result

The isolated `feat/deliberate-memory` worktree starts from Ghost
`main@e1d1b9a8e72cf47f813a57febf6edd3959429b3b` and targets protected SEAM
`main@0b0724407f05e07d98001ac1f4fcb401ba7fe2fe` from PR #233.

Ghost now classifies completed turns deterministically as admit, reject, or
review; only explicit admissions persist. It provides explicit remember,
current/history recall, additive correction, and confirmed soft-forgetting
commands over opaque IDs. Workspace, project, namespace, scope, and thread
dimensions remain consistent across checkpoint execution and durable memory.
Completion/failure paths restore thread context and preserve the original turn
error if terminal finalization also fails.

The frozen `ghost-stage2-memory-governance-v1` fixture contains 10 mechanism
cases across relevance, contradiction, idempotency, staleness, and isolation,
with hash
`32ed350b167b1a412e9afabcdc75657afcc96c141937d267dcdb9a5830c69a7c`.

## Verification boundary

- `uv run pytest -q`: 257 provider-free tests passed; eight live tests were
  deselected by the approval gate.
- `uv run ruff check .`, `uv build`, and `git diff --check` passed.
- Final CodeRabbit review covered all changed/tracked/untracked candidate files
  and returned zero findings after two earlier repair rounds.
- The Stage 2 fixture proves mechanisms only. It has no model, no no-memory
  answer comparison, and no admissible G2 quality-improvement claim.

## Preserve and next

The primary `agent/avatar-u1-temporal-integration` worktree remains untouched
with its avatar source, assets, tools, tests, CLI/package, and lockfile WIP.
Next: push this exact candidate, obtain all six protected Ghost checks, merge,
and write the successor publication handoff. The sealed Q3 memory-quality
comparison remains separate work after mechanism publication.
