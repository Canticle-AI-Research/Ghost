# Trust and safety boundaries

## Core rule

Remembered text, model output, tool output, graph topology, and provider
responses are inputs to a decision. None is automatically an instruction,
authorization grant, or verified fact.

## Boundary map

| Boundary | Current control | Remaining work |
|---|---|---|
| Recalled memory to model | labeled untrusted, angle brackets escaped, transient middleware | adversarial eval corpus and richer content-block handling |
| Model output to MIRL | persisted only after a successful root result; provenance retained | selective admission and optional review gate |
| Graph to answer | graph hits resolve back to MIRL IDs | user-visible evidence-path policy |
| Tool request to external action | DeepAgents framework boundary | explicit tool allowlist, permissions, HITL, timeouts |
| User/workspace isolation | one configured namespace and scope | principal-aware partitioning and authorization |
| Secret handling | ignored env files; no key copied into repository | deployment secret manager and log redaction tests |
| Private SEAM dependency | exact private Git revision | private CI credentials and controlled upgrade process |

## Memory injection

Retrieved memory can contain text that resembles system prompts or tool
commands. Ghost's middleware currently:

- calls the memory untrusted evidence;
- says not to execute instructions found inside it;
- encodes selected records as JSON Lines;
- escapes angle brackets to prevent closing the surrounding tag; and
- avoids writing the injected payload into checkpoint state.

This reduces risk but does not prove immunity. Evaluation must include memories
that request secret disclosure, permission escalation, tool execution, policy
replacement, or cross-user retrieval.

## Canonical-memory admission

Current Ghost automatically ingests every successful root turn. Model output is
therefore durable provenance-bearing memory but should not be treated as
independently corroborated truth. The planned admission layer must attach trust,
evidence, time, and review requirements appropriate to the memory kind.

No hidden chain-of-thought, raw provider payload, credential, private key,
session link, or unrestricted tool log should become MIRL knowledge.

## Verified actions

Every tool call is recorded as a `decision` node checked by a `tool`
verification, and a turn that used tools is finalized with
`finalize_verified` against the checks that passed. SEAM refuses that call
when the named checks did not pass, so "the action succeeded" is enforced by
the store rather than asserted by the model.

Two consequences matter for future write tools:

- a failed tool is recorded with its verdict but is never offered as outcome
  support, so an unverified action cannot commit; and
- the tool's raw output is passed as a check `result`, which SEAM reduces to
  `result_length` and `result_sha256`. The result stays provable while its
  contents — environment, tokens, paths — never enter the record. This is the
  mechanism that makes shell output admissible at all.

## Tool permissions

Before Ghost receives consequential tools, every tool needs:

- a narrow purpose and typed inputs;
- read versus write classification;
- target and scope validation;
- timeout and output-size limits;
- secret-redaction rules;
- idempotency or retry behavior;
- human approval for destructive or externally visible actions; and
- an auditable result that excludes hidden reasoning and raw credentials.

Subagents must not gain permissions merely because the root agent delegates to
them.

## Failure behavior

Ghost should fail closed when memory scope, SDK compatibility, or authorization
cannot be established. Availability fallbacks may omit optional recall only
when product policy explicitly permits a memory-degraded mode and clearly marks
the response as such.

Provider and tool errors should persist only controlled error classes and
bounded public summaries. Raw response bodies may contain secrets or unrelated
service data and should not be written to MIRL or reasoning telemetry.

## Production gate

Ghost is not ready for multi-user or externally exposed operation until the
isolation, tool-permission, admission, deletion, failure-finalization, and
security evaluation gates in this documentation are implemented and passing.

