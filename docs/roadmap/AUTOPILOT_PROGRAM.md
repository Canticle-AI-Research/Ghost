# Ghost autopilot program

The dependency-ordered plan for making Ghost capable, and the benchmark-gated
loop that builds it without drifting back into documentation.

This program supplements [`SECOND_BRAIN_ROADMAP.md`](SECOND_BRAIN_ROADMAP.md);
it does not replace it. The roadmap says what Ghost should become. This says
what the autopilot loop is allowed to spend a cycle on, and what it must prove.

Its premises are the findings in
[`../audits/2026-09-03-capability-versus-provenance-audit.md`](../audits/2026-09-03-capability-versus-provenance-audit.md).

## The correction

Twenty-nine merged pull requests grew the evidence around four tools without
growing the four tools. The cause was the rubric, not the work: `AGENTS.md`
governs provenance and says nothing about capability, so an agent optimizing it
produces provenance. The correction is a second gate that provenance cannot
satisfy — a number that only a real capability change can move.

That number is `task_success_delta` from the two-arm evaluation. It is already
computed. It is not yet real. Phase 1 exists to make it real, and until it is,
the gate runs in substrate mode.

## Operator decisions carried by this program

1. **Ghost runs on SEAM** in all three senses: a live SEAM service and a real
   turn; Ghost doing real engineering work on the Seam repository; and the
   private integration lane running on the `seam-box` self-hosted runner.
2. **The next capability is SEAM's unused surface** — promotion and
   consolidation, graph products, recoverable operations — so memory compounds
   rather than accumulates.
3. **The autopilot gate is the benchmark score.** A cycle that does not move a
   real number does not count as progress.

Decisions 2 and 3 fit together: memory consolidation is exactly the kind of
capability a memory benchmark can measure. The capability track and the
measurement track share one number.

## Phase 0 — reconcile and make runnable

Nothing downstream is verifiable until Ghost can execute one turn and status
reports describe the real head.

- **P0.1 Reconcile the checkout.** The primary checkout is 19 commits behind
  `origin/main`. Fast-forward `main`, and rebase or retire the stale
  `agent/avatar-u1-temporal-integration` branch.
- **P0.2 Quarantine the avatar work.** The avatar subsystem exists only as
  untracked files. Commit it to its own branch and document its five `GHOST_*`
  variables in `CONFIGURATION.md`, which clears the two failing tests. It is a
  U-track concern and must not gate G-track capability.
- **P0.3 Collapse the worktree sprawl.** Eleven sibling worktrees under
  `Documents/Projects/` violate the standing operator instruction. Land or
  retire each, then relocate any survivor under `<repo>/.worktrees/`.
- **P0.4 Bring SEAM up.** `seam serve --port 8765` against the running
  pgvector, with `SEAM_BASE_URL` and `SEAM_API_TOKEN` wired into Ghost's
  environment.
- **P0.5 Execute one real turn.** One verified end-to-end invocation: recall,
  model, tool, `finalize_verified`, durable record. This is the first time
  Ghost's own contract is exercised against a real service rather than a fake.

Exit gate: a live turn, recorded, with the resulting SEAM record recalled by a
second Ghost process started fresh.

## Phase 1 — make the number real

The gate cannot gate a constant. Today `ghost-memory` scores 1.0 against
pre-written answers; the suite proves the harness, not the agent.

- **P1.1 Live-judged arm.** Replace the scripted `_SmokeGraph` answer with a
  real model turn for a `live` integrity level, keeping the deterministic stub
  as the provider-free lane. Same fixtures, same two arms, real answers.
- **P1.2 A judge that can disagree.** The scripted judge scores substring
  containment against expectations authored beside the answers. A live arm
  needs a judge whose verdict is not implied by the fixture.
- **P1.3 Headroom.** A saturated candidate arm cannot show improvement. Extend
  the corpus with cases the current Ghost fails — multi-hop recall, temporal
  ordering, contradiction across sessions, stale-versus-current views — so the
  score starts below 1.0 and has somewhere to go.
- **P1.4 Seal a live baseline.** One sealed bundle at a known revision that
  every later cycle is compared against.

Exit gate: two live runs at the same revision produce a stable score below 1.0,
and a deliberately weakened recall path measurably lowers it. A number that
does not fall when memory is broken is not measuring memory.

## Phase 2 — wire SEAM's unused surface

The chosen capability, built against Phase 1's number. Each slice ships a
capability *and* its movement in the score, or it does not ship.

- **P2.1 Consolidation.** `promotion_eligibility` and `promotion` so repeated
  or reinforced facts are promoted rather than re-stored. Targets contradiction
  and staleness cases.
- **P2.2 Graph products.** `graph_products` and `rebuild_graph_products` so
  recall reaches derived structure, not only raw records. Targets multi-hop.
- **P2.3 Durable operations.** `recoverable_operations` and `resume_operation`
  so an interrupted ingest or promotion resumes instead of stranding a run.
- **P2.4 Correction and forgetting end to end.** The lifecycle operations are
  already reachable from the CLI; carry them through the agent surface so Ghost
  can act on an operator correction within a turn.

Exit gate: each slice moves `task_success_delta` on the live suite, with the
sealed before-and-after bundles recorded.

## Phase 3 — Ghost works on Seam

The capability proof. An agent that improves its own substrate is the claim
worth making.

- **P3.1 Point Ghost at Seam.** `GHOST_TOOL_ROOTS` and `GHOST_SHELL_WORKDIR`
  set to the Seam checkout, shell enabled with approval on.
- **P3.2 Private integration CI on `seam-box`.** Assign the self-hosted runner
  so the live SEAM and live provider lane runs. This lane has never run.
  Detach the runner before the repository's visibility changes.
- **P3.3 Supervised real work.** Ghost takes a scoped, real Seam task under
  operator approval, and the result is reviewed as engineering output.

Exit gate: a merged Seam change whose authoring turn is recallable from SEAM
with its provenance intact.

## Deferred deliberately

- **Specialist activation.** `specialists.py` is a finished contract with no
  adapter — the largest finished-design-to-absent-capability ratio in the
  repository, and tempting for that reason. It stays deferred until Phase 1
  gives a number that can tell whether delegation actually helps. Activating it
  first would repeat the original error at a larger scale.
- **New write tools.** `edit_file` and friends are real gaps, but they widen
  the trust boundary without moving the memory number this program gates on.
- **The avatar and operator UI.** Parallel U-track. Cannot promote core
  maturity and must not consume capability cycles.

## Phase status

| Phase | Status | Blocking condition |
|---|---|---|
| P0 reconcile and make runnable | next | none; start here |
| P1 make the number real | next | P0.4 and P0.5 |
| P2 wire SEAM's unused surface | planned | P1 exit gate |
| P3 Ghost works on Seam | planned | P0.3, P2.1 |
| Specialist activation | deferred | P1 exit gate |

The loop that executes this program, and the gate that keeps it honest, are
specified in
[`../operations/AUTOPILOT_LOOP.md`](../operations/AUTOPILOT_LOOP.md).
