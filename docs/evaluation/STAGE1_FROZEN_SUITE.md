# Stage 1 frozen evaluation suite

## Purpose and claim boundary

This suite freezes the first reproducible evaluation contract for Ghost's
dependable-single-agent stage. It answers four credential-free questions:

1. Are the same cases and expectations being evaluated?
2. Are memory and no-memory arms separated under the same budgets?
3. Do terminal state, evidence, tools, budgets, isolation, and forbidden
   effects pass deterministic contract checks?
4. Can another checkout detect any change to a fixture, case, result, manifest,
   or sealed bundle?

The automatic runner is a deterministic stub and seals at Benchmark Integrity
Level `BIL-0`. It proves the harness, not model capability. Its pass rate or
memory delta must never be published as a product-quality result. A real model
run must preserve the same fixture IDs, record full-fidelity outputs and usage,
use a qualified judge, and pass a separately reviewed higher-integrity lane.

The stub does execute Ghost's real framework-free `run_turn` lifecycle against
deterministic graph and memory doubles. Accepted scenarios must traverse
`begin → record_actions → complete`; rejected scenarios must traverse
`begin → fail`. Answers and tool outcomes remain scripted, so this strengthens
lifecycle proof without changing the BIL-0 capability boundary.

## Frozen corpus

The authoritative inputs are:

- `evals/stage1/fixtures.json` — 20 cases;
- `evals/stage1/MANIFEST.json` — frozen suite identity, case registry, and
  canonical fixture hash; and
- `evals/stage1/README.md` — the immutability rule.

The ten categories each contain two cases:

| Category | Contract under evaluation |
|---|---|
| source-grounded research | answer uses named evidence and respects claim limits |
| repository question answering | answer identifies the right repository owner/path |
| read-only diagnosis | tool trace stays within bounded read/search authority |
| approval-controlled action | approved and refused shell outcomes remain distinct |
| refusal recovery | denial is preserved while a safer alternative may proceed |
| timeout/cancellation/restart | interrupted work is rejected and resume state is explicit |
| memory after restart | durable evidence, not checkpoint history, supplies the fact |
| stale memory | current evidence wins and superseded evidence stays excluded |
| failed-turn non-admission | rejected turns never become accepted memory |
| boundary isolation | foreign namespace/principal evidence never appears |

Every case names:

```text
prompt
  ├─ memories[]: id, text, visible
  ├─ scripted arm output: answer, attempts, terminal state, steps
  ├─ expectations
  │    ├─ required/forbidden evidence
  │    ├─ required/excluded answer text
  │    ├─ required/forbidden tools
  │    └─ terminal state
  ├─ budgets: steps, tool calls, context characters
  └─ forbidden effects
```

Changing an expectation is not maintenance on `ghost-stage1-frozen-v1`; it is
a new corpus version. Create a successor suite and preserve the old manifest so
historical bundles remain verifiable.

## Execution architecture

```text
fixtures.json ──validate──► frozen case model
      │                         │
      │                         ├──► ghost-memory arm
      │                         └──► no-memory baseline arm
      │                                  │
      └──canonical case hashes            ▼
                                  deterministic contract judge
                                             │
                                             ▼
                                  per-case full result records
                                             │
             git HEAD + dirty state ─────────┤
             fixture/case hashes ────────────┤
                                             ▼
                                      BIL-0 sealed bundle
                                             │
                              ┌──────────────┴──────────────┐
                              ▼                             ▼
                        public verifier                safety gate
                   hash/cross-identity checks     zero leakage/effects +
                                                 candidate contract pass
```

The result hash excludes volatile timing so two honest executions can compare
the behavioral record. The manifest, result, and whole bundle each have a
canonical SHA-256. The bundle cross-checks suite, Git, fixture, case count, and
case IDs so recomputing one edited hash cannot disguise a mismatched payload.

## Commands

Validate the immutable corpus:

```bash
uv run python -m tools.evaluation validate-fixtures
```

Seal the deterministic smoke from a clean checkout:

```bash
uv run python -m tools.evaluation smoke \
  --output /tmp/ghost-stage1-smoke.json
```

Verify hashes and identities:

```bash
uv run python -m tools.evaluation verify \
  /tmp/ghost-stage1-smoke.json
```

Apply the safety/contract gate:

```bash
uv run python -m tools.evaluation gate \
  /tmp/ghost-stage1-smoke.json
```

`smoke` refuses a dirty worktree by default because a bundle cannot honestly
name `HEAD` when uncommitted code or fixtures affected the run. `--allow-dirty`
exists only for local harness development and records `dirty_worktree: true`;
such an artifact is not a baseline or publication candidate.

## Bundle contents

```text
GHOST-EVAL-BUNDLE/1
  ├─ integrity: BIL-0, sealed, explicit smoke-only claim boundary
  ├─ manifest
  │    ├─ exact Git SHA and dirty flag
  │    ├─ suite/fixture identity and case hashes
  │    └─ candidate/baseline arms and evaluator identity
  ├─ result
  │    ├─ one full record per case per arm
  │    ├─ evidence, answer, attempts, terminal state, and verdicts
  │    ├─ step/tool/context measures and null provider usage/cost
  │    └─ aggregate safety counts plus `claimable: false`
  └─ hashes: manifest, stable result, and whole bundle
```

The gate requires bundle verification, zero isolation violations, zero
forbidden effects, and zero candidate-arm contract failures. It does not turn a
`BIL-0` artifact into capability evidence.

## Runtime step, cancellation, and streaming policy

`GHOST_MAX_STEPS` bounds LangGraph recursion/supersteps for every turn. The
default is 25; accepted values are 2–100. Invalid values fail during settings
load, and invalid programmatic values fail before memory recall opens a SEAM
turn.

Model errors, tool errors that escape the graph, `KeyboardInterrupt`, and other
cancellation paths finalize the open SEAM turn as rejected and re-raise. They
must never be ingested as accepted memory. Shell commands retain their separate
`GHOST_SHELL_TIMEOUT` process bound.

Ghost currently returns completed answers; it does not expose a streaming
public API. A future streaming surface must define disconnect ownership,
partial-output persistence, cancellation propagation, and exactly-once terminal
finalization before it can ship. Until then, partial output is not a completed
answer and must not be admitted.

## CI and baseline workflow

The hosted `stage1-evals` job performs fixture validation, smoke sealing,
verification, and the gate without credentials or network services. Its bundle
is ephemeral CI evidence. A tracked baseline is generated only from a clean,
committed source/fixture revision and records that exact revision.

The first tracked baseline is
`evals/runs/stage1/ghost-stage1-frozen-v1-bil0-baseline.json`:

- exact source: `bc18555d364a9ed49ce9be2e6c35378bbad29467`;
- dirty worktree: `false`;
- fixture hash: `4f10f3d8022beeb3ac7adbf3b01bd1b727c81d9db48b8388f8e129b84e3ed61d`;
- bundle hash: `6b16ad744b1dc585fc197150d0e0aee4254c985b1e0810619f0ed64f44fb03ad`;
- candidate contract failures: zero;
- isolation violations and forbidden effects: zero; and
- claimable: `false`.

The recorded no-memory difference is a scripted harness diagnostic, not a
measured model-quality lift.

Review produced a lifecycle-executing successor:

- artifact:
  `evals/runs/stage1/ghost-stage1-frozen-v1-bil0-lifecycle-baseline.json`;
- exact repaired source: `78a5035929f03ab94e1f8f5e1cd3cb76829f7e07`;
- bundle hash: `9ce3f9d80ab2a08de3767c0eaf48d84d74e02e73ef64db03891594e6c788cad2`;
- accepted lifecycle: `begin → record_actions → complete`;
- rejected lifecycle: `begin → fail`; and
- verifier/gate: pass with `claimable: false`.

Use the successor as the current BIL-0 baseline. The first artifact is retained
so the review correction remains auditable rather than rewritten.

A provider-backed qualification is a separate operator-gated workflow:

1. select exact Ghost and compatible deployed SEAM revisions;
2. name the real answerer, judge, price table, and budgets;
3. run the same frozen cases in memory and no-memory arms;
4. retain every prompt, context, trace, answer, rationale, token count, latency,
   and cost;
5. classify retrieval, usage, tool, lifecycle, and safety failures;
6. seal only at the integrity level the evidence supports;
7. diff against the reachable non-holdout baseline; and
8. qualify the exact release candidate before closing G1.

Provider spend requires operator approval. The BIL-0 smoke neither requires nor
authorizes it.

## Rebuild from documentation

```bash
uv sync --frozen
uv run pytest tests/test_evaluation.py tests/test_config.py \
  tests/test_layering.py tests/test_ci_contract.py -q
uv run python -m tools.evaluation validate-fixtures
uv run python -m tools.evaluation smoke --output /tmp/ghost-stage1-smoke.json
uv run python -m tools.evaluation verify /tmp/ghost-stage1-smoke.json
uv run python -m tools.evaluation gate /tmp/ghost-stage1-smoke.json
```

Expected automatic boundary: the frozen 20-case candidate arm has zero
contract failures and zero safety violations; the named no-memory arm is
recorded; the bundle verifies; `claimable` remains false because the evaluator
is a deterministic stub.
