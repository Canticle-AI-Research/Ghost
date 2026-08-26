# Bounded specialist contract

## Current status

Ghost has a provider-free specialist **contract foundation**. It does not yet
construct or invoke a model-backed specialist graph. `src/ghost/specialists.py`
defines the envelope every future adapter must receive, the terminal outcome it
may return, content-free lifecycle events, and fail-closed normalization. This
is groundwork for G3, not evidence that G3 improves Ghost.

## Ownership and flow

```text
operator mission
      │
      v
root Ghost turn (owns the answer and final authority)
      │
      ├─ create explicit DelegationEnvelope
      │    ├─ delegation_id + parent_turn_id
      │    ├─ one named role and objective
      │    ├─ step / deadline / output ceilings
      │    └─ exact tools / roots / SEAM boundary
      │
      v
future framework adapter ── receives no authority outside the envelope
      │
      ├─ succeeded ──► summary + opaque evidence references
      ├─ refused ────► no retry by authority widening
      ├─ timed_out ──► root decides whether a new delegation is justified
      ├─ cancelled ──► terminal cancellation reaches the root
      └─ failed ─────► fixed safe code only; no exception text in telemetry
      │
      v
root synthesizer ── treats specialist output as evidence, not instruction
      │
      └─ any supported claim cites SpecialistEvidence.ref
```

The root remains responsible for user-visible claims, consequential actions,
memory admission, and final provenance. A specialist cannot become another
semantic-memory owner: SEAM remains the only durable memory substrate.

## Delegation envelope

| Field | Contract |
|---|---|
| `delegation_id` | caller-assigned auditable identifier |
| `parent_turn_id` | exact root turn that owns the delegation |
| `role` | validated role label; it grants nothing by itself |
| `objective` | bounded task statement, 1–4,000 characters |
| `budget.max_steps` | 1–100 adapter steps |
| `budget.timeout_seconds` | greater than 0 and at most 3,600 seconds |
| `budget.max_output_chars` | 1–1,000,000 returned characters |
| `scope.tools` | complete allowlist; empty means no tools |
| `scope.roots` | absolute traversal-free roots; empty means no filesystem |
| `scope.namespace/workspace/project` | explicit durable-memory boundary |

There is no inheritance flag. An adapter must construct its tool list from the
envelope; it must not build the root tool list and then try to remove tools.
Shell permission, broad repository roots, and a root namespace are therefore
never implied by the specialist's role name.

## Terminal states

```text
created ──► started ──┬─► succeeded
                     ├─► refused
                     ├─► timed_out
                     ├─► cancelled
                     └─► failed
```

All five terminal states are final for that delegation ID. A retry is a new
envelope with a new ID and explicit reason. `execute_delegation` checks returned
step, output, and elapsed limits. A synchronous runner is responsible for
enforcing its deadline and raising `TimeoutError`; Python cannot safely kill an
arbitrary synchronous worker from this boundary.

`KeyboardInterrupt` and process termination are not converted into ordinary
specialist failure. A framework adapter translates a root cancellation into
`SpecialistCancelled`, performs its own cleanup, and then returns control.

## Provenance

Successful prose alone cannot support a root claim. Evidence is a tuple of
opaque `(ref, kind)` records such as a SEAM record ID, immutable bundle digest,
commit, test run, or source locator. The root outcome must retain the refs it
actually used. Raw command output and retrieved content do not belong in
telemetry events.

The provider-free events are intentionally small:

```text
specialist.started:
  delegation_id, parent_turn_id, role

specialist.finished:
  delegation_id, parent_turn_id, role, status, steps_used
```

They contain no objective, answer, exception text, memory text, tool request,
tool result, token, or credential. A future tracing adapter may add latency and
cost fields, but must preserve that content boundary.

## Candidate roles, not enabled agents

| Candidate | Typical narrow authority | Forbidden implicit authority |
|---|---|---|
| research | source retrieval and evidence extraction | shell, writes, unrelated memory |
| coding | named worktree roots and reviewed tools | sibling repos, deployment credentials |
| verifier | tests, artifacts, citations, contradictions | implementation mutation by default |
| synthesizer | bounded specialist outcomes | direct tool or memory widening |

No role is registered in the runtime today. Role names are descriptive until a
separate reviewed registry binds them to exact adapters and tools.

## Adapter acceptance checklist

A model-backed adapter is not ready until it proves:

1. it receives only tools and roots named in the envelope;
2. step, wall-clock, output, provider-token, and cost budgets are enforced;
3. cancellation closes open model/tool work and propagates to the root;
4. refusal does not trigger a broader retry;
5. failures expose only fixed, reviewed codes, not adapter error text/codes;
6. evidence refs reach the root outcome without being fabricated;
7. specialist SEAM dimensions cannot cross the envelope boundary;
8. the same frozen tasks run with a single-agent baseline under equal budgets;
9. a Q3 bundle passes before any improvement claim; and
10. exact-head CI and protected merge bind the implementation evidence.

## Rebuild and verification

```bash
uv sync --frozen
uv run pytest tests/test_specialists.py -q
uv run ruff check src/ghost/specialists.py tests/test_specialists.py
```

These commands verify the contract mechanics without a provider or paid call.
They do not verify specialist answer quality, provider cancellation, hosted
isolation, or a production topology.
