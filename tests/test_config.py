"""Tests for environment-backed settings.

`GhostSettings.from_env` is the only place operator input becomes runtime
behaviour, and the recall bounds are a safety control rather than a preference:
`GHOST_RECALL_BUDGET` sizes how much attacker-influenceable memory text is
pasted into the model prompt each turn, and `GHOST_GRAPH_HOPS` sizes how far a
single record can drag unrelated ones in behind it. A typo that silently
widened either would be a quiet expansion of the injection surface.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ghost.config import GhostSettings


def _clear(monkeypatch) -> None:
    for name in (
        "GHOST_MODEL",
        "GHOST_SEAM_DB",
        "GHOST_SEAM_NAMESPACE",
        "GHOST_SEAM_SCOPE",
        "SEAM_BASE_URL",
        "SEAM_API_TOKEN",
        "GHOST_SEAM_TIMEOUT",
        "GHOST_RECALL_BUDGET",
        "GHOST_GRAPH_HOPS",
    ):
        monkeypatch.delenv(name, raising=False)


def test_defaults_are_operator_local_and_conservative(monkeypatch) -> None:
    _clear(monkeypatch)
    settings = GhostSettings.from_env()

    assert settings.namespace == "ghost.default"
    assert settings.scope == "thread"
    assert settings.recall_budget == 8
    assert settings.graph_hops == 2
    assert settings.agent_id == "ghost"
    assert settings.seam_base_url == "http://127.0.0.1:8765"
    assert settings.seam_api_token is None
    assert settings.seam_timeout == 30.0
    # Default store is per-operator, never a shared unified SEAM store.
    assert settings.seam_db == Path.home() / ".local" / "share" / "ghost" / "seam.db"


def test_environment_overrides_are_honoured(monkeypatch) -> None:
    _clear(monkeypatch)
    monkeypatch.setenv("GHOST_MODEL", "anthropic:claude-opus-5")
    monkeypatch.setenv("GHOST_SEAM_NAMESPACE", "ghost.research")
    monkeypatch.setenv("GHOST_SEAM_SCOPE", "project")
    monkeypatch.setenv("GHOST_RECALL_BUDGET", "16")
    monkeypatch.setenv("GHOST_GRAPH_HOPS", "0")
    monkeypatch.setenv("SEAM_BASE_URL", "https://seam.example/")
    monkeypatch.setenv("SEAM_API_TOKEN", "operator-token")
    monkeypatch.setenv("GHOST_SEAM_TIMEOUT", "12.5")

    settings = GhostSettings.from_env()

    assert settings.model == "anthropic:claude-opus-5"
    assert settings.namespace == "ghost.research"
    assert settings.scope == "project"
    assert settings.recall_budget == 16
    assert settings.graph_hops == 0
    assert settings.seam_base_url == "https://seam.example"
    assert settings.seam_api_token == "operator-token"
    assert settings.seam_timeout == 12.5
    assert "operator-token" not in repr(settings)


def test_seam_db_path_expands_user(monkeypatch) -> None:
    _clear(monkeypatch)
    monkeypatch.setenv("GHOST_SEAM_DB", "~/mirl/ghost.db")
    assert GhostSettings.from_env().seam_db == Path.home() / "mirl" / "ghost.db"


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("GHOST_RECALL_BUDGET", "0"),  # below minimum: recall would return nothing
        ("GHOST_RECALL_BUDGET", "51"),  # above public API maximum
        ("GHOST_GRAPH_HOPS", "-1"),
        ("GHOST_GRAPH_HOPS", "4"),  # above maximum: unbounded graph expansion
        ("GHOST_SEAM_TIMEOUT", "0"),
        ("GHOST_SEAM_TIMEOUT", "301"),
    ],
)
def test_out_of_range_bounds_are_rejected(monkeypatch, name, value) -> None:
    _clear(monkeypatch)
    monkeypatch.setenv(name, value)
    with pytest.raises(ValueError, match="must be between"):
        GhostSettings.from_env()


@pytest.mark.parametrize("name", ["GHOST_RECALL_BUDGET", "GHOST_GRAPH_HOPS"])
def test_non_integer_bounds_are_rejected(monkeypatch, name) -> None:
    """Fail at startup, not with a confusing TypeError deep inside the SDK."""
    _clear(monkeypatch)
    monkeypatch.setenv(name, "lots")
    with pytest.raises(ValueError, match="must be an integer"):
        GhostSettings.from_env()


def test_non_numeric_timeout_is_rejected(monkeypatch) -> None:
    _clear(monkeypatch)
    monkeypatch.setenv("GHOST_SEAM_TIMEOUT", "eventually")
    with pytest.raises(ValueError, match="must be a number"):
        GhostSettings.from_env()


@pytest.mark.parametrize(
    ("model", "provider", "model_name"),
    [
        ("openai:gpt-5.6-terra", "openai", "gpt-5.6-terra"),
        ("anthropic:claude-opus-5", "anthropic", "claude-opus-5"),
        # No separator: the whole string is the model and the provider is unknown,
        # which is what SeamMemory records as provenance on the reasoning run.
        ("gpt-4o", None, "gpt-4o"),
        # Only the FIRST colon splits; model ids may contain their own.
        ("bedrock:us.anthropic.claude:1", "bedrock", "us.anthropic.claude:1"),
    ],
)
def test_provider_and_model_name_split_on_the_first_separator(
    model, provider, model_name
) -> None:
    settings = GhostSettings(
        model=model, seam_db=Path("unused.db"), namespace="ghost.test", scope="thread"
    )
    assert settings.provider == provider
    assert settings.model_name == model_name


def test_settings_are_frozen() -> None:
    """Settings are captured once per process; a mutated namespace mid-run would
    split one agent's memory across two isolation boundaries."""
    settings = GhostSettings(
        model="openai:test", seam_db=Path("unused.db"), namespace="ghost.test", scope="thread"
    )
    with pytest.raises((AttributeError, TypeError)):
        settings.namespace = "ghost.other"  # type: ignore[misc]
