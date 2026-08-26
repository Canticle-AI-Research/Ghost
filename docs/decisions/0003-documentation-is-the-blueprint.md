# ADR-0003: Documentation is part of the build blueprint

- Status: accepted
- Date: 2026-08-25
- Governing history: HISTORY#023

## Context

Ghost's source expressed behavior that the roadmap and README no longer
described accurately. Installation, command, configuration, and architecture
knowledge was distributed between code comments, commit messages, local
handoffs, and prior conversations. That is not sufficient to rebuild or safely
operate a persistent agent.

## Decision

Every material behavior change updates, in the same review unit:

- the complete architecture/rebuild blueprint;
- command reference and task-oriented how-to when invocation changes;
- configuration reference and `.env.example` when settings change;
- security/trust documentation when authority changes;
- evaluation/qualification contract when claims change;
- roadmap/status/ledger/ADR where their authority changes; and
- canonical history/handoff state.

`docs/README.md` is the human wiki home. `docs/INDEX.md` is the exhaustive
machine-audited registry. All active Markdown documents must be reachable and
all relative links must resolve inside the repository.

## Consequences

- “Docs later” is not a complete implementation.
- A clean-room engineer receives enough information to reconstruct the system
  while secrets and private authorization remain external inputs.
- Documentation commands are executable contracts and must be tested/reviewed.
- Duplicate volatile facts are minimized through authority links.
- Local and planned work must remain labeled so the blueprint does not create
  false shipping claims.

## Rejected alternatives

- Generated API docs alone: cannot explain trust, lifecycle, operations, or
  evidence boundaries.
- README-only documentation: becomes unscannable and conflates audiences.
- Wiki outside Git: breaks commit-level provenance and review coupling.
- Source comments as the only design record: explain local mechanics without
  full system reconstruction or temporal state.
