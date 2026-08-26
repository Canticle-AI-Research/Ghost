# Ghost build history

This is Ghost's authoritative append-only repository event stream. Entries are
ordered oldest to newest. Routine startup uses `HISTORY_INDEX.md` or
`tools.history.build_context_pack`; do not load this entire file as the project
grows.

The first 21 entries are a provenance-preserving bootstrap from the exact Git
commit graph. `git show <sha>` remains the byte-level authority for each
historical diff. Entry 22 records the later local avatar work that never
entered Git. Entry 23 begins the canonical continuity system itself.

## HISTORY#001 — Seed the Ghost repository
- Date: `2026-08-14T14:04:28-05:00`
- Agent: `operator`
- Status: `done`
- Topics: `repository, docs`
- Commits: `fb341001ddd49cb0c0ae0314e5a5a9b2ffe82e9a`
- Refs: `README.md`
- Supersedes: `none`
- Verification: `historical reconstruction from git show fb341001`

The repository began with a minimal README identity. No runtime, package,
memory adapter, or verification surface was present in this commit.

## HISTORY#002 — Define Ghost as a SEAM-backed DeepAgent
- Date: `2026-08-14T14:18:54-05:00`
- Agent: `operator`
- Status: `done`
- Topics: `agent, architecture, memory, sdk, docs`
- Commits: `e03d29288a95b7a4af84a2d16ad003b65b0d0d60`
- Refs: `README.md`
- Supersedes: `HISTORY#001`
- Verification: `historical reconstruction from git show e03d292`

The README established Ghost's product identity and intended SEAM/MIRL memory
boundary before the implementation landed.

## HISTORY#003 — Land the DeepAgent, architecture documentation, and identity
- Date: `2026-08-14T15:29:16-05:00`
- Agent: `operator`
- Status: `done`
- Topics: `agent, architecture, branding, docs, memory, sdk, verification`
- Commits: `2869bf4e385034d02bee73d99baa176556b68c44`
- Refs: `src/ghost/application.py, src/ghost/seam_memory.py, docs/INDEX.md, branding/ghost.svg, tests/test_application.py`
- Supersedes: `HISTORY#002`
- Verification: `historical commit reports package, architecture, tests, and exact SDK-backed behavior; see git show 2869bf4`

The first working package established the root agent, SEAM adapter, transient
recall middleware, CLI/configuration, extensive second-brain documentation,
tests, and the initial Ghost mark. This is the first implemented memory spine.

## HISTORY#004 — Add the Ghost expression system
- Date: `2026-08-14T15:35:58-05:00`
- Agent: `operator`
- Status: `done`
- Topics: `avatar, branding, docs`
- Commits: `cde39de949ba8b143b5b028f95877708991b0772`
- Refs: `branding/ghost-faces.svg, branding/README.md`
- Supersedes: `HISTORY#003`
- Verification: `historical reconstruction from git show cde39de`

The identity gained twelve swappable terminal-native expressions while the
default prompt/cursor face remained the small-mark identity.

## HISTORY#005 — Vendor reproducible brand tooling
- Date: `2026-08-14T15:41:57-05:00`
- Agent: `operator`
- Status: `done`
- Topics: `branding, build, tools, verification`
- Commits: `6537e95d48bb012355e74daac94338b41f13d2f8`
- Refs: `tools/branding/assets.py, branding/tokens.json, tests/test_brand_assets.py`
- Supersedes: `HISTORY#004`
- Verification: `historical commit reports 18 tests and clean Ruff; see git show 6537e95`

Brand regeneration stopped depending on a separate private checkout. The
vendored toolkit and tests made the identity reproducible from Ghost alone.

## HISTORY#006 — Move the memory dependency behind the private SEAM SDK
- Date: `2026-08-15T04:56:11-05:00`
- Agent: `operator`
- Status: `changed`
- Topics: `architecture, memory, sdk, packaging`
- Commits: `5df8bea902b2b76d63a0246fd386512d51da08d9`
- Refs: `pyproject.toml, src/ghost/seam_memory.py, README.md`
- Supersedes: `HISTORY#005`
- Verification: `historical commit reports resolved lock, sync, and 18 tests against seam_sdk; see git show 5df8bea`

Ghost stopped importing the private runtime directly. The SDK became the
reviewed integration boundary and retained private runtime access transitively.

## HISTORY#007 — Add the initial Pylint workflow
- Date: `2026-08-18T23:24:47-05:00`
- Agent: `automation`
- Status: `done`
- Topics: `ci, verification`
- Commits: `7ac103fe5fde709667b6544e0068517b9b1099ea`
- Refs: `https://github.com/Canticle-AI-Research/Ghost/commit/7ac103fe5fde709667b6544e0068517b9b1099ea`
- Supersedes: `HISTORY#006`
- Verification: `historical reconstruction from git show 7ac103f`

GitHub automation introduced a Pylint matrix. Later evidence showed the
workflow was incompatible with the package floor and dependency environment;
HISTORY#021 removed it.

## HISTORY#008 — Correct vendored brand metadata
- Date: `2026-08-19T00:14:54-05:00`
- Agent: `operator`
- Status: `done`
- Topics: `branding, correction, docs`
- Commits: `94d49a00e697afc3e4e41b0a679355c0455cf051`
- Refs: `branding/README.md, tools/branding/assets.py`
- Supersedes: `HISTORY#007`
- Verification: `historical reconstruction from git show 94d49a0`

The vendored toolkit's token path, font claims, and expression-asset table were
corrected to match the repository that actually shipped them.

## HISTORY#009 — Repair graph-triple memory rendering
- Date: `2026-08-19T00:14:54-05:00`
- Agent: `operator`
- Status: `done`
- Topics: `memory, correction, security, verification`
- Commits: `e3a6a045bb772744153d2ebc1eef6a6893322181`
- Refs: `src/ghost/seam_memory.py, tests/test_memory_rendering.py`
- Supersedes: `HISTORY#008`
- Verification: `historical commit pins full and partial triple rendering plus injection boundaries; see git show e3a6a04`

MIRL triples stopped collapsing to a bare object before prompt injection. The
new tests also bounded recalled text and prevented fence/newline injection.

## HISTORY#010 — Make the documented test command real and cover missing surfaces
- Date: `2026-08-19T00:15:16-05:00`
- Agent: `operator`
- Status: `done`
- Topics: `cli, config, correction, tests, verification`
- Commits: `f372670f48c67ea154acb286d5efb49d98001bba`
- Refs: `pyproject.toml, tests/test_cli.py, tests/test_config.py, tests/test_middleware.py, tests/conftest.py`
- Supersedes: `HISTORY#009`
- Verification: `historical commit reports uv run pytest repaired and 49 tests; see git show f372670`

The advertised pytest invocation was repaired. CLI exit/cleanup, configuration
bounds, real middleware integration, and strict no-skip behavior gained tests.

## HISTORY#011 — Enforce the single durable-memory owner
- Date: `2026-08-19T00:15:16-05:00`
- Agent: `operator`
- Status: `done`
- Topics: `architecture, memory, trust, verification`
- Commits: `d43840cd372e525c11250a59f7b4b4633a7b0714`
- Refs: `docs/decisions/0001-seam-memory-boundary.md, tests/test_memory_boundary.py`
- Supersedes: `HISTORY#010`
- Verification: `historical tests build the real graph and reject DeepAgents memory/store/backend ownership; see git show d43840c`

ADR-0001 became executable: DeepAgents cannot silently gain a second memory
surface and the SEAM adapter must remain framework-free.

## HISTORY#012 — Add tiered continuous integration
- Date: `2026-08-19T00:15:36-05:00`
- Agent: `operator`
- Status: `done`
- Topics: `ci, security, verification`
- Commits: `648940decbd7a3a2031671196d9c37291e6d1d00`
- Refs: `.github/workflows/ci.yml, tests/test_ci_contract.py, .github/dependabot.yml`
- Supersedes: `HISTORY#011`
- Verification: `historical commit reports local execution and mutation testing of CI contract; see git show 648940d`

Credential-free hygiene/brand/package jobs were separated from private-SDK
tests, with a live-provider lane, secret scan, and a public-repository tripwire.

## HISTORY#013 — Merge the first protected review slice
- Date: `2026-08-19T00:18:53-05:00`
- Agent: `github`
- Status: `done`
- Topics: `ci, correction, provenance, verification`
- Commits: `c9f40dacfab5711a1f444c042b392d9677840d47`
- Refs: `https://github.com/Canticle-AI-Research/Ghost/pull/1, docs/updates/2026-08-19-ci-and-test-coverage.md`
- Supersedes: `HISTORY#012`
- Verification: `GitHub PR #1 merged; merge commit c9f40da`

PR #1 integrated CI, the three tested defects, and the executable memory
boundary. Later direct main commits continued the Stage 1 build.

## HISTORY#014 — Establish the dated update provenance track
- Date: `2026-08-19T00:32:29-05:00`
- Agent: `operator`
- Status: `done`
- Topics: `docs, history, provenance`
- Commits: `f69cff6d84dd7f2c8536483bc173eb619e5e1f29`
- Refs: `docs/updates/README.md, docs/updates/2026-08-19-ci-and-test-coverage.md`
- Supersedes: `HISTORY#013`
- Verification: `historical reconstruction from git show f69cff6`

Ghost gained append-only dated implementation reports. This was useful but did
not yet provide root status, ledger, a complete history, handoff chain, or
continuity verifier.

## HISTORY#015 — Finalize failed turns and add read-first tools
- Date: `2026-08-19T01:50:08-05:00`
- Agent: `operator`
- Status: `done`
- Topics: `agent, memory, security, tools, verification`
- Commits: `2f017a620c5978efc80d99cf2db8e6e4dba2559b`
- Refs: `src/ghost/lifecycle.py, src/ghost/tools.py, tests/test_failure_finalization.py, tests/test_tools.py`
- Supersedes: `HISTORY#014`
- Verification: `historical commit reports 125 tests; see git show 2f017a6`

Crashes stopped leaving open reasoning runs or ingesting incomplete answers.
Ghost gained always-on memory recall plus operator-scoped file read and literal
repository search tools.

## HISTORY#016 — Prove the live root-agent and memory round trip
- Date: `2026-08-19T02:56:14-05:00`
- Agent: `operator`
- Status: `done`
- Topics: `agent, evaluation, memory, verification`
- Commits: `eba3ee579b5e9078a438383dea14b2886536fda3`
- Refs: `tests/test_live_agent.py, src/ghost/application.py, src/ghost/seam_memory.py`
- Supersedes: `HISTORY#015`
- Verification: `historical commit records six live tests and repaired prompt/model behavior; see git show eba3ee5`

Real-provider tests exercised the end-to-end model, recall, ingest, and memory
reuse path. Those historical live results do not substitute for exact-current-
head live qualification.

## HISTORY#017 — Persist threads and separate the three runtime layers
- Date: `2026-08-19T03:26:04-05:00`
- Agent: `operator`
- Status: `done`
- Topics: `architecture, memory, operations, verification`
- Commits: `8f6ec11cff691e847e18c4a5e6aab51280ff830a`
- Refs: `src/ghost/lifecycle.py, src/ghost/application.py, tests/test_layering.py, docs/architecture/SYSTEM_MAP.md`
- Supersedes: `HISTORY#016`
- Verification: `historical commit tests restart-persistent SQLite checkpointing and framework separation; see git show 8f6ec11`

Ghost split into the SDK memory layer, framework-free turn lifecycle, and agent
adapter. LangGraph execution checkpoints became persistent and physically
separate from semantic memory.

## HISTORY#018 — Turn tool activity into verified reasoning graphs
- Date: `2026-08-19T04:10:00-05:00`
- Agent: `operator`
- Status: `done`
- Topics: `agent, provenance, tools, verification`
- Commits: `696c479dc780e423efbacd16851b4a82a6e3dd95`
- Refs: `src/ghost/lifecycle.py, src/ghost/seam_memory.py, tests/test_reasoning_graph.py, docs/updates/2026-08-19-verified-action-graph.md`
- Supersedes: `HISTORY#017`
- Verification: `historical commit reports 141 provider-free tests and six live tests; see git show 696c479`

Each tool call became a decision plus verification. Only passed checks may
support a verified accepted outcome; failed checks remain visible without
supporting the conclusion.

## HISTORY#019 — Add opt-in operating-system control
- Date: `2026-08-19T04:42:29-05:00`
- Agent: `operator`
- Status: `done`
- Topics: `agent, security, shell, tools, verification`
- Commits: `ce812de5dd47254e04a800ddb42d6d8ebb0c4a4e`
- Refs: `src/ghost/tools.py, tests/test_shell_tool.py, docs/updates/2026-08-19-operating-system-control.md`
- Supersedes: `HISTORY#018`
- Verification: `historical commit reports 174 provider-free tests and eight live tests; see git show ce812de`

Ghost gained an opt-in real shell with operator approval, bounded timeout,
recoverable refusal, and SEAM-verified results. The shell remained explicitly
unsandboxed and retained the full authority of the operator account.

## HISTORY#020 — Consolidate linting on Ruff
- Date: `2026-08-19T04:54:32-05:00`
- Agent: `operator`
- Status: `done`
- Topics: `ci, correction, security, verification`
- Commits: `25f47c4de9946e2ef97fc4ad82be2328be55b1ed`
- Refs: `pyproject.toml, src/ghost/tools.py, .github/workflows/ci.yml`
- Supersedes: `HISTORY#019`
- Verification: `historical commit fixes five Ruff findings and removes the incompatible Pylint workflow; see git show 25f47c4`

Ruff became the sole linter and gained security/bug rules appropriate to the
shell boundary. The failing, incompatible Pylint workflow was removed.

## HISTORY#021 — Mainline Stage 1 mechanism boundary
- Date: `2026-08-19T05:00:00-05:00`
- Agent: `history-bootstrap`
- Status: `done`
- Topics: `agent, architecture, roadmap, status`
- Commits: `25f47c4de9946e2ef97fc4ad82be2328be55b1ed`
- Refs: `docs/roadmap/SECOND_BRAIN_ROADMAP.md, docs/updates/README.md, README.md`
- Supersedes: `HISTORY#020`
- Verification: `git history through main@25f47c4 reconstructed on 2026-08-25`

At the latest merged implementation boundary, most Stage 1 mechanisms existed:
persistent checkpoints, failure finalization, bounded read tools, verified
actions, and opt-in shell control. Frozen task/memory evaluation, production
isolation, and exact-head CI qualification remained incomplete. This entry
separates implementation inventory from an unsupported full-stage exit claim.

## HISTORY#022 — Preserve the local desktop-avatar workstream
- Date: `2026-08-21T23:59:00-05:00`
- Agent: `operator-handoff`
- Status: `in-progress`
- Topics: `avatar, handoff, tools, verification`
- Commits: `working-tree`
- Refs: `docs/updates/2026-08-21-desktop-pet-handoff.md, docs/superpowers/specs/2026-08-21-desktop-avatar.md, docs/handoffs/2026-08-21-desktop-pet.md`
- Supersedes: `HISTORY#021`
- Verification: `2026-08-25 current-tree run: uv run pytest -> 171 passed, 8 deselected; uv build passed; uv run ruff check . -> five local avatar/image-tool findings`

The B2 jelly-ghost desktop pet, avatar director/hook, GTK surface, artwork, and
CLI wiring existed only in the local dirty checkout. The next requested visual
step was mood-driven neural-constellation and neon-gas interior lighting. No
branch, PR, merge, release, or deployment was recorded.

## HISTORY#023 — Begin canonical documentation and continuity foundation
- Date: `2026-08-25T12:00:00-05:00`
- Agent: `codex`
- Status: `in-progress`
- Topics: `continuity, docs, handoff, history, ledger, status, wiki`
- Commits: `working-tree`
- Refs: `AGENTS.md, PROJECT_STATUS.md, REPO_LEDGER.md, docs/history/REPOSITORY_CONTINUITY.md, docs/handoffs/INDEX.md, docs/audits/INDEX.md, tools/history`
- Supersedes: `HISTORY#022`
- Verification: `in progress; final commands and results belong in a successor closeout entry`

Ghost began a SEAM-derived but Ghost-specific continuity system: canonical
status and ledger authorities, append-only history bootstrapped from the exact
commit graph, a derived bounded index, one linear handoff chain, ignored local
snapshots, bounded context packs, and fail-closed verification. The same slice
expands the documentation into an installation/command/how-to/architecture/
rebuild wiki and defines the workflow that keeps it synchronized with code.

## HISTORY#024 — Locally qualify the rebuildable wiki and continuity foundation
- Date: `2026-08-25T14:00:00-05:00`
- Agent: `codex`
- Status: `done`
- Topics: `architecture, commands, continuity, docs, history, installation, roadmap, verification, wiki`
- Commits: `working-tree`
- Refs: `docs/README.md, docs/architecture/COMPLETE_SYSTEM_BLUEPRINT.md, docs/operations/COMMAND_REFERENCE.md, docs/operations/HOW_TO.md, docs/operations/INSTALLATION.md, docs/product/REBUILD_BLUEPRINT.md, docs/roadmap/SECOND_BRAIN_ROADMAP.md, docs/handoffs/2026-08-25-public-runner-next.md, tests/test_history_tools.py`
- Supersedes: `HISTORY#023`
- Verification: `27 focused docs/history/CI-contract tests passed; full default suite 181 passed and 8 live deselected; uv build passed; continuity tooling/tests Ruff-clean; git diff --check passed; full Ruff retained five local avatar/image-tool findings`

Ghost's local documentation is now an engineering blueprint rather than a
README map: it covers zero-state installation, every repository command,
operator/developer how-tos, every runtime layer, ASCII data/trust/failure flows,
configuration, testing, release/deployment boundaries, the local avatar lane,
and a dependency-ordered roadmap. CI now requires documentation, rebuild
blueprint, history index, and handoff continuity to move with code.

The result remains a dirty local working-tree candidate. It has not been
committed, pushed, reviewed, merged, released, or deployed. The successor
handoff makes the public-repository/self-hosted-runner contradiction the next
issue and preserves the unrelated avatar WIP.

## HISTORY#025 — Integrate reusable continuity and safe workflow candidate
- Date: `2026-08-25T14:30:00-05:00`
- Agent: `codex`
- Status: `done`
- Topics: `ci, continuity, handoff, history, repository, security, tools, verification`
- Commits: `working-tree`
- Refs: `templates/repository-continuity/README.md, .github/workflows/public-ci.yml, .github/workflows/ci.yml, tools/history/verify_append_only.py, docs/security/PUBLIC_REPOSITORY_AND_RUNNER.md, docs/handoffs/2026-08-25-continuity-template-integrated.md`
- Supersedes: `HISTORY#024`
- Verification: `29 focused docs/history/CI-contract tests passed before closeout; continuity-template install into a fresh temporary Git repository passed four standard-library tests plus snapshot closeout; scoped Ruff and git diff --check passed; final closeout and full provider-free suite recorded in the handoff`

Ghost generalized its SEAM-derived temporal substrate into a standalone,
standard-library template with status, ledger, append-only history, generated
index, bounded packs, snapshots, a single-head handoff chain, tests, and hosted
CI. The new append-only verifier compares candidate history with the exact Git
base so a valid-looking rewrite cannot pass as chronology.

The local workflow candidate sends automatic public pull-request continuity to
`ubuntu-latest`, makes the privileged `seam-box` workflow manual-only, and
requires an explicit `run_live` input before provider-paid tests. This is local
working-tree evidence only. It is not committed, pushed, reviewed, merged, or
active on GitHub, and it does not prove external runner-group/fork settings.

## HISTORY#026 — Place the company licensing architecture
- Date: `2026-08-25T15:00:00-05:00`
- Agent: `codex`
- Status: `in-progress`
- Topics: `architecture, docs, packaging, sdk, security, status`
- Commits: `working-tree`
- Refs: `LICENSE, NOTICE, TRADEMARKS.md, CONTRIBUTING.md, docs/product/CANTICLE_PRODUCT_AND_LICENSING_STRUCTURE.md, docs/legal/LICENSING_STRUCTURE.md, docs/decisions/0004-open-edge-shielded-product-proprietary-core.md, docs/audits/2026-08-25-company-licensing-architecture.md`
- Supersedes: `HISTORY#025`
- Verification: `pre-closeout Ghost run passed 191 tests and stopped on the expected missing HISTORY#026 handoff reference; SEAM SDK 9 tests and Ruff passed; Apache thin client 58 tests and Ruff passed; Shield files had one SHA-256 across four product repositories`

Ghost and adjacent product scaffolds adopted a local three-lane candidate:
Apache-2.0 for thin integration code, PolyForm Shield 1.0.0 for distributed
runnable products, and permanent proprietary controls for undistributed
SEAM/MIRL, SEAM-U, hosted-control, and confidential assets. Ghost and the SEAM
SDK now carry exact Shield text, required notices, matching package metadata,
and source-available language. Canticle Core and SEAM Node scaffolds carry
Shield; the thin client remains Apache-2.0; and the noncanonical SEAM Runtime
scaffold records an All Rights Reserved target without touching the canonical
private runtime.

The current licensor remains Nicholas Thomas. No company formation, IP
assignment, counsel approval, commit, push, merge, release, or deployment is
claimed. External contributions are paused and trademarks remain separate from
the software grants while final local qualification runs.

## HISTORY#027 — Qualify the licensing and company-readiness foundation
- Date: `2026-08-25T15:30:00-05:00`
- Agent: `codex`
- Status: `done`
- Topics: `architecture, docs, packaging, sdk, security, status, verification`
- Commits: `working-tree`
- Refs: `docs/audits/2026-08-25-company-licensing-architecture.md, docs/handoffs/2026-08-25-company-licensing-foundation.md, tests/test_licensing.py, pyproject.toml, .github/workflows/public-ci.yml`
- Supersedes: `HISTORY#026`
- Verification: `Ghost provider-free suite passed 190 tests with 8 live tests deselected; uv build passed with License-Expression plus LICENSE/NOTICE in the wheel; scoped Ruff and git diff --check passed; full Ruff retained 5 known avatar/image-tool findings; SEAM SDK passed 9 tests, Ruff, and build/metadata inspection; Apache thin client passed 58 tests and Ruff; all four Shield LICENSE files shared SHA-256 67530f8e9adfcc5d2e9d72b804500cebb7472ff84c34a6729a80a2a9be901ee6`

The company-readiness candidate is internally consistent and reconstructable:
the legal router, product matrix, ADR, architecture diagrams, roadmap,
installation/release gates, package metadata, audit, tests, and continuity
chain agree on the same layer boundaries. The pre-company contribution pause
and interim trademark policy prevent the source license from silently becoming
an inbound-IP or brand grant.

Qualification does not make these changes remote or legally approved. The
Ghost and SEAM SDK changes remain local working-tree candidates; adjacent
Canticle Core, client, node, and runtime paths are local non-Git scaffolds or
packages; the canonical private SEAM runtime was not relicensed; and SEAM-U
remains a planned proprietary model boundary without located artifacts.

## HISTORY#028 — Name the Temporal Chain and gate documentation drift
- Date: `2026-08-25T16:10:00-05:00`
- Agent: `claude`
- Status: `done`
- Topics: `continuity, docs, history, roadmap, tests, tools, verification`
- Commits: `working-tree`
- Refs: `templates/temporal-chain/README.md, docs/history/PATH_MOVES.md, docs/operations/AGENT_HARNESSES.md, docs/roadmap/SECOND_BRAIN_ROADMAP.md, tools/history/model.py, tools/launchers/install.py, tests/test_docs.py, tests/test_history_tools.py, tests/test_layering.py, tests/test_temporal_chain.py`
- Supersedes: `HISTORY#027`
- Verification: `provider-free suite passed 196 tests with 8 live tests deselected; verify_continuity, verify_handoffs, and closeout passed; scoped Ruff passed on changed tools/tests; grok inspect and agy agent both list canticle-ghost; git diff --check passed`

The SEAM-derived protocol this repository builds with now has its real name.
`templates/repository-continuity/` became `templates/temporal-chain/`, and the
glossary, ledger, blueprint, wiki, and command reference all call it the
Temporal Chain: the git protocol, the stable ledger, the append-only history,
the derived index, the handoff chain, the snapshots, and the streams as one
protocol rather than a folder of conventions. The template's `AGENTS.md` gained
the git half it was missing — session reconciliation, branch/PR discipline, and
the committed/merged/released/deployed distinction — so an installing repository
receives both halves.

Renaming the template immediately broke continuity verification, which is the
gap worth recording: `HISTORY#025` refers to the old path, history is
append-only, and ref validation resolved against the current tree. That forced a
choice between a failing gate and an illegal edit to history. The path-move
ledger at `docs/history/PATH_MOVES.md` removes the choice. Verification now
follows a transitive move chain, with cycle detection, before checking that a
file exists, so Ghost can reorganize itself without dangling a historical
reference or rewriting its past.

Documentation maintenance moved from convention to enforcement. Environment
variables in `src/ghost/` must match the configuration page, console scripts
must appear in the command reference, history topics and roadmap statuses must
use their controlled vocabularies, and no module may exceed 450 lines. The
topic gate immediately found real drift: `HISTORY#010` used `config` and `tests`,
which were absent from the `AGENTS.md` vocabulary. The vocabulary was incomplete
rather than the entry wrong, so the vocabulary was completed.

The roadmap gained the tracks it was missing. Track T states the Temporal Chain
as a substrate track and records honestly that Ghost runs the core and handoff
layers while SEAM's streams and routing layers are documented but not installed
here. Track Q states the quality gates: coverage scaled the way SEAM scales it,
where every test is load-bearing and none is written to reach a count, and no
god files, currently enforced at a 450-line ceiling meant to be tightened rather
than raised.

Ghost's persona is now launchable from four agent clients. `tools/launchers/`
renders one shared persona body into each harness's own frontmatter and agent
directory, so a charter change is never copied by hand. `grok inspect` and
`agy agent` both list `canticle-ghost`. Two defects surfaced while wiring it:
`ghost-codex` selected a `[profiles.ghost]` that did not exist in
`~/.codex/config.toml`, now defined to mirror the `seam` profile with
approval on-request; and the shared charter still lives outside the repository
at `~/.config/canticle-agents/ghost.md`, so a clean-room rebuild cannot yet
reproduce it. That gap is recorded on the roadmap rather than papered over.

## HISTORY#029 — Correct the Q1 gate to behavior verification
- Date: `2026-08-25T16:40:00-05:00`
- Agent: `claude`
- Status: `done`
- Topics: `correction, docs, evaluation, roadmap, status, tests`
- Commits: `working-tree`
- Refs: `docs/roadmap/SECOND_BRAIN_ROADMAP.md, PROJECT_STATUS.md, docs/handoffs/2026-08-25-temporal-chain-named.md`
- Supersedes: `HISTORY#028`
- Verification: `provider-free suite passed 196 tests with 8 live tests deselected; verify_continuity and verify_handoffs passed; git diff --check passed`

`HISTORY#028` framed the Q1 quality gate as scaling coverage the way SEAM scales
it, and the roadmap section it landed carried staged numeric milestones of
roughly 500, 1,200, and 3,000 tests. That framing was wrong, and the operator
corrected it: a test exists to verify a behavior, not to reach an amount.

The distinction is not cosmetic. A numeric target makes padding rational — it
rewards adding tests that cannot fail for any reason an operator would care
about, which buys false confidence and raises the cost of every later change.
It also makes a passing total look like evidence when it is not; "196 tests
pass" says nothing about whether any particular behavior is verified.

Q1 is now titled "Behavior verification" and states the standard directly: every
behavior Ghost claims gets a test that fails when that behavior stops happening.
SEAM's suite is large because SEAM has that many behaviors worth verifying, so
its size is an output of the discipline rather than a target to chase. The
staged milestones are deleted rather than restated. The exit gate is unchanged
in substance — mutating any documented behavior must fail at least one test, and
no test may pass regardless of the code under it — but it now adds that
uncovered behavior is named explicitly instead of hidden behind a passing total.

The same count-based framing was removed from the roadmap position table,
`PROJECT_STATUS.md`, and the current handoff's known gaps. No test was added,
removed, or changed by this correction; only the standard that governs them.

## HISTORY#030 — Adopt SEAM's benchmark and proof standard as Q3
- Date: `2026-08-25T17:05:00-05:00`
- Agent: `claude`
- Status: `done`
- Topics: `evaluation, ledger, roadmap, status, verification`
- Commits: `working-tree`
- Refs: `docs/roadmap/SECOND_BRAIN_ROADMAP.md, REPO_LEDGER.md, PROJECT_STATUS.md`
- Supersedes: `HISTORY#029`
- Verification: `provider-free suite passed 196 tests with 8 live tests deselected; verify_continuity and verify_handoffs passed; git diff --check passed; SEAM repository read only, no file modified there`

Q1 established that a test verifies a behavior. That is necessary but does not
cover the business Ghost is actually in: proving claims with evidence a skeptic
can re-run. Q3 closes that gap, and it adopts SEAM's existing benchmark standard
rather than inventing a second one.

The governing invariant is ported verbatim from SEAM's repository ledger:
benchmark claims must be auditable by bundle hash, case hashes, fixture hashes,
and git SHA; diffed against a prior run; passing the benchmark gate; and kept
separated from publish-only holdout runs. Ghost's ledger now carries it as a
stable decision alongside the rule that a test is never written to reach a count
and that a passing total is not evidence for any particular behavior.

Q3's deliverables port the mechanics that make the invariant enforceable: sealed
bundles with canonical-JSON hashing that excludes volatile timing fields so two
honest re-runs compare equal; Benchmark Integrity Levels where an unjudged or
stub-judged result cannot seal above the lowest level without a recorded
override; baselines resolved from the merge-base of HEAD and origin/main with
holdout runs excluded and a first run performing no regression check rather than
inventing one; holdout sets reserved for publish-time audit behind an explicit
confirmation; full-fidelity per-case capture so a paid run is never reduced to
aggregates; failure classification that splits a wrong answer by which layer
failed; tokens-exact table-priced cost where an unpriced model reports null
rather than a fabricated number; recording the model that actually served a
request so a silent substitution cannot pass as the model requested; and a CI
posture where credential-free stub-judge smoke runs on every pull request while
paid runs stay operator-gated.

The G-track exit gates were rewritten to depend on this. G1's frozen evaluation,
G2's recall improvement, and G3's specialist comparison are now claims that
require a sealed bundle naming its baseline and integrity level, not a reported
score.

Ghost has no benchmark infrastructure today, and Q3 is recorded as planned
rather than partially satisfied. Nothing in this entry claims a measurement.
SEAM was read for its standard and not modified: its working tree carries only
changes predating this session, and no file under the SEAM repository was
written.

## HISTORY#031 — Enforce the protocol at the commit gate and audit recorded facts
- Date: `2026-08-25T18:05:00-05:00`
- Agent: `claude`
- Status: `done`
- Topics: `ci, continuity, correction, docs, gates, history, tests, tools, verification`
- Refs: `tools/git-hooks/pre-commit, tools/git-hooks/install.sh, tools/history/recorded_fact_audit.py, tools/history/verify_continuity.py, tools/history/closeout.py, tests/test_recorded_facts.py, tests/test_local_gates.py, .github/workflows/ci.yml, .github/workflows/public-ci.yml, AGENTS.md, REPO_LEDGER.md, docs/status/CURRENT_STATE.md`
- Commits: `working-tree`
- Supersedes: `HISTORY#030`
- Verification: `213 passed, 8 deselected; recorded_fact_audit clean; commit hook proven to block a staged .claude/ path and a stale count, and to pass a clean tree; verify_continuity, verify_handoffs, and closeout passed; git diff --check passed; SEAM read only, nothing modified there`

Ghost's continuity gates were enforced only by an agent remembering to run
closeout, which is not enforcement. `tools/git-hooks/pre-commit` is now the
canonical commit gate: git runs it for every commit regardless of which agent or
operator started it. It scope-blocks agent-local and generated paths
(`.claude/`, `.ghost/`, `checkpoints.db`, SQLite sidecars), then runs
`verify_continuity`, `verify_handoffs`, and the recorded-fact audit. Both block
paths were proven by staging a real file and observing the refusal, not asserted.

The recorded-fact audit closes the gap that nothing checked: factual claims an
agent writes in prose. It caught a live instance immediately. `CURRENT_STATE.md`
recorded `184 passed` while `PROJECT_STATUS.md` said 196 and the suite ran 196,
so a reader routed to either current-state authority got a different answer and
neither file looked wrong alone. Three fact types are checked — test counts
across the status authorities, cited module lengths against the files, and
handoff pointers against the registry.

Building it produced two false negatives worth recording, because both are the
failure mode the audit exists to prevent. First, the extractor matched only one
word order, so `passes 196 provider-free tests` was never extracted and a
disagreement could not be detected at all; an injected `173 passed` passed
clean. Second, the rule that distinguished a record of the past from a claim
about now keyed on a `HISTORY#NNN` citation, but current-state prose cites
history entries as supporting evidence, so the live claim was skipped. The
discriminator now keys on explicit past-tense language, which is the convention a
superseded number must be written with. Both were found by injecting the drift
and confirming the audit failed, rather than by observing it pass.

There is deliberately no suppression flag anywhere in the chain, and
`tests/test_local_gates.py` fails if one appears, if the hook drops a required
gate, or if it stops scope-blocking. A local gate that is quieter than the check
which blocks a PR converts "unverified" into "verified", and "verified" is the
state the next agent acts on.

Ghost's own CI contract test then caught that the two new suites were wired into
`public-ci.yml` but not the credential-free lane of `ci.yml`, which would have
left them silent whenever the private tier could not run. Both workflows and the
closeout now run the same set.

The status authorities are reconciled to `213 passed, 8 deselected`, and a
ground-truth test compares the documented count against a real collection so
cross-document agreement cannot hide every authority being equally wrong.

## HISTORY#032 — Split CI so public verification needs no self-hosted runner
- Date: `2026-08-25T18:50:00-05:00`
- Agent: `claude`
- Status: `done`
- Topics: `ci, gates, roadmap, security, status, tests, verification`
- Commits: `working-tree`
- Refs: `.github/workflows/ci.yml, .github/workflows/public-ci.yml, tests/test_ci_contract.py, docs/roadmap/SECOND_BRAIN_ROADMAP.md, PROJECT_STATUS.md`
- Supersedes: `HISTORY#031`
- Verification: `213 passed, 8 deselected; uv run ruff check . passed with zero findings for the first time; test_ci_contract passed against both workflows; verify_continuity, verify_handoffs, closeout, and the commit hook passed; git diff --check passed`

`gh api` showed zero runners registered on the repository while all six `ci.yml`
jobs targeted `[self-hosted, seam-box]`. That is the mechanical cause of the
24-hour cancellation recorded against `25f47c4`: the jobs were never slow, they
were unroutable, and no runner ever claimed them.

Inspecting the jobs showed only two genuinely need the private SEAM SDK.
`tests` and `live` run `uv sync`, which resolves a git+ssh dependency across two
private repositories. `repo-hygiene`, `brand-assets`, and `package-smoke` use
`uv run --no-project` throwaway environments and `uv build`, and need no
credential at all — a split `tests/test_ci_contract.py` already encoded.

Those three moved to `public-ci.yml` on `ubuntu-latest`, where they run
automatically on every push and pull request. `ci.yml` shrank to the private
tier alone and stays `workflow_dispatch`-only, so a fork pull request still has
no path to the runner. Public verification no longer depends on a self-hosted
runner existing, which was the actual blocker on R2.

The header comment justifying the runner claimed two reasons: credentials and
hosted-minute cost. The cost half is stale — the repository is public, so hosted
minutes are free — and it was corrected rather than left to mislead the next
reader. The credential half stands, and is why the private tier keeps the runner
instead of storing a two-repository PAT as a secret in a public repository.

The private tier previously declared `needs:` on the three moved jobs. A
`needs:` cannot cross workflows, so that invariant was replaced rather than
deleted: the contract test now asserts the fast gates run automatically on
hosted infrastructure, which is a stronger guarantee than waiting on a dispatch
that requires a registered runner to move at all.

Full-tree lint became possible in the public lane because `ruff check .` now
passes with zero findings. The five long-standing avatar and image-tool findings
were fixed rather than excluded: PyGObject's require-version-before-import
contract and two seeded-RNG uses carry `noqa` with the reason, and two genuinely
unused unpacked variables were renamed. Two further findings introduced earlier
in this session — an unnecessary `noqa` and an unsorted import block — were also
repaired. The public lane lints the whole tree rather than a named subset,
because a narrowed scope is how a finding in an unlisted path stays green.

The runner is now optional. Registering `seam-box` remains required only for the
private SDK integration and paid live lanes, and can happen whenever the
operator chooses without blocking public exact-head verification.

## HISTORY#033 — Close the public repository and private-runner safety boundary
- Date: `2026-08-25T20:04:30-05:00`
- Agent: `codex`
- Status: `done`
- Topics: `ci, correction, gates, history, repository, security, status, verification`
- Commits: `232048faefee15f9153f6f3fe216e6f745cc9175, dbd421babf0703c8c339e7b8db8d51fc51b58282`
- Refs: `docs/security/PUBLIC_REPOSITORY_AND_RUNNER.md, docs/audits/2026-08-25-public-runner-safety-closure.md, docs/handoffs/2026-08-25-public-runner-closed.md, https://github.com/Canticle-AI-Research/Ghost/pull/5, https://github.com/Canticle-AI-Research/Ghost/actions/runs/32907313331`
- Supersedes: `HISTORY#032`
- Verification: `PR #5 merged; exact main head dbd421b passed repo-hygiene, brand-assets, and package-smoke in run 32907313331; branch protection and repository Actions/security settings queried after merge; zero repository runners and zero repository secrets observed; private integration not run`

The safety candidate recorded by HISTORY#032 was reviewed, corrected, and
published. CodeRabbit's first staged review found that clean-checkout diff
hygiene needed an event range and that the private trigger test needed an exact
allowlist. Both were fixed; a second complete staged review reported no
findings. Provider-free tests, Ruff, build, and diff hygiene passed before the
eight-file commit.

PR #5 merged the exact safety commit through protected review. The resulting
`main@dbd421b` completed all three credential-free GitHub-hosted jobs. Private
CI did not dispatch. GitHub settings now require approval for every external-
contributor workflow, limit allowed Actions, default workflow permissions to
read, enable secret scanning and push protection, and expose no repository
secret or assigned runner.

Protected `main` requires an up-to-date PR with `repo-hygiene`, `brand-assets`,
and `package-smoke`, enforces the policy for administrators, requires resolved
conversations, and blocks force pushes and deletion. Organization runner-group
inventory could not be queried without organization-admin authority; zero
repository-visible assigned runners is therefore the recorded fail-closed
boundary. A future runner assignment requires a new review and history entry.

## HISTORY#034 — Isolate and qualify the canonical foundation candidate
- Date: `2026-08-25T20:17:58-05:00`
- Agent: `codex`
- Status: `in-progress`
- Topics: `architecture, ci, continuity, docs, gates, handoff, history, packaging, security, tests, tools, verification, wiki`
- Commits: `working-tree`
- Refs: `docs/README.md, docs/architecture/COMPLETE_SYSTEM_BLUEPRINT.md, docs/operations/COMMAND_REFERENCE.md, docs/roadmap/SECOND_BRAIN_ROADMAP.md, docs/handoffs/2026-08-25-canonical-foundation-candidate.md, tools/history, templates/temporal-chain, https://github.com/Canticle-AI-Research/Ghost/pull/5`
- Supersedes: `HISTORY#033`
- Verification: `clean docs/canonical-blueprint worktree: uv sync --frozen; uv run pytest -q passed provider-free with live tests deselected by the default marker; uv run ruff check . passed; uv build passed; focused credential-free continuity suites passed; git diff --check passed; initial complete CodeRabbit review produced 21 findings, 20 accepted and corrected, one private-remote redaction suggestion rejected because the exact non-secret dependency locator is already public package metadata and required for rebuild documentation; final re-review pending`

The large dirty candidate was split at the Git index rather than by resetting
the operator's working tree. The clean `docs/canonical-blueprint` branch holds
the wiki, Temporal Chain, license/company foundation, and launcher tooling. The
primary checkout retains only the avatar runtime/assets/test/tool candidate plus
its CLI, package, and lock changes.

Clean-room verification caught that local-avatar environment variables had
leaked into the canonical configuration page even though their source was not
part of this slice. They were removed until the avatar lands. Review then found
real fail-open edges in append-only history, handoff index/document parity,
handoff timestamp ordering, blocked-path rename handling, and template input
validation. Each accepted finding gained either a focused regression test or a
template install assertion.

The documentation was also reconciled to merged `main@dbd421b`, the exact
33-entry predecessor history, the local-only avatar boundary, the partial
harness-installer boundary, credential-free public bundle verification, and
machine-neutral handoff commands. Publication remains in progress until the
exact pushed head passes required CI and merges through protected `main`.
