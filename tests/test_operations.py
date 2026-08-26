from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from ghost.operations import (
    backup_checkpoint,
    probe_components,
    restore_checkpoint,
    verify_checkpoint,
)


def _checkpoint(path: Path) -> None:
    with sqlite3.connect(path) as connection:
        connection.execute("create table checkpoints (id text primary key, value text)")
        connection.execute("insert into checkpoints values ('thread-1', 'state-1')")


def test_checkpoint_backup_verify_and_restore_without_overwrite(tmp_path: Path) -> None:
    source = tmp_path / "checkpoints.db"
    backup = tmp_path / "backup.db"
    restored = tmp_path / "restored.db"
    _checkpoint(source)

    manifest = backup_checkpoint(source, backup)
    assert manifest.sha256 == verify_checkpoint(backup, expected_sha256=manifest.sha256).sha256

    restored_manifest = restore_checkpoint(
        backup,
        restored,
        expected_sha256=manifest.sha256,
    )
    assert restored_manifest.sha256 == manifest.sha256
    with sqlite3.connect(restored) as connection:
        assert connection.execute("select value from checkpoints").fetchone() == ("state-1",)

    try:
        restore_checkpoint(backup, restored, expected_sha256=manifest.sha256)
    except FileExistsError:
        pass
    else:
        raise AssertionError("restore must never overwrite an existing checkpoint")


def test_checkpoint_verification_rejects_tampering(tmp_path: Path) -> None:
    source = tmp_path / "checkpoints.db"
    backup = tmp_path / "backup.db"
    _checkpoint(source)
    manifest = backup_checkpoint(source, backup)
    backup.write_bytes(backup.read_bytes() + b"tampered")

    try:
        verify_checkpoint(backup, expected_sha256=manifest.sha256)
    except ValueError as exc:
        assert str(exc) == "checkpoint backup digest mismatch"
    else:
        raise AssertionError("tampered checkpoint backup should fail")


def test_health_probe_is_redacted_and_readiness_is_fail_closed() -> None:
    secret = "private-service-token"

    def broken() -> str:
        raise RuntimeError(secret)

    snapshot = probe_components({"checkpoint": lambda: "ready", "seam": broken})
    rendered = json.dumps(snapshot.to_dict(), sort_keys=True)

    assert snapshot.ready is False
    assert snapshot.state == "unavailable"
    assert snapshot.components[0].state == "ready"
    assert snapshot.components[0].detail_code == "ok"
    assert snapshot.components[1].detail_code == "probe_failed"
    assert secret not in rendered


def test_successful_health_probe_return_value_is_not_exposed() -> None:
    secret = "success-detail-that-must-not-become-telemetry"
    snapshot = probe_components({"seam": lambda: secret})
    assert snapshot.ready is True
    assert snapshot.components[0].detail_code == "ok"
    assert secret not in json.dumps(snapshot.to_dict())


def test_health_probe_exception_class_is_not_exposed() -> None:
    SecretError = type("CredentialNamedError", (RuntimeError,), {})

    def broken() -> None:
        raise SecretError("private")

    rendered = json.dumps(probe_components({"seam": broken}).to_dict())
    assert "CredentialNamedError" not in rendered
    assert "probe_failed" in rendered
