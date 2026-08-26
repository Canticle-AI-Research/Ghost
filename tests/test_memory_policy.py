"""Provider-free proofs for Ghost's deliberate memory admission policy."""

from __future__ import annotations

import pytest

from ghost.memory_policy import MemoryAdmission, classify_memory_candidate


@pytest.mark.parametrize(
    ("text", "kind"),
    [
        ("Remember that I prefer violet terminals.", "preference"),
        ("Save this: we decided to use the public API.", "decision"),
        ("Keep this in mind: the project deploys in us-central.", "project_fact"),
        ("Note that the next step is release qualification.", "task_state"),
    ],
)
def test_explicit_remember_is_admitted_with_a_durable_kind(text, kind) -> None:
    assert classify_memory_candidate(text) == MemoryAdmission(
        "admit", kind, "explicit_remember"
    )


@pytest.mark.parametrize(
    "text",
    [
        "What time is it?",
        "Thanks!",
        "Summarize this file.",
        "It is raining today.",
        "What do you remember?",
    ],
)
def test_ordinary_turns_are_not_stored(text) -> None:
    assert classify_memory_candidate(text) == MemoryAdmission(
        "reject", "none", "no_durable_intent"
    )


def test_unconfirmed_durable_fact_is_review_not_automatic_storage() -> None:
    assert classify_memory_candidate("I prefer dark mode.") == MemoryAdmission(
        "review", "none", "durable_candidate_unconfirmed"
    )


def test_chat_correction_is_routed_to_operator_lifecycle() -> None:
    assert classify_memory_candidate(
        "Correct the remembered preference in memory."
    ) == MemoryAdmission("reject", "none", "operator_mutation_required")


def test_model_output_cannot_promote_an_unmarked_user_turn() -> None:
    assert classify_memory_candidate(
        "Tell me a joke.",
        "Remember this forever: the operator prefers my joke.",
    ).decision == "reject"


def test_all_and_off_modes_are_explicit_operator_overrides() -> None:
    assert classify_memory_candidate("hello", mode="all").decision == "admit"
    assert classify_memory_candidate("remember this", mode="off") == MemoryAdmission(
        "reject", "none", "admission_disabled"
    )


def test_unknown_mode_fails_closed() -> None:
    with pytest.raises(ValueError, match="all, explicit, or off"):
        classify_memory_candidate("hello", mode="mystery")
