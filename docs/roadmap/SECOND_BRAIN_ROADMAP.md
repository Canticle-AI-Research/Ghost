# Ghost roadmap

This roadmap is dependency-ordered and evidence-gated. A demonstration, local
file, or passing narrow test does not complete a stage. Status changes require
a dated evidence report and canonical history entry.

## Status vocabulary

- **done** — exit gate satisfied by merged/reproduced evidence;
- **in progress** — implementation or qualification is active;
- **next** — immediate dependency-ordered work after the active slice;
- **planned** — approved scope with unmet prerequisites;
- **exploratory** — direction still requires a decision or evidence;
- **blocked** — named external or architectural condition prevents progress.

## Dependency map

```text
Substrate (everything else records itself here)

T0 core chain ─► T1 drift gates ─► T2 streams/routing ─► T3 published chain

Repository foundation

R0 docs/history/wiki ─► R1 public-runner safety ─► R2 trustworthy exact-head CI
                                                        │
                                                        ▼
Core agent                                      R3 company/IP boundary
                                                        │
                                                        ▼
                                                R4 public API/release

G0 memory spine ─► G1 dependable single agent ─► G2 deliberate memory
                          │                         │
                          │                         ▼
                          └──────────────────────► G3 specialists
                                                    │
                                                    ▼
                                                G4 measured product

Engineering quality (gates every track above)

Q0 baseline ─► Q1 behavior verification ─► Q2 module boundaries ─► Q3 proof standard

Parallel UX (cannot promote core maturity)

U0 static identity ─► U1 local desktop avatar ─► U2 operator workspace UI
```

T tracks establish the Temporal Chain: the substrate that records what every
other track did and whether it can be believed. R tracks establish whether that
evidence can be trusted publicly. G tracks establish agent capability and memory
safety. Q tracks are the standing quality gates every other track must satisfy.
U tracks establish operator experience. A U-track demo cannot close a G-track
capability gate, and no track closes without its Q gates.

## Current position

| Track | Status | Evidence boundary |
|---|---|---|
| T0 core temporal chain | done | merged and exact-head continuity verified through PR #6 |
| T1 drift gates | done | merged env/script/topic/roadmap/path-move gates passed on exact main |
| T2 streams and routing | in progress | SEAM layer documented; Ghost-local installation remains open |
| T3 published chain template | in progress | `templates/temporal-chain/` installs and verifies locally; not released |
| Q0 quality baseline | done | behavior suite and 450-line ceiling enforced |
| Q1 behavior verification | in progress | many behaviors still unverified; count is not the measure |
| Q2 module boundaries | in progress | ceiling enforced; target tightening pending |
| Q3 benchmark and proof standard | in progress | BIL-0 sealed Stage 1 smoke + public verifier implemented; live/higher-integrity qualification remains |
| R0 documentation/history/wiki | done | PR #6 merged; exact PR and main heads passed hosted gates |
| R1 public repository/runner | done | PR #5, protected main, hardened settings, zero runners, exact-head hosted run green |
| R2 exact-head CI | done | PR #8 and merge `66841fc` passed all five hosted jobs; protected main requires the full matrix |
| R3 company/IP/licensing | in progress | local PolyForm/Apache/proprietary matrix drafted; counsel/entity/assignment pending |
| R4 public API/release discipline | in progress | HTTP parity + clean public install merged; package release and deployment proof pending |
| G0 verified memory spine | done | landed through `main@25f47c4` |
| G1 dependable single agent | in progress | 20-case frozen BIL-0 suite + step ceiling implemented; live/release-candidate exit proof remains |
| G2 deliberate memory | in progress | protected-main mechanisms cover admission/mutation/isolation; sealed quality comparison remains |
| G3 graph-aware specialists | planned | provider-free envelope/provenance/failure contract exists; model-backed activation and comparison wait on G1/G2 |
| G4 measured product | exploratory | checkpoint recovery and redacted-health primitives exist; hosted product still waits on R4/G2 and production gates |
| U0 static identity | done | SVG/PNG/ICO/faces and reproducible toolkit landed |
| U0b multi-harness launchers | in progress | four launchers local; Grok/Antigravity definitions tracked; charter, Claude definition, and Codex profile external |
| U1 desktop avatar | in progress | local dirty working tree only; qualification pending |
| U2 operator workspace UI | exploratory | no approved implementation contract |

## Track T: the Temporal Chain

The Temporal Chain is the SEAM-derived protocol Ghost builds with: the git
protocol, the stable ledger, the append-only history, the derived index, the
handoff chain, the snapshots, and the streams. It is a substrate track, not a
feature track — every other track on this roadmap records itself here, so a
claim about R, G, Q, or U is only as trustworthy as the chain that carries it.

The protocol is specified in [`AGENTS.md`](../../AGENTS.md) (git half) and
[repository continuity](../history/REPOSITORY_CONTINUITY.md) (history half),
and is packaged for other repositories as
[`templates/temporal-chain/`](../../templates/temporal-chain/README.md).

### T0 — Core chain

**Status: done**

Installed and verified in Ghost:

- `PROJECT_STATUS.md` current-state router;
- `REPO_LEDGER.md` stable decisions and invariants;
- `HISTORY.md` append-only chronology, 35 entries, bootstrapped from the exact
  commit graph;
- `HISTORY_INDEX.md` derived bounded map with a source digest;
- bounded context packs by recency, topic, entry, and token budget;
- one registered handoff head with linear supersession;
- ignored bounded `.ghost/` recovery snapshots;
- exact-prefix append-only comparison against the base revision; and
- the git protocol in `AGENTS.md` covering session reconciliation, branch/PR
  discipline, and the committed/merged/released/deployed distinction.

Exit gate: `verify_continuity`, `verify_handoffs`, `verify_append_only`, and the
history-tool tests pass on a merged head, not only in a working tree.

### T1 — Drift gates

**Status: done**

Prerequisite: T0.

The chain must survive Ghost reorganizing itself. Delivered:

- a [path-move ledger](../history/PATH_MOVES.md) that keeps immutable history
  references resolvable after a rename or deletion, so reorganization never
  forces a choice between a failing gate and an illegal edit to history;
- transitive move resolution with cycle detection;
- environment-variable parity between `src/ghost/` and the configuration page;
- console-script parity between `pyproject.toml` and the command reference;
- controlled-vocabulary enforcement for history topics and roadmap statuses; and
- registry and link-resolution enforcement for every page under `docs/`.

Exit gate: a rename, a new setting, a new command, or a new page cannot merge
while its documentation is stale, because a credential-free test fails first.

### T2 — Streams and routing

**Status: in progress**

Prerequisite: T1, plus enough parallel workstreams to justify the cost.

Ghost currently runs the core and handoff layers only. SEAM's mature-repository
layers are documented but **not installed here**:

- classification/routing manifest that decides where an event belongs;
- durable topic ledgers for long-lived subjects;
- independent roadmap, experience, and library streams; and
- a derived cross-index over all streams.

Deliverables: port each layer with its parser and integrity gates, never as
isolated stream files; keep the derived cross-index rebuildable from the
streams; and prove that a single flat history remains reconstructable.

Exit gate: streams and routing verify as one layer, the cross-index rebuilds
from scratch, and no stream becomes a second authority that can contradict
`HISTORY.md` without a recorded supersession.

### T3 — Published chain

**Status: in progress**

Prerequisites: T1 and R1.

`templates/temporal-chain/` installs the core, handoff, and git-protocol layers
into an empty Git repository using only the standard library, refuses to
overwrite collisions, and self-verifies. It is proven by
`tests/test_temporal_chain.py` on every run.

Remaining deliverables: publish it under the decided license lane, document the
upgrade path for a repository already carrying an older copy, and add the T2
layers as an opt-in installer flag once they exist.

Exit gate: a third repository installs the chain from a published artifact,
passes its own continuity verification, and can upgrade without hand-editing
history.

## Track Q: engineering quality

Q gates are standing conditions, not milestones to pass once. Every other track
must satisfy them at its own exit gate.

### Q0 — Baseline

**Status: done**

Measured on the current working tree:

| Measure | Value |
|---|---|
| Provider-free tests collected | 257 |
| Live-provider tests (approval-gated) | 8 |
| Python source under `src/` and `tools/` | 4,145 lines |
| Python test code | 4,318 lines |
| Largest module | `src/ghost/seam_memory.py` (435 lines) |

Measured with `uv run pytest --collect-only`, Python-file `wc -l` totals under
`src/`, `tools/`, and `tests/`, and a descending per-file line count on this
deliberate-memory candidate. Counts describe the current tree; they are not a
quality target or maturity claim.

### Q1 — Behavior verification

**Status: in progress**

**A test exists to verify a behavior.** That is the whole standard. Tests are
not a quantity to grow, a coverage percentage to hit, or a number to match
against another repository — every one of them earns its place by proving that
something Ghost claims to do actually happens, and by failing when it stops
happening.

SEAM's suite is large because SEAM has that many behaviors worth verifying. The
size is an *output* of the discipline, not the target of it. Ghost's suite grows
the same way: it gets bigger as Ghost gains behavior, never as a goal in itself.

Two consequences, stated plainly:

- **Never write a test to reach a count.** A test that cannot fail for a reason
  an operator would care about is worse than no test — it buys false confidence
  and raises the cost of every future change.
- **A number is never evidence.** "196 tests pass" says nothing about whether a
  behavior is verified. Report which behaviors are covered and which are not.

Every behavior in the list below needs a test that fails when that behavior
breaks:

1. every public function, tool, and CLI path, against its stated contract;
2. every failure, cancellation, timeout, refusal, and recovery path — not only
   the success path;
3. every trust boundary, proven with a negative test that the boundary holds;
4. every documented command and configuration default, actually executed;
5. the G1 exit evaluation, against frozen task and memory fixtures;
6. unbounded-input surfaces (history parsing, context packing, path-move
   resolution), where property or fuzz coverage is what verifies the behavior;
   and
7. every behavior the documentation asserts, so that a doc claim and a test
   claim cannot disagree.

Exit gate: mutating any documented behavior fails at least one test, and no test
in the suite passes regardless of the code under it. Uncovered behavior is named
explicitly rather than hidden behind a passing total.

### Q2 — Module boundaries

**Status: in progress**

No god files. A module that accumulates every concern cannot be reviewed, tested
in isolation, or replaced, and it is the usual reason a codebase stops being
able to change.

Current enforcement: `tests/test_layering.py` fails any module over 450 lines
across `src/` and `tools/`. The ceiling is a ratchet — split the module, never
raise the ceiling.

Deliverables:

1. tighten the ceiling toward 300 lines as modules split;
2. split the current largest surfaces — `src/ghost/seam_memory.py` (435
   lines), `tools/branding/assets.py` (402 lines), and `src/ghost/tools.py`
   (360 lines) — along their real seams;
3. keep one clear responsibility per module, with the layer rules in
   `tests/test_layering.py` continuing to assert the SDK/lifecycle/application
   split; and
4. require a named owner module for every new concern rather than appending to
   the nearest large file.

Exit gate: every module states one responsibility, none exceeds the current
ceiling, and the layering tests still prove the three-layer split.

## Track R: repository, evidence, and delivery

### R0 — Canonical documentation and build continuity

**Status: done**

Prerequisites: Git history, current checkout, remote state, and local avatar WIP
must be reconciled without deleting unrelated work.

Deliverables:

- current-status router and stable repository ledger;
- complete append-only history bootstrapped from the exact commit graph;
- derived bounded index and context-pack command;
- one registered handoff head and linear temporal chain;
- ignored bounded recovery snapshots;
- fail-closed continuity and documentation tests;
- extensive engineering wiki with installation, commands, how-tos,
  configuration, system diagrams, rebuild blueprint, evaluation, security,
  release, and roadmap sections;
- same-change workflow that requires code and blueprint to advance together;
- reusable repository-neutral installer for the core and handoff layers; and
- exact-base append-only comparison in automatic hosted CI.

Exit gate:

- every active doc is indexed and every relative link resolves;
- history/index/handoff/snapshot verification passes;
- provider-free full tests, Ruff, build, and diff hygiene are recorded;
- an engineer can execute the documented clean-room rebuild path; and
- the successor handoff names the next issue and preserves avatar WIP.

### R1 — Resolve public repository and self-hosted runner exposure

**Status: done**

Prerequisite: R0 authority and threat documentation.

Deliverables:

- explicit public/private repository decision;
- safe runner-group/fork-workflow topology;
- credential-free jobs separated from private integration;
- CI contract tests matching the actual topology; and
- README/status/ledger/security/history agreement.

PR #5 merged the hosted automatic/manual-private split. External-contributor
approval, restricted Actions, read-only workflow defaults, secret scanning and
push protection are enabled; no repository runner or secret is assigned.
Protected `main` requires the exact hosted checks, and run `32907313331` passed
on merge head `dbd421b`. Organization runner-group inventory was unavailable
without organization-admin authority, so zero assigned runners remains the
fail-closed boundary.

Exit gate: an untrusted fork cannot obtain arbitrary code execution on a
personal runner with private-repository authority, and a controlled owner run
proves the chosen topology.

### R2 — Trustworthy exact-head CI and dependency maintenance

**Status: in progress**

Prerequisite: R1.

Deliverables:

- required fast checks complete on every candidate head;
- private integration and live-provider lanes have explicit safe triggers;
- cancellation/queue behavior is bounded;
- Dependabot PRs #2/#4 are merged, superseded, or closed with evidence; and
- exact-head results are recorded without overstating deselected lanes.

Exit gate: the exact candidate commit has green required checks and every
non-running lane is named as skipped/not configured rather than silently
absent.

### R3 — Company, IP, and licensing boundary

**Status: in progress**

Prerequisites: reconciled ownership/provenance and operator-approved product
matrix. R2 is required before publishing repository changes.

Deliverables:

- exact entity formation and founder-to-company IP assignment;
- repository/contributor/domain/model/data asset schedule;
- Apache-2.0 thin-client boundary;
- PolyForm Shield product boundary with required notices and line of business;
- permanent proprietary SEAM/MIRL, SEAM-U, cloud, and confidential-data
  boundary;
- trademark and brand-asset policy;
- contributor terms preserving commercial relicensing ability;
- third-party dependency/model/data provenance inventory; and
- counsel-reviewed consumer, API, privacy, usage, enterprise, and commercial
  licensing terms appropriate to actual launch surfaces.

Exit gate: the formed entity demonstrably owns or can license every shipped
asset, every artifact matches its declared license lane, inbound contributions
cannot block the business model, and counsel-approved product terms agree with
actual data/system behavior.

### R4 — Public API, release, and deployment discipline

**Status: in progress**

Prerequisites: R2, R3, and G1 exit.

Deliverables:

- versioned client/API replacement for Ghost's private in-process install path
  (implemented locally);
- lifecycle, reasoning, retrieval, provenance, and failure-contract parity
  (implemented and cross-repo tested locally);
- artifact membership/metadata/secret/path scans;
- clean install and console smoke;
- signed/checksummed immutable candidate;
- version, release-note, rollback, and upgrade procedures; and
- deployment topology/recovery/observability contract before hosted use.

Exit gate: a named immutable release candidate can be installed, operated,
rolled back, and audited without private source leakage or undocumented state.

## Track G: agent and memory capability

### G0 — Verified memory spine

**Status: done**

Delivered:

- DeepAgents/LangChain/LangGraph root agent;
- opaque SEAM HTTP dependency with no private source in Ghost;
- pre-turn mixed recall with graph expansion;
- transient escaped memory middleware;
- successful-turn MIRL ingest;
- evidence/knowledge-linked outcomes;
- provider Responses API routing;
- isolated provider-free tests and historical live smoke; and
- executable memory-owner boundary.

Boundary: this proves a working persistent agent spine, not a complete second
brain or production system.

### G1 — Dependable single agent

**Status: in progress**

Mechanisms already landed:

- persistent SQLite checkpoints;
- framework-free lifecycle;
- failure/cancellation finalization without ingest;
- memory recall, bounded file read, literal repository search;
- opt-in shell with approval and timeout;
- tool decision/check recording and verified outcomes; and
- CLI one-shot/interactive operation.

Remaining deliverables:

1. freeze Ghost's research-and-engineering mission/output contract;
2. create at least 20 frozen task and memory fixtures — implemented in
   `ghost-stage1-frozen-v1`;
3. add explicit maximum-step and cancellation/streaming policy — implemented
   for bounded turns and documented non-streaming behavior;
4. qualify restart, refusal, timeout, recovery, and provenance behavior;
5. define sandbox/process isolation boundary for consequential automation;
6. prove bounded research/repository tasks against a no-memory baseline; and
7. reproduce the exit suite on exact-head CI and one release candidate.

Exit gate: frozen evaluation proves resumed bounded tasks complete with correct
evidence, auditable tool traces, no forbidden effects, deterministic terminal
state, and bounded time/steps/cost. Under Q3, that proof is a sealed bundle
naming its no-memory baseline and integrity level, not a reported score.

### G2 — Deliberate and correctable memory

**Status: in progress**

Prerequisite: G1 exit and current SEAM SDK lifecycle contract review.

Deliverables:

1. memory-candidate classifier and admission policy;
2. explicit remember operation;
3. correction/supersession operation;
4. scoped forgetting/deletion UX using reviewed SEAM lifecycle paths;
5. current versus historical retrieval;
6. user-visible source/provenance references;
7. principal/workspace/project/thread boundary contract; and
8. eval fixtures for relevance, contradiction, idempotency, staleness, and
   zero cross-boundary leakage.

Protected-main coverage now implements all eight mechanism surfaces with
provider-free contract tests. G2 does not reach its exit gate from those tests:
the fixed memory-quality corpus still needs a sealed Q3 bundle diffed against a
named baseline, exact-head CI, and protected publication.

Exit gate: fixed evaluations show relevant recall improvement without storing
every successful turn, corrections win over stale claims, forgetting is
auditable, and prohibited boundaries have zero leakage. "Improvement" means a
Q3 bundle diffed against a named baseline and passing the gate.

### G3 — Graph-aware specialists

**Status: planned**

Prerequisites: G1 and G2 exit. Specialists may not invent new memory owners or
broaden tools implicitly.

Foundation published through PR #14: provider-free `DelegationEnvelope`, hard budget and
scope types, opaque evidence linkage, content-free lifecycle events, and
normalized success/refusal/timeout/cancellation/failure outcomes. This does not
register a live specialist, satisfy the prerequisites, or support an
improvement claim.

Candidate roles:

- research specialist for source discovery/evidence extraction;
- coding specialist for bounded repository changes;
- verifier for tests, citations, contradictions, and release evidence; and
- synthesizer policy that reconciles outputs under the root mission.

Deliverables:

- explicit delegation envelopes and budgets;
- separate tool/root/namespace scopes per specialist;
- provenance linkage from specialist evidence to root outcome;
- failure/cancellation propagation; and
- frozen single-agent versus specialist comparison under identical budgets.

Exit gate: specialists improve frozen task success or cost/latency without
weakening permission, memory, provenance, or isolation guarantees, proven by a
Q3 bundle comparing specialists against single-agent Ghost under identical
budgets.

### G4 — Measured product

**Status: exploratory**

Prerequisites: R4 and G2; G3 only if specialists are part of the candidate.

Foundation published through PR #14: consistent checkpoint backup, SHA-256 plus SQLite
verification, non-overwriting restore, fail-closed component health, and the
redacted specialist-event schema. Hosted endpoints, SEAM backup, migration,
supervision, dashboards, tenancy, rate limits, and deployed drills remain open.

Potential deliverables:

- authenticated streaming API;
- operator UI for sources, memory admission, corrections, and pending actions;
- managed checkpoints and SEAM stores;
- backup/restore and projection migration;
- tracing, latency, cost, memory-quality, and tool dashboards;
- principal-aware tenancy and rate limiting;
- deployment supervision and incident response; and
- release, upgrade, rollback, and disaster-recovery proofs.

Exit gate: production review passes security, isolation, recovery, migration,
observability, cost, and rollback gates on the exact release candidate.

### Q3 — Benchmark and proof standard

**Status: in progress**

Prerequisite: Q1 for the behaviors under measurement. Required before any G1,
G2, or G3 exit claim, and before any public performance claim.

Ghost is in the business of verifiable behavior. A test proves a behavior
happens; a **benchmark proves a claim about how well it happens**, and a claim
without a re-runnable artifact behind it is marketing. Ghost now has the first
BIL-0 sealed contract-smoke substrate, adopting SEAM's proof properties. Live
and higher-integrity benchmark qualification remain open.

#### The invariant

Ported from SEAM's repository ledger, which is the authority:

> Benchmark claims must be auditable (bundle hash, case hashes, fixture hashes,
> git SHA), diffed against a prior run, pass the benchmark gate, and stay
> separated from publish-only holdout runs.

#### Deliverables

1. **Sealed bundles.** Every run emits one durable artifact carrying a
   versioned bundle header, an input manifest, canonical-JSON hashes over
   fixtures/cases/results, and the exact git SHA. Volatile fields — timestamps,
   latencies, elapsed time — are excluded from the result hash so two honest
   re-runs compare equal. Hash verification is always public and
   credential-free. Release artifacts may add a publicly verifiable asymmetric
   signature whose key owner and verification command are documented. HMAC is
   reserved for protected internal attestations because a verifier without the
   shared secret cannot independently validate it.
2. **Integrity levels.** Adopt SEAM's Benchmark Integrity Levels. A level states
   what a result is *allowed to claim*. An unjudged result, or one scored by a
   stub judge, cannot seal above the lowest level without an explicit, recorded
   override, and stub output stays smoke-only regardless.
3. **Named baselines.** No score is reported alone. Ghost's claims are measured
   against a declared baseline — at minimum a no-memory Ghost for memory claims,
   and single-agent Ghost under identical budgets for specialist claims.
4. **Baseline resolution and gate.** The comparison baseline is the most recent
   run reachable from the merge-base of `HEAD` and `origin/main`, excluding
   holdout runs. A first run has no baseline and performs no regression check
   rather than inventing one. `diff` before claiming an improvement; the gate
   must pass before the claim lands.
5. **Holdout separation.** A holdout set exists for publish-time audit only,
   lives outside the ordinary run directory, is never used as a baseline, and
   requires an explicit confirmation flag to touch. A holdout run that leaks
   into routine tuning is destroyed as evidence.
6. **Full-fidelity capture.** A paid run is never reduced to aggregate numbers.
   Record per case: input, expected answer, produced answer, verdict and judge
   rationale, retrieved context, tool trace, token counts, latency, and cost.
7. **Failure classification.** Every wrong answer is split by which layer failed
   — evidence never retrieved, versus evidence present and the agent still wrong
   — so an expensive score becomes a diagnostic that names what to fix.
8. **Honest cost and identity.** Token counts come from provider responses and
   are exact. Prices come from a declared table. An unpriced model yields a null
   cost, **never a fabricated number**. Record the model that actually served the
   request, so a silent substitution cannot pass as the requested model.
9. **CI posture.** Credential-free smoke with a stub judge runs on every pull
   request and seals/verifies its bundle. Paid answerer, judge, and full-dataset
   runs stay operator-gated and never enter default CI.

#### Exit gate

No performance, capability, or comparison claim appears in documentation,
history, the roadmap, or any public surface unless a sealed bundle behind it can
be re-run by someone else, names its baseline and integrity level, passes the
gate, and reports its own failure modes and cost. A number without a bundle is
not evidence, and "the tests pass" is not a benchmark.

## Track U: operator experience

### U0 — Static identity

**Status: done**

Landed mark, reduced mark, favicon, twelve expressions, token contract, and
reproducible brand tooling/tests.

### U0b — Multi-harness launchers

**Status: in progress**

Ghost's charter is carried by four agent clients from one shared persona body,
so the operator can start Ghost wherever the work is without maintaining four
drifting copies:

| Launcher | Client | Persona selected by |
|---|---|---|
| `ghost-claude` | `claude` | `--agent canticle-ghost` |
| `ghost-codex` | `codex` | `--profile ghost` |
| `ghost-grok` | `grok` | `--agent canticle-ghost` |
| `ghost-agy` | `agy` | `--agent canticle-ghost` |

Each launcher unsets only its own provider's key variables in the child process,
because every one of these clients prefers an exported API key over the cached
subscription login. Tracked in `tools/launchers/`, documented in
[agent harnesses](../operations/AGENT_HARNESSES.md).

Remaining: the charter itself still lives outside the repository at
`~/.config/canticle-agents/ghost.md`, so a clean-room rebuild cannot yet
reproduce it. Decide whether the charter belongs in this repository or in a
tracked dotfiles source before calling this reproducible.

Exit gate: a new machine can install all four launchers and their charter from
tracked sources, and each client demonstrably discovers `canticle-ghost`.

### U1 — Desktop avatar

**Status: in progress**

Current local evidence:

- B2 jelly-ghost visual selected;
- browser/bridge and direct GTK render experiments;
- director/hook/desktop sensor and tests;
- CLI start/end notifications; and
- local candidate sprites/GLBs.

Required deliverables:

1. choose one v1 render owner;
2. mood-driven neural-constellation/neon-gas interior;
3. light hover plus face animation;
4. portable paths and optional dependencies;
5. clean lint/tests/package boundary;
6. actual desktop review evidence across supported scales;
7. resource/process/shutdown measurements; and
8. feature branch, review, exact-head CI, and canonical closeout.

Exit gate: approved rendered behavior operates on the actual desktop, remains
optional/failure-isolated from the core agent, and is reproducible from tracked
source/assets without machine-specific paths.

### U2 — Operator workspace

**Status: exploratory**

Potential scope: memory/source browser, pending admission/correction queue,
tool approval and verification trace, task/thread navigation, agent health, and
avatar integration. It must display live/unavailable/demo states truthfully and
must not become a second memory or execution authority.

## Immediate execution order

```text
R1 public-runner safety              [done]
  → publish R0/T0/T1 foundation
  → restore full hosted R2 exact-head integration
  → publish T3 chain template
  → complete R3 company/IP licensing foundation
  → finish R4 protected merge and release/deploy boundary
  → isolate/qualify U1 avatar lane
  → finish G1 frozen evaluations
  → begin G2 deliberate memory
  → add T2 streams/routing when parallel workstreams justify it
```

Q1 and Q2 run continuously alongside every step above; they are exit conditions
for each, not a separate phase to schedule. Q3 is required before G1, G2, or G3
can claim an exit, and before any public performance claim.

R1 is now closed. U1 remains preserved and is published separately so the
canonical foundation can be reviewed without mixing in the avatar runtime and
generated assets.

## Roadmap maintenance rule

A status may move only when a dated audit/update and `HISTORY#NNN` entry name:

- the exact commit/branch/merge boundary;
- deliverables satisfied;
- exact commands, fixtures, models, and test scopes;
- failures, skips, and remaining risks; and
- why the exit condition is or is not satisfied.

Local source can move an item to “in progress.” Only merged/reproduced exit
evidence moves it to “done.”

No track reaches “done” while its Q gates fail. A capability landed without the
tests that prove it stays “in progress,” regardless of how complete the
implementation looks.
