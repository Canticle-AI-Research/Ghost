# Specialist and operations foundation qualified

handoff_id: `ghost-specialist-ops-foundation-qualified-20260826`
supersedes: `ghost-deliberate-memory-published-20260826`
handoff_status: `superseded`
history: `HISTORY#049`
created_at: `2026-08-26T00:32:11-05:00`

## Candidate result

The isolated `feat/specialist-ops-foundation` candidate is based on protected
`main@4cebdd8646a4f5fe4d760c01c2172341ff4886ea`. It adds provider-free
delegation envelopes, explicit budgets and tool/root/memory scopes, opaque
evidence linkage, fixed terminal states, safe start/finish events, and failure
normalization. It does not register or run a model-backed specialist.

The same candidate adds SQLite-consistent checkpoint backup, SHA-256 and
`quick_check` verification, restore to a new path only, fail-closed redacted
component health, `ghost checkpoint backup|verify|restore`, and extensive
architecture/operator/recovery documentation. Checkpoint recovery does not
recover SEAM semantic memory.

## Verification and risk boundary

- `uv run ruff check .` passed.
- `uv run pytest -q` passed 270 provider-free tests; 8 live tests were
  deselected by the project marker.
- `uv build` passed for wheel and source distribution.
- `git diff --check` passed.
- Two CodeRabbit rounds reviewed the complete candidate and found three major
  redaction/coverage gaps. Successful probe results, health failure classes,
  and specialist-returned failure summaries/codes are now discarded in favor
  of fixed safe codes; telemetry redaction has regression coverage. A final
  automated rerun was unavailable when the free CLI reset extended to 50
  minutes; manual final review and the complete local gates passed.

No provider, paid judge, live SEAM service, package release, hosted endpoint,
backup deletion, restore over an existing path, or deployment ran. G1/G2/Q3
exit evidence remains open, so this candidate cannot support a G3 improvement
or G4 production claim. The primary avatar worktree remains untouched.

## Resume route

1. run `uv run python -m tools.history.closeout --agent codex`;
2. rerun Ruff, all provider-free tests, build, and diff hygiene;
3. commit only the explicit candidate paths and push this branch;
4. open a focused PR and require all six exact-head hosted checks;
5. merge through protected `main` only after review/checks pass; and
6. append a successor publication record without claiming live specialists or
   a hosted deployment.
