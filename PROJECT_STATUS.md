# Ghost project status

> This file is a current-state router, not an archive. Chronology lives in
> `HISTORY.md`; stable decisions live in `REPO_LEDGER.md`; detailed current
> evidence lives in `docs/status/CURRENT_STATE.md`.

## Current headline

**2026-08-25 — `main@66841fc` publishes Ghost's public-only install boundary
and opaque SEAM lifecycle through PR #8, alongside the verified memory-backed
single-agent spine, hardened CI, canonical engineering wiki/build history,
Temporal Chain, licensing foundation, and multi-harness launchers. Exact merge
head run `32924125667` passed all five hosted jobs. The isolated desktop avatar
remains separate WIP. No package or service is released or deployed, and
nothing is assigned to a company or counsel-approved.**

PRs #6, #7, and #8 and their exact merge-head Public CI are green. SEAM PR #231
is protected-main server source; Ghost PR #8 is protected-main client source.
This proves public installability and contract parity, not a compatible hosted
endpoint, package release, or deployment. See `docs/status/CURRENT_STATE.md`,
HISTORY#022, HISTORY#038, and the current handoff.

Live GitHub reconciliation on 2026-08-25 established:

- repository visibility is public;
- PR #5 merged the hosted automatic/manual-private workflow boundary;
- PR #6 merged the canonical wiki/history/licensing/launcher foundation;
- PR #7 merged the canonical follow-up through `main@10a2b45`;
- exact `main@66841fc` passed all five hosted required checks;
- all external-contributor workflows require approval;
- secret scanning and push protection are enabled;
- Ghost has no repository secret and no assigned runner; and
- protected `main` requires PRs and the five strict hosted checks, enforces
  administrators and conversation resolution, and blocks force pushes/deletes.

Organization runner-group inventory was unavailable without organization-admin
authority. The zero-assigned-runner state remains fail-closed. The candidate
moves the full provider-free suite to hosted CI; only paid live provider/service
validation stays manual.

## Product boundary

Ghost is Canticle's research-and-engineering DeepAgent. Ghost owns cognition,
mission, orchestration, tools, and operator-facing surfaces. SEAM owns durable
RAW/MIRL memory, retrieval, provenance, and reasoning records. LangGraph
checkpoints store execution state only.

The merged Ghost distribution architecture uses Apache-2.0 for thin clients
and protocols, PolyForm Shield 1.0.0 for user-runnable source-available product
software, and permanent proprietary protection for undistributed SEAM/MIRL
internals, planned SEAM-U assets, and hosted control planes. Ghost's opaque HTTP
path is locally qualified; protected merge, release, and deployment remain
incomplete.

## Roadmap position

- Temporal Chain (Track T): core, handoff, drift-gate, and reusable-template
  layers are merged; SEAM streams/routing and artifact release remain open.
- Engineering quality (Track Q): tests exist to verify behavior, not to reach a
  count; many behaviors remain unverified. 450-line module ceiling enforced.
  Ghost has no benchmark infrastructure yet; Q3 adopts SEAM's sealed-bundle
  proof standard, and no performance claim is admissible until it exists.
- Stage 0 memory spine: landed.
- Stage 1 dependable single agent: most mechanisms landed; exit evaluation and
  bounded-product qualification remain incomplete.
- Stage 2 deliberate memory: not implemented.
- Stage 3 graph-aware specialists: not implemented.
- Stage 4 measured product: exploratory.
- Desktop avatar: local/in-progress parallel UX track, not a roadmap gate.
- Multi-harness launchers: Ghost starts from `claude`, `codex`, `grok`, and
  `agy`; the shared charter is still untracked outside the repository.

## Active order

1. Obtain counsel review and execute founder-to-company IP assignment after
   the legal entity is formed.
2. Complete Stage 1 frozen task/memory evaluations.
3. Implement deliberate memory admission, correction, forgetting, and
   isolation only after the Stage 1 baseline is frozen.
4. Resume the isolated desktop-avatar workstream after its asset and
   consequential-action boundaries are approved.

## Resume route

Read `docs/handoffs/INDEX.md`, then its `latest` document. Use
`HISTORY_INDEX.md` or a bounded context pack instead of loading all history.
