# Ghost can use the computer

- Date: 2026-08-19
- Tests: 141 → 174 (8 live)
- Status: shell access is **off by default**; the operator opts in

## What shipped

`run_command` — a real shell, with the account's full authority. It is the
first write tool Ghost has had, and the first thing in the repository that can
change the machine.

```bash
export GHOST_ENABLE_SHELL=1
export GHOST_SHELL_WORKDIR="/path/to/work"
```

Live, on this machine:

```
decision  run_command: {"command": "printf 'kernel='; uname -r; ..."}
check     tool/run_command  verdict=passed  exit=0  len=72  sha=ec64445be959
outcome   accepted — "Ghost completed the user turn with verified actions."
```

## What bounds it, and what does not

There is deliberately **no denylist of dangerous commands.** Pattern-matching
shell strings is trivially bypassable and would imply a protection that does
not exist. A shell is exactly as powerful as the account running it, and no
wrapper changes that. What the design can do is make its use bounded and
accountable.

- **Opt-in.** Without `GHOST_ENABLE_SHELL` the tool is not built. A default
  deployment, or an import of Ghost as a library, cannot reach a shell.
- **Approval.** `GHOST_SHELL_APPROVAL` defaults on whenever the shell is on.
  The CLI prompts on `/dev/tty` rather than stdin, so a piped prompt cannot
  answer its own approval. With no terminal to ask, the answer is no — an
  unattended process must not silently inherit consent.
- **Timeouts.** Every command is capped. The model may narrow the cap and never
  widen it.
- **Verification.** Each command becomes a `decision` node with a `tool` check
  carrying its real exit code. `finalize_verified` refuses to accept the turn's
  outcome against a check that failed.
- **Output is fingerprinted, not stored.** SEAM keeps `result_length` and
  `result_sha256` and discards the text. This is the only reason shell output
  may touch the record at all: it routinely carries environment and tokens that
  `TRUST_BOUNDARIES.md` forbids becoming MIRL knowledge.

## Two defects found by building it

**The model could override the operator's timeout.** A model-supplied
`timeout_seconds` was capped against the global maximum rather than the
operator's setting, so an operator ceiling of 1s lost to a model request of
999s. That is the model overriding the operator rather than configuring itself.
Now it may only narrow.

**A refused tool killed the turn.** `ToolError` was a plain exception, so any
refusal — a path outside the roots, a declined command — crashed the whole
conversation. It now subclasses LangChain's `ToolException` and every tool sets
`handle_tool_error`, so a refusal comes back as a result the model reads and
works around. This affected every tool, not just the shell.

## A behaviour worth knowing

A live test asserting thread isolation failed, and the code was right:
`GHOST_SEAM_SCOPE=thread` is a scope *label*, not a binding to the LangGraph
thread id. `NAMESPACE_AND_SCOPE.md` says so — "the current `thread` label does
not itself partition data by LangGraph thread ID."

Memory therefore crosses threads within a namespace. That is what makes Ghost
remember across sessions, and it is correct for single-operator use. It is not
a tenancy boundary, and it matters more now: **what Ghost learns while running
commands in one thread is recallable from every other thread in the namespace.**
A test now pins this so real partitioning has to change it deliberately.

## Still not done

- **No sandbox.** Ghost runs as the operator's account on the operator's
  machine. Nothing containerises it.
- **Selective admission** (Stage 2) is still open. Every successful turn is
  still ingested wholesale, so the memory store remains a persistence surface
  for anything that reaches it.
- `patterns` / `use_pattern` unused — stored reasoning recipes.
