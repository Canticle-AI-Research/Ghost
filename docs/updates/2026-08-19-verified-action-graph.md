# Turns become verified reasoning graphs

- Date: 2026-08-19
- Roadmap: Stage 1 complete; foundation for Stage 2 admission and write tools
- Tests: 125 → 141 (6 live)

## Why

Ghost was using SEAM as a memory store and ignoring its reasoning layer — 4 of
18 `ReasoningSession` methods. A turn produced one flat outcome, always
accepted, whatever happened inside it.

The question that prompted this was whether Ghost should control the operating
system, and where that belongs. Investigating it turned up that SEAM's
reasoning layer is not a log. It is a transaction manager for agent actions,
and it was designed for exactly this: `verify` takes `check_kind`, `exit_code`,
and `duration_ms`, and `tool` is a first-class check kind.

## What is enforced

Two properties were verified against a real store before anything was built:

- `finalize_verified` **refuses** an outcome whose named checks did not pass —
  `ValueError: verified outcomes require current passed verifications`. It is
  not advisory.
- a check `result` is reduced to `result_length` and `result_sha256`. The raw
  text is never stored.

So "the action succeeded" became a property the database enforces rather than a
claim the model makes about itself.

## What changed

A turn now emits, per tool call, a `decision` node and a `tool` verification
carrying the verdict; the turn finalizes with `finalize_verified` against the
checks that passed, or plainly when there were none.

A failed tool is recorded with its verdict and deliberately **not** returned as
outcome support. A failed tool does not fail the turn — the model may have
recovered — but it cannot support the outcome.

Live, one real turn now produces:

```
decision   seam_recall: {"limit": 5, "query": "deploy window"}
outcome    Ghost completed the user turn with verified actions.   [accepted]

CHECKS  tool/seam_recall  verdict=passed  exit=0  len=761  sha=0dd8eb376748
```

## Layering

`ToolAttempt` is a plain dataclass and `record_actions` lives in the
framework-free layer. Translating LangChain's `tool_calls` and `ToolMessage`
into it is adapter work, in `application.py`, because only the adapter knows
those shapes. `tests/test_layering.py` keeps that split honest.

## Why this matters for OS control

This is the prerequisite, not a detour. With it:

- an OS action is a `decision` that must pass a `tool` check before its outcome
  can commit, so an injected instruction in recalled memory cannot drive an
  action to completion;
- command output can be admitted at all, because it is fingerprinted rather
  than stored — shell output routinely carries environment and tokens that
  `TRUST_BOUNDARIES.md` forbids becoming MIRL knowledge; and
- "why did Ghost run this" is answerable from the store, by walking the
  decision back to the evidence that motivated it.

## Not done

- `patterns` / `use_pattern` — stored reasoning recipes. Worth having only once
  a corpus of verified runs exists to learn from.
- `propose_promotion` — Stage 2 selective admission, replacing "ingest every
  successful turn".
- no write tools yet, by design.
