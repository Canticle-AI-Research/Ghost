# Public repository and private-runner boundary

Ghost is public. Public pull requests must never receive automatic code
execution on a personal or privileged self-hosted runner that can read private
SEAM repositories or operator files.

## Enforced topology

```text
public pull request or main push
        │
        ▼
GitHub-hosted Public CI
        ├─ no project install
        ├─ no private dependency resolution
        ├─ no repository secrets
        └─ no self-hosted runner

reviewed owner decision
        │ explicit workflow dispatch
        ▼
manual Private CI
        ├─ private SEAM dependency
        ├─ self-hosted runner, if deliberately assigned
        └─ paid live lane only with run_live=true and a configured key
```

The YAML split is enforced by `tests/test_ci_contract.py`. Repository settings
provide the external controls: every external contributor workflow requires
approval; default workflow permission is read-only; allowed actions are
restricted; secret scanning and push protection are enabled; and no runner is
currently assigned to Ghost.

## Operator rules

- The private workflow permits exactly `workflow_dispatch`. Never add
  `workflow_call`, `workflow_run`, `repository_dispatch`, `pull_request`,
  `pull_request_target`, `push`, `schedule`, or any other trigger.
- Never move a public workflow job to `self-hosted`.
- Never install Ghost or resolve `seam-sdk` in Public CI.
- Never store a broad private-repository credential in this public repository.
- Treat a private workflow dispatch as authorizing the checked-out revision to
  act with the runner account's filesystem, network, and credential authority.
- Keep paid live-provider tests behind the explicit `run_live` input.

## External settings checked on 2026-08-25

- visibility: public;
- external-contributor workflow approval: all external contributors;
- default workflow permissions: read;
- allowed actions: GitHub-owned, verified, and `astral-sh/setup-uv@*`;
- secret scanning: enabled;
- push protection: enabled;
- repository secrets: none; and
- runners assigned to Ghost: zero.

Organization runner-group configuration requires separate organization-admin
authority. Zero repository-visible assigned runners is the current fail-closed
state; any later assignment requires a new recorded review.
