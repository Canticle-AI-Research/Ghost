# Canonical foundation candidate isolated and qualified

handoff_id: `ghost-canonical-foundation-candidate-20260825`
supersedes: `ghost-public-runner-closed-20260825`
handoff_status: `superseded`
history: `HISTORY#034`
created_at: `2026-08-25T20:17:58-05:00`

## Candidate boundary

The clean `docs/canonical-blueprint` branch contains the rebuildable wiki,
Temporal Chain, documentation/history drift gates, PolyForm/legal foundation,
and multi-harness launcher tooling. The avatar runtime and its generated assets,
CLI hook wiring, test, WebSocket dependency, and lock change remain only in the
primary checkout.

## Verification

- frozen private dependency installation completed in the clean worktree;
- full provider-free pytest passed with paid/live tests deselected;
- Ruff, package build, focused credential-free continuity tests, and diff
  hygiene passed;
- the reusable template installed and tested in a fresh temporary repository;
- a complete committed-diff review was reconciled; and
- final exact-head hosted CI and protected merge remain the publication gate.

## Preserve

- Do not reset or delete the primary avatar-only working tree.
- Keep provider/live tests approval-gated.
- Keep the exact SDK dependency locator; it is package metadata, not a secret.
- Do not call this foundation merged or released until GitHub proves it.

## Resume commands

```bash
git status --short --branch
uv run python -m tools.history.closeout --agent codex
uv run pytest -q
uv run ruff check .
uv build
git diff --check
```
