# Public repository and runner safety

**State:** merged and exact-head hosted checks green.

Ghost's former automatic CI targeted `seam-box`, a personal self-hosted runner,
from a public repository. Its early YAML tripwire was not a security boundary
because a fork controls its workflow revision.

PR #5 moved automatic pull-request and `main` verification to credential-free
GitHub-hosted jobs. Private SDK integration is manual-only, and the paid live
lane additionally requires `run_live=true`. The exact merged commit
`dbd421babf0703c8c339e7b8db8d51fc51b58282` passed `repo-hygiene`,
`brand-assets`, and `package-smoke` in Actions run
[`32907313331`](https://github.com/Canticle-AI-Research/Ghost/actions/runs/32907313331).

Repository settings require approval for all external-contributor workflows,
restrict Actions, default workflow permissions to read, enable secret scanning
and push protection, and assign Ghost no runner or repository secret. Protected
`main` requires the three hosted jobs, an up-to-date branch, a pull request, and
resolved conversations; administrators are enforced and force pushes/deletions
are blocked.

Private integration remains unqualified because no self-hosted runner is
assigned and no owner dispatch was made. The complete boundary and operator
rules are in
[`../security/PUBLIC_REPOSITORY_AND_RUNNER.md`](../security/PUBLIC_REPOSITORY_AND_RUNNER.md).
