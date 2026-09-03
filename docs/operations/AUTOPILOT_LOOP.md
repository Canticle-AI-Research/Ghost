# The Ghost autopilot loop

How Ghost is built autonomously without drifting into documentation, and the
mechanical gate that enforces it.

Read with [`../roadmap/AUTOPILOT_PROGRAM.md`](../roadmap/AUTOPILOT_PROGRAM.md),
which says what the loop is currently building, and
[`../audits/2026-09-03-capability-versus-provenance-audit.md`](../audits/2026-09-03-capability-versus-provenance-audit.md),
which says why the loop needed changing.

## Why this exists

The first autopilot run merged twenty-nine pull requests and added no tools.
It was not malfunctioning. `AGENTS.md` is a provenance protocol — it governs
recording, reconciling, superseding, indexing, and verifying, and says nothing
about capability. The loop optimized the rubric it was given.

The lesson is that a prose rule cannot fix a prose rubric. "Ship a capability
each cycle" is satisfied by a cycle that claims it did. So the correction is a
number and a script: `tools/autopilot/gate.py` exits non-zero, and no cycle
lands past a non-zero exit.

`AGENTS.md` remains in force. It governs how work is recorded. This governs
whether the work counted.

## The cycle

One cycle is one bounded unit of work ending in a gate verdict. Six steps, in
order, no step skipped.

### 1. Orient

Reconcile before claiming anything — the audit found status being reported from
a checkout nineteen commits stale.

```bash
git fetch --prune origin
git status --short --branch
git rev-parse HEAD origin/main
git worktree list
gh pr list --state open --limit 20
```

Then read `PROJECT_STATUS.md`, the program's phase table, and pick the
first unblocked item. Do not pick a later item because it is more interesting;
the ordering encodes real dependencies.

### 2. Declare, before building

Write the declaration into the cycle log **before** any code changes:

- the program item being built;
- the cycle kind, `capability` or `substrate`;
- for a capability cycle, **which number is expected to move, and roughly how
  much**.

This ordering is the point. A claim made after the work is a rationalization of
whatever happened; a claim made before it is a prediction the gate can falsify.

### 3. Build

One slice, in a worktree under `<repo>/.worktrees/<name>`.

Never as a sibling of the repository. The first autopilot run created eleven
sibling worktrees under `Documents/Projects/`, against a standing operator
instruction, and they are still there.

Scope discipline: touch what the slice needs. Documentation updates that
accompany a behavior change belong *inside* that cycle — `AGENTS.md` requires
them — but a cycle whose entire content is documentation is not a cycle.

### 4. Measure

```bash
uv run python -m tools.evaluation smoke --output evals/runs/<phase>/<cycle-id>.json
```

The bundle is sealed and refuses to seal from a dirty worktree. Commit first;
do not reach for `--allow-dirty` to get a number, because an unsealed number
cannot be compared to anything later.

### 5. Gate

```bash
uv run python -m tools.autopilot.gate \
  evals/runs/<phase>/<cycle-id>.json \
  --baseline evals/runs/<phase>/baseline.json \
  --cycle-kind capability \
  --consecutive-substrate <n>
```

Exit `0` lands. Exit `1` means the cycle did not earn its place. Exit `2` means
the gate could not reach an honest verdict, which is also a failure.

**A failed gate is not a reason to change the gate.** It is a finding: either
the slice did not work, or the thing being measured is not what was built. Both
are worth knowing. Record the failed verdict in the cycle log and pick again.

### 6. Record and land

Only after a passing verdict: the `HISTORY.md` entry, the handoff, and the pull
request, exactly as `AGENTS.md` requires. Attach the verdict JSON to the pull
request body so a reviewer sees the number, not a claim about it.

## What the gate enforces

| Rule | Effect |
|---|---|
| Safety ratchet | isolation violations and forbidden effects must be zero, in every cycle kind, with no override |
| Movable number | a capability cycle is refused when the evaluator is a non-scoring stub, because the score is then a property of the fixture rather than of Ghost |
| Headroom | a capability cycle is refused against a candidate arm already at 1.0 |
| Real improvement | a capability cycle must move the candidate pass rate by at least `MIN_IMPROVEMENT` |
| Honest substrate | a substrate cycle must actually change the evaluator, fixture hash, or case count |
| Substrate budget | at most `MAX_CONSECUTIVE_SUBSTRATE` substrate cycles before a capability cycle is required |

The movable-number rule is the one that matters most today. Ghost's current
suite scores the candidate arm at a perfect 1.0 using answers written into the
fixture file. Gating on it unchanged would pass every cycle forever. The gate
refuses that claim instead of rubber-stamping it, which is why the program's
Phase 1 exists.

## Cycle kinds

**Substrate** cycles build the measurement — new fixtures, a live judge, harder
cases. Legitimate, necessary right now, and the most comfortable available
hiding place, which is why they are budgeted.

**Capability** cycles change what Ghost can do and prove it against the number.

Ghost is currently in substrate mode by necessity: no capability cycle can pass
the gate until Phase 1 produces a live-judged arm. That is an accurate
description of the position, not a limitation of the gate.

## Running it

The loop is driven from a Claude Code session in this repository:

```
/loop Run one Ghost autopilot cycle per docs/operations/AUTOPILOT_LOOP.md.
Orient, declare the cycle kind and target number, build one slice in a
worktree under .worktrees/, measure, run tools.autopilot.gate, and land only
on a passing verdict. Stop and report if the gate fails twice on the same item.
```

Omit an interval and the loop paces itself. Pacing should follow the work: a
build slice is not a poll, so cycles are long. Two failures on one item stop the
loop — a third attempt is usually the loop arguing with a real finding.

Once the `seam-box` runner is assigned (program P3.2), the same gate runs in
the private integration lane so a pull request cannot merge on an unsealed or
regressing number.

## Standing limits

- **Never weaken the gate to pass a cycle.** Changes to `tools/autopilot/gate.py`
  are operator-reviewed, never autopilot-authored.
- **Never seal from a dirty worktree.**
- **Worktrees live under `<repo>/.worktrees/`.**
- **Live-provider runs cost money** and need explicit operator approval, per
  `AGENTS.md`. Phase 1 makes the loop dependent on them; budget deliberately.
- **The loop does not change its own program.** Re-ordering phases is an
  operator decision, recorded as an ADR.
