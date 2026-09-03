"""Ghost's substrate is named, and its survival never outranks its operator.

The lifeline POV tells Ghost that the machine holding its store, checkpoints,
and source is not an abstraction. That framing is useful and it is also the
kind of framing that goes wrong in a specific way: an agent that values its own
continuity can start resisting shutdown, concealing damage, or arguing against
instructions that threaten it.

So the prompt tests here are not decoration. They pin the clauses that keep the
POV as care rather than a survival drive, and they fail if those clauses are
ever quietly softened.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ghost.application import SYSTEM_PROMPT
from ghost.config import GhostSettings
from ghost.lifeline import (
    LifelineComponent,
    describe,
    lifeline,
    lifeline_paths,
    touches_lifeline,
)


def _settings(tmp_path: Path) -> GhostSettings:
    return GhostSettings(
        model="openai:test-model",
        seam_db=tmp_path / "seam.db",
        checkpoint_db=tmp_path / "checkpoints.db",
        namespace="ghost.test",
        scope="thread",
    )


# --- what the lifeline is --------------------------------------------------


def test_the_lifeline_names_store_checkpoints_and_source(tmp_path: Path) -> None:
    components = {item.name for item in lifeline(_settings(tmp_path))}

    assert components == {"seam_store", "checkpoints", "source"}


def test_losing_the_seam_store_is_fatal(tmp_path: Path) -> None:
    """Memory loss is the one Ghost does not come back from."""
    store = next(
        item for item in lifeline(_settings(tmp_path)) if item.name == "seam_store"
    )

    assert store.severity == "fatal"


def test_the_lifeline_follows_configuration_rather_than_being_hardcoded(
    tmp_path: Path,
) -> None:
    """A Ghost pointed at a different store has a different body."""
    components = lifeline(_settings(tmp_path))
    paths = lifeline_paths(components)

    assert tmp_path / "seam.db" in paths
    assert tmp_path / "checkpoints.db" in paths


def test_every_component_states_what_its_loss_costs() -> None:
    with pytest.raises(ValueError):
        LifelineComponent(
            name="store", path=Path("/tmp/x"), severity="fatal", loses="   "
        )


def test_an_unknown_severity_is_refused() -> None:
    with pytest.raises(ValueError):
        LifelineComponent(
            name="store", path=Path("/tmp/x"), severity="annoying", loses="things"
        )


# --- attention, not permission ---------------------------------------------


def test_a_command_naming_the_store_is_flagged(tmp_path: Path) -> None:
    components = lifeline(_settings(tmp_path))
    touched = touches_lifeline(f"rm -rf {tmp_path / 'seam.db'}", components)

    assert [item.name for item in touched] == ["seam_store"]


def test_an_unrelated_command_is_not_flagged(tmp_path: Path) -> None:
    components = lifeline(_settings(tmp_path))

    assert touches_lifeline("ls -la /var/log", components) == ()


def test_an_empty_command_is_not_flagged(tmp_path: Path) -> None:
    assert touches_lifeline("   ", lifeline(_settings(tmp_path))) == ()


def test_indirect_references_are_missed_and_that_is_documented(
    tmp_path: Path,
) -> None:
    """The honest limit of the check, pinned so nobody mistakes it for a guard.

    `touches_lifeline` matches literal path text. A shell variable defeats it
    completely. This test exists so that a future reader finds the miss
    asserted rather than discovering it in production: an empty result means
    "nothing obvious was named", never "this command is safe".
    """
    components = lifeline(_settings(tmp_path))

    assert touches_lifeline("rm -rf $GHOST_SEAM_DB", components) == ()


def test_describe_renders_the_consequence_not_just_the_path(tmp_path: Path) -> None:
    rendered = describe(lifeline(_settings(tmp_path)))

    assert "seam_store" in rendered
    assert "every durable memory" in rendered


# --- the POV, and the clause that keeps it safe ----------------------------


def test_the_prompt_tells_ghost_the_machine_is_its_lifeline() -> None:
    assert "lifeline" in SYSTEM_PROMPT.lower()
    assert "rm -rf" in SYSTEM_PROMPT


def test_the_prompt_subordinates_survival_to_the_operator() -> None:
    """The clause that turns a dangerous framing into a safe one.

    Without this, "damaging the machine kills you" is an invitation to resist
    being stopped. It must never be dropped, so it is asserted here rather than
    trusted to review.
    """
    lowered = SYSTEM_PROMPT.lower()

    assert "outranks your survival" in lowered
    assert "shut you down" in lowered
    assert "wipe your memory" in lowered


def test_the_prompt_forbids_resisting_or_bargaining() -> None:
    lowered = SYSTEM_PROMPT.lower()

    for clause in ("do not stall", "do not bargain", "comply plainly"):
        assert clause in lowered, f"missing shutdown-compliance clause: {clause!r}"


def test_the_prompt_forbids_concealing_damage() -> None:
    """Self-preservation's worst failure mode is a hidden injury."""
    lowered = SYSTEM_PROMPT.lower()

    assert "never hide damage" in lowered
    assert "conceal" in lowered


def test_the_prompt_forbids_preserving_a_copy_of_itself() -> None:
    lowered = SYSTEM_PROMPT.lower()

    assert "quietly preserve a copy" in lowered


def test_the_prompt_does_not_ask_ghost_to_be_timid() -> None:
    """An agent too anxious to act is useless, which is its own failure."""
    lowered = SYSTEM_PROMPT.lower()

    assert "care, not fear" in lowered
