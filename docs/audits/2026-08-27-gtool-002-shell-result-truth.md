# GTOOL-002 shell-result truth closure

- Date: 2026-08-27
- Governing history: HISTORY#055
- Scope: command execution result, LangChain transport, Ghost lifecycle adapter,
  SEAM action evidence, accepted-outcome support
- Qualification: provider-free source candidate

## Outcome

GTOOL-002 is closed in the qualified source candidate. A shell process that
exits nonzero can no longer become a successful Ghost tool attempt merely
because LangChain transported the tool message successfully. Ghost now carries
one versioned, framework-free result from process completion through
`ToolMessage.artifact`, validates it without coercion, records the real exit
code in SEAM action evidence, and withholds failed verifications from outcome
support.

This report does not close GTOOL-003 process-tree termination, GTOOL-004
pre-buffer output bounds, GST-001/GST-002 authority configuration, GTOOL-005
request redaction, package publication, a live provider/SEAM lane, release, or
deployment. Normal shell use remains off until the remaining governing gates
close.

## Reproduced defect

Before this repair, `run_command` returned a string such as
`exit=3 duration_ms=4`, but an ordinary LangChain return still produced a
`ToolMessage` with transport status `success`. `extract_tool_attempts` treated
that framework status as the process verdict, synthesized `exit_code=0`, and
sent `ok=true` to the SEAM `/actions` boundary. The failed command could then
produce a passed verification ID and support an accepted outcome.

The failure crossed five planes:

```text
process exit 3
    -> model-facing text containing "exit=3"
    -> LangChain transport status "success"
    -> Ghost synthesized ok=true / exit_code=0
    -> SEAM passed verification and accepted-outcome support
```

The text happened to state the truth, but no authoritative typed field carried
that truth to the lifecycle boundary.

## Governing contract

`src/ghost/command_result.py` now owns `ghost.command_result/v1`. It is
framework-free and deliberately separates execution truth from agent-framework
transport.

| Field | Type | Meaning |
|---|---|---|
| `schema` | exact string | `ghost.command_result/v1` compatibility boundary |
| `status` | exact string | `succeeded` only for exit zero; otherwise `failed` |
| `ok` | boolean | derived from `exit_code == 0` |
| `exit_code` | integer, not boolean | real completed-process return code |
| `duration_ms` | finite nonnegative number | measured execution duration |
| `truncated` | boolean | model-facing result exceeded the output character cap |

Validation refuses absent artifacts, unknown schemas, coerced or wrong field
types, non-finite or negative durations, and any contradiction between status,
success, and exit code. Invalid evidence fails closed with `ok=false`, no
invented exit code, no duration, and no passed support.

## End-to-end repaired flow

```text
subprocess.CompletedProcess
    -> CommandResult(exit_code, duration_ms, truncated)
    -> ToolMessage(content=model text,
                   status=transport status,
                   artifact=ghost.command_result/v1)
    -> ordered request/result identity and transport validation
    -> CommandResult.from_artifact()
    -> ToolAttempt(ok, real exit_code, real duration_ms)
    -> SEAM /actions
    -> only exit-zero evidence may return a passed verification ID
    -> accepted outcome receives only those passed IDs
```

The adapter also rejects a result that precedes its request, reused or
duplicated call IDs, duplicate results, missing results, non-success transport
states, and a result whose tool name does not match `run_command`. This prevents
stale or unrelated evidence from being paired with a later command request.

## Evidence matrix

| Case | LangChain transport | Artifact | Ghost attempt | SEAM support |
|---|---|---|---|---|
| completed exit 0 | `success` | valid, exit 0 | `ok=true`, exit 0 | eligible |
| completed exit 3 | `success` | valid, exit 3 | `ok=false`, exit 3 | withheld |
| refused command | `error` | absent | failed, exit unknown | withheld |
| timed-out command | `error` | absent | failed, exit unknown | withheld |
| missing/malformed artifact | any | invalid | failed, exit unknown | withheld |
| status/name/order/ID mismatch | invalid exchange | ignored | failed | withheld |

## Changed surfaces

- `src/ghost/command_result.py`: strict framework-free result schema and
  validator.
- `src/ghost/tools.py`: separate model content from the typed command artifact.
- `src/ghost/application.py`: ordered, identity-aware, fail-closed extraction.
- `tests/test_command_result.py`: schema and contradiction regressions.
- `tests/test_shell_tool.py`: real full-ToolCall success, nonzero, and
  truncation transport coverage.
- `tests/test_reasoning_graph.py`: adapter adversarial cases and full lifecycle
  proof that nonzero/refused/timed-out commands cannot support completion.
- `tests/conftest.py`: fake SEAM rejects a command claimed successful without an
  exact zero exit code.
- `tests/test_layering.py`: the new contract is enforced framework-free.
- Governing README, ledger, architecture, operations, and trust documentation.

## Verification boundary

Provider-free focused regressions passed, including full LangChain ToolCall
messages, ToolNode transport, SQLite checkpoint persistence, handled errors,
malformed artifacts, and the SEAM lifecycle. The complete suite passed 306
tests with eight live tests deselected. Ruff, build, continuity, diff hygiene,
recorded-fact audit, and the changed-path secret-shaped scan passed. Protected
exact-head CI remains a publication gate recorded by the successor publication
entry.

The first PR run `33124878342` passed five jobs and failed `repo-hygiene`
because the current-state router asserted a volatile local suite count while
that narrow job intentionally collected only its documentation dependency
subset. The count was removed from the router, as the recorded-fact gate itself
recommends; the full 306-test evidence remains an explicit historical
qualification fact here and in HISTORY#055.

No paid model, live provider, live SEAM service, package publication, release,
deployment, or avatar lane was run. The preserved avatar checkout was not
modified.

## Course of action

1. Publish this focused repair through protected review and all six exact-head
   provider-free checks.
2. Close GTOOL-003 by terminating and reaping the whole process group on
   timeout, with a delayed-side-effect regression.
3. Close GTOOL-004 by bounding combined stdout/stderr while the process runs,
   rather than after unbounded buffering.
4. Close GST-001/GST-002 so malformed booleans and working-directory dotenv
   files cannot weaken shell approval or redirect authority.
5. Close GTOOL-005 typed/redacted request evidence, resource ownership,
   checkpoint, transport, CLI, and source-distribution boundaries.
6. Only then advance provider-free Q3 G1/G2 mechanics; stop before paid model
   execution for explicit operator approval.
