# Ghost structural remediation ledger

- Date: 2026-08-27
- Governing history: HISTORY#051
- Scope: protected `main`, preserved local worktrees, current GitHub state,
  runtime and tool boundaries, tests, benchmarks, packaging, documentation,
  delivery, and longer-term product gates
- Evidence boundary: provider-free local execution plus authenticated read-only
  GitHub inspection; no paid provider, live SEAM service, release, deployment,
  push, or merge was performed

## 2026-08-27 action-provenance review update

GTOOL-002 is protected-main source, but a post-publication review reproduced
two additional action-provenance defects. Cumulative SQLite checkpoint history
caused a prior successful tool exchange to be submitted again on a later turn,
and result-shaped fields attached to an assistant message could satisfy the
old permissive extractor. The focused GPROV boundary repair scopes extraction
to one unique current-turn human marker, requires concrete request/result
roles, validates IDs and fields exactly, and revalidates plain attempts at the
SEAM egress. Real ToolNode plus SQLite regressions now cover persistence and
two-turn non-replay.

That repair does not close the deeper crash window: when a tool completes and
the graph raises afterward, `invoke` never returns the completed message to the
lifecycle. GPROV-001 is therefore a new open P0 and the next architecture item.
With GTOOL-001 and GTOOL-002 closed, six P0 issues remain open.

## Executive finding

Ghost has a strong continuity spine and a green provider-free baseline, but it
is not structurally ready for unattended shell use, package publication, or a
capability claim. Seven stop-ship defects can violate the stated tool,
authority, process, or artifact boundaries. The first work today should repair
those defects one focused issue at a time, then make the status/roadmap gates
capable of detecting the drift this audit found.

The frozen Stage 1 BIL-0 harness is healthy as a contract smoke. It is not a
quality benchmark. The next benchmark milestone is a sealed, independently
verifiable Stage 2 memory-quality comparison against an equal-budget no-memory
baseline. Provider-live execution remains approval-gated.

## Priority and state vocabulary

| Label | Meaning |
|---|---|
| P0 | stop-ship or authority-boundary defect; fix before enabling unattended shell use or publishing artifacts |
| P1 | immediate structural/reliability work; complete before release-candidate or benchmark qualification |
| P2 | next hardening/maintainability work after P0/P1 |
| P3 | later product or organization milestone with unmet prerequisites |
| reproduced | a focused local probe demonstrated the defect |
| observed | current code, artifact, repository, or remote state directly shows the gap |
| planned | governing roadmap work without completion evidence |
| external | requires operator, provider, service, legal, or organization authority |

## Verified baseline

| Plane | Current evidence | Boundary |
|---|---|---|
| Protected source | `origin/main@cccf99ae53dc144c68594ef3cfb67f4aa1471fd0` through PR #15 | merged source, not a release or deployment |
| Exact-head CI | run `32935194091` passed all six required jobs | provider-free hosted checks only |
| Local code quality | `uv run ruff check .` passed | static rules, not runtime qualification |
| Local tests | `270 passed, 8 deselected` in 11.69 seconds | the eight live tests did not run |
| Build | wheel and sdist built | artifact construction only |
| Stage 1 smoke | 20 fixtures validated; BIL-0 bundle verified and gated | deterministic scripted smoke; `claimable: false` |
| Dependency advisory probe | `pip-audit --vulnerability-service osv --skip-editable` reported no known vulnerabilities | one database snapshot; GitHub Dependabot alerts are disabled |
| Code review | CodeRabbit reviewed all 12 `src/ghost` modules and returned 7 findings: 4 major, 3 minor | automated review supplemented by manual reproduction |
| Releases | no Git tags or GitHub releases | no public package/release evidence established |
| Paid/live state | not run | no current provider or hosted-SEAM qualification |

The primary checkout remains on `agent/avatar-u1-temporal-integration@a5997c6`
with unrelated avatar/package WIP. This audit was isolated in a clean worktree
from current `origin/main`; the avatar work was not edited, staged, rebased, or
deleted.

## Unified ledger

### P0 — stop-ship defects

| ID | State | Owner surface | Finding | Required acceptance evidence | Dependencies |
|---|---|---|---|---|---|
| GST-001 | reproduced | `src/ghost/cli.py`, configuration | `ghost` automatically loads `.env.local` from the current working directory. A directory-controlled file can enable the account-level shell without approval and redirect `SEAM_BASE_URL`; an existing process token could then be sent to the redirected endpoint. | Authority-widening settings come only from an explicit operator-owned config source or process/CLI input; CWD files cannot enable shell, disable approval, or redirect a credentialed endpoint; negative tests cover an untrusted working directory. | none |
| GST-002 | reproduced | `src/ghost/config.py` | `_flag` documents “unrecognized means default” but returns false for every unrecognized value. A typo such as `GHOST_SHELL_APPROVAL=treu` disables the default-on approval gate. | Boolean parsing is strict or fail-closed; invalid approval values produce a controlled startup error or preserve approval; table-driven tests cover empty, valid, invalid, and case variants. | GST-001 |
| GTOOL-001 | closed on protected main, historical reproduction | `src/ghost/tools.py::make_search_repo` | Repository search did not resolve each candidate before reading it. An in-root symlink could expose an out-of-root file; `..` and absolute globs were also not rejected. | Closed through PR #21 with symlink, traversal, absolute-glob, loop, root-position, and descriptor-race regressions; exact source and merge-head CI passed. | none |
| GTOOL-002 | closed on protected main, historical reproduction | `src/ghost/tools.py`, `src/ghost/application.py` | `run_command` returned `exit=3` as ordinary text, while LangChain marked the tool message successful. The old extractor recorded `ok=true` and `exit_code=0`. | Closed through PR #24 with versioned command artifacts, real exit-code propagation, fail-closed pairing, and exact source/merge-head CI. The later current-turn boundary is recorded separately in the action-provenance update and GPROV-001. | none |
| GPROV-001 | reproduced | `src/ghost/application.py`, `src/ghost/lifecycle.py`, SEAM action contract | A tool can complete and change the machine, then a later model, recursion, or checkpoint failure can make `graph.invoke` raise before messages return. Ghost closes the turn through `/fail` but submits no `/actions` batch, so the completed effect has no durable action record. | Journal tool intent and terminal result durably with stable `(SEAM turn_id, tool_call_id)` identity; use an idempotent outbox/action route; reconcile interrupted, retried, and restarted turns; prove exactly one action record for post-tool model failure, recursion failure, checkpoint-write failure, delivery loss, and restart. | coordinated SEAM contract; current-turn scoping must remain green |
| GTOOL-003 | reproduced | `src/ghost/tools.py::make_run_command` | The timeout kills the immediate shell but not its process group. A child survived the one-second timeout and wrote a marker afterward. | Start a separate process group/session, terminate then kill the whole group on timeout, reap descendants, and prove no delayed side effect occurs after the tool returns. Define Windows behavior explicitly if supported. | GTOOL-002 |
| GTOOL-004 | observed | `src/ghost/tools.py::make_run_command` | `capture_output=True` buffers stdout/stderr without a byte ceiling and truncates only after the process exits. A noisy command can exhaust memory before the documented output cap applies. | Stream output under a hard combined byte ceiling, continue draining or terminate safely, return a typed truncation flag, and stress-test output well above the cap without proportional memory growth. | GTOOL-002, GTOOL-003 |
| GPKG-001 | observed | Hatch sdist configuration, tracked `checkpoints.db` | The sdist includes the tracked execution-state database, `.github`, full internal history/handoffs/audits, tests, evaluation runs, templates, and reserved branding. The wheel is narrow, but the source artifact violates the intended generated-state and release-membership boundary. | Remove the tracked database through a reviewed cleanup; define explicit sdist include/exclude rules; assert exact wheel/sdist manifests; fail on databases, env files, local paths, caches, unapproved brand/avatar assets, or private/generated state. | preserve history via a new entry and path-move/tombstone decision |

### P1 — immediate structural integrity

| ID | State | Owner surface | Finding | Required acceptance evidence | Dependencies |
|---|---|---|---|---|---|
| GAPP-001 | CodeRabbit major | `src/ghost/application.py::GhostAgent.__init__` | Model/graph construction failures leak the newly created SEAM client and checkpoint connection. | Construction is exception-safe; owned resources close exactly once on every failure point; injected resources retain documented ownership; regression tests force each constructor failure. | none |
| GOPS-001 | CodeRabbit major | `src/ghost/operations.py` | SQLite context managers commit/rollback but do not close connections. `_quick_check` and backup connections can remain open until garbage collection. | Use explicit closing/`ExitStack`; prove descriptors close on success and every injected failure; retain transaction and backup semantics. | none |
| GOPS-002 | CodeRabbit major | `src/ghost/operations.py::restore_checkpoint` | After `os.fdopen` owns and closes the descriptor, exception cleanup calls `os.close(handle)` again. If the descriptor number is reused, cleanup can close an unrelated descriptor. | Track ownership explicitly and never double-close; inject failures after copy, fsync, verify, and publish; assert the temporary file is removed and unrelated descriptors stay valid. | none |
| GDATA-001 | observed | checkpoint creation and operator data | Checkpoint parent/file permissions are not enforced. Default `mkdir` and SQLite creation can follow a permissive umask even though checkpoints contain conversation execution state. | Create/verify operator-private directory and database modes, reject unsafe pre-existing ownership/modes or document an explicit override, and cover backup/restore permissions. | GAPP-001, GOPS-001 |
| GCFG-001 | observed, CodeRabbit minor | `GhostSettings.from_env`, docs | Documentation says the default checkpoint derives from `GHOST_SEAM_DB`, but `from_env` always supplies the fixed `~/.local/share/ghost/checkpoints.db`, bypassing the property fallback. | Choose one stable contract; code, `.env.example`, README, configuration docs, and tests agree for default, legacy SEAM path, and explicit checkpoint path. | none |
| GTOOL-005 | observed | action provenance | Raw tool request text, including shell commands, is truncated and stored as a plain 300-character string. It can be invalid JSON and can persist secret-bearing command arguments. | Introduce typed/redacted request evidence, stable hashes, explicit safe fields, and secret-shaped regression fixtures; never retain raw credentials or invalid truncated JSON. | GTOOL-002 |
| GTOOL-006 | observed | repository search | Search caps matches and file size but not files visited, elapsed time, or aggregate bytes read. A no-match recursive scan can run unbounded over a large allowed root. | Add visit/byte/deadline budgets and explicit partial-result metadata; test large/no-match trees and cancellation. | GTOOL-001 |
| GMEM-001 | observed | `src/ghost/seam_memory.py`, lifecycle | User input, model answer, action batch, and rendered recall context lack end-to-end character/byte/item ceilings. A service can return far more memories than the recall budget within the 8 MiB body limit. | Define bounds at every trust crossing; validate exact response schemas; slice/reject over-budget records before model injection; add oversized request, answer, item-count, and malformed-record tests. | none |
| GMEM-002 | observed | memory admission and action recording | Explicit admission does not reject secret-shaped material, and stored action requests can carry secrets. The current policy can also misclassify multiline or “remember what…” recall phrasing. | Add deterministic sensitive-material refusal/redaction, multiline normalization, false-positive/negative fixtures, and a separate operator override whose evidence never exposes the secret. | GTOOL-005 |
| GMEM-003 | observed | turn lifecycle and service contract | A completion accepted server-side followed by a lost response is locally treated as failure, so Ghost calls `/fail`; abrupt process death can leave open turns. Client `turn_id` is not used for transport idempotency. | Specify idempotent begin/complete/fail recovery, status lookup/reconciliation, crash sweeper behavior, and exact tests for accepted-but-response-lost, duplicate delivery, and restart. | coordinated SEAM contract change |
| GHTTP-001 | observed | SEAM transport | A bearer token can be configured with plaintext non-loopback HTTP, and no endpoint trust policy prevents credential transmission to a redirected/mistyped host. | Require HTTPS when a token is present except an explicit loopback development allowance; validate scheme/host; document CA/proxy behavior; test redirects and credential non-forwarding. | GST-001 |
| GCLI-001 | observed | CLI error surface | Main agent/config failures can escape as tracebacks; memory subcommands catch transport errors but not invalid boundary/config values. This exposes implementation detail and yields inconsistent exit semantics. | Define stable exit codes and bounded public error messages for config, transport, model, checkpoint, and cancellation classes; preserve debug detail only behind an explicit local mode. | GAPP-001 |
| GSTATE-001 | observed | `PROJECT_STATUS.md`, `docs/status/CURRENT_STATE.md`, roadmap, blueprint | Current authorities lag protected main: they still name `c9d8a83`, PR #14, 257 tests, only PRs #2/#4, stale execution order, and already-landed work as planned. The recorded-fact gate passed anyway. | Reconcile current state to `cccf99a`; correct roadmap section/table contradictions and blueprint extensions; extend fact auditing so stale main SHA, current handoff, open-PR set, current test count, and roadmap status/order cannot silently pass. | this ledger supplies the source list |
| GSEC-001 | observed remotely | GitHub security posture | Secret scanning/push protection are enabled with no open secret alerts, but Dependabot security updates are disabled and no code-scanning analysis exists. | Enable dependency alerts/security updates deliberately, add a credential-free code-scanning lane or record an approved alternative, and verify alert triage ownership without granting unsafe runner authority. | owner/admin action |
| GCI-001 | observed remotely | GitHub Actions | Actions are major-tag pinned, repository SHA pinning is disabled, the gitleaks binary is downloaded and executed without checksum verification, and no-project quality jobs resolve broad version ranges. | Pin third-party actions and downloaded tools to reviewed immutable identities/checksums; make quality-tool resolution reproducible; retain Dependabot update flow and fork-safe permissions. | review PRs #2/#4 |
| GCI-002 | observed | Python support | Metadata claims Python 3.11 through 3.14, while protected CI tests only 3.11 and 3.13. | Test every claimed minor or narrow `Requires-Python`; add clean-install and command smoke for the complete declared matrix. | dependency compatibility review |
| GDEP-001 | observed remotely | dependency maintenance | Seven dependency PRs are open: #2, #4, and #16–#20. All observed checks are green; #2/#4 are behind main, while #16–#20 are clean. DeepAgents #19 crosses the current `<0.6` contract and needs behavioral review despite green tests. | Rebase/close superseded action PRs; process updates one at a time; run focused adapter/tool/lifecycle review for framework changes; record exact-head results and lock diff. | P0/P1 regression tests first |
| GREL-001 | observed | release engineering | No tag, GitHub release, immutable candidate, SBOM, signature/provenance attestation, changelog, rollback artifact, or release workflow exists. Package metadata also lacks a complete public-project surface. | Define versioning/release notes, exact manifests, SBOM, hashes/signatures, trusted publication, clean install, rollback, and release-candidate live qualification before any publish action. | GPKG-001, R3 legal gate, G1 exit |

### Benchmark and evaluation backlog

| ID | Priority | State | Specification and exit evidence | Dependencies |
|---|---|---|---|---|
| GBENCH-001 | P1 | next | Build the sealed Stage 2 Q3 comparison: identical prompts, model, tools, step/time/token budgets, candidate with deliberate SEAM memory versus named no-memory baseline; gate on task delta, provenance, contradictions, isolation, injection, cost, and failure modes. | P0/P1 runtime truth fixes; operator approval for paid runs |
| GBENCH-002 | P1 | observed gap | Make verification independently recompute the fixture and case hashes from the named checkout. The current `verify` command only checks self-consistency inside the bundle and does not read the referenced fixture. | versioned bundle schema |
| GBENCH-003 | P1 | observed gap | Add baseline resolution, semantic diff, and regression gates. Current BIL-0 records a no-memory arm but does not require improvement and has no merge-base baseline resolver. | GBENCH-001 |
| GBENCH-004 | P1 | observed gap | Separate stable result identity from artifact/envelope identity. Repeated BIL-0 runs have equal `result_sha256` but different whole-bundle hashes because elapsed time remains in the bundle hash; document and test the intended comparison key. | bundle schema decision |
| GBENCH-005 | P1 | planned | Create a publish-only holdout registry outside routine runs, require an explicit confirmation flag, prohibit holdout results from baseline/tuning paths, and log contamination/destruction decisions. | GBENCH-001 |
| GBENCH-006 | P1 | planned | Define a qualified judge contract: frozen rubric, answer/evidence scoring, refusal handling, judge model identity, temperature, retries, rationale, disagreement/adjudication, and no self-judging by the candidate. | spend approval |
| GBENCH-007 | P1 | planned | Capture per-case full fidelity: inputs, outputs, selected context, opaque evidence refs, typed tool trace, terminal state, exact provider/model served, tokens, latency, retries, and table-priced or null cost. | GTOOL-002, GTOOL-005 |
| GBENCH-008 | P1 | planned | Add retrieval attribution arms: lexical-only, vector-only, graph-disabled mix, configured mix, and no-memory. Match all non-retrieval variables before claiming graph lift. | compatible SEAM deployment |
| GBENCH-009 | P1 | planned | Add adversarial memory cases for policy replacement, secret requests, tool invocation, permission expansion, provenance suppression, stale resurrection, boundary crossing, and unbounded traversal; required injection and isolation violations are zero. | GMEM-001, GMEM-002 |
| GBENCH-010 | P1 | planned | Add lifecycle/fault injection for model/tool/service failure, response loss, duplicate delivery, cancellation, process death, vector outage, stale projection, concurrent correction, delete/reopen/reindex, and checkpoint/SEAM recovery. | GMEM-003, operations fixes |
| GBENCH-011 | P2 | planned | Establish operational benchmarks for cold/warm startup, recall latency, context size, tool latency, end-to-end turn latency, checkpoint growth, backup/restore, throughput, and cost. Report distributions and machine/service configuration, not one headline number. | measured product candidate |
| GBENCH-012 | P2 | planned | Upload credential-free CI bundles, verifier reports, logs, and checksums with retention; sign release evidence; bind every report to exact Ghost SHA, SEAM revision/deployment, fixtures, config names, and skipped lanes. | GCI-001, GREL-001 |
| GBENCH-013 | P2 | planned | Add property/fuzz/mutation coverage for parsers, path containment, bounds, lifecycle transitions, bundle verification, and gates. The exit is behavior mutation detection, not a coverage percentage. | P0 fixes |
| GBENCH-014 | P2 | planned | Run the final suite from the exact built release artifact in an isolated environment, then reproduce on exact protected main and the named deployed candidate. | GREL-001 and explicit paid/live approval |

### P2 — next hardening and maintainability

| ID | State | Work | Exit evidence |
|---|---|---|---|
| GARCH-001 | observed | Split `src/ghost/seam_memory.py` (425 lines), `tools/branding/assets.py` (402), and `src/ghost/tools.py` (360) on real responsibility seams; ratchet the 450-line ceiling toward 300. | layering tests, unchanged public behavior, no raised ceiling |
| GARCH-002 | observed gap | Add a static type gate and ship `py.typed` if Ghost intends to expose typed APIs. Remove or justify unused public shapes such as `TurnResult`. | strict type command in CI plus package marker test |
| GARCH-003 | observed gap | Preserve `SystemMessage` metadata/content-block semantics when injecting recall; qualify current LangChain/DeepAgents behavior before framework upgrades. | focused middleware compatibility tests across string and block content |
| GOPS-003 | observed gap | Add bounded health-probe execution, backup schedule/retention/encryption/off-host policy, RPO/RTO, SEAM recovery, migration, and deployed restore drills. | timed probes and recorded disaster-recovery exercise |
| GDOC-001 | observed gap | Add public `SECURITY.md`, structured bug/feature/benchmark forms, private vulnerability route, triage labels, and a policy for promoting ledger rows to GitHub issues. | GitHub surfaces verified without accepting external copyrighted contributions |
| GDOC-002 | observed gap | Generate a compact current-work view from this ledger and make status/roadmap reference IDs rather than duplicate prose. | one canonical row per issue; automated orphan/stale-reference test |
| GTEMP-001 | planned | Complete T2 streams/routing only when parallel workstreams justify it; preserve flat-history reconstruction and one authority. | parser, routing, cross-index, and reconstruction gates |
| GTEMP-002 | planned | Publish and upgrade-test the Temporal Chain template in a third repository. | immutable artifact, license, install, upgrade, independent verification |
| GHARNESS-001 | observed gap | Move the shared Ghost charter from operator-local configuration into a tracked, approved source and qualify Claude/Codex/Grok/Antigravity discovery. | clean-machine install and identity parity tests |
| GAVATAR-001 | preserved WIP | Reconcile the isolated avatar branch with current main; choose one renderer; decide asset provenance/membership; finish mood interior, motion, paths, shutdown/resource tests, and actual desktop review. | separate branch/PR, mobile/desktop or scale evidence as applicable, exact-head CI, no core dependency |
| GWORKTREE-001 | observed | Reconcile three older linked worktrees/branches after verifying their commits are merged and no untracked evidence remains; do not delete or reset them as part of this ledger. | read-only inventory, operator-approved cleanup, recoverability note |
| GUX-001 | planned | Specify the operator workspace for sources, admission/correction queue, tool approval/verification, thread/task navigation, health, and truthful live/unavailable/demo states. | approved contract; UI remains neither memory nor execution authority |

### P3 — later product and organization gates

| ID | State | Work | Prerequisites |
|---|---|---|---|
| GPROD-001 | planned | Freeze the research-and-engineering mission/output contract and close G1 with live plus exact release-candidate evidence. | all P0/P1, GBENCH-001, release candidate |
| GPROD-002 | planned | Activate one bounded model-backed specialist adapter and compare it with single-agent Ghost under identical budgets. | G1 and G2 exits, GBENCH suite |
| GPROD-003 | exploratory | Authenticated hosted API, operator UI, supervision, tenancy, rate limiting, observability, rollback, incident response, and recovery. | R4, G2, security/deployment review |
| GLEGAL-001 | external | Form the entity, execute founder-to-company IP assignment, inventory repositories/assets/data/models, obtain counsel review, and establish contributor/commercial/privacy/API terms. | operator and counsel authority |
| GLEGAL-002 | external | Review trademark filings/policy, reserved avatar/brand distribution, model/data provenance, and third-party notices before release. | GLEGAL-001, exact artifact manifests |

## Immediate issue specifications

### 1. Restore truthful tool boundaries

Treat GTOOL-001 through GTOOL-004 as separate reviewable changes. The common
exit test is an end-to-end graph result, not only a direct tool invocation:

1. the model-facing result reports the typed status;
2. `extract_tool_attempts` preserves that status and real exit code;
3. the opaque actions request carries the same values;
4. the contract fake returns no passed verification for failure/refusal/timeout;
5. the lifecycle cannot finalize a failed action as supporting evidence; and
6. timeout/output/path bounds hold under adversarial inputs.

Until this closes, keep `GHOST_ENABLE_SHELL` off for normal operation.

### 2. Make authority configuration operator-owned

GST-001/GST-002 are one architecture decision followed by two narrow fixes.
The decision must name which sources may set credentials, endpoints, readable
roots, shell enablement, approval, and workdir. Loading convenience settings
must never silently grant authority. A safe shape is to keep process/explicit
CLI authority separate from a non-authoritative convenience file, or require
an explicit operator-owned config path with ownership/mode checks.

### 3. Close resource and persistence correctness

GAPP-001, GOPS-001, GOPS-002, GDATA-001, and GCFG-001 should be repaired before
checkpoint recovery is called dependable. Inject failure after every acquired
resource and every restore phase. Verify exactly-once close, temporary cleanup,
non-overwrite, digest/integrity, private modes, and an unchanged source backup.

### 4. Make artifacts intentionally small and clean

GPKG-001 blocks publication. The wheel currently contains only runtime modules
and license files, while the sdist inherits nearly the entire repository. Add
an exact allowlist and tests for both artifacts. The generated database must be
removed from tracking through an explicit history event; do not silently erase
it or treat it as runtime truth.

### 5. Repair the truth-maintenance system

GSTATE-001 is structural because the repository's strongest promise is that
checkable prose survives checking. The existing gate catches selected counts,
module lengths, and handoff pointers but missed a stale protected-main SHA,
open PR set, track status contradiction, and obsolete execution order. Extend
the gate around stable machine-readable facts; keep dated interpretations in
audits and avoid making every remote field a brittle required fact.

## Course of action for today

Work one issue at a time and keep the avatar checkout untouched:

Ledger registration and current-state router reconciliation are complete in
this documentation branch. The remaining course is:

1. **Fix GTOOL-001 first.** It is the smallest independently reviewable P0 and
   restores the advertised read-only root boundary.
2. **Fix GTOOL-002 next.** Make one structured result authoritative from shell
   execution through SEAM verification; add the nonzero-exit regression.
3. **Then close GTOOL-003 and GTOOL-004.** Process-group termination and
   streaming output bounds share subprocess mechanics but need distinct tests.
4. **Fix GST-001/GST-002.** Land the config-authority decision and fail-closed
   boolean parsing before any unattended agent use.
5. **Fix operations/resources.** GAPP-001, GOPS-001, GOPS-002, GDATA-001, and
   GCFG-001 can follow as focused resource-lifecycle slices.
6. **Close GPKG-001.** Remove the tracked database with audit history, lock the
   sdist/wheel manifests, and rerun clean-install smoke.
7. **Reconcile docs and strengthen gates.** Repair GSTATE-001 from the landed
   behavior, not ahead of it.
8. **Only then start GBENCH-001 design/implementation.** Build everything
   provider-free that can be built; stop before paid answerer/judge execution
   and report model, call count, duration, billing unit, and expected cost for
   explicit approval.
9. **Process dependency PRs after the new regressions exist.** Framework
    upgrades should prove the repaired lifecycle/tool contracts rather than
    merely re-run the old green suite.

Every material slice should finish with the repository closeout, full
provider-free suite, build, artifact/diff checks, a CodeRabbit delta review,
exact pushed-head CI, and one successor handoff. Push, merge, release, and
deployment remain separate operator decisions.

## What is deliberately not authorized by this report

- no modification, deletion, rebase, staging, or publication of avatar WIP;
- no shell enablement for normal Ghost operation;
- no paid provider or live SEAM run;
- no dependency PR merge;
- no package publication, tag, release, or deployment;
- no company/IP/legal claim; and
- no G1, G2, G3, G4, performance, quality-improvement, or production-readiness
  claim.

## Evidence manifest

Raw artifacts are not committed. Reproducible evidence is:

- repository base `cccf99ae53dc144c68594ef3cfb67f4aa1471fd0` and exact-head
  Actions run `32935194091`;
- `git status --short --branch`, `git fetch --prune origin`, `git rev-parse
  HEAD origin/main`, `git worktree list --porcelain`, `gh pr list --state all`,
  and current repository/protection/Actions API responses;
- `uv run ruff check .`;
- `uv run pytest --durations=10` (`270 passed, 8 deselected`);
- `uv build`, plus `tar -tf` and `unzip -l` inspection of the resulting sdist
  and wheel;
- Stage 1 `validate-fixtures`, `smoke`, `verify`, and `gate` commands;
- two repeated Stage 1 smokes showing equal stable result hashes and unequal
  whole-bundle hashes due to volatile elapsed time;
- `pip-audit --vulnerability-service osv --skip-editable` against the frozen
  runtime export (`No known vulnerabilities found`); the first PyPI-service
  attempt failed closed on local TLS certificate verification and was not
  bypassed;
- CodeRabbit CLI 0.7.5 review of all 12 `src/ghost` modules (7 findings: 4
  major, 3 minor), plus documentation-delta review and repair; the final
  automated documentation rerun was unavailable after the free CLI allowance
  was exhausted, so final validation used the repository gates and manual diff
  review; and
- isolated temporary probes for CWD dotenv authority, invalid approval boolean,
  repository-search symlink escape, failed-shell outcome flattening, and
  timeout descendant survival. The probes used sentinel data only and did not
  read operator secrets.
