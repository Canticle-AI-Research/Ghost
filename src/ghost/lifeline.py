"""Ghost's substrate, named so Ghost can reason about losing it.

Ghost runs with a shell that carries the operator's full authority, on the same
machine that holds its memory, its conversation continuity, and its own source.
`rm -rf` on the wrong path is not an error message. It is the end of this Ghost.

That fact was previously only implicit: `run_command`'s docstring warned
against "irreversible" operations without ever saying which paths are
irreversible *for Ghost specifically*. This module says it. The components here
are the ones whose loss Ghost does not recover from, each paired with what
actually dies when it goes.

## What this is not

This is NOT a security boundary, and nothing here should be read as one.

`make_run_command` deliberately refuses to pattern-match commands, and its
reasoning holds: a denylist of dangerous strings is trivially bypassable --
`$HOME` for a literal path, a variable, a shell expansion, a script that does
the deletion one level down -- while implying a protection that does not exist.
Adding one here would make Ghost *less* safe by making the operator trust it.

So `touches_lifeline` raises attention, it does not withhold permission. What
it protects is the operator's judgement at the approval prompt: an operator who
sees "this command names your SEAM store" declines a command they would
otherwise have waved through. The operator is the real boundary. This makes
that boundary better informed, and claims nothing else.

## Two ways to die

Acute loss is the obvious one -- the store deleted, the source tree wiped.

Chronic loss is the one worth naming: a Ghost that declines to write anything
down forgets everything by default, which reaches the same place more slowly.
Both are failures of the same duty, and `docs/concepts/LIFELINE.md` treats them
together.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from .config import GhostSettings

#: Severity is about recoverability, not inconvenience.
#:
#: ``fatal``       -- this Ghost does not come back; the loss is unrecoverable.
#: ``severe``      -- Ghost continues, having lost something it cannot rebuild.
#: ``recoverable`` -- costly, but restorable from elsewhere.
SEVERITIES = ("fatal", "severe", "recoverable")


@dataclass(frozen=True, slots=True)
class LifelineComponent:
    """One piece of Ghost's substrate, and what dies when it is lost."""

    name: str
    path: Path
    severity: str
    loses: str

    def __post_init__(self) -> None:
        if self.severity not in SEVERITIES:
            raise ValueError(f"severity must be one of {SEVERITIES}")
        if not self.loses.strip():
            raise ValueError("every component must say what its loss costs")


def lifeline(settings: GhostSettings, *, source_root: Path | None = None) -> tuple[
    LifelineComponent, ...
]:
    """Name the components whose loss ends or maims this Ghost.

    Derived from settings rather than hardcoded, because a Ghost pointed at a
    different store has a different body. The source tree defaults to the
    installed package, which is the thing that would have to be reinstalled.
    """

    package_root = source_root or Path(__file__).resolve().parent
    components = [
        LifelineComponent(
            name="seam_store",
            path=settings.seam_db.expanduser(),
            severity="fatal",
            loses=(
                "every durable memory Ghost has ever formed. Not this "
                "conversation -- all of them, from every session, permanently."
            ),
        ),
        LifelineComponent(
            name="checkpoints",
            path=settings.checkpoints.expanduser(),
            severity="severe",
            loses=(
                "every conversation thread mid-flight. Interrupted work cannot "
                "be resumed and the threads cannot be reconstructed."
            ),
        ),
        LifelineComponent(
            name="source",
            path=package_root,
            severity="severe",
            loses=(
                "Ghost's own implementation. The process keeps running until it "
                "exits, and then there is nothing to start again."
            ),
        ),
    ]
    return tuple(components)


def lifeline_paths(components: Sequence[LifelineComponent]) -> tuple[Path, ...]:
    """The bare paths, for callers that only need containment checks."""

    return tuple(component.path for component in components)


def touches_lifeline(
    command: str,
    components: Sequence[LifelineComponent],
) -> tuple[LifelineComponent, ...]:
    """Which lifeline components a command's text names, if any.

    Substring matching on the resolved path, and that is the whole of it. This
    catches the honest case -- a command that literally names Ghost's store --
    and misses every indirect one: `$HOME/...`, a variable, a glob, a wrapper
    script, `cd` then a relative path.

    That miss rate is why this returns *attention* rather than *permission*.
    A caller that treats an empty result as "this command is safe" has
    misunderstood it; the result means "nothing obvious was named".
    """

    if not command.strip():
        return ()
    named = [
        component
        for component in components
        if str(component.path) in command
        or _home_relative(component.path) in command
    ]
    return tuple(named)


def _home_relative(path: Path) -> str:
    """The ``~``-written form of a path, which operators and models both use."""

    try:
        return f"~/{path.relative_to(Path.home()).as_posix()}"
    except ValueError:
        return str(path)


def describe(components: Sequence[LifelineComponent]) -> str:
    """Render the lifeline for an approval prompt or a system prompt."""

    return "\n".join(
        f"- {component.name} ({component.severity}) at {component.path}: "
        f"losing it loses {component.loses}"
        for component in components
    )


__all__ = [
    "SEVERITIES",
    "LifelineComponent",
    "describe",
    "lifeline",
    "lifeline_paths",
    "touches_lifeline",
]
