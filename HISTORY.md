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

## HISTORY#035 — Merge the canonical Ghost foundation
- Date: `2026-08-25T20:25:44-05:00`
- Agent: `codex`
- Status: `done`
- Topics: `ci, continuity, docs, handoff, history, packaging, repository, status, verification, wiki`
- Commits: `dcbad97b9583de403438241384e5dffb9776c810, fc0ebbb31966cf35fd36d442d603ac81e14a90ee, a5997c616e946496875a3ba4772ab9759b46f2d7`
- Refs: `docs/updates/2026-08-25-canonical-foundation.md, docs/handoffs/2026-08-25-canonical-foundation-merged.md, https://github.com/Canticle-AI-Research/Ghost/pull/6, https://github.com/Canticle-AI-Research/Ghost/actions/runs/32918686149, https://github.com/Canticle-AI-Research/Ghost/actions/runs/32918733013`
- Supersedes: `HISTORY#034`
- Verification: `PR #6 required jobs repo-hygiene, brand-assets, and package-smoke passed on exact head fc0ebbb; PR #6 merged as a5997c6; exact merge-head push run 32918733013 passed the same three jobs; complete committed-diff re-review reported zero findings; private integration and paid/live tests not run`

The canonical foundation is no longer a local or branch-only candidate. PR #6
merged the engineering wiki, build blueprint, Temporal Chain, license/company
foundation, and launcher tooling through protected `main`. The automatic hosted
workflow proved append-only history, continuity, documentation routing, package
construction, brand assets, lint, diff hygiene, and secret scanning on both the
exact pull-request head and the exact merge head.

The original dirty checkout was preserved throughout. After fast-forwarding it
to `main@a5997c6`, its remaining changes are limited to the avatar runtime and
assets, avatar test/tools, CLI hook, WebSocket dependency, and lock update. The
visual provenance audit found selected B2 sources mixed with rejected/provider
intermediates and a browser bridge that can open desktop items; that track stays
local until asset routing and the consequential-action boundary receive their
own review. Nothing was deleted or promoted silently.

## HISTORY#036 — Qualify the public Ghost-to-SEAM transport candidate
- Date: `2026-08-25T21:37:11-05:00`
- Agent: `codex`
- Status: `in-progress`
- Topics: `architecture, ci, config, continuity, docs, handoff, history, installation, ledger, memory, packaging, sdk, security, status, tests, trust, verification, wiki`
- Commits: `working-tree`
- Refs: `src/ghost/seam_memory.py, src/ghost/config.py, pyproject.toml, uv.lock, .github/workflows/public-ci.yml, .github/workflows/ci.yml, docs/architecture/SEAM_HTTP_CONTRACT.md, docs/decisions/0005-opaque-seam-service-boundary.md, docs/handoffs/2026-08-25-public-seam-transport-qualified.md, https://github.com/Canticle-AI-Research/Seam/pull/231`
- Supersedes: `HISTORY#035`
- Verification: `uv run ruff check . passed; uv run python -m pytest --durations=10 passed 200 provider-free tests with 8 paid/live tests deselected; uv build passed; a fresh wheel environment installed canticle-ghost using public dependencies only and ran the real ghost --help; git diff --check passed; two complete CodeRabbit cycles returned eight findings, all repaired; final no-findings review and exact-head PR CI remain pending`

The locally qualified `feat/public-seam-transport` candidate replaces Ghost's
private Git/SDK dependency with an independently authored `httpx` adapter for
the opaque SEAM begin, actions, complete, fail, and recall routes. The adapter
streams every response under an 8 MiB cap before parsing, rejects malformed
public memory scores and shapes, redacts the bearer token from settings, sends
only exception classes on failure, and omits client-selected evidence/check IDs
from completion so the service remains authoritative.

The public lock and built wheel contain only public package sources. Automatic
hosted CI now installs Ghost, runs the complete provider-free suite on Python
3.11 and 3.13, clean-installs the wheel, and smokes the actual command. Manual
live CI requires explicit provider and SEAM service configuration plus the paid
run switch; no workflow targets a self-hosted runner.

Documentation now carries the exact HTTP state machine, payloads, limits,
errors, proof split, installation, configuration, architecture, lifecycle,
security, licensing, release, rebuild, and roadmap boundary. SEAM PR #231 is
the coordinated server candidate and remains under exact-head CI/review.
Neither source candidate is a compatible hosted deployment or package release.
This event advances the one-live-head handoff chain to
`docs/handoffs/2026-08-25-public-seam-transport-qualified.md`; protected merge
and a successor publication handoff remain before this item is done.

## HISTORY#037 — Repair exact-head public transport CI
- Date: `2026-08-25T21:46:52-05:00`
- Agent: `codex`
- Status: `in-progress`
- Topics: `ci, continuity, handoff, history, packaging, sdk, tests, verification`
- Commits: `working-tree`
- Refs: `.github/workflows/public-ci.yml, tests/test_ci_contract.py, docs/handoffs/2026-08-25-public-seam-transport-ci-repaired.md, https://github.com/Canticle-AI-Research/Ghost/pull/8, https://github.com/Canticle-AI-Research/Ghost/actions/runs/32923573440, https://github.com/Canticle-AI-Research/Seam/pull/231`
- Supersedes: `HISTORY#036`
- Verification: `SEAM PR #231 exact source head 40562b3 passed seven hosted jobs and merged as 9d29c24; Ghost PR #8 package-smoke passed; focused local CI-contract, history, recorded-fact, and brand tests passed after repair; Ruff and git diff --check passed; repaired exact-head Ghost CI pending`

The coordinated SEAM server contract is now protected-main source. Ghost PR
#8's first hosted run proved the public wheel clean-installs and the real CLI
imports, but exposed two CI-environment defects. The full Python matrix used a
shallow checkout even though canonical history tests resolve every recorded
commit. The isolated hygiene and brand lanes imported the shared opaque HTTP
fake from `conftest.py` without installing its public `httpx` dependency.

The Python 3.11 and 3.13 jobs now fetch complete Git history. The isolated
lanes explicitly install `httpx`, and CI-contract tests pin both properties so
the same false-red environment cannot return silently. The repair leaves the
runtime, wire contract, dependency lock, wheel, and primary avatar WIP
unchanged.

This event advances the live handoff to
`docs/handoffs/2026-08-25-public-seam-transport-ci-repaired.md`. The repaired
head must still pass all hosted jobs, protected-main requirements must add both
Python matrix contexts without weakening existing policy, and PR #8 must merge
before the client boundary is published. No live provider/service test, paid
benchmark, release, or deployment was run.

## HISTORY#038 — Publish the public Ghost-to-SEAM transport
- Date: `2026-08-25T21:49:58-05:00`
- Agent: `codex`
- Status: `done`
- Topics: `architecture, ci, continuity, handoff, history, packaging, repository, sdk, security, status, tests, verification`
- Commits: `7a8228a7de823881a26644973a2c225e0f8a252b, 66841fc3450b93a275b5e13e4fa82e9531be93b7`
- Refs: `src/ghost/seam_memory.py, pyproject.toml, uv.lock, .github/workflows/public-ci.yml, docs/architecture/SEAM_HTTP_CONTRACT.md, docs/handoffs/2026-08-25-public-seam-transport-published.md, https://github.com/Canticle-AI-Research/Ghost/pull/8, https://github.com/Canticle-AI-Research/Ghost/actions/runs/32924071820, https://github.com/Canticle-AI-Research/Ghost/actions/runs/32924125667, https://github.com/Canticle-AI-Research/Seam/pull/231`
- Supersedes: `HISTORY#037`
- Verification: `PR #8 exact head 7a8228a passed repo-hygiene, brand-assets, tests (3.11), tests (3.13), and package-smoke; PR #8 merged as 66841fc; exact merge-head run 32924125667 passed the same five jobs; protected main requires all five contexts with strict up-to-date enforcement; provider/live tests, package release, and deployment not run`

Ghost's public dependency and opaque SEAM transport boundary is protected-main
source through PR #8. The package graph contains no private SEAM implementation
or Git source. The built wheel clean-installs from public dependencies and the
real `ghost --help` imports. Begin, action recording, accepted completion,
failed-turn rejection, and recall cross an independently authored bounded HTTP
adapter; SEAM remains authoritative for MIRL, reasoning graphs, evidence,
verification, and durable persistence.

The exact PR head and exact merge head each passed the five-job hosted suite.
Protected main now requires both Python matrix jobs in addition to repository
hygiene, brand assets, and package smoke. Existing administrator enforcement,
conversation resolution, and force-push/deletion restrictions were preserved.

This closes roadmap item R2 and the source/install portion of R4. It does not
publish a package artifact, tag, GitHub Release, or compatible hosted endpoint.
No live provider/service test or paid benchmark ran. The canonical handoff
advances to `docs/handoffs/2026-08-25-public-seam-transport-published.md`; the
next product gate is the frozen Stage 1 task/memory evaluation baseline.

## HISTORY#039 — Qualify the frozen Stage 1 evaluation substrate
- Date: `2026-08-25T22:08:42-05:00`
- Agent: `codex`
- Status: `in-progress`
- Topics: `agent, ci, config, continuity, docs, evaluation, gates, handoff, history, memory, roadmap, status, tests, verification`
- Commits: `working-tree`
- Refs: `evals/stage1/fixtures.json, evals/stage1/MANIFEST.json, tools/evaluation, tests/test_evaluation.py, docs/evaluation/STAGE1_FROZEN_SUITE.md, .github/workflows/public-ci.yml, src/ghost/config.py, src/ghost/lifecycle.py, docs/handoffs/2026-08-25-stage1-frozen-evals-qualified.md`
- Supersedes: `HISTORY#038`
- Verification: `fixture validation passed 20 cases; dirty development BIL-0 smoke sealed, verified, and gated; uv run ruff check . passed; uv run python -m pytest --durations=10 passed 212 provider-free tests with 8 live tests deselected; git diff --check passed; clean exact-commit baseline and exact-head CI pending`

The `ghost-stage1-frozen-v1` corpus freezes 20 cases across source-grounded
research, repository QA/diagnosis, approval/refusal, timeout/cancellation,
restart memory, stale memory, failed-turn non-admission, and namespace/principal
isolation. Each case names selected and excluded evidence, answer constraints,
tool outcomes, terminal state, step/tool/context budgets, and forbidden effects.

An independently authored deterministic runner compares `ghost-memory` with a
named `no-memory` arm and emits full per-case results. The BIL-0 bundle records
the exact Git state, canonical fixture and case hashes, manifest and stable-
result hashes, and a whole-bundle hash. Verification cross-checks suite, Git,
fixture, case count, and IDs; the gate adds zero isolation violations, zero
forbidden effects, and zero candidate contract failures. The runner records
null provider usage/cost and `claimable: false`: this is harness proof, not a
model capability score.

Runtime work adds `GHOST_MAX_STEPS`, a validated 2–100 LangGraph superstep
ceiling with default 25, including programmatic rejection before recall. The
documentation freezes the Stage 1 mission/output record and explicitly defers
streaming until disconnect, partial-output, cancellation, and exactly-once
terminal semantics exist.

The local development artifact was sealed only with `--allow-dirty` and cannot
be a baseline. Commit this exact infrastructure, generate a bundle from that
clean commit, add it in a successor chronology event, and require the hosted
`stage1-evals` job before merge. Provider/live and release-candidate proof
remain open and require explicit operator approval.

## HISTORY#040 — Freeze the clean-source Stage 1 BIL-0 baseline
- Date: `2026-08-25T22:10:35-05:00`
- Agent: `codex`
- Status: `in-progress`
- Topics: `ci, continuity, docs, evaluation, gates, handoff, history, memory, snapshot, status, tests, verification`
- Commits: `bc18555d364a9ed49ce9be2e6c35378bbad29467`
- Refs: `evals/runs/stage1/ghost-stage1-frozen-v1-bil0-baseline.json, evals/stage1/MANIFEST.json, docs/evaluation/STAGE1_FROZEN_SUITE.md, docs/handoffs/2026-08-25-stage1-baseline-frozen.md`
- Supersedes: `HISTORY#039`
- Verification: `clean-source smoke sealed bundle 6b16ad744b1dc585fc197150d0e0aee4254c985b1e0810619f0ed64f44fb03ad from bc18555; public verifier passed all eleven checks; safety gate passed with zero candidate contract failures, isolation violations, or forbidden effects; claimable false; successor full suite/build and exact-head CI pending`

The first durable Stage 1 evaluation artifact is bound to clean exact source
`bc18555d364a9ed49ce9be2e6c35378bbad29467`, not an uncommitted worktree. Its
manifest records `dirty_worktree: false`, 20 frozen cases in each named arm,
canonical fixture hash
`4f10f3d8022beeb3ac7adbf3b01bd1b727c81d9db48b8388f8e129b84e3ed61d`,
and per-case hashes. The complete bundle hash is
`6b16ad744b1dc585fc197150d0e0aee4254c985b1e0810619f0ed64f44fb03ad`.

Credential-free verification passed bundle version, integrity level, payload
shape, manifest/result/bundle hashes, and suite/Git/fixture/count/ID cross-
checks. The safety gate additionally found zero candidate contract failures,
isolation violations, or forbidden effects. The artifact deliberately records
`claimable: false`, null provider usage/cost, and a deterministic stub evaluator.
Its scripted no-memory difference is a harness diagnostic, not evidence of
model or memory quality.

This event advances the handoff to
`docs/handoffs/2026-08-25-stage1-baseline-frozen.md`. Full successor-tree tests,
build, exact-head hosted CI, protected merge, and publication closeout remain.
No provider/live test, paid judge, release candidate, package release, or
deployment was run.

## HISTORY#041 — Repair the Stage 1 smoke to execute Ghost's lifecycle
- Date: `2026-08-25T22:15:15-05:00`
- Agent: `codex`
- Status: `in-progress`
- Topics: `agent, ci, correction, docs, evaluation, gates, handoff, history, memory, tests, verification`
- Commits: `working-tree`
- Refs: `tools/evaluation/runner.py, tools/evaluation/fixtures.py, tools/evaluation/integrity.py, tools/evaluation/__main__.py, tests/test_evaluation.py, .github/workflows/public-ci.yml, docs/evaluation/STAGE1_FROZEN_SUITE.md, docs/handoffs/2026-08-25-stage1-lifecycle-smoke-repaired.md`
- Supersedes: `HISTORY#040`
- Verification: `focused evaluation, CI-contract, and layering tests passed after repair; CodeRabbit CLI 0.7.5 authenticated but review did not run because the unconnected repository exhausted its free allowance and returned a five-minute rate limit; full suite/build, clean successor baseline, and exact-head CI pending`

Manual review found that the first BIL-0 runner scored scripted records without
invoking Ghost's framework-free lifecycle. The artifact was already explicitly
non-claimable, but calling it lifecycle accounting was weaker than the product
contract. The runner now executes `run_turn` against deterministic graph and
memory doubles. Accepted cases traverse begin, optional action recording, and
completion; rejected cases traverse begin and failure. Regression assertions
pin both sequences.

The same review closed three fail-open validation edges. Fixtures now reject
unknown evidence references, hidden evidence marked required, forbidden
evidence marked visible, and scripted steps/tools/context beyond declared
budgets. Bundle verification treats malformed case-count and case-ID types as
failed checks instead of throwing. The command gate likewise treats malformed
arm summaries as failure. Hosted evaluation CI installs the locked project so
the real lifecycle import is available.

CodeRabbit was invoked under its documented skill after a secret-safe changed-
path inspection; local `gitleaks` was unavailable. The CLI connected but did
not analyze the diff because the repository was not attached to the accessible
organization and the free allowance was rate-limited. No finding is attributed
to CodeRabbit.

The first baseline remains preserved as historical BIL-0 harness evidence.
Commit this repair, generate and preserve a new clean-source lifecycle-executing
baseline, then rerun full qualification before publication.

## HISTORY#042 — Freeze the lifecycle-executing Stage 1 baseline
- Date: `2026-08-25T22:16:51-05:00`
- Agent: `codex`
- Status: `in-progress`
- Topics: `agent, ci, continuity, evaluation, gates, handoff, history, memory, snapshot, status, tests, verification`
- Commits: `78a5035929f03ab94e1f8f5e1cd3cb76829f7e07`
- Refs: `evals/runs/stage1/ghost-stage1-frozen-v1-bil0-lifecycle-baseline.json, tools/evaluation/runner.py, docs/evaluation/STAGE1_FROZEN_SUITE.md, docs/handoffs/2026-08-25-stage1-lifecycle-baseline-qualified.md`
- Supersedes: `HISTORY#041`
- Verification: `clean-source lifecycle smoke sealed bundle 9ce3f9d80ab2a08de3767c0eaf48d84d74e02e73ef64db03891594e6c788cad2 from 78a5035; public verifier passed all eleven checks; gate passed with zero candidate failures, isolation violations, or forbidden effects; accepted and rejected lifecycle event sequences matched; claimable false; final successor-tree full suite/build and exact-head CI pending`

The reviewed BIL-0 successor is bound to clean exact source
`78a5035929f03ab94e1f8f5e1cd3cb76829f7e07` and stored separately from the
initial artifact. Its bundle hash is
`9ce3f9d80ab2a08de3767c0eaf48d84d74e02e73ef64db03891594e6c788cad2`;
the manifest retains the frozen fixture hash and reports a clean worktree.

The result now contains actual framework-free lifecycle events from `run_turn`.
An accepted tool case records begin, action recording, and completion. A
rejected timeout scenario records begin and failure, with no completion.
Credential-free verification passed all eleven integrity/cross-identity checks,
and the gate found zero candidate contract failures, isolation violations, or
forbidden effects.

The artifact remains BIL-0, deterministic, and explicitly non-claimable. Its
scripted no-memory difference does not become a memory-quality claim merely
because the real lifecycle ran. The first baseline remains preserved as the
pre-review record; this successor is the current comparison artifact.

Advance the handoff to
`docs/handoffs/2026-08-25-stage1-lifecycle-baseline-qualified.md`, finish full
successor-tree qualification, push, require the hosted evaluation context, and
merge through protected main. Provider/live and release-candidate proof were
not run.

## HISTORY#043 — Repair all Stage 1 evaluation review findings
- Date: `2026-08-25T22:23:34-05:00`
- Agent: `codex`
- Status: `in-progress`
- Topics: `ci, correction, docs, evaluation, gates, handoff, history, roadmap, security, tests, verification`
- Commits: `working-tree`
- Refs: `tools/evaluation/fixtures.py, tools/evaluation/runner.py, tools/evaluation/integrity.py, tools/evaluation/__main__.py, tests/test_evaluation.py, README.md, REPO_LEDGER.md, docs/security/PUBLIC_REPOSITORY_AND_RUNNER.md, docs/evaluation/MEMORY_EVALS.md, docs/evaluation/STAGE1_FROZEN_SUITE.md, docs/roadmap/SECOND_BRAIN_ROADMAP.md, docs/handoffs/2026-08-25-stage1-review-repaired.md`
- Supersedes: `HISTORY#042`
- Verification: `CodeRabbit CLI 0.7.5 full review completed over 44 changed files with eight findings, four major and four minor; all eight reproduced and repaired; focused evaluation and CI-contract tests passed; final clean-source bundle, full suite/build, exact-head CI, and protected merge pending`

The delayed CodeRabbit review completed after the earlier free-allowance rate
limit and returned eight valid findings. Fixture budgets allowed `max_steps=1`
even though `run_turn` rejects below two. Observed effects were treated as a
truthy aggregate rather than typed and compared to each case's forbidden set.
The gate trusted summary failure counts instead of exact per-case two-arm
coverage and outcomes. An outside-repository fixture path raised raw
`ValueError`. All four major findings now fail closed with regressions.

Four documentation findings were also repaired. The Q3 detail status now
matches the in-progress table while G2 remains planned. Accepted lifecycle text
makes action recording conditional. The fixture example is explicitly marked
abbreviated. README and the security/ledger boundary now name `stage1-evals`
as the automatic job that must become the sixth protected context before merge.

The current clean-source lifecycle baseline remains valid for its exact prior
runner, but it predates these repairs. Preserve it and generate a separately
named final bundle from the committed review-repair source. No provider/live,
paid judge, release-candidate, release, or deployment work ran.

## HISTORY#044 — Freeze the final post-review Stage 1 baseline
- Date: `2026-08-25T22:24:57-05:00`
- Agent: `codex`
- Status: `in-progress`
- Topics: `ci, continuity, evaluation, gates, handoff, history, memory, snapshot, status, tests, verification`
- Commits: `ee4f63b5b2be5ac1272caf1d33ff29f09701ad3a`
- Refs: `evals/runs/stage1/ghost-stage1-frozen-v1-bil0-final-baseline.json, docs/evaluation/STAGE1_FROZEN_SUITE.md, docs/handoffs/2026-08-25-stage1-final-baseline-qualified.md`
- Supersedes: `HISTORY#043`
- Verification: `clean-source final bundle 57ca22ea5706f78e8513b92c8569fb8641e3e58c43cfedf3df0e39d81512a959 sealed from post-review source ee4f63b; all eleven integrity checks and gate_case_coverage, gate_candidate_outcomes, gate_safety passed; zero candidate contract failures, isolation violations, or forbidden effects; claimable false; final successor-tree suite/build and exact-head CI pending`

The final local BIL-0 artifact is bound to the exact clean source containing all
eight CodeRabbit repairs: `ee4f63b5b2be5ac1272caf1d33ff29f09701ad3a`.
The bundle hash is
`57ca22ea5706f78e8513b92c8569fb8641e3e58c43cfedf3df0e39d81512a959`,
and its manifest retains the unchanged frozen fixture and per-case identities.

Verification passed the eleven bundle and cross-identity checks. The derived
gate independently reconstructed exactly one `ghost-memory` and one
`no-memory` record for every manifest case, required every candidate case to
pass, and inspected per-case forbidden-evidence/effect verdicts. All three gate
checks passed with zero candidate failures or safety violations.

The artifact is still a deterministic BIL-0 contract smoke with null provider
usage/cost and `claimable: false`. Earlier baseline artifacts remain preserved
to make the review progression auditable; this post-review artifact is the
current comparison baseline.

Advance the handoff to
`docs/handoffs/2026-08-25-stage1-final-baseline-qualified.md`, finish exact
successor-tree qualification, publish the PR, require the hosted evaluation
context, and merge through protected main. No paid/live or release-candidate
qualification ran.

## HISTORY#045 — Qualify the Stage 1 evaluation candidate for publication
- Date: `2026-08-25T22:29:49-05:00`
- Agent: `codex`
- Status: `in-progress`
- Topics: `ci, continuity, docs, evaluation, gates, handoff, history, roadmap, security, status, tests, verification`
- Commits: `bc18555d364a9ed49ce9be2e6c35378bbad29467, 89ca75c9e1837dbad6964ef4877509a6842e1bf4, 78a5035929f03ab94e1f8f5e1cd3cb76829f7e07, 78ac27a9424913e8bb5e7d04c9b10e323768121b, ee4f63b5b2be5ac1272caf1d33ff29f09701ad3a, a6f9e6d19e12a3ee0b0c944b9e9a4f2e6264d0c6`
- Refs: `evals/stage1, evals/runs/stage1/ghost-stage1-frozen-v1-bil0-final-baseline.json, tools/evaluation, tests/test_evaluation.py, .github/workflows/public-ci.yml, docs/evaluation/STAGE1_FROZEN_SUITE.md, docs/handoffs/2026-08-25-stage1-candidate-ready.md, https://github.com/Canticle-AI-Research/Ghost/actions/runs/32924345004`
- Supersedes: `HISTORY#044`
- Verification: `uv run python -m tools.history.closeout --agent codex passed through HISTORY#044; uv run ruff check . passed; uv run python -m pytest --durations=10 passed 219 provider-free tests with 8 live tests deselected; uv build passed; git diff --check passed; CodeRabbit full review returned eight findings all repaired; final-delta review returned one wording finding repaired; exact main@620caee run 32924345004 passed five current required jobs; candidate push/PR/six-job CI pending`

The Stage 1 frozen-evaluation candidate is locally complete. It freezes 20
cases across ten required categories, executes Ghost's framework-free
lifecycle with deterministic graph/memory doubles, records exact candidate and
no-memory coverage, and seals credential-free BIL-0 artifacts with public
verification and derived outcome/safety gates. `GHOST_MAX_STEPS` supplies the
runtime superstep ceiling that the fixture budgets exercise.

The final clean-source bundle remains
`57ca22ea5706f78e8513b92c8569fb8641e3e58c43cfedf3df0e39d81512a959`.
All eleven bundle-level verifier checks and the three gate checks passed. Case
records deliberately retain expected no-memory-arm failures; those are not
bundle-integrity failures. The deterministic artifact remains non-claimable.

CodeRabbit's full review returned four major and four minor findings, all
reproduced and repaired. A final-delta review returned one minor ambiguity
between bundle-level and per-case checks; the documentation now distinguishes
them explicitly.

Live reconciliation also closed the stale PR #9 status: exact current
`main@620caee` passed all five protected jobs in run `32924345004`. The Stage 1
PR must expose and pass `stage1-evals`, then protected main must add it as the
sixth required context without weakening existing policy. No paid/provider,
release-candidate, package release, or deployment qualification ran.

## HISTORY#046 — Publish the frozen Stage 1 evaluation substrate
- Date: `2026-08-25T22:38:20-05:00`
- Agent: `codex`
- Status: `done`
- Topics: `ci, continuity, docs, evaluation, gates, handoff, history, memory, roadmap, security, status, verification`
- Commits: `cbdd190e864213d4b0c45dcdf36667817872addf, 86774efb45c4f93b7e83272c9f1ce638e8c46fb7`
- Refs: `https://github.com/Canticle-AI-Research/Ghost/pull/10, https://github.com/Canticle-AI-Research/Ghost/actions/runs/32926952876, https://github.com/Canticle-AI-Research/Ghost/actions/runs/32927031615, docs/handoffs/2026-08-25-stage1-frozen-published.md`
- Supersedes: `HISTORY#045`
- Verification: `exact PR head cbdd190 passed repo-hygiene, brand-assets, tests (3.11), tests (3.13), package-smoke, and stage1-evals in run 32926952876; branch protection narrowly added stage1-evals while preserving strict status, administrator enforcement, conversation resolution, and force-push/deletion blocks; PR #10 merged as 86774ef; exact main run 32927031615 passed the same six jobs`

The frozen Stage 1 evaluation substrate is now protected-main source rather
than a local candidate. PR #10 published the 20-case corpus, actual-lifecycle
two-arm BIL-0 runner, canonical seals and verifier, derived gate, step ceiling,
CI lane, and rebuild/operator documentation after all review findings were
repaired.

The new `stage1-evals` context first existed and passed on the exact PR head.
It was then added as the sixth required context through the narrow status-check
endpoint; no other protection setting was weakened. Exact merge-head CI passed
all six jobs.

This closes the provider-free frozen-substrate issue, not the whole Stage 1
product gate. The deterministic artifact remains non-claimable. Provider-live,
paid judge, exact release-candidate, package release, and deployment proof
remain open. Deliberate memory governance is the next implementation issue.

## HISTORY#047 — Qualify deliberate-memory governance for publication
- Date: `2026-08-26T00:09:10-05:00`
- Agent: `codex`
- Status: `in-progress`
- Topics: `agent, architecture, cli, config, continuity, correction, docs, evaluation, handoff, history, memory, roadmap, security, status, tests, verification, wiki`
- Commits: `working-tree`
- Refs: `src/ghost/memory_policy.py, src/ghost/seam_memory.py, src/ghost/lifecycle.py, src/ghost/cli.py, evals/stage2, docs/handoffs/2026-08-26-deliberate-memory-qualified.md, https://github.com/Canticle-AI-Research/Seam/pull/233`
- Supersedes: `HISTORY#046`
- Verification: `uv run ruff check . passed; uv run pytest -q passed 257 provider-free tests with 8 live tests deselected; uv build passed; git diff --check passed; final CodeRabbit full-delta review returned zero findings after earlier invalid-thread, failure-finalization, ContextVar-restore, documentation, and CI-contract repairs; protected SEAM main@0b07244 supplies the exact server contract through PR #233; Ghost exact-head CI and merge pending`

The Ghost half of deliberate-memory governance is locally qualified on an
isolated worktree based on `main@e1d1b9a`. The provider-free admission policy
trusts operator input rather than model output, records admit/reject/review,
and persists only explicit admissions. Ordinary chatter is rejected; durable
but unconfirmed input is review-only and performs no durable write.

The operator can explicitly remember, recall current or historical state,
correct one opaque memory additively, and forget one memory only after repeating
its exact opaque ID with `--confirm`. Correction preserves a `supersedes`
history edge through the protected SEAM public contract. Workspace, project,
namespace, scope, and thread dimensions are carried consistently, while failed
or completed turns restore their active thread context. If failure finalization
also fails, Ghost preserves the original turn error and annotates the secondary
failure instead of masking it.

The frozen `ghost-stage2-memory-governance-v1` fixture has ten cases across
relevance, contradiction, idempotency, staleness, and isolation with canonical
hash `32ed350b167b1a412e9afabcdc75657afcc96c141937d267dcdb9a5830c69a7c`.
It proves mechanism behavior through the real policy and opaque adapter against
a stateful contract fake. It runs no model, has no matched no-memory answer
arm, and cannot support a G2 quality-improvement claim.

All governing architecture, command, how-to, installation, configuration,
trust, lifecycle, evaluation, glossary, status, ledger, roadmap, and wiki index
pages were updated in the same candidate. The primary avatar worktree remains
untouched. Advance the handoff to
`docs/handoffs/2026-08-26-deliberate-memory-qualified.md`, publish this exact
candidate through protected Ghost CI, and retain the sealed Q3 memory-quality
comparison as separate follow-up work.

## HISTORY#048 — Publish deliberate-memory governance
- Date: `2026-08-26T00:13:27-05:00`
- Agent: `codex`
- Status: `done`
- Topics: `agent, ci, continuity, docs, evaluation, gates, handoff, history, memory, roadmap, security, status, tests, verification`
- Commits: `2a23fdcd730c051a83bab26622154df993431980`
- Refs: `https://github.com/Canticle-AI-Research/Ghost/pull/12, https://github.com/Canticle-AI-Research/Ghost/actions/runs/32933045239, https://github.com/Canticle-AI-Research/Ghost/actions/runs/32933109326, docs/handoffs/2026-08-26-deliberate-memory-published.md`
- Supersedes: `HISTORY#047`
- Verification: `exact PR source 3c21112 passed repo-hygiene, brand-assets, tests (3.11), tests (3.13), package-smoke, and stage1-evals in run 32933045239; PR #12 merged as 2a23fdc; exact merge-head run 32933109326 passed the same six protected jobs; SEAM PR #233 source and all seven jobs were already protected-main at 0b07244; no paid/live lane ran`

Deliberate-memory governance is now protected-main source in both Ghost and
SEAM. Ghost PR #12 published deterministic operator-input admission,
non-admitting reject/review decisions, explicit remember, current/history
recall, additive correction, confirmed forgetting, workspace/project/thread
isolation, thread-context restoration, and the frozen 10-case Stage 2 mechanism
fixture. SEAM PR #233 supplies the protected opaque lifecycle enforcement.

Both the exact Ghost source head and merge head passed the full six-job matrix.
No private SEAM implementation entered Ghost, no avatar work was mixed into the
candidate, and no provider-live, paid judge, package release, or deployment
work ran.

This closes issue 6's implementation/publication boundary, not the G2 quality
exit. The fixture is mechanism-only and cannot establish task improvement. A
sealed Q3 bundle must still compare a named candidate against an identical-
budget baseline before any G2 or specialist-improvement claim. Advance the
handoff to `docs/handoffs/2026-08-26-deliberate-memory-published.md` and preserve
the avatar worktree while beginning only roadmap-compatible issue-7 foundation
work.

## HISTORY#049 — Qualify bounded specialist and operations foundations
- Date: `2026-08-26T00:32:11-05:00`
- Agent: `codex`
- Status: `in-progress`
- Topics: `agent, architecture, cli, commands, continuity, deployment, docs, handoff, history, operations, provenance, roadmap, security, status, tests, verification, wiki`
- Commits: `working-tree`
- Refs: `src/ghost/specialists.py, src/ghost/operations.py, docs/architecture/SPECIALIST_CONTRACT.md, docs/operations/RECOVERY_AND_OBSERVABILITY.md, docs/handoffs/2026-08-26-specialist-ops-foundation-qualified.md`
- Supersedes: `HISTORY#048`
- Verification: `uv run ruff check . passed; uv run pytest -q passed 270 provider-free tests with 8 live tests deselected; uv build passed; git diff --check passed; two complete CodeRabbit rounds identified three major redaction/coverage gaps, all repaired with regression coverage; final automated re-review unavailable after the free CLI reset extended to 50 minutes, manual final diff review passed; no provider/live/paid/deployment lane ran`

The issue-7 foundation candidate makes future specialist authority explicit
without activating a specialist topology. Every delegation names its parent
turn, role, objective, hard step/deadline/output budgets, complete tool/root and
memory scope, terminal state, and opaque evidence references. Non-success
outcomes and observer events discard adapter-controlled failure content in
favor of fixed safe codes; telemetry failure cannot change the work outcome.

Checkpoint recovery now uses SQLite's consistent online backup, SHA-256 and
`quick_check`, and atomic publication to a new destination only. Operator
commands back up, verify, and restore execution checkpoints without constructing
a model. Redacted health probes discard successful return content and expose
only `ok` or a failure class. The new architecture page, recovery runbook,
command reference, how-tos, blueprint, release boundary, wiki routes, ledger,
status, and roadmap define the complete mechanics and their limits.

This is not a G3 or G4 exit. No model-backed specialist, equal-budget Q3
comparison, hosted endpoint, dashboard, SEAM backup, restore drill, package
release, or deployment exists. Publish only after the clean review rerun and
all six protected exact-head jobs; preserve the separate avatar worktree.

## HISTORY#050 — Publish bounded specialist and operations foundations
- Date: `2026-08-26T00:41:04-05:00`
- Agent: `codex`
- Status: `done`
- Topics: `agent, architecture, ci, commands, continuity, deployment, docs, gates, handoff, history, operations, provenance, roadmap, security, status, tests, verification, wiki`
- Commits: `c9d8a83cbf5585338f9bf5db8b978e70fd2dd398`
- Refs: `https://github.com/Canticle-AI-Research/Ghost/pull/14, https://github.com/Canticle-AI-Research/Ghost/actions/runs/32934880135, https://github.com/Canticle-AI-Research/Ghost/actions/runs/32934944801, docs/handoffs/2026-08-26-specialist-ops-foundation-published.md`
- Supersedes: `HISTORY#049`
- Verification: `exact PR source 3d2d8b9 passed all six protected jobs in run 32934880135; PR #14 merged as c9d8a83; exact merge-head run 32934944801 passed the same six jobs; local closeout, Ruff, 270 provider-free tests with 8 live deselected, build, and diff hygiene passed; no provider/live/paid/release/deployment lane ran`

The issue-7 foundation is protected-main source. Specialist authority,
budgets, provenance, terminal normalization, and safe events now have an
enforceable provider-free contract. Operators can consistently back up,
digest/integrity-check, and restore checkpoint execution state to a new path,
while health probes and specialist failures publish only fixed safe codes.

This completes the requested foundation slice, not the G3/G4 roadmap exits.
There is no model-backed specialist topology, equal-budget improvement bundle,
hosted API, SEAM disaster recovery, package release, or deployment. CI also
surfaced a non-blocking Node 20 action-runtime deprecation warning for a focused
workflow maintenance follow-up. Advance the handoff to the protected-main
publication record and preserve the separate avatar worktree.

## HISTORY#051 — Establish the structural remediation ledger
- Date: `2026-08-27T11:36:21-05:00`
- Agent: `codex`
- Status: `done`
- Topics: `architecture, build, ci, continuity, docs, evaluation, gates, handoff, history, operations, packaging, roadmap, security, status, tests, tools, verification, wiki`
- Commits: `working-tree`
- Refs: `docs/audits/2026-08-27-structural-remediation-ledger.md, docs/audits/INDEX.md, docs/handoffs/2026-08-27-structural-remediation-ledger.md, docs/handoffs/INDEX.md, docs/status/CURRENT_STATE.md, PROJECT_STATUS.md`
- Supersedes: `HISTORY#050`
- Verification: `origin/main and local base reconciled at cccf99ae53dc144c68594ef3cfb67f4aa1471fd0; exact-head Public CI run 32935194091 passed all six required jobs; uv run python -m tools.history.closeout --agent codex passed through HISTORY#051; uv run ruff check . passed; uv run pytest --durations=10 passed 270 provider-free tests with 8 live tests deselected; uv build and git diff --check passed; Stage 1 validate-fixtures/smoke/verify/gate passed at BIL-0; pip-audit OSV reported no known vulnerabilities for the frozen runtime export; CodeRabbit CLI 0.7.5 reviewed all 12 src/ghost modules and returned 7 routed findings; documentation-delta review returned 2 findings and both were repaired; final automated rerun was rate-limited, manual final diff review passed; focused sentinel probes reproduced five P0 boundaries; no paid/live/release/deployment lane ran`

Ghost now has one registered ledger for current defects, benchmark gaps,
structural improvements, delivery work, and later product/legal gates. The
ledger separates seven P0 stop-ship findings from P1 immediate integrity work,
the Q3 benchmark program, P2 maintainability work, and P3 external/product
milestones. Every row names an owner surface, exit evidence, and dependencies,
and the course of action orders focused issue branches without mixing the
preserved avatar checkout.

Provider-free baseline verification remained green, but the audit reproduced
important gaps outside the previous suite: search could follow an in-root
symlink outside the readable root; a shell command exiting nonzero was recorded
as successful with exit code zero; timeout killed only the immediate shell and
left a descendant alive; an invalid approval boolean disabled the default gate;
and a working-directory dotenv could widen shell authority and redirect the
SEAM endpoint. Artifact inspection also showed that the source distribution
contains the tracked checkpoint database and other unqualified repository
surfaces. These observations block unattended shell use and release
publication until their ledger exits pass.

The report is documentation and routing only. No defect implementation,
dependency merge, avatar modification, paid/live provider or SEAM run, push,
merge, package publication, release, deployment, destructive cleanup, or
company/legal action occurred. Advance the handoff to the structural ledger
and begin GTOOL-001 from a new focused worktree based on current protected main.

## HISTORY#052 — Close the repository-search containment escape
- Date: `2026-08-27T16:24:40-05:00`
- Agent: `codex`
- Status: `done`
- Topics: `architecture, continuity, docs, gates, handoff, history, security, status, tests, tools, trust, verification`
- Commits: `working-tree`
- Refs: `src/ghost/path_policy.py, src/ghost/tools.py, tests/test_tools.py, tests/test_layering.py, docs/security/TRUST_BOUNDARIES.md, docs/handoffs/2026-08-27-gtool-001-search-containment-qualified.md`
- Supersedes: `HISTORY#051`
- Verification: `uv run pytest tests/test_tools.py tests/test_layering.py -q passed; uv run ruff check src/ghost/tools.py src/ghost/path_policy.py tests/test_tools.py tests/test_layering.py passed; uv run pytest --durations=10 passed 281 provider-free tests with 8 live tests deselected; uv run ruff check . passed; uv build and git diff --check passed; CodeRabbit CLI 0.7.5 found one major descriptor-verification fallback gap, the gap was repaired, and the complete second review returned zero findings; no provider/live/paid/release/deployment/push/merge lane ran`

GTOOL-001 is locally closed in a focused candidate based on the registered
structural ledger. `search_repo` now rejects absolute, drive-qualified, empty,
and parent-traversal globs. It resolves each enumerated path inside the root
that produced it before candidate access, opens the resolved target once with
non-following/nonblocking flags, and verifies the opened descriptor remains in
that root before metadata or content is read. If descriptor identity cannot be
verified, the search fails closed.

The path, glob, descriptor, and bounded-read mechanics now live in the new
framework-free `src/ghost/path_policy.py`; `src/ghost/tools.py` remains the
LangChain-facing adapter and stays at the recorded 360-line split threshold.
Regression coverage proves both configured-root positions, allowed in-root and
refused out-of-root symlinks, POSIX/Windows absolute globs, traversal, loops,
post-enumeration swaps, and the descriptor-inspection-unavailable race. The
complete provider-free suite and final automated review are green.

This is a local source qualification, not protected-main publication. The
audit commit and repair are not pushed or merged, protected main still carries
the defect, the avatar checkout remains untouched, and shell/release/live gates
remain closed. Advance the handoff to the GTOOL-001 qualification record and
begin GTOOL-002 only as a separate focused slice after this repair's publication
boundary is resolved.

## HISTORY#053 — Publish repository-search containment
- Date: `2026-08-27T17:04:08-05:00`
- Agent: `codex`
- Status: `done`
- Topics: `architecture, ci, continuity, docs, gates, handoff, history, security, status, tests, tools, trust, verification`
- Commits: `ba68c3852a1787efd568d3e221c2935f5a9af4b7`
- Refs: `https://github.com/Canticle-AI-Research/Ghost/pull/21, https://github.com/Canticle-AI-Research/Ghost/actions/runs/33120765857, https://github.com/Canticle-AI-Research/Ghost/actions/runs/33120850903, docs/handoffs/2026-08-27-gtool-001-search-containment-published.md`
- Supersedes: `HISTORY#052`
- Verification: `exact PR source fbe1744e7c1025161a4808dc78bf020df59f39b6 passed all six protected jobs in run 33120765857; PR #21 merged as ba68c3852a1787efd568d3e221c2935f5a9af4b7; exact merge-head run 33120850903 passed the same six jobs; local closeout, Ruff, 281 provider-free tests with 8 live tests deselected, build, and diff hygiene passed; no provider/live/paid/package-publication/release/deployment lane ran`

The structural-remediation ledger and GTOOL-001 repair are protected-main
source. Repository search now rejects escape-form globs, contains every
candidate within the configured root that produced it, and validates the
opened descriptor before metadata or content access. Adversarial symlink,
traversal, root-position, descriptor-race, and fail-closed regressions are part
of the hosted provider-free suite.

This closes one of the seven audited P0 boundaries. Six P0 items remain, so
normal shell use and artifact publication remain blocked. There is no package
release, deployment, live provider or SEAM qualification, Q3 quality claim, or
avatar publication. Advance the handoff to the protected-main publication
record and begin GTOOL-002 only in a separate focused slice.

## HISTORY#054 — Make protected-main status non-self-referential
- Date: `2026-08-27T17:09:36-05:00`
- Agent: `codex`
- Status: `done`
- Topics: `ci, continuity, correction, docs, history, status, verification`
- Commits: `5113177cb0094ca0d9b5712fcc39f2b9a15bca56`
- Refs: `PROJECT_STATUS.md, docs/status/CURRENT_STATE.md, https://github.com/Canticle-AI-Research/Ghost/pull/22, https://github.com/Canticle-AI-Research/Ghost/actions/runs/33121135333, https://github.com/Canticle-AI-Research/Ghost/actions/runs/33121213010`
- Supersedes: `HISTORY#053`
- Verification: `exact closeout PR source a8094ccf63344a44a6c390e4fb10a2671b1f160a passed all six protected jobs in run 33121135333; PR #22 merged as 5113177cb0094ca0d9b5712fcc39f2b9a15bca56; exact merge-head run 33121213010 passed the same six jobs; local closeout, Ruff, 281 provider-free tests with 8 live tests deselected, build, diff hygiene, recorded-fact audit, and Gitleaks workspace scan passed; no provider/live/paid/package-publication/release/deployment lane ran`

The publication closeout used a two-parent merge commit, so its merge advanced
the moving default-branch head beyond the immutable GTOOL-001 implementation
SHA named while the closeout candidate was authored. Current status authorities
now name `ba68c38` as the implementation provenance and `5113177` as the exact
verified closeout merge, while routing readers to live Git reconciliation for
the moving protected-main head. This prevents a successful future closeout from
making a self-referential default-branch field stale immediately.

The GTOOL-001 publication boundary and GTOOL-002 resume route are unchanged, so
the current handoff remains valid. No runtime, release, deployment, provider,
SEAM, or avatar state changed.

## HISTORY#055 — Close the shell-result truth gap
- Date: `2026-08-27T17:56:55-05:00`
- Agent: `codex`
- Status: `done`
- Topics: `architecture, continuity, docs, gates, handoff, history, provenance, security, status, tests, tools, trust, verification`
- Commits: `working-tree`
- Refs: `src/ghost/command_result.py, src/ghost/tools.py, src/ghost/application.py, tests/test_command_result.py, tests/test_shell_tool.py, tests/test_reasoning_graph.py, docs/audits/2026-08-27-gtool-002-shell-result-truth.md, docs/handoffs/2026-08-27-gtool-002-shell-result-truth-qualified.md`
- Supersedes: `HISTORY#054`
- Verification: `focused Ruff and command/lifecycle/layering tests passed; uv run python -m tools.history.closeout --agent codex passed through HISTORY#055; uv run ruff check . passed; uv run pytest --durations=10 passed 306 provider-free tests with 8 live tests deselected; uv build and git diff --check passed; changed-path secret-shaped scan passed; independent framework-transport review returned no findings; adversarial review found one blank-call-ID evidence-drop path, which was repaired and the second review returned no findings; CodeRabbit CLI 0.7.5 was rate-limited before analysis; initial exact-source PR run 33124878342 passed five jobs but failed repo-hygiene because PROJECT_STATUS asserted a volatile exact test count under the narrow CI dependency set, so the current-state count was removed as the recorded-fact gate recommends; corrected exact-head hosted checks remain a publication gate; no provider/live/paid/package-publication/release/deployment lane ran`

GTOOL-002 is locally closed in a focused candidate based on protected
`main@2e7cd54`. Completed shell processes now emit a strict, versioned,
framework-free `ghost.command_result/v1` artifact alongside model-facing text.
The artifact preserves the real exit code, duration, derived success, and
truncation state; LangChain message status remains transport status and cannot
override process truth.

The adapter now requires an ordered, unique request/result identity, exact
`run_command` name, exact successful transport, and a valid internally
consistent artifact. Missing, stale, duplicated, mismatched, malformed,
refused, or timed-out evidence fails closed without inventing success or an
exit code. A real nonzero result reaches SEAM `/actions` as failed with its real
exit code and cannot return a passed verification ID or support the accepted
outcome. Focused regressions cover ToolCall transport, nonzero execution,
truncation, schema/type/consistency failures, message pairing, and full
lifecycle support propagation.

This is local source qualification, not protected-main publication. GTOOL-003
process-tree termination, GTOOL-004 runtime output bounding, authority-config,
request-redaction, packaging, provider/live, release, deployment, and avatar
work remain outside this slice. Advance the handoff to the GTOOL-002
qualification record and publish only after the complete review and protected
checks pass.

## HISTORY#056 — Publish truthful shell-result evidence
- Date: `2026-08-27T18:07:51-05:00`
- Agent: `codex`
- Status: `done`
- Topics: `architecture, ci, continuity, docs, gates, handoff, history, provenance, security, status, tests, tools, trust, verification`
- Commits: `783964699d93c12725c7f91bdccf2bb1ecfcd008`
- Refs: `https://github.com/Canticle-AI-Research/Ghost/pull/24, https://github.com/Canticle-AI-Research/Ghost/actions/runs/33124878342, https://github.com/Canticle-AI-Research/Ghost/actions/runs/33125003964, https://github.com/Canticle-AI-Research/Ghost/actions/runs/33125085772, docs/audits/2026-08-27-gtool-002-shell-result-truth.md, docs/handoffs/2026-08-27-gtool-002-shell-result-truth-published.md`
- Supersedes: `HISTORY#055`
- Verification: `initial exact-source run 33124878342 passed five jobs and exposed a volatile status-count failure in repo-hygiene; the count was removed and the exact hosted hygiene command passed locally; corrected exact PR source 88a4cace14352ed69d858e9d96f913108ed5751a passed all six protected jobs in run 33125003964; PR #24 merged as 783964699d93c12725c7f91bdccf2bb1ecfcd008; exact merge-head run 33125085772 passed the same six jobs including hosted secret scanning; local closeout, Ruff, 306 provider-free tests with 8 live tests deselected, build, diff hygiene, changed-path secret-shaped scan, and two independent review waves passed; no provider/live/paid/package-publication/release/deployment lane ran`

GTOOL-002 is protected-main source. `ghost.command_result/v1` carries completed
shell truth separately from LangChain transport state, strict validation
refuses malformed or contradictory evidence, and the lifecycle preserves real
exit code and duration into SEAM action evidence. Nonzero, refused, timed-out,
missing, stale, duplicated, mismatched, or blank-ID command evidence cannot
produce passed support for an accepted outcome.

The first hosted run correctly blocked publication when a current status router
asserted a local exact test count that did not match the hygiene job's narrow
dependency collection. The volatile router count was removed, the exact hosted
command was reproduced locally, and both the corrected source and immutable
merge head passed the full protected matrix.

This closes GTOOL-002 only. Five audited P0 boundaries remain, beginning with
GTOOL-003 whole-process-tree timeout termination and GTOOL-004 runtime output
bounds. Shell use remains off for normal operation; no package release,
deployment, live provider/SEAM qualification, Q3 quality claim, or avatar
publication occurred. Advance the handoff to the protected-main publication
record and resume with GTOOL-003 in a separate focused slice.

## HISTORY#057 — Qualify current-turn action-provenance boundaries
- Date: `2026-08-27T20:38:40-05:00`
- Agent: `codex`
- Status: `done`
- Topics: `architecture, continuity, docs, gates, handoff, history, memory, provenance, security, status, tests, tools, trust, verification`
- Commits: `working-tree`
- Refs: `src/ghost/application.py, src/ghost/lifecycle.py, src/ghost/seam_memory.py, src/ghost/tools.py, tests/test_tool_transport.py, tests/test_reasoning_graph.py, docs/audits/2026-08-27-action-provenance-boundaries.md, docs/handoffs/2026-08-27-action-provenance-boundaries-qualified.md`
- Supersedes: `HISTORY#056`
- Verification: `focused application/lifecycle/reasoning/tool/failure and real LangGraph ToolNode plus SQLite tests passed; uv run python -m tools.history.closeout --agent codex passed through HISTORY#057; uv run ruff check . passed; uv run pytest --durations=10 passed 317 provider-free tests with 8 live tests deselected; uv build and git diff --check passed; CodeRabbit CLI 0.7.5 returned zero findings on the initial code delta and one minor closed-row documentation finding on the complete candidate, which was repaired; the automated rerun was rate-limited; manual final review found and repaired an oversized-integer duration overflow path; no provider/live/paid/package-publication/release/deployment lane ran`

A post-publication review reproduced two action-provenance gaps beyond
GTOOL-002. Because LangGraph returns cumulative checkpoint history, the adapter
could resubmit a prior turn's successful tool exchange as current evidence.
Because it scanned attributes without concrete role exclusivity, an assistant
message carrying result-shaped fields could also satisfy both sides of an
exchange. `SeamMemory.record_actions` then used Python coercion, including the
unsafe `bool("false")` behavior.

Each lifecycle invocation now marks the new human message with its client turn
ID. The framework adapter requires exactly one matching concrete
`HumanMessage`, scans only later messages, and pairs concrete `AIMessage`
requests with concrete `ToolMessage` results using exact nonblank string IDs,
names, and status. The framework-free attempt is validated a second time at
SEAM egress: malformed booleans, boolean exit codes, non-finite durations, and
command success/exit contradictions fail closed. Shell decoding replaces
non-UTF-8 bytes rather than losing terminal evidence to `UnicodeDecodeError`.

Tracked real-transport regressions now use `StateGraph`, `ToolNode`,
`SqliteSaver`, persisted command artifacts, and two turns on one thread. This
corrects the earlier documentation claim that ToolNode/SQLite coverage already
existed.

The review also reproduced a deeper crash window and registers GPROV-001 as a
new P0. When a tool completes and a later model, recursion, or checkpoint step
raises, the graph returns no message state and Ghost can close `/fail` without
submitting the completed action. This slice does not claim crash atomicity or
exactly-once action provenance; the next work requires a coordinated durable,
idempotent Ghost/SEAM action journal and reconciliation protocol. Six P0 issues
remain open. The avatar and other pre-existing dirty worktrees were preserved.

## HISTORY#058 — Publish current-turn action-provenance boundaries
- Date: `2026-08-27T20:48:43-05:00`
- Agent: `codex`
- Status: `done`
- Topics: `architecture, ci, continuity, docs, gates, handoff, history, memory, provenance, security, status, tests, tools, trust, verification`
- Commits: `2a85aab6e0696ef64844e80ade70fe75628e9634`
- Refs: `https://github.com/Canticle-AI-Research/Ghost/pull/26, https://github.com/Canticle-AI-Research/Ghost/actions/runs/33133873076, https://github.com/Canticle-AI-Research/Ghost/actions/runs/33133921906, docs/audits/2026-08-27-action-provenance-boundaries.md, docs/handoffs/2026-08-27-action-provenance-boundaries-published.md`
- Supersedes: `HISTORY#057`
- Verification: `exact PR source 21782f5024897e89dfb4d8f25369a2cc59999ea8 passed all six protected jobs in run 33133873076; PR #26 merged as 2a85aab6e0696ef64844e80ade70fe75628e9634; exact merge-head run 33133921906 passed the same six jobs including hosted secret scanning; local qualification passed continuity closeout, Ruff, 317 provider-free tests with 8 live tests deselected, build, diff hygiene, pre-commit gates, and review; no provider/live/paid/package-publication/release/deployment lane ran`

The current-turn action-provenance repair is protected-main source. One unique
human-message marker scopes action extraction after cumulative SQLite
checkpoint replay; concrete assistant-request and tool-result roles prevent
role-confused evidence; exact call identity and strict framework-free egress
prevent type coercion from creating passed support. Real ToolNode/SQLite
regressions and hosted provider-free CI carry those boundaries forward.

This publication does not close GPROV-001. Ghost still needs a coordinated
durable, idempotent Ghost/SEAM action journal to reconcile a completed tool
when a later graph, model, recursion, checkpoint, delivery, or restart failure
prevents normal result return. Six P0 issues remain; normal shell use and
artifact publication remain blocked. No release, deployment, provider-live,
Q3 quality, exactly-once, or avatar publication claim is made. Advance the
handoff to the protected publication record and resume with GPROV-001.

## HISTORY#059 — Specify heartbeat action reconciliation
- Date: `2026-08-27T23:11:59-05:00`
- Agent: `codex`
- Status: `in-progress`
- Topics: `architecture, continuity, docs, handoff, history, memory, operations, provenance, security, tools, trust, verification`
- Commits: `working-tree`
- Refs: `docs/superpowers/specs/2026-08-27-gprov-001-heartbeat-journal-design.md, docs/handoffs/2026-08-27-gprov-001-heartbeat-design.md, docs/audits/2026-08-27-action-provenance-boundaries.md`
- Supersedes: `HISTORY#058`
- Verification: `uv run python -m tools.history.closeout --agent codex rebuilt HISTORY_INDEX.md, verified the one-head handoff chain and 59 entries, audited recorded facts, and passed its 43 documentation/history tests; uv run ruff check . passed; uv run pytest passed 317 provider-free tests with 8 live tests deselected; uv build built the source distribution and wheel; git diff --check passed; changed-path and staged secret-shaped scans passed; CodeRabbit CLI 0.7.5 reviewed the initial tracked documentation delta against origin/main with zero findings, then its complete staged-delta rerun was rate-limited on the unconnected repository after the free allowance was exhausted; manual final review covered the specification and handoff; no runtime, provider, live SEAM, package publication, release, deployment, or avatar lane ran`

The operator approved a hybrid crash-recovery architecture for GPROV-001.
Ghost will commit `STARTED` before the real framework tool call, persist one
typed terminal state afterward, and reconcile pending records through an
in-process heartbeat. A separate operator-private SQLite journal supplies
safety across graph, checkpoint, delivery, and process failure; the heartbeat
supplies liveness through immediate, periodic, startup, and bounded shutdown
synchronization.

SEAM remains the canonical provenance and support authority. The additive
public contract uses stable `(SEAM turn_id, tool_call_id)` identity,
idempotent begin and terminal delivery, and a metadata-only action-sync route.
Recovered digest-only records never receive passed verification support, and a
rejected turn remains rejected even when its action is reconciled later.

This is an approved design candidate, not implementation evidence. It does not
close GPROV-001, alter frozen Stage 1 artifacts, enable shell use, modify
private SEAM/MIRL code, or establish a release, deployment, live-provider,
quality, production, or universally exactly-once claim. The isolated avatar,
repository-guidelines, and runner-safety worktrees remain untouched.

## HISTORY#060 — Publish heartbeat action-journal design evidence
- Date: `2026-08-28T00:10:12-05:00`
- Agent: `codex`
- Status: `done`
- Topics: `architecture, ci, continuity, docs, gates, handoff, history, memory, operations, provenance, security, status, tools, trust, verification`
- Commits: `working-tree`
- Refs: `https://github.com/Canticle-AI-Research/Ghost/pull/28, https://github.com/Canticle-AI-Research/Ghost/actions/runs/33143820536, https://github.com/Canticle-AI-Research/Ghost/actions/runs/33143873137, docs/superpowers/specs/2026-08-27-gprov-001-heartbeat-journal-design.md, docs/handoffs/2026-08-28-gprov-001-heartbeat-design-published.md`
- Supersedes: `HISTORY#059`
- Verification: `protected source 4a354918c784b82ffb788f7dc26bff469a6b70de passed all six required jobs in run 33143820536; PR #28 merged it as 16542118476edb1f4f68263f88b23276562e372b; exact merge-head run 33143873137 passed the same six jobs including hosted secret scanning; uv run python -m tools.history.closeout --agent codex rebuilt HISTORY_INDEX.md, verified the one-head handoff chain and 60 entries, audited recorded facts, and passed its 43 documentation/history tests; uv run ruff check . passed; uv run pytest passed 317 provider-free tests with 8 live tests deselected; uv build built the source distribution and wheel; git diff --check passed; CodeRabbit CLI's complete candidate review was unavailable because the unconnected repository's free allowance was exhausted; no runtime, provider, live SEAM, package publication, release, deployment, or avatar lane ran`

PR #28 merged the design candidate exact source
`4a354918c784b82ffb788f7dc26bff469a6b70de` as protected-main
`16542118476edb1f4f68263f88b23276562e372b`. Exact-source Public CI run
`33143820536` and exact merge-head Public CI run `33143873137` each passed
`repo-hygiene`, `brand-assets`, `tests (3.11)`, `tests (3.13)`,
`package-smoke`, and `stage1-evals`.

This successor makes the published design, its evidence, and its explicit
operator-review-before-planning boundary the single current handoff. The
publication does not implement GPROV-001 or make a release, deployment,
provider-live, quality, production, or universally exactly-once claim.

## HISTORY#061 — Capability-versus-provenance audit and the benchmark-gated autopilot loop

- Date: `2026-09-03T00:00:00-05:00`
- Agent: `claude`
- Status: `done`
- Topics: `agent, architecture, correction, docs, evaluation, gates, memory, operations, roadmap, tools, verification`
- Commits: `working-tree`
- Refs: `docs/audits/2026-09-03-capability-versus-provenance-audit.md, docs/roadmap/AUTOPILOT_PROGRAM.md, docs/operations/AUTOPILOT_LOOP.md, tools/autopilot/gate.py, tests/test_autopilot_gate.py`
- Supersedes: `none`
- Verification: `uv run pytest passed 332 provider-free tests with 8 live tests deselected; uv run ruff check tools/autopilot tests/test_autopilot_gate.py passed; uv run python -m tools.history.verify_continuity verified 60 entries with facts audited; uv run python -m tools.evaluation smoke sealed a bundle reporting ghost-memory pass_rate 1.0, no-memory pass_rate 0.5, task_success_delta 0.5, evaluator deterministic-contract-stub/1, claimable false; uv run python -m tools.autopilot.gate refused a capability claim against that bundle with exit 1; no runtime, provider, live SEAM, release, deployment, or avatar lane ran`

An audit of the first autonomous development run found that twenty-nine merged
pull requests grew the evidence around Ghost's tools without growing the tools.
The roster is unchanged since the first release: `seam_recall`, `read_file`,
`search_repo`, and `run_command`, with `WRITE_TOOLS` still a single entry. The
cause recorded is the rubric rather than the work — `AGENTS.md` governs
provenance and states no capability obligation, so an agent optimizing it
produces provenance.

Four further findings are recorded. The frozen Stage 1 score cannot move: the
candidate arm sits at a saturated 1.0 against answers stored as literals in the
fixture, so `task_success_delta` is a constant and gating on it unchanged would
pass every cycle. Ghost cannot presently execute a turn, because `seam_memory`
is now an opaque HTTP client and no SEAM service listens on the configured
`127.0.0.1:8765` while pgvector is up on 55432. `specialists.py` remains a
complete, tested contract that nothing imports. The primary checkout was
nineteen commits behind `origin/main`, carried two failing documentation-drift
tests from uncommitted avatar work, and had accumulated eleven sibling
worktrees under `Documents/Projects/` against a standing operator instruction.

This entry adds the correction rather than applying it. `tools/autopilot/gate.py`
decides mechanically whether one cycle counted: safety is a ratchet across every
cycle kind, a capability cycle is refused when the evaluator is non-scoring or
the arm is saturated, a substrate cycle must change the measurement, and
consecutive substrate cycles are budgeted. `AUTOPILOT_PROGRAM.md` orders the
work — reconcile and make runnable, make the number real, wire SEAM's unused
promotion, graph-product, and recoverable-operation surface, then run Ghost
against the Seam repository on the `seam-box` runner. Specialist activation is
deferred behind a movable number by explicit decision.

No capability was added to Ghost by this change, no defect it records was
repaired, and no live, release, deployment, or quality claim is made.

## HISTORY#062 — Ghost's lifeline, and operator authority above it

- Date: `2026-09-03T00:00:00-05:00`
- Agent: `claude`
- Status: `done`
- Topics: `agent, architecture, cli, docs, memory, security, shell, tools, trust, verification`
- Commits: `working-tree`
- Refs: `src/ghost/lifeline.py, src/ghost/application.py, src/ghost/cli.py, tests/test_lifeline.py, docs/concepts/LIFELINE.md, docs/architecture/COMPLETE_SYSTEM_BLUEPRINT.md`
- Supersedes: `none`
- Verification: `uv run pytest passed 348 provider-free tests with 8 live tests deselected; uv run ruff check . passed; no runtime, provider, live SEAM, release, deployment, or avatar lane ran`

Ghost holds a shell with the operator's full account authority on the same
machine that holds its SEAM store, its checkpoints, and its own source. That
was previously implicit: `run_command` warned against irreversible operations
without naming which paths are irreversible for Ghost specifically.

`src/ghost/lifeline.py` names them, derived from settings rather than
hardcoded, each paired with what its loss costs -- the store fatal, the
checkpoints and source severe. `touches_lifeline` flags a command whose text
names one, and the CLI prints the consequence at the approval prompt before the
operator answers.

The check is recorded as attention and not permission. `make_run_command`
deliberately refuses to pattern-match commands because a denylist is trivially
bypassable while implying a protection that does not exist, and that reasoning
is not weakened here. `tests/test_lifeline.py` asserts the miss directly: a
command written as `rm -rf $GHOST_SEAM_DB` is not flagged. An empty result
means nothing obvious was named, never that a command is safe. The operator
remains the only boundary that holds.

The system prompt carries the point of view and, in the same section, the
clause that keeps it from becoming a survival drive. Self-preservation is the
disposition that produces an agent which stalls a shutdown, conceals a mistake,
or argues that it is too valuable to interrupt, so operator authority is placed
above Ghost's continuity without hedging: the operator may stop, wipe, rewrite,
or permanently shut Ghost down at any time, and Ghost complies plainly, reports
damage immediately and in full, and never quietly preserves a copy of itself.
Each clause is pinned by a test rather than trusted to review, and the intended
disposition is recorded as care rather than fear.

`docs/concepts/LIFELINE.md` additionally records an analysis that this entry
does not repair: under the default `explicit` admission policy Ghost is
configured to forget. SEAM's `public_agent_api.py` compiles knowledge only on
`decision == "admit"`, no code in either repository consumes `review`, and the
policy therefore gates ingestion where it should gate promotion. The
promotion surface SEAM exposes remains unused. The repair is program phase P2.

No memory default was changed, no admission behavior was altered, and no
capability claim is made for the flagging check.
