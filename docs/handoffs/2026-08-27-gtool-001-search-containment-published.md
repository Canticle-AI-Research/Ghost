# GTOOL-001 search containment published

handoff_id: `ghost-gtool-001-search-containment-published-20260827`
supersedes: `ghost-gtool-001-search-containment-qualified-20260827`
handoff_status: `current`
history: `HISTORY#053`
created_at: `2026-08-27T17:04:08-05:00`

## Protected-main result

PR #21 merged exact source
`fbe1744e7c1025161a4808dc78bf020df59f39b6` as
`main@ba68c3852a1787efd568d3e221c2935f5a9af4b7`. Exact PR run
`33120765857` and exact merge-head run `33120850903` passed all six protected
jobs: repository hygiene, brand assets, Python 3.11, Python 3.13, package smoke,
and Stage 1 evaluations.

The protected source now contains the registered structural-remediation ledger
and closes GTOOL-001. Repository search rejects empty, absolute,
drive-qualified, and parent-traversal globs; resolves candidates against the
root that produced them; opens with non-following/nonblocking flags; and checks
the opened descriptor remains inside that root before metadata or bounded
content reads. If descriptor identity is unavailable, search fails closed.

This is merged source, not a package publication, release, deployment, live
provider validation, or claim that the remaining ledger items are closed. The
separate avatar worktree remains untouched.

## Resume order

1. Start GTOOL-002 in a new focused branch/worktree from current protected
   main. Preserve the real shell exit code from execution through tool-result
   parsing, SEAM action evidence, and accepted-outcome support.
2. Then close GTOOL-003 process-tree timeout/output bounds and GTOOL-004
   authority-config parsing before normal shell use.
3. Keep `GHOST_ENABLE_SHELL` off for normal operation until GTOOL-002 through
   GTOOL-004 and GST-001/GST-002 close.
4. Keep the avatar workstream separate and do not publish the sdist until
   GPKG-001 closes.
5. After the immediate P0/P1 lane, build provider-free Q3 G1/G2 mechanics and
   stop before any paid execution for explicit operator approval.
