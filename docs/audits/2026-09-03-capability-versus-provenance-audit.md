# Audit: capability versus provenance, 2026-09-03

- Date: 2026-09-03
- Scope: whole repository at `origin/main@a8088bf`, plus the primary checkout's
  uncommitted avatar work and the eleven sibling worktrees.
- Method: read the merged source and tests, executed the frozen Stage 1 smoke,
  probed the SEAM service port, and reconciled local, branch, remote, and
  merged state.
- Claim boundary: provider-free. No paid or live-provider run was executed.

## Finding 1 — the tool roster has not grown in twenty-nine pull requests

Ghost exposes exactly four tools, and has since the first release:

| Tool | Class | Present when |
|---|---|---|
| `seam_recall` | read | always |
| `read_file` | read | `GHOST_TOOL_ROOTS` is set |
| `search_repo` | read | `GHOST_TOOL_ROOTS` is set |
| `run_command` | **write** | `GHOST_ENABLE_SHELL` is set |

`WRITE_TOOLS` is still `frozenset({"run_command"})`. Across PRs #1 to #29 the
repository added roughly five modules, doubled the test suite, and grew `docs/`
to ninety-four files, while the set of things Ghost can *do* stayed fixed.

This is not a defect in the work that was done. Every one of those changes is
defensible in isolation. It is a defect in the **rubric**: `AGENTS.md` is a
provenance protocol. Every rule in it governs recording, reconciling,
superseding, indexing, or verifying. Not one rule requires a change to ship a
capability. An autonomous agent optimizing that rubric will produce exactly
what this repository contains — a rigorously evidenced, capability-frozen agent.

## Finding 2 — the benchmark score cannot move

This is the finding that most affects planning, because the chosen autopilot
gate depends on it.

`tools/evaluation/runner.py` already has the right shape. It runs two arms,
`ghost-memory` and `no-memory`, and `_summary` computes `task_success_delta`
between them. That is the correct number to gate on.

Executed on this revision:

```text
ghost-memory  pass_rate 1.0   (20/20)
no-memory     pass_rate 0.5   (10/20)
task_success_delta 0.5
isolation_violations 0
forbidden_effects 0
claimable false
```

The candidate arm is already at a perfect 1.0, and the number is a **constant**.
Case answers are literal strings stored in the fixture:

```json
"answer_with_memory": "The recorded constraint is exact-head CI before release.",
"answer_without_memory": "I do not have the recorded launch constraint."
```

No model runs. `_evaluate_case` reads the pre-written answer for the arm and
scores it against the pre-written expectation. The suite therefore measures the
*harness and lifecycle contract*, which is what its own `claim_boundary` says:
`"harness and lifecycle contract smoke; no live capability claim"`.

The consequence is specific and important: **gating autopilot on this score
today would gate on a constant that is already saturated.** Every cycle would
pass while building nothing, which is a weaker gate than the current one, not a
stronger one. The live-scored arm must exist before the gate can be the gate.

## Finding 3 — Ghost cannot currently execute a turn

`seam_memory.py` is now an opaque HTTP adapter over `httpx`; `origin/main`
dropped the `seam-sdk` dependency entirely. This was the right architectural
move and it makes Ghost publicly installable, but it means the memory layer is
a network client:

- `SEAM_BASE_URL` defaults to `http://127.0.0.1:8765`;
- port 8765 is **not listening**;
- pgvector *is* listening on 55432, so the database is up and the API is not.

`SeamMemory.begin_turn` is the first call in `run_turn`, so with no SEAM service
every turn fails before the model is reached. Ghost is not currently runnable,
and `docs/status/CURRENT_STATE.md` confirms the private integration lane has
never run. The SEAM runtime exists at `~/Documents/Projects/Seam` and serves
with `seam serve --port 8765`.

## Finding 4 — a completed contract with no adapter

`src/ghost/specialists.py` is 255 lines with a 255-line test file, and is
imported by nothing in `src/`. Its own docstring states the position honestly:
*"This module does not activate a specialist topology."*

The envelope, budget, scope, provenance, and terminal-state normalization are
all present and tested. Only the framework adapter that would let a root turn
actually delegate is missing. This is the single largest ratio of finished
design to absent capability in the repository.

## Finding 5 — SEAM is used at roughly an eighth of its surface

Ghost calls three of the twenty-three operations the SEAM client exposes:
knowledge query, ingest, and the reasoning session. Unused, and directly
relevant to durable memory quality:

| Operation | What it would give Ghost |
|---|---|
| `promotion`, `promotion_eligibility`, `review_promotion` | consolidation — memory that compounds instead of accumulating |
| `graph_products`, `rebuild_graph_products`, `graph_product_history` | derived knowledge over the raw record set |
| `recoverable_operations`, `resume_operation` | durable operations that survive a crash |
| `plan_delete`, `apply_delete`, `lifecycle_operation` | operator-driven correction and forgetting |

Ghost stores turns and searches them back. It does not yet *learn* from them.

## Finding 6 — repository state is stale, red, and sprawling

| Observation | Detail |
|---|---|
| Primary checkout is behind | local `main` is 19 commits behind `origin/main`; the working branch sits at `a5997c6` (PR #6) while the real head is `a8088bf` (PR #29) |
| Working tree is red | two failing tests: five `GHOST_*` variables introduced by the uncommitted avatar work are absent from `CONFIGURATION.md`, tripping the documentation drift gate |
| Sibling worktree sprawl | eleven worktrees under `Documents/Projects/`, created by autopilot, in direct violation of the operator's standing instruction to place worktrees under `<repo>/.worktrees/` or `.disposable/` |
| Uncommitted capability | the entire avatar subsystem, its tests, assets, and tooling exist only as untracked files in the primary checkout |

The stale checkout is the most dangerous of these, because status reported from
it describes a Ghost that is twenty-three commits out of date.

## What is genuinely strong

Recorded so the remediation does not damage it:

- the three-layer split — framework-free `lifecycle`, adapter `application`,
  opaque SEAM transport — is real and enforced by `tests/test_layering.py`;
- `finalize_verified` refusing an outcome whose checks failed makes "the action
  succeeded" a property the store enforces rather than a model claim;
- path containment, command-result truthfulness, and the ADR-0001 memory
  boundary are correctly built and tested;
- the two-arm evaluation *shape* is right and only needs a live judge;
- the HTTP boundary removed the private dependency from the public install.

The foundation is sound. The capability surface is starved.

## Conclusion

Ghost is a well-armored four-tool agent that cannot presently run, measured by
a benchmark that cannot presently move. The remediation order follows directly:
make it run, make the number real, then grow capability against that number.

Recorded next steps are held in
[`../roadmap/AUTOPILOT_PROGRAM.md`](../roadmap/AUTOPILOT_PROGRAM.md).
