# Ghost project status

> This file is a current-state router, not an archive. Chronology lives in
> `HISTORY.md`; stable decisions live in `REPO_LEDGER.md`; detailed current
> evidence lives in `docs/status/CURRENT_STATE.md`.

## Current headline

**2026-08-25 — `main@dbd421b` contains the verified memory-backed single-agent
spine and the merged public/private CI safety boundary. The local working tree
adds the canonical-history/wiki foundation, a company-wide
Apache-edge/PolyForm-product/proprietary-core licensing candidate, the named
Temporal Chain with documentation-drift gates, multi-harness launchers, and an
isolated desktop-avatar workstream. Those local slices are not yet merged,
released, assigned to a company, or deployed.**

The local branch is fast-forwarded to `origin/main@dbd421b` and preserves the
uncommitted candidate. Public CI is green on the exact merged head; provider-
free current-tree verification and the publication-slice counts belong in the
latest history entry and handoff after closeout. See
`docs/status/CURRENT_STATE.md`, HISTORY#022, and HISTORY#034.

Live GitHub reconciliation on 2026-08-25 established:

- repository visibility is public;
- PR #5 merged the hosted automatic/manual-private workflow boundary;
- exact `main@dbd421b` passed all three hosted required checks;
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

The approved local distribution architecture uses Apache-2.0 for thin clients
and protocols, PolyForm Shield 1.0.0 for user-runnable source-available product
software, and permanent proprietary protection for undistributed SEAM/MIRL
internals, planned SEAM-U assets, and hosted control planes. Ghost still uses
the private in-process SDK; the public API/client topology is planned.

## Roadmap position

- Temporal Chain (Track T): core, handoff, and drift-gate layers run locally;
  publication is active; SEAM streams and routing are not installed.
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

1. Publish the canonical documentation/history/licensing/launcher foundation.
2. Isolate, review, and publish the desktop-avatar workstream.
3. Restore trustworthy private integration and dependency handling.
4. Obtain counsel review and execute founder-to-company IP assignment after
   the legal entity is formed.
5. Design and qualify Ghost's public client/API migration without losing its
   lifecycle, reasoning, and provenance contract.
6. Complete Stage 1 frozen task/memory evaluations.

## Resume route

Read `docs/handoffs/INDEX.md`, then its `latest` document. Use
`HISTORY_INDEX.md` or a bounded context pack instead of loading all history.
