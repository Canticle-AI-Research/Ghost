# Public repository and hosted-runner boundary

Ghost is public. Public pull requests must never receive automatic code
execution on a personal or privileged self-hosted runner that can read private
SEAM repositories or operator files.

## Enforced topology

```text
public pull request or main push
        │
        ▼
GitHub-hosted Public CI
        ├─ frozen public project install
        ├─ full provider-free suite
        ├─ clean wheel install + command smoke
        ├─ no repository secrets
        └─ no self-hosted runner

reviewed owner decision
        │ explicit workflow dispatch
        ▼
manual Live Provider CI
        ├─ disposable GitHub-hosted runner
        ├─ paid live lane only with run_live=true
        └─ provider + SEAM endpoint credentials required
```

`.github/workflows/public-ci.yml` owns automatic fork-safe verification.
`.github/workflows/ci.yml` permits exactly `workflow_dispatch`; its jobs also
target `ubuntu-latest`, and its paid lane additionally requires `run_live=true`
plus explicit provider and SEAM service configuration.
`tests/test_ci_contract.py` fails if these boundaries drift.

## GitHub controls verified on 2026-08-25

- visibility: public;
- external-contributor workflow approval: all external contributors;
- default workflow permission: read;
- allowed actions: GitHub-owned, verified, and `astral-sh/setup-uv@*`;
- secret scanning: enabled;
- push protection: enabled;
- repository secrets: none;
- runners assigned to Ghost: zero; and
- `main`: pull requests required, administrators enforced, conversations
  resolved, force pushes/deletions blocked, and exact hosted checks
  `repo-hygiene`, `brand-assets`, `tests`, and `package-smoke` required with strict
  up-to-date status.

Organization runner-group inventory requires organization-admin authority and
was not queried. Zero repository-visible assigned runners is the current
fail-closed state. Any later assignment requires a new recorded review of the
host, group allowlist, and checked-out revision.

## Exact-head evidence

Safety commit `232048faefee15f9153f6f3fe216e6f745cc9175` merged through PR #5
as `dbd421babf0703c8c339e7b8db8d51fc51b58282`. The exact merge head passed all
three Public CI jobs in Actions run
[`32907313331`](https://github.com/Canticle-AI-Research/Ghost/actions/runs/32907313331).
Private CI did not auto-dispatch.

That run proves the earlier public workflow and settings boundary. The later
public-transport candidate must produce its own exact-head four-job evidence
before merge; no paid live run is implied.

## Operator rules

- Never add any trigger besides `workflow_dispatch` to Live Provider CI.
- Never move an automatic public job to `self-hosted`.
- Never add a private source dependency to Ghost or its lock.
- Never store a broad private-repository credential in this public repository.
- Treat a live workflow dispatch as authorizing the checked-out revision to
  spend provider credit and act through the configured SEAM principal.
- Keep paid live-provider tests behind the explicit `run_live` input.
- Reconcile GitHub settings again before assigning any runner or widening
  allowed Actions.

## Why a YAML tripwire is insufficient

A fork controls its workflow revision and can delete an early `exit 1` step.
The real boundary combines hosted-only automatic YAML with external repository
settings. Neither half is sufficient alone.

## Verification commands

```bash
uv run --no-project --with 'pytest>=8.3,<10' --with 'pyyaml>=6,<7' \
  pytest tests/test_ci_contract.py tests/test_local_gates.py -q
gh api repos/Canticle-AI-Research/Ghost/branches/main/protection
gh api repos/Canticle-AI-Research/Ghost/actions/permissions
gh api repos/Canticle-AI-Research/Ghost/actions/runners
gh run view 32907313331
```

Do not print secret values, runner registration tokens, SSH material, or
private session links while collecting this evidence.
