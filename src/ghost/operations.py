"""Fail-closed health and checkpoint recovery primitives for Ghost operators."""

from __future__ import annotations

import hashlib
import os
import sqlite3
import tempfile
from collections.abc import Callable, Mapping
from contextlib import suppress
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True, slots=True)
class CheckpointManifest:
    path: Path
    sha256: str
    size_bytes: int

    def to_dict(self) -> dict[str, str | int]:
        return {
            "path": str(self.path),
            "sha256": self.sha256,
            "size_bytes": self.size_bytes,
        }


def _digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _quick_check(path: Path) -> None:
    uri = path.resolve().as_uri() + "?mode=ro"
    with sqlite3.connect(uri, uri=True) as connection:
        result = connection.execute("pragma quick_check").fetchone()
    if result != ("ok",):
        raise ValueError("checkpoint database failed SQLite quick_check")


def _manifest(path: Path) -> CheckpointManifest:
    return CheckpointManifest(path.resolve(), _digest(path), path.stat().st_size)


def _publish_without_overwrite(temporary: Path, destination: Path) -> None:
    try:
        os.link(temporary, destination)
    except FileExistsError:
        raise
    finally:
        temporary.unlink(missing_ok=True)


def backup_checkpoint(source: Path, destination: Path) -> CheckpointManifest:
    """Create a transaction-consistent SQLite backup without overwriting."""

    source = source.expanduser().resolve()
    destination = destination.expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if destination.exists():
        raise FileExistsError(destination)
    if not destination.parent.is_dir():
        raise FileNotFoundError(destination.parent)
    handle, raw_temporary = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    os.close(handle)
    temporary = Path(raw_temporary)
    try:
        source_uri = source.as_uri() + "?mode=ro"
        with (
            sqlite3.connect(source_uri, uri=True) as current,
            sqlite3.connect(temporary) as backup,
        ):
            current.backup(backup)
        _quick_check(temporary)
        _publish_without_overwrite(temporary, destination)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    return _manifest(destination)


def verify_checkpoint(
    backup: Path,
    *,
    expected_sha256: str | None = None,
) -> CheckpointManifest:
    """Verify digest and SQLite integrity for one checkpoint backup."""

    backup = backup.expanduser().resolve()
    if not backup.is_file():
        raise FileNotFoundError(backup)
    manifest = _manifest(backup)
    if expected_sha256 is not None and manifest.sha256 != expected_sha256.lower():
        raise ValueError("checkpoint backup digest mismatch")
    _quick_check(backup)
    return manifest


def restore_checkpoint(
    backup: Path,
    destination: Path,
    *,
    expected_sha256: str,
) -> CheckpointManifest:
    """Restore a verified byte-identical backup to a new path only."""

    source = verify_checkpoint(backup, expected_sha256=expected_sha256).path
    destination = destination.expanduser().resolve()
    if destination.exists():
        raise FileExistsError(destination)
    if not destination.parent.is_dir():
        raise FileNotFoundError(destination.parent)
    handle, raw_temporary = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    temporary = Path(raw_temporary)
    try:
        with source.open("rb") as source_stream, os.fdopen(handle, "wb") as target:
            for block in iter(lambda: source_stream.read(1024 * 1024), b""):
                target.write(block)
            target.flush()
            os.fsync(target.fileno())
        verify_checkpoint(temporary, expected_sha256=expected_sha256)
        _publish_without_overwrite(temporary, destination)
    except BaseException:
        with suppress(OSError):
            os.close(handle)
        temporary.unlink(missing_ok=True)
        raise
    return _manifest(destination)


@dataclass(frozen=True, slots=True)
class ComponentHealth:
    name: str
    state: str
    detail_code: str


@dataclass(frozen=True, slots=True)
class HealthSnapshot:
    state: str
    ready: bool
    checked_at: str
    components: tuple[ComponentHealth, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "state": self.state,
            "ready": self.ready,
            "checked_at": self.checked_at,
            "components": [
                {
                    "name": component.name,
                    "state": component.state,
                    "detail_code": component.detail_code,
                }
                for component in self.components
            ],
        }


def probe_components(probes: Mapping[str, Callable[[], object]]) -> HealthSnapshot:
    """Run named probes while exposing only state codes, never exception text."""

    components: list[ComponentHealth] = []
    for name in sorted(probes):
        try:
            probes[name]()
            components.append(ComponentHealth(name, "ready", "ok"))
        except Exception:
            components.append(ComponentHealth(name, "unavailable", "probe_failed"))
    ready = bool(components) and all(item.state == "ready" for item in components)
    return HealthSnapshot(
        state="ready" if ready else "unavailable",
        ready=ready,
        checked_at=datetime.now(UTC).isoformat(),
        components=tuple(components),
    )


__all__ = [
    "CheckpointManifest",
    "ComponentHealth",
    "HealthSnapshot",
    "backup_checkpoint",
    "probe_components",
    "restore_checkpoint",
    "verify_checkpoint",
]
