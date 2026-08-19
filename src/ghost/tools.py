"""Ghost's read-only tools.

Every tool here is built to the contract in `docs/security/TRUST_BOUNDARIES.md`
-- narrow purpose, typed inputs, explicit read/write classification, scope
validation, output-size limits, and an auditable result. All three are READ
ONLY, and that is enforced structurally rather than by convention:

* `seam_recall` touches only the SDK's query surface. `SeamSDK` also exposes
  `apply_delete`, `plan_delete`, `ingest`, `batch_ingest`, `apply_promotion`,
  `reverse_promotion`, and `lifecycle_operation`; none of them is reachable
  from here, and `tests/test_tools.py` fails if that changes. A tool that can
  delete memory is a tool that lets a prompt injection delete memory.
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
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from langchain_core.tools import BaseTool, tool

# One record's rendered text, and one tool result overall. A tool result is
# pasted into the model's context verbatim, so an unbounded read is an
# unbounded context cost and an easy way to crowd out the conversation.
MAX_RECORD_CHARS = 1_200
MAX_RESULT_CHARS = 20_000
MAX_FILE_BYTES = 200_000
MAX_MATCHES = 50


class ToolError(Exception):
    """A tool refused its input. The message is shown to the model."""


def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return f"{text[:limit]}\n... [truncated at {limit} characters]"


def _resolve_within(candidate: str, roots: Sequence[Path]) -> Path:
    """Resolve `candidate` and refuse anything outside `roots`.

    `Path.resolve()` follows symlinks, so the containment check runs on the
    real target -- a symlink inside a root that points at /etc/shadow resolves
    outside it and is refused here rather than read.
    """

    if not roots:
        raise ToolError("no readable roots are configured")
    try:
        resolved = Path(candidate).expanduser().resolve()
    except (OSError, RuntimeError) as exc:  # RuntimeError: symlink loop
        raise ToolError(f"cannot resolve path: {exc}") from exc
    for root in roots:
        if resolved == root or resolved.is_relative_to(root):
            return resolved
    allowed = ", ".join(str(r) for r in roots)
    raise ToolError(f"path is outside the readable roots ({allowed})")


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

    return seam_recall


def make_read_file(roots: Sequence[Path]) -> BaseTool:
    """Read one text file inside the configured roots. READ ONLY."""

    resolved_roots = [Path(r).expanduser().resolve() for r in roots]

    @tool("read_file", parse_docstring=False)
    def read_file(path: str) -> str:
        """Read a UTF-8 text file from Ghost's readable roots.

        Args:
            path: the file to read. Must resolve inside a configured root.
        """
        target = _resolve_within(path, resolved_roots)
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

    return read_file


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

        matches: list[str] = []
        for root in resolved_roots:
            for path in sorted(root.glob(glob)):
                if not path.is_file() or any(p in skip for p in path.parts):
                    continue
                try:
                    if path.stat().st_size > MAX_FILE_BYTES:
                        continue
                    text = path.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError):
                    continue
                for number, line in enumerate(text.splitlines(), start=1):
                    if needle in line:
                        rel = path.relative_to(root)
                        matches.append(f"{rel}:{number}: {line.strip()[:200]}")
                        if len(matches) >= MAX_MATCHES:
                            joined = "\n".join(matches)
                            return _truncate(
                                f"{joined}\n... [stopped at {MAX_MATCHES} matches]",
                                MAX_RESULT_CHARS,
                            )
        if not matches:
            return f"No matches for {needle!r}."
        return _truncate("\n".join(matches), MAX_RESULT_CHARS)

    return search_repo
