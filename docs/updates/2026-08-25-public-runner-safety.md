# Public repository and runner safety

**State:** candidate until merged and exact-head Public CI passes.

Ghost's former automatic CI targeted `seam-box`, a personal self-hosted runner,
from a public repository. Its early YAML tripwire was not a security boundary
because a fork controls its workflow revision.

This change makes automatic pull-request and `main` verification credential-
free on `ubuntu-latest`. Private SDK integration becomes manual-only, and the
paid live lane additionally requires `run_live=true`. CI contract tests fail if
the public workflow gains a self-hosted job, the private workflow gains an
automatic trigger, credential-free jobs resolve the private SDK, or paid tests
lose their explicit input.

Repository settings were also hardened before opening the pull request: all
external contributor workflows require approval, Actions are restricted,
workflow permissions default to read, secret scanning and push protection are
enabled, no repository secrets exist, and Ghost has zero assigned runners.

The complete boundary and operator rules are in
[`../security/PUBLIC_REPOSITORY_AND_RUNNER.md`](../security/PUBLIC_REPOSITORY_AND_RUNNER.md).
