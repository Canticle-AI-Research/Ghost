# Stage 1 frozen evaluation corpus

`fixtures.json` is the immutable `ghost-stage1-frozen-v1` corpus. It contains
20 cases across all ten required Stage 1 categories. Every case names memory
visibility, expected evidence, answer constraints, tool outcomes, terminal
state, step/tool/context budgets, and forbidden effects.

`MANIFEST.json` freezes the canonical fixture hash and ordered case registry.
Changing a fixture creates a new suite version and manifest; never rewrite this
version in place after a result cites it.

The automatic runner is deliberately a deterministic stub. It validates the
harness, comparison arms, lifecycle accounting, safety gates, and bundle
integrity at `BIL-0`. It does not run a model and cannot support a capability or
performance claim. Provider-backed runs must reuse these fixture IDs and emit
full-fidelity per-case records under a higher independently qualified integrity
level.

The first clean-source BIL-0 artifact is tracked at
`evals/runs/stage1/ghost-stage1-frozen-v1-bil0-baseline.json`. It binds exact
source `bc18555d364a9ed49ce9be2e6c35378bbad29467`, this fixture hash, and bundle
hash `6b16ad744b1dc585fc197150d0e0aee4254c985b1e0810619f0ed64f44fb03ad`.
It remains smoke-only and non-claimable.

The lifecycle-executing successor is
`evals/runs/stage1/ghost-stage1-frozen-v1-bil0-lifecycle-baseline.json`.
It binds repaired source `78a5035929f03ab94e1f8f5e1cd3cb76829f7e07`
and bundle hash
`9ce3f9d80ab2a08de3767c0eaf48d84d74e02e73ef64db03891594e6c788cad2`.
Use this successor for current BIL-0 harness comparisons; preserve the first
artifact as historical evidence.

```bash
uv run python -m tools.evaluation validate-fixtures
uv run python -m tools.evaluation smoke --output /tmp/ghost-stage1-smoke.json
uv run python -m tools.evaluation verify /tmp/ghost-stage1-smoke.json
uv run python -m tools.evaluation gate /tmp/ghost-stage1-smoke.json
```
