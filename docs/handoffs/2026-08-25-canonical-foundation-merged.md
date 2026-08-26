# Canonical foundation merged; public API boundary next

handoff_id: `ghost-canonical-foundation-merged-20260825`
supersedes: `ghost-canonical-foundation-candidate-20260825`
handoff_status: `superseded`
history: `HISTORY#035`
created_at: `2026-08-25T20:25:44-05:00`

## Completed boundary

- PR #6 merged as `main@a5997c6`.
- Required hosted checks passed on the exact PR and merge heads.
- The canonical wiki, history, Temporal Chain, licensing foundation, and
  launcher tooling are mainline.
- The primary checkout was fast-forwarded without losing avatar WIP.

## Next objective

Close the public API/client distribution boundary so Ghost can install and run
without resolving private Git-over-SSH implementation sources. Preserve the
lifecycle, recall, provenance, verified-outcome, and failure contracts.

## Preserve

- Avatar source/assets/tools/tests and CLI/package/lock changes remain local in
  `agent/avatar-u1-temporal-integration`; do not reset, delete, or mix them into
  the API migration.
- No private CI or provider-live qualification has been claimed.
- Company formation, counsel review, and founder IP assignment remain external
  legal work, not repository facts.

## Resume commands

```bash
git fetch --prune origin
git status --short --branch
uv run python -m tools.history.build_context_pack --topics sdk packaging architecture --latest 6
rg -n 'seam-sdk|seam-client|SeamSDK' pyproject.toml uv.lock src tests docs
```
