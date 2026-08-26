# Stage 1 frozen evaluation candidate ready for exact-head CI

handoff_id: `ghost-stage1-candidate-ready-20260825`
supersedes: `ghost-stage1-final-baseline-qualified-20260825`
handoff_status: `superseded`
history: `HISTORY#045`
created_at: `2026-08-25T22:29:49-05:00`

## Candidate result

The six-commit `feat/stage1-frozen-evals` candidate is locally complete:

- 20 immutable cases across ten required categories;
- real `run_turn` lifecycle execution with a named no-memory arm;
- exact step/tool/context budgets and case-specific forbidden effects;
- BIL-0 sealing, verification, exact coverage/outcome/safety gates;
- final clean-source artifact hash
  `57ca22ea5706f78e8513b92c8569fb8641e3e58c43cfedf3df0e39d81512a959`;
- `GHOST_MAX_STEPS` bounded 2–100 with default 25;
- complete provider-free suite: 219 passed, 8 live tests deselected;
- Ruff, build, continuity, handoff, docs, and diff hygiene passed; and
- CodeRabbit full review returned eight findings, all repaired; final-delta
  review returned one wording finding, repaired here.

The eleven reported verifier checks are bundle-level integrity/cross-identity
checks. Per-case checks deliberately retain expected failures in the scripted
no-memory arm. The artifact remains `claimable: false`.

## Remote publication route

Push this exact successor, open a focused PR, observe `stage1-evals`, add that
context to protected main without weakening the existing five checks/settings,
and merge only when all six hosted jobs pass. Then publish a protected-main
successor handoff. Provider/live, paid judge, and release-candidate qualification
remain open G1 exits.
