# GTOOL-001 search containment qualified

handoff_id: `ghost-gtool-001-search-containment-qualified-20260827`
supersedes: `ghost-structural-remediation-ledger-20260827`
handoff_status: `current`
history: `HISTORY#052`
created_at: `2026-08-27T16:24:40-05:00`

## Current boundary

Protected `origin/main@cccf99ae53dc144c68594ef3cfb67f4aa1471fd0`
remains green in exact-head run `32935194091` but still contains the GTOOL-001
search-root escape. Local audit commit `0cd12e3` registers the remediation
ledger. The local branch `fix/gtool-001-search-containment` is based on that
commit and contains the qualified repair; neither local commit nor this repair
is pushed or merged.

The primary checkout remains on
`agent/avatar-u1-temporal-integration@a5997c6` with its pre-existing
avatar/package WIP untouched.

## Qualified repair

- `search_repo` rejects empty, absolute, drive-qualified, and parent-traversal
  globs before enumeration.
- Every enumerated candidate resolves inside the root that produced it before
  any candidate metadata, content, or display-path use.
- The contained path is opened once with non-following and nonblocking flags;
  the open descriptor must resolve inside the same root before `fstat` or read.
- A runtime that cannot inspect the open descriptor refuses the search rather
  than weakening containment.
- Bounded reads use the descriptor and cap bytes even if a file grows after
  opening.
- Framework-free path policy now lives in `src/ghost/path_policy.py`; the
  LangChain-facing tool adapter remains in `src/ghost/tools.py` at 360 lines.

Regression coverage includes both configured-root positions, outside and
inside symlinks, POSIX and Windows absolute globs, parent traversal, symlink
loops, a post-enumeration target swap, and an intermediate-directory swap when
descriptor inspection is unavailable.

## Verification

- `uv run pytest tests/test_tools.py tests/test_layering.py -q` passed.
- `uv run ruff check src/ghost/tools.py src/ghost/path_policy.py tests/test_tools.py tests/test_layering.py` passed.
- `uv run pytest --durations=10` passed 281 provider-free tests with eight live
  tests deselected.
- `uv run ruff check .`, `uv build`, and `git diff --check` passed.
- CodeRabbit CLI 0.7.5 found one major descriptor-verification fallback gap;
  the gap was repaired and the complete second review returned zero findings.
- No provider/model, live SEAM, paid judge, package publication, release,
  deployment, push, merge, avatar change, or destructive cleanup ran.

## Resume order

1. Inspect the exact repair diff and HISTORY#052.
2. Push and merge only on explicit operator authorization, through a feature PR
   and all six required exact-head checks.
3. After GTOOL-001 is protected-main, start GTOOL-002 on a new focused branch:
   preserve real shell exit status from execution through ToolMessage parsing,
   SEAM action evidence, and accepted-outcome support.
4. Keep `GHOST_ENABLE_SHELL` off for normal operation until GTOOL-002 through
   GTOOL-004 and GST-001/GST-002 close.
5. Keep the avatar workstream separate and do not publish the sdist until
   GPKG-001 closes.
