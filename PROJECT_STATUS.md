# Ghost project status

> This file is a current-state router, not an archive. Chronology lives in
> `HISTORY.md`; stable decisions live in `REPO_LEDGER.md`; detailed current
> evidence lives in `docs/status/CURRENT_STATE.md`.

## Current headline

**2026-08-27 — protected `main@cccf99a` publishes the bounded specialist and
operations foundation plus its canonical PR #15 closeout. Exact-head Public CI
run `32935194091` passed all six required provider-free jobs.** No package or
service is released or deployed, and the BIL-0 evaluation remains explicitly
non-claimable.

A local isolated audit commit `0cd12e3` adds the registered
`docs/audits/2026-08-27-structural-remediation-ledger.md`. It records seven P0
tool/config/artifact defects, immediate resource and security work, the Q3
benchmark program, later product gates, and a dependency-ordered course of
action. The report itself is not pushed or merged. The dirty avatar checkout
remains untouched on its older branch.

The local `fix/gtool-001-search-containment` candidate is based on that audit
commit and closes GTOOL-001 in source: search globs must be relative and
traversal-free, every candidate resolves inside its originating root, and the
opened descriptor is checked before metadata or content is read. This repair
is locally qualified but not pushed or merged, so protected main must still be
treated as vulnerable to the recorded search-root escape.

Current GitHub reconciliation established:

- repository visibility is public and `main@cccf99a` is the default branch;
- PRs #1, #5 through #15 are merged; Dependabot PRs #2, #4, and #16 through
  #20 are open;
- protected `main` requires the six strict hosted checks, enforces
  administrators and conversation resolution, and blocks force pushes/deletes;
- secret scanning and push protection are enabled with no open secret alert;
- Dependabot security updates are disabled and no code-scanning analysis is
  registered;
- Ghost has no repository secret and no assigned runner; and
- paid live provider/service validation remains manual and was not run.

The provider-free current repair tree passes Ruff, 281 tests with eight live
tests deselected, build, and the Stage 1 BIL-0 validate/smoke/verify/gate path.
That green baseline does not negate the reproduced defects or qualify a
release, live provider, hosted service, G1/G2 exit, or production claim.

## Product boundary

Ghost is Canticle's research-and-engineering DeepAgent. Ghost owns cognition,
mission, orchestration, tools, and operator-facing surfaces. SEAM owns durable
RAW/MIRL memory, retrieval, provenance, and reasoning records. LangGraph
checkpoints store execution state only.

The merged Ghost distribution architecture uses Apache-2.0 for thin clients
and protocols, PolyForm Shield 1.0.0 for user-runnable source-available product
software, and permanent proprietary protection for undistributed SEAM/MIRL
internals, planned SEAM-U assets, and hosted control planes. Ghost's opaque HTTP
path and Stage 1 evaluation substrate are merged; compatible hosted-service
qualification, release, and deployment remain incomplete.

## Roadmap position

- Temporal Chain (Track T): core, handoff, drift-gate, and reusable-template
  layers are merged; SEAM streams/routing and artifact release remain open.
- Engineering quality (Track Q): tests exist to verify behavior, not to reach a
  count; many behaviors remain unverified. 450-line module ceiling enforced.
  Ghost's first BIL-0 sealed contract-smoke infrastructure is merged with a
  tracked clean-source baseline and protected CI gate; no performance claim is
  admissible from the deterministic stub.
- Stage 0 memory spine: landed.
- Stage 1 dependable single agent: 20-case frozen corpus, smoke verifier/gate,
  and step ceiling are merged; provider-live and release-candidate exit proof
  remain incomplete.
- Stage 2 deliberate memory: mechanisms are protected-main; a sealed Q3
  quality comparison remains incomplete.
- Stage 3 graph-aware specialists: provider-free contract published; no
  model-backed topology or improvement evidence.
- Stage 4 measured product: exploratory recovery/health foundation published;
  no hosted product or deployment.
- Desktop avatar: local/in-progress parallel UX track, not a roadmap gate.
- Multi-harness launchers: Ghost starts from `claude`, `codex`, `grok`, and
  `agy`; the shared charter is still untracked outside the repository.

## Active order

1. Publish the locally qualified P0 search-containment repair, then repair
   shell truth/process/output, authority-config, and sdist boundaries one issue
   at a time.
2. Repair resource ownership, checkpoint permissions/defaults, transport
   bounds, and controlled CLI failures.
3. Reconcile roadmap/blueprint truth and extend recorded-fact gates to catch
   the drift identified by the structural ledger.
4. Build the provider-free Q3 Stage 2 comparison and stop before paid execution
   for explicit model/cost approval.
5. Process dependency PRs against the new regressions, then complete legal and
   release-candidate gates.
6. Resume the isolated avatar only through its separate reviewed workstream.

## Resume route

Read `docs/handoffs/INDEX.md`, then its `latest` document and the registered
structural remediation ledger. Use `HISTORY_INDEX.md` or a bounded context pack
instead of loading all history.
