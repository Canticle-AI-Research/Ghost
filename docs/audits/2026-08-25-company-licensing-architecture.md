# Company licensing architecture audit

Date: 2026-08-25
Governing event: HISTORY#027
Scope: Ghost, adjacent Canticle/SEAM distribution surfaces, planned Canticle
Core and SEAM-U boundaries, and pre-company ownership controls

## Conclusion

The local candidate now uses one deliberate three-lane distribution model:

```text
Apache-2.0 integration edge
        │
        ├─ thin client, protocols, examples, connectors
        │
        ▼
PolyForm Shield 1.0.0 runnable products
        │
        ├─ Ghost, Canticle Core, SEAM SDK, SEAM Node
        │
        ▼
permanent proprietary core and hosted systems
        └─ SEAM/MIRL internals, SEAM-U assets, control plane, private data
```

PolyForm Shield was placed only where source is intended to be distributed for
operators to run or adapt while withholding use to provide competing products.
It was not placed on the Apache thin client, brand assets, undistributed
runtime internals, or planned model assets.

## Observed placements

| Surface | Observed local action | State boundary |
|---|---|---|
| Ghost | exact Shield text, required notice, package metadata, tests, docs | local uncommitted candidate |
| SEAM SDK | BUSL replaced by exact Shield text, notice, metadata, boundary page | local uncommitted sibling-repository candidate |
| Canticle Core | Shield text, notice, distribution architecture | non-Git architecture scaffold; no OS implementation claim |
| SEAM Node | Shield text and notice | non-Git scaffold; no node implementation claim |
| SEAM thin client | Apache-2.0 preserved; notice and boundary clarified | non-Git local package; client only |
| SEAM Runtime scaffold | All Rights Reserved notice, not Shield | non-Git scaffold; does not relicense canonical runtime |
| canonical private SEAM runtime | deliberately untouched in this task | separate repository and continuity authority |
| SEAM-U | no repository, weights, tokenizer, or checkpoint located | planned proprietary model boundary only |

## Ownership and inbound IP

The identified current holder remains Nicholas Thomas. No legal entity or
founder-to-company assignment is recorded. Notices therefore use the founder's
name and must not be changed to a future company name until the entity exists
and the relevant rights are assigned in writing.

External pull requests are paused by the root `CONTRIBUTING.md` until an
authorized receiving entity and contributor agreement exist. The root
`TRADEMARKS.md` makes clear that the software license does not grant the right
to rebrand modified forks with Canticle marks.

## Verification boundary

The official PolyForm Shield 1.0.0 text was compared byte-for-byte with the
Ghost, SEAM SDK, Canticle Core, and SEAM Node `LICENSE` files. Ghost passed 190
provider-free tests with eight live tests deselected; its build and artifact
metadata inspection passed. The SEAM SDK passed its nine tests, Ruff, build,
and artifact metadata inspection using the canonical private runtime checkout
on `PYTHONPATH`. The Apache thin client passed its 58 tests and Ruff. Scoped
Ghost Ruff and `git diff --check` passed; full Ghost Ruff retained five known
avatar/image-tool findings unrelated to licensing.

These checks prove repository consistency and artifact inclusion. They do not
interpret enforceability, establish ownership, approve a trademark, or replace
review by qualified counsel in the company's jurisdiction.

## Required next legal actions

1. Form the entity and execute a scheduled founder IP assignment.
2. Have counsel review the Shield line-of-business notices and interim
   trademark/contribution policies.
3. Adopt commercial, service, privacy, security, contributor, employment, and
   contractor agreements before accepting outside IP or customers.
4. Reconcile the canonical SEAM runtime under its own repository protocol; do
   not infer a runtime relicense from SDK or scaffold files.
5. Commit, review, merge, and release each repository independently, with exact
   artifact and remote evidence.
