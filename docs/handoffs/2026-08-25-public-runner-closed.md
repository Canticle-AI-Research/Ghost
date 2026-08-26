# Public runner boundary closed; publish the canonical foundation next

handoff_id: `ghost-public-runner-closed-20260825`
supersedes: `ghost-temporal-chain-named-20260825`
handoff_status: `superseded`
history: `HISTORY#033`
created_at: `2026-08-25T20:04:30-05:00`

## Completed boundary

- PR #5 merged the public-hosted/manual-private CI split.
- Exact merged head `dbd421b` passed all three hosted required jobs.
- Protected `main`, Actions permissions, external-contributor approval, secret
  scanning/push protection, repository secrets, and assigned runners were
  reconciled and recorded.
- No private or paid workflow was dispatched.

## Current objective

Publish the canonical documentation, Temporal Chain, licensing, and launcher
foundation as one self-contained review slice. Keep the desktop-avatar runtime,
generated assets, CLI wiring, and dependency changes unstaged for their own PR.

## Preserve

- Do not delete or reset `src/ghost/avatar/`, `assets/avatar/`,
  `tests/test_avatar.py`, avatar tools, CLI hook wiring, or the WebSocket lock
  change.
- Do not commit ignored provider, database, snapshot, or agent-local material.
- Do not claim private integration green while no reviewed runner is assigned.

## Resume commands

```bash
git status --short --branch
uv run python -m tools.history.build_context_pack --latest 4 --token-budget 2200
uv run python -m tools.history.closeout --agent codex
uv run ruff check .
uv run pytest
uv build
git diff --check
```
