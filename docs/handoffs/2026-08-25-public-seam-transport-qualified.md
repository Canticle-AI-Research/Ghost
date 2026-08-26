# Public SEAM transport locally qualified; coordinated merge pending

handoff_id: `ghost-public-seam-transport-qualified-20260825`
supersedes: `ghost-canonical-foundation-merged-20260825`
handoff_status: `current`
history: `HISTORY#036`
created_at: `2026-08-25T21:37:11-05:00`

## Completed local boundary

- `feat/public-seam-transport` starts exactly at protected
  `main@10a2b45eeed68bdc9aeb4fca5f1d066982192fcf`.
- `pyproject.toml` and `uv.lock` contain no private SEAM package or Git source.
- `SeamMemory` is an independently authored `httpx` adapter for begin,
  actions, complete, fail, and recall.
- Settings add service URL, redacted bearer token, and bounded timeout.
- Responses stream under an 8 MiB allocation cap before JSON parsing;
  malformed scores and response shapes fail closed.
- Public CI installs the full project and runs all provider-free tests on
  Python 3.11 and 3.13. Package smoke clean-installs the wheel and runs the real
  `ghost --help`; no workflow targets a self-hosted runner.
- Manual live CI requires explicit provider and SEAM service credentials plus
  `run_live=true`.

## Verification

- `uv run ruff check .`: passed.
- `uv run python -m pytest --durations=10`: 200 passed; 8 paid/live tests
  deselected by the default marker.
- `uv build`: wheel and sdist built.
- clean wheel install in a fresh `/mnt/data` environment: passed; real
  `ghost --help` imported; metadata listed only public dependencies.
- `git diff --check`: passed.
- CodeRabbit full-candidate review cycle one returned seven findings and cycle
  two returned one. All eight valid findings were repaired, including the
  streamed response cap, malformed-score handling, roadmap/status drift, and
  exact documentation wording.

## Coordinated SEAM dependency

Private SEAM PR #231 adds the server-owned reasoning lifecycle and is still
under exact-head CI/review. Source parity is not a deployment. Ghost must not
claim a compatible hosted endpoint, public package release, or live service
until those later states are separately proven.

## Preserve

- The primary `agent/avatar-u1-temporal-integration` checkout retains its
  avatar-only WIP and must not be reset, deleted, or folded into this PR.
- No provider/live test or paid benchmark was run.
- Company formation, counsel review, founder IP assignment, package release,
  and deployment remain outside this candidate.

## Next

Run the final no-findings re-review, continuity closeout, explicit-path commit,
push, PR, exact-head hosted checks, and protected merge after SEAM PR #231 is
green. Then publish a successor protected-main handoff, update branch
protection to require both hosted Python test jobs, and remove the clean API
worktree.
