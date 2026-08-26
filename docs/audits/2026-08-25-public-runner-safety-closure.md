# Public repository and runner safety closure

- Date: 2026-08-25
- Governing history: HISTORY#033
- Evidence boundary: GitHub repository settings, PR #5, and exact merged-head
  Actions results

## Result

The public-repository/private-runner exposure is closed in the fail-closed
state: automatic work runs on GitHub-hosted infrastructure, Private CI is
manual-only, and Ghost has no assigned self-hosted runner.

## Durable evidence

| Evidence | Observed state |
|---|---|
| Repository visibility | public |
| Safety PR | #5 merged |
| Merge head | `dbd421babf0703c8c339e7b8db8d51fc51b58282` |
| Exact-head run | `32907313331` |
| Required jobs | `repo-hygiene`, `brand-assets`, `package-smoke`: success |
| Private automatic dispatch | none |
| Assigned repository runners | zero |
| Repository secrets | zero |
| External contributor approval | all external contributors |
| Actions allowlist | GitHub-owned, verified, `astral-sh/setup-uv@*` |
| Secret scanning/push protection | enabled/enabled |
| Protected main | strict checks, PR, admin enforcement, conversation resolution, no force push/delete |

## Qualification boundary

This evidence qualifies the public automatic lane. It does not qualify the
private SDK/full-suite lane: no runner is assigned and no owner dispatch was
made. Organization runner-group inventory was unavailable without organization
admin authority. Any later runner assignment changes the boundary and requires
a fresh review.
