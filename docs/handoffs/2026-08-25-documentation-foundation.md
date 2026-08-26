# Documentation and continuity foundation

handoff_id: `ghost-docs-foundation-20260825`
supersedes: `ghost-desktop-pet-20260821`
handoff_status: `superseded`
history: `HISTORY#023`
created_at: `2026-08-25T12:00:00-05:00`

## Objective

Make Ghost reconstructable from its repository documentation and preserve a
canonical, bounded, append-only build history comparable in discipline to
SEAM's continuity system.

## State boundary

- `main` and `origin/main` were reconciled at `25f47c4` before edits.
- Pre-existing avatar code, assets, CLI/pyproject changes, and handoff material
  remain local WIP and were not treated as landed behavior.
- The documentation foundation adds root status/ledger/history authorities,
  an extensive wiki, command/how-to/install/rebuild blueprints, handoff and
  audit registries, standard-library history tooling, and enforcement tests.
- GitHub is public while the workflow targets a privileged self-hosted runner.
  This remains the next security issue and blocks opening a new PR.

## Resume order

1. Run `git status --short --branch` and confirm the dirty avatar paths remain
   preserved.
2. Run `uv run python -m tools.history.verify_continuity --require-snapshot`.
3. Run `uv run pytest tests/test_docs.py tests/test_history_tools.py -q`.
4. Run `uv run ruff check .`, `uv run pytest`, `uv build`, and
   `git diff --check`.
5. If the documentation slice is clean, address the public-repository and
   self-hosted-runner boundary before opening a pull request.

## Unresolved lanes

- Public repository/self-hosted runner exposure.
- Exact-head CI has no green completion.
- Two open Dependabot pull requests remain.
- Desktop avatar is uncommitted and has five known Ruff findings.
- Stage 1 frozen task/memory qualification is incomplete.

Superseded by `ghost-public-runner-next-20260825` after the local wiki and
continuity foundation passed its provider-free qualification boundary.
