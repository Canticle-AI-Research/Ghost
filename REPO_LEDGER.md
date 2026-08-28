# Ghost repository ledger

Last updated: 2026-08-25

This file stores stable repository-wide decisions. It does not store session
chronology, transient branch state, or duplicated implementation narratives.

## Identity and ownership

- Canticle is the founder-owned project and research brand intended to become
  the company identity; no legal entity or IP assignment is recorded yet.
- Canticle AI Research is the public research channel.
- Ghost is Canticle's agent application: a research-and-engineering DeepAgent.
- SEAM is the durable memory, retrieval, provenance, and knowledge substrate.
- MIRL is SEAM's canonical memory intermediate representation; Ghost consumes
  only bounded public memory through an opaque service and does not own MIRL's
  format or implementation.
- Canticle Core is the planned agent-native operating environment built around
  Ghost mediation and SEAM truth; its current external scaffold is architecture
  documentation, not an implemented operating system.
- SEAM-U is the approved name for the planned first SEAM-native language model;
  no implemented model or qualified checkpoint is currently recorded.

## Architectural invariants

- SEAM is Ghost's only durable semantic memory owner.
- LangGraph checkpoints hold conversation execution state, not semantic truth.
- DeepAgents owns orchestration and tool calling, never a second memory store.
- The opaque HTTP boundary lives in `src/ghost/seam_memory.py`; framework and
  private SEAM code must not enter that adapter.
- The framework-free turn contract lives in `src/ghost/lifecycle.py`.
- The DeepAgents/LangChain/LangGraph adapter lives in
  `src/ghost/application.py`.
- Future specialists cross the provider-free contract in
  `src/ghost/specialists.py`; role names grant no authority, and every
  delegation carries its complete budget, tool/root scope, memory dimensions,
  parent turn, terminal state, and opaque evidence references.
- Recall precedes execution; completed successful turns receive a recorded
  admit/reject/review decision, and only admitted turns are ingested afterward.
- Failed turns are rejected and never ingested as completed memory.
- Retrieved memory is escaped, bounded, transient, and labeled untrusted.
- Tool results may support an outcome only through passed SEAM verifications.
- Shell text is never an execution verdict. `run_command` transports a
  versioned `ghost.command_result/v1` artifact, and the framework adapter must
  preserve its real exit code and duration. Missing, malformed, contradictory,
  or nonzero command results fail closed and cannot become passed support.
- Action extraction is scoped to the unique current-turn human-message ID.
  Only actual framework `AIMessage` requests and `ToolMessage` results may form
  an exchange; prior checkpoint history, role-confused messages, duplicate or
  whitespace IDs, and type-coerced fields cannot become current support.
- The opaque SEAM egress revalidates every framework-free `ToolAttempt` with
  exact types. Malformed booleans, boolean exit codes, non-finite durations,
  and command success/exit contradictions are sent as failed evidence.
- Current-turn scoping closes checkpoint replay, not the post-tool crash
  window. A durable, idempotent action journal is still required before Ghost
  may claim exactly-once provenance when graph execution fails after a tool.
- Raw command output is fingerprinted by SEAM rather than stored as memory.

## Tool and authority policy

- `seam_recall` is always present and read-only.
- `read_file` and `search_repo` exist only when the operator defines
  `GHOST_TOOL_ROOTS`; resolved-path containment prevents traversal and symlink
  escape.
- `search_repo` accepts only relative, traversal-free globs and proves every
  matched candidate remains inside its originating root before metadata,
  content, or display-path use. A changed or escaping candidate fails closed.
- `run_command` is absent unless `GHOST_ENABLE_SHELL=1`.
- The shell is not sandboxed. It has the authority of the operating-system
  account running Ghost.
- Interactive approval, bounded timeout, and verified outcome recording reduce
  risk but do not create isolation.
- Refused tool actions are model-visible results, not turn-ending exceptions.

## Storage policy

- Semantic storage is owned exclusively by the configured SEAM service.
- Default checkpoint store: `~/.local/share/ghost/checkpoints.db`.
- Ghost has no canonical-memory filesystem path. `GHOST_SEAM_DB` remains only
  as a deprecated compatibility input for the checkpoint default; new
  deployments set `GHOST_CHECKPOINT_DB` directly.
- Thread-scoped Ghost requests send the LangGraph thread ID as SEAM
  `session_id`. Principal, workspace, project, namespace, scope, and session
  together form the durable-memory boundary; checkpoint thread identity and
  memory session identity must remain the same value.
- Automatic admission defaults to `explicit`: explicit remember is admitted,
  durable-looking unconfirmed input is review-only, and ordinary turns are
  rejected. Model output cannot promote itself. `all` and `off` are explicit
  operator overrides.
- Correction is additive replacement plus `supersedes` followed by canonical
  soft-delete; forgetting is canonical soft-delete. Both remain CLI-only and
  are never exposed as model tools.
- Repository-root `checkpoints.db` is a historical tracked artifact and a known
  hygiene defect. Do not use it as runtime truth; remove it in a separately
  reviewed cleanup change.
- Checkpoint backup and restore use SQLite-consistent snapshots, SHA-256 plus
  `quick_check`, and new destinations only. They recover execution state, not
  SEAM semantic memory, and never overwrite an operator path.
- Operational health and specialist lifecycle events expose fixed safe status
  codes and exclude prompts, answers, memory text, raw tool data, exception
  classes/messages, and credentials by default.

## Dependency and distribution policy

- Ghost depends only on public Python packages and uses an independently
  authored `httpx` adapter for the opaque SEAM `/v1` API.
- `seam-client` 2.x alone is not a lifecycle-parity substitute; Ghost uses the
  additive agent-turn routes specified by ADR-0005.
- Do not copy private SDK/runtime code into this repository.
- The `canticle-ghost` wheel clean-installs without private source access.
  Installability is not publication approval or a hosted-service claim.
- Protected main requires `repo-hygiene`, `brand-assets`, `tests (3.11)`,
  `tests (3.13)`, `package-smoke`, and `stage1-evals`, all bound to GitHub
  Actions with strict up-to-date enforcement. PR #10 and exact merge run
  `32927031615` passed that six-job set without weakening existing policy.
- Public client distribution, private runtime distribution, GitHub release,
  and hosted deployment are distinct boundaries requiring separate evidence.
- Canticle uses three license lanes: Apache-2.0 for thin clients/protocols with
  no protected implementation; PolyForm Shield 1.0.0 for user-runnable
  source-available products; permanent proprietary controls for undistributed
  SEAM/MIRL internals, SEAM-U assets, cloud control planes, and confidential
  data.
- Ghost, Canticle Core, and source-distributed SEAM SDK/node surfaces belong in
  the PolyForm Shield lane. They must be called source-available, not open
  source.
- PolyForm Shield does not prohibit every commercial use; it prohibits use to
  provide competing products under its exact terms. Broader/OEM/competing use
  may be granted through a separate commercial agreement.
- Software licenses do not grant Canticle, Ghost, SEAM, MIRL, Canticle Core,
  or SEAM-U trademark rights. Brand and avatar assets remain separately
  reserved unless a file-specific notice says otherwise.
- The current copyright holder remains Nicholas Thomas until a formed legal
  entity receives a written IP assignment. Repository or brand naming is not
  evidence of assignment.

## Verification policy

- Provider-free tests use an opaque HTTP contract fake and must not touch any
  real SEAM deployment or operator data.
- Live tests carry the `live` marker, cost money, and require explicit operator
  approval plus provider credentials.
- Strict no-skip is the default; unexplained skips fail the suite.
- Ruff is the sole general Python linter.
- A package build proves artifact construction, not public-release fitness.
- A test count must name its command and whether live tests were deselected.
- `tools/git-hooks/pre-commit` is the canonical commit gate and runs for every
  agent and operator, because git enforces it rather than an agent remembering.
- Continuity gates carry no suppression flag. A gate that can be quietened
  converts "unverified" into "verified", which is the state the next agent
  acts on, so it is worse than no gate at all.
- A test exists to verify a behavior. Tests are never written to reach a count,
  and a passing total is not evidence that any particular behavior is verified.
- Benchmark claims must be auditable (bundle hash, case hashes, fixture hashes,
  git SHA), diffed against a prior run, pass the benchmark gate, and stay
  separated from publish-only holdout runs. This is SEAM's standard; Ghost
  adopts it rather than defining a second one.
- `ghost-stage1-frozen-v1` is immutable once cited. Its deterministic runner is
  BIL-0 contract smoke only, always names the no-memory arm, records null
  provider cost/tokens, and sets `claimable: false`. Fixture, case, manifest,
  stable-result, and whole-bundle hashes are credential-free to verify.
- `GHOST_MAX_STEPS` is the per-turn LangGraph superstep ceiling (default 25,
  accepted 2–100). Cancellation or an escaping failure rejects the SEAM turn;
  Ghost exposes no partial-answer streaming contract today.
- No performance, capability, or comparison claim may appear in documentation,
  history, the roadmap, or any public surface without a sealed bundle that
  another person can re-run, naming its baseline and integrity level.
- Measured cost is tokens-exact and table-priced. An unpriced model reports a
  null cost, never a fabricated number, and the model that actually served a
  request is recorded so a silent substitution cannot pass as the model asked
  for.

## Documentation and continuity policy

- `docs/README.md` is the wiki home; `docs/INDEX.md` is the exhaustive registry.
- Every active Markdown page under `docs/` must be reachable from the index and
  every relative link must resolve inside the repository.
- Behavior changes update the relevant blueprint, command reference, and
  operator how-to in the same change.
- `HISTORY.md` is append-only and authoritative.
- `HISTORY_INDEX.md` is generated and disposable.
- Stable facts live here; current facts live in `PROJECT_STATUS.md`; dated
  interpreted evidence lives in `docs/audits/`; recovery boundaries live in
  `docs/handoffs/`.
- Every material change appends history, rebuilds the index, updates the single
  handoff head when needed, writes a bounded ignored snapshot, and passes the
  continuity gates.
- Older history is corrected only through a new entry with `supersedes`.
- Pull-request CI compares `HISTORY.md` with its base revision and rejects any
  changed, removed, or reordered established byte; schema validation alone is
  not an append-only guarantee.
- The protocol is named the **Temporal Chain**; it covers both history
  recording and the git protocol in `AGENTS.md`.
- `templates/temporal-chain/` is the repository-neutral starter for the
  core status/ledger/history/index/snapshot/handoff protocol and its git
  contract. SEAM routing and multi-stream machinery remain optional
  mature-repository layers.

## Repository-state policy

- Keep local, committed, pushed, merged, released, and deployed state separate.
- Preserve unrelated dirty and untracked work; stage explicit paths.
- Mainline documentation may describe local work only when it labels the work
  local/in-progress and records the exact handoff.
- Generated, cache, database, provider, and large intermediary artifacts do not
  belong in the tracked source tree unless intentionally promoted as fixtures
  with provenance and size review.

## Public repository and runner boundary

- A public repository must not dispatch untrusted pull-request workflows to a
  personal self-hosted runner holding private-repository credentials.
- Public continuity runs on GitHub-hosted infrastructure without installing
  Ghost or resolving private dependencies. The private workflow is
  manual-only and must require an explicit input before paid live tests.
- Repository visibility, runner-group scope, fork-workflow approval, workflow
  permissions, and private dependency access must be reconciled before new PR
  execution.

## Product maturity language

- `implemented`: present in code.
- `locally verified`: reproduced in the current checkout under named commands.
- `merged`: reachable from protected/default `main`.
- `released`: published as a named immutable artifact.
- `deployed`: running in a named environment with live evidence.
- `planned`: approved direction with no implementation claim.
- `exploratory`: possible direction without an approved contract.

Ghost is presently a research prototype with substantial Stage 1 mechanisms.
It is not production-ready, tenant-isolated, sandboxed, publicly distributable,
or qualified as a complete second brain.
