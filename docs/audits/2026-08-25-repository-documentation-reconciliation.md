# Repository and documentation reconciliation

- Date: 2026-08-25
- Governing history: HISTORY#023
- Evidence boundary: local checkout plus authenticated GitHub metadata

## Observed

- Local `main` and fetched `origin/main` both resolved to `25f47c4`.
- The working tree already contained an uncommitted desktop-avatar workstream.
- GitHub reported the repository as public.
- The exact-head CI run for `25f47c4` was cancelled after 24 hours; it did not
  provide a green mainline qualification.
- Pull requests #2 and #4 were open Dependabot updates; PR #1 was merged; #3
  was closed.
- The current local tree passed `uv run pytest`: 171 passed and eight live
  tests deselected.
- `uv build` produced a wheel and source distribution.
- `uv run ruff check .` reported five findings, all in local avatar/image-tool
  paths.

## Interpretation

Ghost's implemented single-agent foundation is materially ahead of the status
label in the old roadmap, but qualification and repository operations lag the
implementation. The avatar is a local prototype. The public/self-hosted-runner
contradiction is a security boundary, not a documentation typo.

## Not proved

- No exact-head remote CI success was observed.
- No public-package fitness was established.
- No tenant isolation, sandbox, hosted deployment, or production readiness was
  established.
- Provider-live tests were deselected in the named local run.
- No avatar branch, pull request, merge, release, or deployment was observed.

## Evidence manifest

No raw logs are committed. Durable evidence is the repository state,
`PROJECT_STATUS.md`, `HISTORY.md`, and GitHub's repository/PR/run records.

## Documentation foundation qualification

After the reconciliation, the local documentation/continuity implementation
passed 27 focused documentation/history/CI-contract tests. The full default
suite passed 181 tests with eight live tests deselected, and `uv build`
produced the wheel and source distribution. New continuity tooling/tests were
Ruff-clean. Full-tree Ruff retained the five already attributed local avatar
and image-tool findings; they were not changed in this bookkeeping slice.
