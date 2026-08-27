# Trust and safety boundaries

## Core rule

Remembered text, model output, tool output, graph topology, and provider
responses are inputs to a decision. None is automatically an instruction,
authorization grant, or verified fact.

## Boundary map

| Boundary | Current control | Remaining work |
|---|---|---|
| Recalled memory to model | labeled untrusted, angle brackets escaped, transient middleware | adversarial eval corpus and richer content-block handling |
| Model output to MIRL | successful turn plus explicit provider-free admission decision; model output cannot self-promote | operator review queue UI and higher-integrity eval |
| Graph to answer | graph hits resolve back to MIRL IDs | user-visible evidence-path policy |
| Tool request to external action | DeepAgents framework boundary | explicit tool allowlist, permissions, HITL, timeouts |
| User/workspace isolation | service-derived principal plus namespace/workspace/project/scope/thread boundary | hosted authorization proof and migration UX |
| Secret handling | ignored env files; no key copied into repository | deployment secret manager and log redaction tests |
| SEAM service boundary | public HTTP adapter, opaque handles, no private source dependency | compatible release/deployment and recovery proof |
| SEAM response to Ghost | streamed 8 MiB cap before JSON parsing | deployment latency/body telemetry without content logging |
| Repository search to filesystem | operator roots, relative traversal-free globs, per-candidate resolution and open-descriptor containment | aggregate visit/byte/deadline budgets |

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

Current Ghost sends a deterministic admission decision with every successful
root turn. The default admits explicit remember requests, rejects ordinary
conversation and mutation requests, and marks unconfirmed durable candidates
for review without storing them. The classifier reads operator input only;
model output cannot promote itself. `GHOST_MEMORY_ADMISSION=all` is an explicit
compatibility override and should not be mistaken for corroboration.

Remember, correct, and forget are CLI-only operator operations. They are not
registered as model tools, so recalled prompt injection cannot reach them.

No hidden chain-of-thought, raw provider payload, credential, private key,
session link, or unrestricted tool log should become MIRL knowledge.

## Verified actions

Every tool call is sent through the opaque actions route and recorded as a
`decision` node checked by a `tool` verification. On completion, SEAM derives
the passed checks server-side and accepts a verified outcome only against
those checks. Ghost cannot submit a client-selected verification ID, so "the
action succeeded" is enforced by the service rather than asserted by the model.

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

`search_repo` applies those rules before candidate access: the glob must be
relative and contain no parent traversal, every candidate must resolve inside
the root that enumerated it, and the opened descriptor must still name an
object inside that root. If the runtime cannot inspect the opened descriptor,
the search refuses rather than weakening containment. Absolute globs,
cross-root symlinks, loops, and candidates changed during enumeration are
refused rather than read.

Subagents must not gain permissions merely because the root agent delegates to
them.

## Failure behavior

Ghost should fail closed when memory scope, API compatibility, or authorization
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
