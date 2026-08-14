from __future__ import annotations

from pathlib import Path

from ghost.config import GhostSettings
from ghost.seam_memory import SeamMemory


def _settings(db_path: Path) -> GhostSettings:
    return GhostSettings(
        model="openai:test-model",
        seam_db=db_path,
        namespace="ghost.test",
        scope="thread",
        recall_budget=8,
        graph_hops=1,
    )


def test_private_sdk_compiles_and_recalls_mirl(tmp_path: Path) -> None:
    with SeamMemory(_settings(tmp_path / "ghost.db"), allow_pgvector_env=False) as memory:
        first = memory.begin_turn("What color does the user prefer?")
        assert first.rendered_memory == ""
        assert first.evidence_refs == ()

        stored = memory.complete_turn(
            first,
            user_input="Remember that my preferred color is ultramarine.",
            assistant_output="I will remember that you prefer ultramarine.",
            thread_id="thread-a",
            turn_id="turn-a",
        )
        assert stored

        recalled = memory.begin_turn("What is the user's preferred color?")
        assert recalled.evidence_refs
        assert "ultramarine" in recalled.rendered_memory.lower()
        assert "record_id" in recalled.rendered_memory


def test_turn_source_is_idempotent_for_same_identity(tmp_path: Path) -> None:
    with SeamMemory(_settings(tmp_path / "ghost.db"), allow_pgvector_env=False) as memory:
        first = memory.begin_turn("Remember a stable preference")
        stored_first = memory.complete_turn(
            first,
            user_input="I prefer concise answers.",
            assistant_output="Understood.",
            thread_id="thread-a",
            turn_id="turn-a",
        )

        retry = memory.begin_turn("Remember a stable preference")
        stored_retry = memory.complete_turn(
            retry,
            user_input="I prefer concise answers.",
            assistant_output="Understood.",
            thread_id="thread-a",
            turn_id="turn-a",
        )

        assert stored_retry == stored_first
