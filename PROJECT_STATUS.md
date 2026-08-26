# Ghost project status

> This file is a current-state router, not an archive. Chronology lives in
> `HISTORY.md`; stable decisions live in `REPO_LEDGER.md`; detailed current
> evidence lives in `docs/status/CURRENT_STATE.md`.

## Current headline

**2026-08-25 — `main@a5997c6` contains the verified memory-backed single-agent
spine, public/private CI safety boundary, canonical engineering wiki and build
history, Temporal Chain tooling/template, Ghost licensing foundation, and
multi-harness launchers. The remaining local candidate is the isolated desktop
avatar workstream. Nothing is released, deployed, assigned to a company, or
counsel-approved.**

PR #6 and exact merge-head Public CI are green. The primary working branch is
fast-forwarded to `origin/main@a5997c6` and preserves only the uncommitted avatar
candidate. See `docs/status/CURRENT_STATE.md`, HISTORY#022, and HISTORY#035.

Live GitHub reconciliation on 2026-08-25 established:

- repository visibility is public;
- PR #5 merged the hosted automatic/manual-private workflow boundary;
- PR #6 merged the canonical wiki/history/licensing/launcher foundation;
- exact `main@a5997c6` passed all three hosted required checks after PR #6;
- all external-contributor workflows require approval;
- secret scanning and push protection are enabled;
- Ghost has no repository secret and no assigned runner; and
- protected `main` requires PRs and the three strict hosted checks, enforces
  administrators and conversation resolution, and blocks force pushes/deletes.

Organization runner-group inventory was unavailable without organization-admin
authority. The zero-assigned-runner state is fail-closed; private integration
remains unqualified until a deliberately isolated runner is assigned and an
owner dispatch passes.

## Product boundary

Ghost is Canticle's research-and-engineering DeepAgent. Ghost owns cognition,
mission, orchestration, tools, and operator-facing surfaces. SEAM owns durable
RAW/MIRL memory, retrieval, provenance, and reasoning records. LangGraph
checkpoints store execution state only.

The merged Ghost distribution architecture uses Apache-2.0 for thin clients
and protocols, PolyForm Shield 1.0.0 for user-runnable source-available product
software, and permanent proprietary protection for undistributed SEAM/MIRL
internals, planned SEAM-U assets, and hosted control planes. Ghost still uses
the private in-process SDK; the public API/client topology is planned.

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

1. Design and qualify Ghost's public client/API migration without losing its
   lifecycle, reasoning, and provenance contract.
2. Restore trustworthy full integration and dependency handling on hosted CI.
3. Obtain counsel review and execute founder-to-company IP assignment after
   the legal entity is formed.
4. Complete Stage 1 frozen task/memory evaluations.
5. Resume the isolated desktop-avatar workstream after its asset and
   consequential-action boundaries are approved.

## Resume route

Read `docs/handoffs/INDEX.md`, then its `latest` document. Use
`HISTORY_INDEX.md` or a bounded context pack instead of loading all history.
