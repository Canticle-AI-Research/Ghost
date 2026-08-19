# CI, three defects, and the memory boundary

- Date: 2026-08-19
- Merged: [#1](https://github.com/Canticle-AI-Research/Ghost/pull/1) — `94d49a0`, `e3a6a04`, `f372670`, `d43840c`, `648940d`
- Roadmap: closes item 6 of the recommended immediate slice
- Tests: 18 → 81

## What prompted it

An audit of the repository. Ghost had a working memory spine and no continuous
verification: 18 tests existed and nothing ran them on push.

## Defects found

Three, all found by writing tests rather than by reading code.

### `uv run pytest` was broken as documented

`tests/test_brand_assets.py` imports `tools`, a repo-root package deliberately
kept out of the wheel. It resolved only under `python -m pytest`, which puts
the working directory on `sys.path`. The README documented `uv run pytest`,
which does not, so the documented verification command failed at collection.
The audit itself missed this by running `python -m pytest`.

Fixed with `pythonpath = ["."]` in `pyproject.toml`; both invocations work.

### Graph triples rendered into the prompt as a bare object

`_record_summary` listed `"object"` in its prose-preference loop, ahead of the
triple branch below it. A MIRL edge `{subject, predicate, object}` therefore
matched on its object and returned that alone — `ultramarine` instead of
`user prefers ultramarine`. The model received a memory with no indication of
what it was about, and the triple branch was dead code for exactly the records
it was written for.

This is a memory-quality defect in the layer the architecture documents treat
as central. Fixed by removing `"object"` from the loop; a record carrying only
an object still renders identically, through the triple branch. Both cases are
pinned as regressions.

### Public repository on a self-hosted runner

`seam-box` is a personal desktop holding a passphrase-less SSH key with read
access to two private repositories. Ghost was public, so a fork pull request —
which supplies its own copy of the workflow file — would have executed on that
machine.

Ghost was made private (0 stars, 0 forks, nothing lost). `repo-hygiene` carries
a tripwire that fails when the repository is public, and the README's "Going
public" section names the real controls. The tripwire is a reminder, not a
boundary: a hostile fork can delete it. The controls are the runner group's
repository list and the fork-PR approval setting.

## CI

Four jobs on `seam-box`, following the SEAM workflow template — job shape, fast
required gates ahead of the heavier tier, `permissions: read-all`, concurrency
with cancel-in-progress, and comments that record why. It drives `uv` where
SEAM drives pip, because `uv.lock` is committed and `uv sync` is the documented
setup.

| Job | Private deps | Covers |
|---|---|---|
| `repo-hygiene` | no | ruff, docs routing, CI contract, gitleaks |
| `brand-assets` | no | brand toolkit against real Chrome and fontconfig |
| `package-smoke` | no | wheel and sdist, shipped modules, entry point |
| `tests` | yes | full suite on 3.11 and 3.13, plus a real `ghost --help` |

The tiering is the design decision. Ghost's only runtime dependency is pinned
to a private `git+ssh` URL; a single-tier CI would say nothing whenever those
repositories were unreachable. 25 of 81 tests need no credential and cover the
whole non-agent surface.

The self-hosted runner is also why the private tier needs no secret. A hosted
runner would require a token with read access to two private repositories held
as a repository secret; `seam-box` already authenticates as the owner.

`tests/test_ci_contract.py` enforces the split by deriving from the test tree
which files import `ghost`, failing if a credential-free file runs only in the
private tier. Derived, never hardcoded — a hardcoded list is how a gate keeps
claiming coverage as the tree grows past it.

## Memory boundary

ADR-0001 items 6 and 7 were prose with nothing behind them. `create_deep_agent`
accepts `memory`, `store`, and `backend`; any of the three installs deepagents'
own `MemoryMiddleware` or `FilesystemMiddleware`, giving Ghost two things that
claim to remember while only one has MIRL, provenance, or a trust boundary.

Ghost passes none of them. Verified by building the real graph, whose only
nodes are `TodoListMiddleware.after_model` and
`PatchToolCallsMiddleware.before_agent`. `tests/test_memory_boundary.py` now
fails if that changes — including the case where a deepagents release starts
installing a memory node by default and Ghost changes nothing.

The same file asserts `seam_memory.py` imports no agent framework. That is what
keeps the harness replaceable: SEAM depends only on `psycopg`, `rich`, and
`tiktoken`, so swapping agent frameworks would cost `application.py` and
`middleware.py` and nothing else.

## How it was verified

- every CI job's commands were run locally before being written into the YAML;
- the CI contract gate was mutation-tested four ways — dropping a file from the
  public tier, sneaking a `uv sync` into `repo-hygiene`, dropping 3.11 from the
  matrix, and deleting the public-repo tripwire each turned it red, and each
  returned green on restore;
- the memory-boundary gate was mutation-tested by adding `store=` to
  `application.py`, which failed with the ADR citation;
- `gitleaks` 8.30.1 reported no leaks.

## Found and not fixed

- **Ghost has no runner.** `seam-box` is repo-scoped to `Seam`, so CI queues
  until it is re-registered at organization level. `gh` lacks `admin:org`.
- **`pylint.yml`** was added separately and fails on every push: it installs
  only pylint, so every third-party import is `E0401`, and it matrixes Python
  3.8–3.10 against a `requires-python` of `>=3.11`. `pyproject.toml` already
  configures ruff, which `repo-hygiene` runs.
- **No LICENSE.** Matters before Ghost goes public again.
- **`openai:gpt-5.6-terra`** is the default model in `config.py` and
  `.env.example`; not verified as reachable.
- **Dangling reasoning runs.** `application.py` opens a SEAM run before
  `graph.invoke`; if that raises, the run is never finalized. Roadmap item 4.
- **No live-model test.** All 81 tests avoid a model call. The MIRL round trip
  is genuinely verified against the real SDK; the agent loop is not verified
  end to end. Roadmap item 5.

## Next, per the roadmap

Recommended order for the remaining slice: item 4 (failure finalization) first,
because an eval harness provokes failures and would pollute the store it
measures; then item 2 (persistent checkpoint, since `MemorySaver` is in-process
and `--thread-id` does not survive a restart, which Stage 1's exit condition
requires); then item 5 (frozen fixtures); then item 3 (read-first tools).
