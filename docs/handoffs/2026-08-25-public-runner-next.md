# Public repository and runner safety next

handoff_id: `ghost-public-runner-next-20260825`
supersedes: `ghost-docs-foundation-20260825`
handoff_status: `superseded`
history: `HISTORY#024`
created_at: `2026-08-25T14:00:00-05:00`

## Completed boundary

The local documentation/continuity slice now contains:

- root status, stable ledger, append-only build history, generated index, and
  repo-local AGENTS protocol;
- one chronological registered handoff chain and ignored bounded snapshots;
- extensive wiki, installation, every-command reference, how-tos,
  configuration, complete ASCII architecture, rebuild blueprint, security,
  testing, release, and dependency-ordered roadmap;
- CI-coupled documentation/history tests; and
- an append-only correction to the prior Stage 1 completion claim.

Provider-free qualification on the dirty current tree:

- focused docs/history/CI contract: 27 passed;
- full default suite: 181 passed, eight live tests deselected;
- wheel and source distribution: built successfully;
- new continuity tooling/tests: Ruff clean;
- full Ruff: five pre-existing local avatar/image-tool findings remain; and
- `git diff --check`: passed.

## Next objective

Resolve the public GitHub repository plus privileged self-hosted `seam-box`
runner contradiction before opening a PR. Follow
`docs/security/PUBLIC_REPOSITORY_AND_RUNNER.md`.

## Preserve

- Do not delete or reset the local avatar source/assets/tools.
- Do not stage `.blender-toolkit/`, local databases, `.env.local`, or ignored
  snapshots.
- Do not open a PR merely to test the unsafe runner topology.
- Keep the documentation slice explicitly local until it is committed/pushed.

## Resume commands

```bash
git status --short --branch
git fetch --prune origin
gh repo view Canticle-AI-Research/Ghost --json visibility,isPrivate,url
gh pr list --repo Canticle-AI-Research/Ghost --state all --limit 20
uv run python -m tools.history.verify_continuity --require-snapshot
```
