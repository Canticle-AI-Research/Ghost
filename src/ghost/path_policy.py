"""Framework-free filesystem containment policy for Ghost's read tools."""

from __future__ import annotations

import errno
import os
import stat
from collections.abc import Sequence
from pathlib import Path, PurePosixPath, PureWindowsPath


class PathPolicyError(ValueError):
    """A path or glob could not be proven safe for the requested read."""


def resolve_within(candidate: str, roots: Sequence[Path]) -> Path:
    """Resolve ``candidate`` and require it to remain within one allowed root."""

    if not roots:
        raise PathPolicyError("no readable roots are configured")
    try:
        resolved = Path(candidate).expanduser().resolve()
    except (OSError, RuntimeError) as exc:
        raise PathPolicyError(f"cannot resolve path: {exc}") from exc
    for root in roots:
        if resolved == root or resolved.is_relative_to(root):
            return resolved
    allowed = ", ".join(str(root) for root in roots)
    raise PathPolicyError(f"path is outside the readable roots ({allowed})")


def validate_search_glob(raw: str) -> str:
    """Return one relative, traversal-free glob or refuse it.

    Both POSIX and Windows spellings are checked. A Windows absolute path is
    only an oddly named relative path on POSIX, but accepting it would make the
    security contract change with the host operating system.
    """

    cleaned = raw.strip()
    if not cleaned:
        raise PathPolicyError("glob is required")
    try:
        variants = (PurePosixPath(cleaned), PureWindowsPath(cleaned))
    except (OSError, ValueError) as exc:
        raise PathPolicyError("glob must be relative and traversal-free") from exc
    if any(path.anchor or path.drive for path in variants) or any(
        part == ".." for path in variants for part in path.parts
    ):
        raise PathPolicyError("glob must be relative and traversal-free")
    return cleaned


def read_search_candidate(target: Path, root: Path, *, max_bytes: int) -> str | None:
    """Open one contained target once and return bounded UTF-8 text.

    ``O_NOFOLLOW`` closes the final-component race between resolution and
    opening on platforms that provide it. On Linux, resolving the open file
    descriptor verifies the object that was actually opened before it is
    inspected or read, covering a replaced parent path as well.
    """

    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NONBLOCK", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(target, flags)
    except OSError as exc:
        if exc.errno == errno.ELOOP:
            raise PathPolicyError(
                "cannot resolve path: symlink loop or changed target"
            ) from exc
        return None
    try:
        descriptor_path = Path("/proc/self/fd") / str(descriptor)
        if not descriptor_path.parent.is_dir():
            raise PathPolicyError(
                "cannot verify the opened path on this platform; search refused"
            )
        try:
            opened_target = descriptor_path.resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            raise PathPolicyError(
                "matched path changed while the search was running"
            ) from exc
        if opened_target != root and not opened_target.is_relative_to(root):
            raise PathPolicyError(
                "matched path escaped its readable root during the search"
            )

        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_size > max_bytes:
            return None
        with os.fdopen(descriptor, "rb", closefd=True) as handle:
            descriptor = -1
            payload = handle.read(max_bytes + 1)
        if len(payload) > max_bytes:
            return None
        try:
            return payload.decode("utf-8")
        except UnicodeDecodeError:
            return None
    finally:
        if descriptor >= 0:
            os.close(descriptor)
