"""Ghost's tools.

Every tool here is built to the contract in `docs/security/TRUST_BOUNDARIES.md`
-- narrow purpose, typed inputs, explicit read/write classification, scope
validation, output-size limits, and an auditable result.

Three of the four are READ ONLY, enforced structurally rather than by
convention. The fourth, `run_command`, is a shell and is exactly as powerful as
the account running Ghost; see `make_run_command` for what bounds it and what
does not. Read/write classification is data, in `WRITE_TOOLS`, so a test can
assert that no tool quietly becomes a write.

The read-only guarantees:

* `seam_recall` touches only the opaque service's recall route. Completion,
  failure, action, and administrative lifecycle routes are not reachable from
  here, and `tests/test_tools.py` fails if that changes. A tool that can
  delete memory is a tool that lets a prompt injection delete memory.
  Administrative mutation stays behind the application lifecycle boundary.
* the filesystem tools resolve every path and refuse anything outside their
  configured roots, so a traversal or a symlink cannot walk out of the tree.

These are deliberately NOT built on the DeepAgents filesystem backend. That
backend is configured through `create_deep_agent(backend=...)`, which
`tests/test_memory_boundary.py` forbids under ADR-0001 -- passing it also
installs deepagents' own memory middleware. Plain tools keep the memory
boundary intact.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

from langchain_core.tools import BaseTool, ToolException, tool

from .path_policy import (
    PathPolicyError,
    read_search_candidate,
    resolve_within,
    validate_search_glob,
)

# One record's rendered text, and one tool result overall. A tool result is
# pasted into the model's context verbatim, so an unbounded read is an
# unbounded context cost and an easy way to crowd out the conversation.
MAX_RECORD_CHARS = 1_200
MAX_RESULT_CHARS = 20_000
MAX_FILE_BYTES = 200_000
MAX_MATCHES = 50
# A command that has not finished in this long is hung, not slow. Without a
# ceiling, one `tail -f` ends the session.
DEFAULT_COMMAND_TIMEOUT = 120
MAX_COMMAND_TIMEOUT = 3_600
#: Tools that can change the machine. Kept as data so `tests/test_tools.py`
#: can assert the set has not grown without the trust-boundary review that
#: TRUST_BOUNDARIES.md requires for consequential tools.
WRITE_TOOLS: frozenset[str] = frozenset({"run_command"})

_TRUTHY = {"1", "true", "yes", "on"}


class ToolError(ToolException):
    """A tool refused its input. The message is shown to the model.

    Subclasses LangChain's ``ToolException`` deliberately. A tool refusing bad
    input is a normal event -- a path outside the roots, a file that is not
    UTF-8, an operator declining a command -- and the model should see the
    reason and choose differently. Raising a plain exception instead kills the
    whole turn, which is both a worse experience and a worse failure mode: the
    turn is finalized as failed and nothing is learned from it.

    Paired with ``handle_tool_error`` on each tool, which turns the raised
    message into a tool result the model reads.
    """


class ApprovalDenied(ToolError):
    """An operator declined a write action.

    A subclass so declining one command reaches the model as a refusal it can
    reason about and work around, rather than ending the turn.
    """


def _recoverable(built: BaseTool) -> BaseTool:
    """Return tool errors to the model instead of ending the turn.

    `handle_tool_error` is a field on the tool, not an argument to the
    decorator. With it set, a raised `ToolError` becomes a tool result the
    model reads and can act on -- "that path is outside the readable roots",
    "the operator declined" -- rather than an exception that kills the turn and
    finalizes it as failed.
    """

    built.handle_tool_error = True
    return built


def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return f"{text[:limit]}\n... [truncated at {limit} characters]"


def _apply_path_policy(function: Callable[..., Any], /, *args: Any, **kwargs: Any) -> Any:
    try:
        return function(*args, **kwargs)
    except PathPolicyError as exc:
        raise ToolError(str(exc)) from exc


def make_seam_recall(memory: Any, *, namespace: str, scope: str) -> BaseTool:
    """Deliberate lookup in Ghost's own memory. READ ONLY.

    Distinct from the automatic pre-turn recall in `SeamRecallMiddleware`:
    that one fires once per turn on the user's message, while this lets Ghost
    go back for something specific mid-reasoning.
    """

    @tool("seam_recall", parse_docstring=False)
    def seam_recall(query: str, limit: int = 8) -> str:
        """Search Ghost's durable SEAM memory for records related to a query.

        Returns matching records as JSON lines with their record ids, so an
        answer can cite provenance. This reads memory and never writes it.

        Args:
            query: what to look for, in natural language.
            limit: maximum records to return (1-32).
        """
        cleaned = query.strip()
        if not cleaned:
            raise ToolError("query is required")
        bounded = max(1, min(int(limit), 32))

        graph = memory.query_knowledge(
            query=cleaned, limit=bounded, namespace=namespace, scope=scope
        )
        nodes = list(graph.get("nodes") or [])[:bounded]
        if not nodes:
            return "No memory matched that query."

        lines: list[str] = []
        for node in nodes:
            label = node.get("label") or node.get("id")
            payload = {
                "record_id": str(node.get("id", "")),
                "kind": str(node.get("kind", "")),
                "memory": _truncate(str(label), MAX_RECORD_CHARS),
            }
            encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True)
            # Same fence-escaping as render_memories: a recalled record must not
            # be able to close the tag the middleware wraps memory in.
            lines.append(encoded.replace("<", "\\u003c").replace(">", "\\u003e"))
        return _truncate("\n".join(lines), MAX_RESULT_CHARS)

    return _recoverable(seam_recall)


def make_read_file(roots: Sequence[Path]) -> BaseTool:
    """Read one text file inside the configured roots. READ ONLY."""

    resolved_roots = [Path(r).expanduser().resolve() for r in roots]

    @tool("read_file", parse_docstring=False)
    def read_file(path: str) -> str:
        """Read a UTF-8 text file from Ghost's readable roots.

        Args:
            path: the file to read. Must resolve inside a configured root.
        """
        target = _apply_path_policy(resolve_within, path, resolved_roots)
        if not target.exists():
            raise ToolError(f"no such file: {path}")
        if not target.is_file():
            raise ToolError(f"not a regular file: {path}")
        if target.stat().st_size > MAX_FILE_BYTES:
            raise ToolError(
                f"file is larger than {MAX_FILE_BYTES} bytes; narrow the read"
            )
        try:
            text = target.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise ToolError("file is not UTF-8 text") from exc
        return _truncate(text, MAX_RESULT_CHARS)

    return _recoverable(read_file)


def make_search_repo(roots: Sequence[Path]) -> BaseTool:
    """Find a literal string across the configured roots. READ ONLY."""

    resolved_roots = [Path(r).expanduser().resolve() for r in roots]
    skip = {".git", ".venv", "__pycache__", "node_modules", ".ruff_cache", ".pytest_cache"}

    @tool("search_repo", parse_docstring=False)
    def search_repo(pattern: str, glob: str = "**/*") -> str:
        """Search Ghost's readable roots for a literal string.

        Returns `path:line: text` for each match. This is a literal substring
        search, not a regular expression.

        Args:
            pattern: the literal text to find.
            glob: which files to search, e.g. "**/*.py".
        """
        needle = pattern.strip()
        if not needle:
            raise ToolError("pattern is required")
        search_glob = _apply_path_policy(validate_search_glob, glob)

        matches: list[str] = []
        for root in resolved_roots:
            try:
                candidates = sorted(root.glob(search_glob))
            except (NotImplementedError, OSError, RuntimeError, ValueError) as exc:
                raise ToolError("cannot evaluate the repository search glob") from exc
            for path in candidates:
                relative = path.relative_to(root)
                if any(part in skip for part in relative.parts):
                    continue
                target = _apply_path_policy(resolve_within, str(path), [root])
                text = _apply_path_policy(
                    read_search_candidate,
                    target,
                    root,
                    max_bytes=MAX_FILE_BYTES,
                )
                if text is None:
                    continue
                for number, line in enumerate(text.splitlines(), start=1):
                    if needle in line:
                        matches.append(f"{relative}:{number}: {line.strip()[:200]}")
                        if len(matches) >= MAX_MATCHES:
                            joined = "\n".join(matches)
                            return _truncate(
                                f"{joined}\n... [stopped at {MAX_MATCHES} matches]",
                                MAX_RESULT_CHARS,
                            )
        if not matches:
            return f"No matches for {needle!r}."
        return _truncate("\n".join(matches), MAX_RESULT_CHARS)

    return _recoverable(search_repo)


def shell_enabled() -> bool:
    """Whether the operator opted this process into shell access."""

    return os.environ.get("GHOST_ENABLE_SHELL", "").strip().lower() in _TRUTHY


def make_run_command(
    *,
    workdir: Path | None = None,
    timeout: int = DEFAULT_COMMAND_TIMEOUT,
    approve: Callable[[str], bool] | None = None,
) -> BaseTool:
    """Run a shell command. THIS IS A WRITE TOOL -- it can change the machine.

    Be honest about what this is. A shell is exactly as powerful as the account
    running Ghost; no wrapper makes that safe, and a denylist of dangerous
    strings would be trivially bypassable while implying a protection that does
    not exist. So this deliberately does not pattern-match commands. What the
    design does instead is make shell use *bounded* and *accountable*.

    Bounded:

    * it refuses to run unless the operator set ``GHOST_ENABLE_SHELL``, so a
      default deployment cannot reach a shell at all;
    * every command carries a timeout, capped, because an agent that runs
      ``tail -f`` otherwise hangs the session forever; and
    * output is truncated before it reaches the model's context.

    Accountable, which is the part that matters and the part SEAM provides:
    the caller records each invocation as a ``decision`` node with a ``tool``
    verification carrying the real exit code, and ``finalize_verified`` refuses
    to accept the turn's outcome against a check that failed. The command's
    output is fingerprinted rather than stored, which is the only reason shell
    output may touch the record at all -- it routinely carries environment and
    tokens that ``TRUST_BOUNDARIES.md`` forbids becoming MIRL knowledge.

    ``approve`` is the operator's stop button, wired by the CLI. It is a chance
    for a human to say no, not a security boundary against the model.
    """

    resolved_workdir = Path(workdir).expanduser().resolve() if workdir else Path.cwd()
    bounded_timeout = max(1, min(int(timeout), MAX_COMMAND_TIMEOUT))

    @tool("run_command", parse_docstring=False)
    def run_command(command: str, timeout_seconds: int | None = None) -> str:
        """Run a shell command on the operator's machine and return its output.

        This CHANGES THE MACHINE. Prefer `read_file` or `search_repo` when you
        only need to look at something. Say what a command will do before you
        run it, and never chain destructive operations speculatively.

        Returns the exit code and duration, then combined stdout and stderr.

        Args:
            command: the shell command to run.
            timeout_seconds: optional override, capped by the operator.
        """
        if not shell_enabled():
            raise ToolError(
                "the shell tool is disabled; the operator must set GHOST_ENABLE_SHELL=1"
            )
        line = command.strip()
        if not line:
            raise ToolError("command is required")

        if approve is not None and not approve(line):
            raise ApprovalDenied(f"the operator declined to run: {line}")

        # The model may NARROW the timeout and never widen it. Capping its
        # request against MAX_COMMAND_TIMEOUT instead of the operator's limit
        # let it ask for 999s against an operator ceiling of 1s and win, which
        # is the model overriding the operator rather than configuring itself.
        limit = (
            bounded_timeout
            if timeout_seconds is None
            else max(1, min(int(timeout_seconds), bounded_timeout))
        )
        started = time.monotonic()
        try:
            # S602 is suppressed, not overlooked. `shell=True` is the feature:
            # this tool exists to run shell commands, so pipes, redirection,
            # globs and `&&` must work. Passing an argv list would make it a
            # worse-behaved `exec` while removing none of the risk, because the
            # risk is not in how the process is spawned. It is managed above
            # this line -- the opt-in flag, the approval hook, the timeout --
            # and by SEAM refusing to accept an outcome whose check failed.
            completed = subprocess.run(  # noqa: S602
                line,
                shell=True,
                cwd=str(resolved_workdir),
                capture_output=True,
                text=True,
                timeout=limit,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise ToolError(f"command exceeded {limit}s and was killed: {line}") from exc
        except OSError as exc:
            raise ToolError(f"could not run command: {exc}") from exc

        elapsed_ms = (time.monotonic() - started) * 1000
        body = (completed.stdout or "") + (completed.stderr or "")
        return _truncate(
            f"exit={completed.returncode} duration_ms={elapsed_ms:.0f}\n{body}",
            MAX_RESULT_CHARS,
        )

    return _recoverable(run_command)
