# Ghost project status

> This file is a current-state router, not an archive. Chronology lives in
> `HISTORY.md`; stable decisions live in `REPO_LEDGER.md`; detailed current
> evidence lives in `docs/status/CURRENT_STATE.md`.

## Current headline

**2026-08-25 — `main@10a2b45` contains the verified memory-backed single-agent
spine, public/private CI safety boundary, canonical engineering wiki and build
history, Temporal Chain tooling/template, Ghost licensing foundation, and
multi-harness launchers. `feat/public-seam-transport` is a separate locally
qualified candidate that removes the private package dependency and preserves
Ghost's reasoning lifecycle through an opaque SEAM service. The isolated
desktop avatar remains separate WIP. Nothing is released, deployed, assigned
to a company, or counsel-approved.**

PRs #6 and #7 and their exact merge-head Public CI are green. The public-SEAM
candidate is not protected-main behavior until its coordinated SEAM and Ghost
PRs pass exact-head checks and merge. See `docs/status/CURRENT_STATE.md`,
HISTORY#022, HISTORY#035, and the current handoff.

Live GitHub reconciliation on 2026-08-25 established:

- repository visibility is public;
- PR #5 merged the hosted automatic/manual-private workflow boundary;
- PR #6 merged the canonical wiki/history/licensing/launcher foundation;
- PR #7 merged the canonical follow-up through `main@10a2b45`;
- exact `main@10a2b45` passed all three hosted required checks;
- all external-contributor workflows require approval;
- secret scanning and push protection are enabled;
- Ghost has no repository secret and no assigned runner; and
- protected `main` requires PRs and the three strict hosted checks, enforces
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

1. Merge the coordinated SEAM/Ghost public transport candidates after
   exact-head review and CI.
2. Require the full hosted Ghost suite as a protected-main check.
3. Obtain counsel review and execute founder-to-company IP assignment after
   the legal entity is formed.
4. Complete Stage 1 frozen task/memory evaluations.
5. Resume the isolated desktop-avatar workstream after its asset and
   consequential-action boundaries are approved.

## Resume route

Read `docs/handoffs/INDEX.md`, then its `latest` document. Use
`HISTORY_INDEX.md` or a bounded context pack instead of loading all history.
