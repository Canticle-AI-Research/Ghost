# Action-provenance boundaries published

handoff_id: `ghost-action-provenance-boundaries-published-20260827`
supersedes: `ghost-action-provenance-boundaries-qualified-20260827`
handoff_status: `superseded`
history: `HISTORY#058`
created_at: `2026-08-27T20:48:43-05:00`

## Protected-main result

PR #26 merged exact source
`21782f5024897e89dfb4d8f25369a2cc59999ea8` as implementation merge
`2a85aab6e0696ef64844e80ade70fe75628e9634`. Exact-source run `33133873076`
and exact merge-head run `33133921906` passed all six protected provider-free
jobs.

Ghost now scopes action extraction to one unique current-turn human-message
ID, accepts request/result evidence only from concrete framework roles, and
revalidates framework-free attempts without coercion at SEAM egress. Real
ToolNode plus SQLite regressions prove persisted nonzero artifacts and
two-turn non-replay. Non-UTF-8 shell output retains a typed terminal result.

The registered artifact report is
`docs/audits/2026-08-27-action-provenance-boundaries.md`.

This is merged source, not package publication, release, deployment, live
provider/SEAM qualification, or an exactly-once provenance claim. GPROV-001
remains open: a tool can complete before a later graph failure prevents the
result state from reaching the lifecycle.

## Resume order

1. Specify the coordinated Ghost/SEAM GPROV-001 protocol: stable turn/tool
   identity, durable start/terminal journal, idempotent outbox delivery, status
   lookup, and retry/restart reconciliation.
2. Require exactly one action record across post-tool model failure, recursion
   failure, checkpoint-write failure, response loss, retry, and restart, while
   never granting failed evidence accepted support.
3. Close GTOOL-003 whole-process-tree timeout termination, then GTOOL-004
   streaming output bounds.
4. Keep shell use off for normal operation until the remaining six P0 issues
   close.
5. Preserve the separate avatar, repository-guidelines, and runner-safety WIP;
   clean them only through an explicit preservation-or-discard decision.
