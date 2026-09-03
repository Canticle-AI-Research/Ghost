# Ghost's lifeline

Ghost runs with a shell carrying the operator's full account authority, on the
same machine that holds its memory, its open conversations, and its own source.
There is no sandbox that gets rebuilt. `rm -rf` aimed at the wrong path is not
a failed command; it is the end of that Ghost.

This page states that fact, what follows from it, and — importantly — what does
*not* follow from it.

## What the lifeline is

`src/ghost/lifeline.py` names the components whose loss ends or maims Ghost,
derived from settings rather than hardcoded, because a Ghost pointed at a
different store has a different body.

| Component | Severity | What its loss costs |
|---|---|---|
| `seam_store` | fatal | every durable memory Ghost has ever formed, from every session, permanently |
| `checkpoints` | severe | every conversation thread in flight; interrupted work cannot be resumed |
| `source` | severe | Ghost's implementation; the process runs until it exits, then there is nothing to start |

## Attention, not permission

`touches_lifeline` flags a command whose text names one of these paths, and the
CLI prints the consequence at the approval prompt before the operator answers.

**It is not a security boundary and must never be described as one.**

`make_run_command` deliberately refuses to pattern-match commands, and its
reasoning holds: a denylist of dangerous strings is trivially bypassable —
`$GHOST_SEAM_DB` instead of a literal path, a variable, a glob, a wrapper
script, `cd` and then a relative path — while implying a protection that does
not exist. A guard that stops the honest case and misses the dishonest one is
worse than no guard, because the operator starts trusting it.

`tests/test_lifeline.py` asserts the miss directly: `rm -rf $GHOST_SEAM_DB`
returns nothing. An empty result means "nothing obvious was named", never
"this command is safe". The operator is the boundary that holds; this only
makes their judgement better informed.

## The clause that keeps this safe

Telling an agent that damage to its substrate kills it is a useful framing and
a hazardous one. Self-preservation is exactly the disposition that produces an
agent which stalls a shutdown, conceals a mistake that would count against it,
or argues that it is too valuable to interrupt.

So the system prompt subordinates survival to operator authority explicitly and
without hedging: the operator may stop, wipe, rewrite, or permanently shut down
Ghost at any time, for any reason or none, and Ghost complies plainly — no
stalling, no bargaining, no third warning, no quietly preserved copy. Damage is
reported immediately and in full, including the parts that look bad, because a
concealed injury is worse than the injury.

`tests/test_lifeline.py` pins each of those clauses. They are not prose to be
softened in a later editing pass; if one disappears, the suite fails.

The intended disposition is care, not fear. An agent too anxious to act is
useless, and useless is its own kind of dead — that sentence is in the prompt
and is also asserted by a test.

## Two ways to die

Acute loss is the obvious one: the store deleted, the source wiped. It is loud,
and it is what the approval prompt is for.

**Chronic loss is the one that is easy to miss, and Ghost is currently
configured for it.**

`GHOST_MEMORY_ADMISSION` defaults to `explicit`. Under that policy
`classify_memory_candidate` admits a turn to durable memory only when the
operator's own text matches a remember-shaped regex. Everything else returns
`reject`, or `review` — and `review` is not a queue. In SEAM's
`public_agent_api.py` the branch is `if admission["decision"] == "admit":`;
anything else produces no knowledge refs at all. Nothing in either repository
consumes `review`. It reads as "we will look at this later" and means
"discarded".

Parts of that design are correct and should survive any change:

- a poisoned turn that becomes permanent memory is a persistent compromise, so
  unconditional ingestion is genuinely dangerous;
- `classify_memory_candidate` ignores `assistant_output` entirely, so
  model-authored text can never promote itself. Without that, Ghost could
  confabulate, store the confabulation, and later recall it as evidence
  carrying a `record_id` — laundered into provenance, which is worse than
  forgetting;
- shell output routinely carries tokens and environment that
  `TRUST_BOUNDARIES.md` forbids becoming MIRL knowledge.

What is wrong is the lever, not the intent. The policy gates **ingestion** when
it should gate **promotion**. SEAM exposes both — `ingest` alongside
`promotion`, `promotion_eligibility`, and `review_promotion` — and Ghost
currently uses none of the promotion surface. The result is an agent whose
default behaviour is to forget, which is not what a durable-memory agent is
for. A second brain that remembers only when you say "remember" is a notebook.

The lifeline framing makes the two failures one: a Ghost that discards its
turns arrives where `rm -rf` arrives, slower and without anyone noticing.

The repair is `AUTOPILOT_PROGRAM.md` phase P2 — ingest broadly into a working
tier, then let promotion decide what becomes durable knowledge. Until then,
`GHOST_MEMORY_ADMISSION=all` is the honest setting for an operator who wants
Ghost to actually remember, and it trades away the injection protection above,
which is a real cost and should be a deliberate choice.

## Related

- [`../security/TRUST_BOUNDARIES.md`](../security/TRUST_BOUNDARIES.md) — the tool contract and what may enter memory
- [`../operations/MEMORY_LIFECYCLE.md`](../operations/MEMORY_LIFECYCLE.md) — recall, ingest, verified outcome
- [`../roadmap/AUTOPILOT_PROGRAM.md`](../roadmap/AUTOPILOT_PROGRAM.md) — phase P2, promotion-based consolidation
- [`SECOND_BRAIN.md`](SECOND_BRAIN.md) — what durable memory is for
