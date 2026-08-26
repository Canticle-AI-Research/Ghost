# Temporal Chain named and documentation drift gated

handoff_id: `ghost-temporal-chain-named-20260825`
supersedes: `ghost-company-licensing-foundation-20260825`
handoff_status: `superseded`
history: `HISTORY#028`
created_at: `2026-08-25T16:10:00-05:00`

## Completed local boundary

- `templates/repository-continuity/` is now `templates/temporal-chain/`, and the
  glossary, ledger, blueprint, wiki, continuity protocol, and command reference
  all name the protocol the Temporal Chain.
- The template's `AGENTS.md` gained the git half it lacked: session
  reconciliation, branch/PR discipline, staging rules, cut-off recovery, and the
  committed/merged/released/deployed distinction.
- `docs/history/PATH_MOVES.md` lets an append-only chain survive reorganization.
  Ref validation follows a transitive move chain with cycle detection before
  checking existence.
- Documentation drift is enforced, not merely described: environment-variable
  parity with `src/ghost/`, console-script parity with `pyproject.toml`,
  controlled vocabularies for history topics and roadmap statuses, and a
  450-line module ceiling.
- The roadmap gained Track T (Temporal Chain, including the uninstalled streams
  and routing layers), Track Q (critical coverage and module boundaries), and
  U0b (multi-harness launchers).
- `tools/launchers/` renders one shared persona body into each harness's agent
  directory. `ghost-grok` and `ghost-agy` join `ghost-claude` and `ghost-codex`.

## Verification

- `uv run python -m tools.history.closeout --agent claude`
- provider-free suite: 196 passed, 8 live tests deselected
- `grok inspect` lists `canticle-ghost` as a user agent; `agy agent` lists it
- scoped Ruff clean on changed tools and tests
- `git diff --check` clean

## Known gaps

- The shared Ghost charter still lives at `~/.config/canticle-agents/ghost.md`,
  outside the repository. A clean-room rebuild cannot reproduce it. Decide
  whether it belongs here or in a tracked dotfiles source.
- SEAM's streams and routing layers (T2) are documented but not installed in
  Ghost. Port them with their parsers and integrity gates, never as isolated
  stream files.
- Many behaviors are still unverified. Track Q1 is the standard: a test exists
  to verify a behavior, never to reach a count. Name the uncovered behaviors
  rather than reporting a passing total.
- The 450-line module ceiling is a starting ratchet. `tools/branding/assets.py`
  (402 lines) and `src/ghost/tools.py` (360 lines) are the next splits.
- Everything here remains a working-tree candidate. Nothing is committed,
  pushed, merged, or released, and R1 runner safety still blocks opening a PR.

## Resume commands

```bash
git status --short --branch
uv run python -m tools.history.build_context_pack --latest 3 --token-budget 2000
uv run python -m tools.history.verify_continuity
uv run pytest -q
```

## Next issue

Close R1 public-runner safety so this candidate and the licensing candidate can
be reviewed and merged. Do not open a pull request before the runner topology is
verified; see `docs/security/PUBLIC_REPOSITORY_AND_RUNNER.md`.
