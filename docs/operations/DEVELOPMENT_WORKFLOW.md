# Development and documentation workflow

The repository treats documentation as part of the implementation contract.
The workflow below keeps the wiki, commands, architecture, status, roadmap,
history, and code synchronized as Ghost evolves.

## Change loop

```text
reconcile
   │
   ▼
define contract ──► update blueprint/tests first when behavior is ambiguous
   │
   ▼
implement smallest coherent slice
   │
   ├─► code/tests
   ├─► command + how-to + configuration docs
   ├─► architecture/security/evaluation docs
   ├─► roadmap/status/ledger/ADR if authority changed
   └─► append-only history + handoff
   │
   ▼
local closeout ──► review ──► branch/push/PR ──► exact-head CI ──► merge
```

## 1. Reconcile before editing

```bash
git status --short --branch
git fetch --prune origin
git rev-parse HEAD origin/main
git worktree list --porcelain
gh pr list --repo Canticle-AI-Research/Ghost --state all --limit 20
```

Read status, ledger, history index, docs index, and current handoff. Name dirty
files and keep unrelated work out of the new slice.

## 2. Classify the change

| Change | Required documentation |
|---|---|
| New runtime component | complete blueprint, runtime layer, rebuild map |
| New/changed command | command reference plus how-to example |
| New setting | configuration, `.env.example`, tests |
| New tool/authority | trust boundaries, tool ladder, tests, ADR if durable |
| Memory behavior | lifecycle, memory layers, eval plan, ADR/ledger |
| Packaging/release | installation, command reference, release/deployment |
| Avatar/visual | avatar architecture, actual render evidence, handoff/status |
| Roadmap status | dated evidence report plus history entry |
| Stable invariant | ledger and usually ADR |

## 3. Keep code and blueprint in one review unit

Do not merge implementation with “docs later.” A reviewer must be able to
answer from the same diff:

- What changed?
- Why does the architecture allow it?
- How is it configured and invoked?
- What authority does it gain?
- How is failure handled?
- How is it tested?
- How could another engineer rebuild it?
- What roadmap gate moved, if any?

## 4. Verification ladder

Fast documentation/continuity loop:

```bash
uv run pytest tests/test_docs.py tests/test_history_tools.py -q
uv run python -m tools.history.verify_continuity
```

Provider-free repository qualification:

```bash
uv run ruff check .
uv run pytest
uv build
git diff --check
```

Live provider qualification is separate, explicitly approved, and recorded
with model/revision/test scope. GitHub exact-head CI is separate again.

## 5. Canonical closeout

Update current status and stable ledger only when their facts changed. Append
one history entry. Register a successor handoff when work must continue.

```bash
uv run python -m tools.history.closeout --agent codex
```

Review the generated `HISTORY_INDEX.md` and ignored snapshot. A wrapper success
does not override a failing Ruff/full test/build result.

## 6. Candidate review

Before staging:

- inspect `git diff --stat` and `git status --short`;
- stage explicit paths only;
- exclude databases, `.env*`, provider artifacts, local generation caches,
  unapproved large binaries, and private session URLs;
- verify every documentation link and command;
- ensure status language separates local/merged/released/deployed;
- check the candidate contains no secret-shaped values.

## 7. Branch and PR

Use a focused feature branch. The local candidate routes public continuity to
hosted infrastructure and makes private CI manual-only, but the default branch
still contains the old topology. Review GitHub's effective workflow and runner
settings before opening a PR; do not use a PR as the safety experiment.

A PR body records:

- scope and architecture boundary;
- documentation/blueprint pages changed;
- exact local verification and deselections;
- exact pushed head;
- remaining risks and intentionally excluded WIP; and
- history/handoff entry.

## 8. Merge and post-merge truth

A PR is not merged because local tests pass. Verify required checks on the
exact head, review remaining risk, then merge. After merge:

- fetch and confirm `origin/main` contains the merge;
- record merge as a new history event when not already covered;
- update handoff/status from local candidate to protected-main truth;
- treat package release and deployment as later separate events.

## CI enforcement target

The `repo-hygiene` job should run:

```bash
uv run --no-project --with 'pytest>=8.3,<10' \
  pytest tests/test_docs.py tests/test_history_tools.py -q
```

`tests/test_ci_contract.py` must require both credential-free files to run in a
credential-free lane. Continuity verification uses only the standard library
and repository data, so it must not depend on private SDK availability.

## Periodic documentation audit

At milestone close or monthly, whichever comes first:

1. follow every wiki learning route from a clean checkout;
2. execute every non-paid installation and command example;
3. compare source modules/entry points/environment variables with the index;
4. reconcile roadmap status against history and code;
5. inspect current handoff and remove forks/stale heads through new history;
6. verify public/private/package/deployment language against live state; and
7. write a dated audit registered in `docs/audits/INDEX.md`.
