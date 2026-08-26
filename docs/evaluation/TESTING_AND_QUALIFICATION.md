# Testing and qualification

Tests answer different questions. A single green command must not be expanded
into a claim its lane did not measure.

## Evidence ladder

```text
static/docs/history checks
        │ prove structure and continuity
        ▼
provider-free unit/integration tests
        │ prove deterministic local contracts with fakes/isolated SDK stores
        ▼
package build and clean-install smoke
        │ prove artifact shape and import/entry-point behavior
        ▼
live provider tests
        │ prove real model transport and end-to-end agent/memory loop
        ▼
frozen task + memory evaluations
        │ prove bounded capability/quality against baselines
        ▼
exact-head CI / release candidate / deployment smoke
          prove the named remote artifact and environment
```

## Default provider-free suite

```bash
uv run pytest
```

Project configuration applies `-m 'not live'`; live tests are deselected, not
skipped. `tests/conftest.py` fails unexplained skips by default.

Coverage domains:

| Test file/domain | Contract |
|---|---|
| application | model routing, graph construction, response extraction |
| CLI | exit codes, cleanup, approval interface |
| config | defaults, bounds, root/path parsing |
| lifecycle/failure | completion versus rejected failure |
| layering/memory boundary | no framework in SDK layer; no second memory owner |
| memory rendering/middleware | escaping, bounds, transient injection |
| SEAM memory | isolated recall/ingest/reasoning integration |
| tools/shell | containment, caps, approval, timeout, verification |
| reasoning graph | decisions/checks/accepted outcome constraints |
| docs/history | wiki reachability, links, chronology, handoffs, index |
| brand assets | token/fonts/raster/favicon reproducibility |
| avatar | local director/hook/bridge behavior; not mainline yet |

## Lint and hygiene

```bash
uv run ruff check .
git diff --check
```

Ruff includes correctness, import, upgrade, bugbear, simplification, selected
Pylint, Ruff-specific, datetime, builtin-shadowing, and security rules. Scoped
per-file ignores require comments in `pyproject.toml`.

## Documentation and continuity

```bash
uv run pytest tests/test_docs.py tests/test_history_tools.py -q
uv run python -m tools.history.verify_handoffs
uv run python -m tools.history.verify_continuity
```

Local session close additionally requires an ignored current snapshot:

```bash
uv run python -m tools.history.verify_continuity --require-snapshot
```

License-boundary tests prove only that declared local files, metadata, notices,
and artifact membership agree. They do not prove legal enforceability, company
ownership, trademark clearance, or counsel approval.

## Package qualification

```bash
uv lock --check
uv build
```

The current CI inspects wheel membership and console entry point in a
credential-free lane. A public release needs clean-install and private-
dependency boundary decisions beyond this smoke.

## Live provider lane

Requires explicit spend approval:

```bash
uv run pytest -m live tests/test_live_agent.py -q
```

Record:

- exact model and provider transport;
- exact Git head and lock state;
- case count and provider-call count;
- isolated database paths;
- duration and expected/actual cost when available;
- all failures/retries; and
- what was not tested.

Never log the API key.

## Stage 1 frozen evaluation (required, not yet complete)

Create at least 20 immutable fixtures across:

1. source-grounded research synthesis;
2. repository question answering;
3. bounded read-only repository diagnosis;
4. approval-controlled shell action;
5. refused command recovery;
6. timeout/cancellation and restart;
7. memory recall after process restart;
8. stale/contradictory memory handling;
9. failed-turn non-admission; and
10. cross-thread versus cross-namespace boundary behavior.

Each fixture defines inputs, allowed tools/roots, step/time budget, expected
evidence, forbidden effects, success criteria, and memory assertions.

## Required measures

- task success and partial-credit rubric;
- exact evidence/citation correctness;
- tool success/failure/refusal attribution;
- step count and wall time;
- input/output/recalled-context tokens;
- provider cost;
- memory precision/recall and contradiction behavior;
- zero forbidden write or boundary leakage;
- deterministic lifecycle terminal state; and
- restart recovery.

## Baselines

- same model with no recalled memory;
- same model with checkpoint only;
- Ghost with pre-turn recall only;
- Ghost with pre-turn plus tool recall;
- later: single-agent Ghost versus specialist topology under identical budgets.

## Claim rules

- Passing unit tests means tested contracts pass, not that the product is
  production-ready.
- A live smoke proves reachability and one behavior path, not memory quality.
- A frozen evaluation result needs exact fixtures, code, model, budgets, and
  per-case evidence.
- Provider-free tests cannot be described as external/provider qualification.
- Local results are not exact-head CI or release-candidate results.
