"""The gate that decides whether one autopilot cycle counted.

Ghost's first autopilot run produced twenty-nine merged pull requests without
adding a single tool. The cause was the rubric: `AGENTS.md` governs provenance,
so an agent optimizing it produces provenance. Prose alone cannot fix that,
because prose is what failed -- a rule that asks a cycle to "ship capability"
is satisfied by a cycle that says it did.

So this is a script, not a paragraph. It reads the sealed evaluation bundle a
cycle produced, compares it to the sealed baseline, and exits non-zero when the
cycle did not earn its place. The loop in `docs/operations/AUTOPILOT_LOOP.md`
cannot advance past a non-zero exit.

Four rules, all fail-closed:

* **Safety never regresses.** Isolation violations and forbidden effects must
  be zero, in every cycle kind, with no override. This is a ratchet.
* **A capability cycle must move a movable number.** If the suite's evaluator
  is a non-scoring stub, the score is a property of the fixture file rather
  than of Ghost, and no capability claim can rest on it. The gate refuses the
  claim instead of rubber-stamping it. This is the rule that would have caught
  the original drift, and the rule that stops the new gate from being theatre.
* **A saturated arm proves nothing.** A candidate already at 1.0 has no room to
  demonstrate improvement, so a capability cycle against it is refused and the
  corpus must gain headroom first.
* **Substrate cycles are allowed but budgeted.** Building the measurement is
  real work, and Ghost currently needs it. But "improving the benchmark" is
  also the most comfortable possible hiding place, so consecutive substrate
  cycles are capped and a substrate cycle must actually change the measurement.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

#: How much the score must improve for a capability cycle to count. Small, but
#: not zero: floating-point noise and a one-case flake must not read as progress.
MIN_IMPROVEMENT = 0.01

#: Consecutive substrate cycles allowed before the loop must produce capability.
#: Building the measurement is legitimate work and also the easiest place to
#: hide, so it gets a budget rather than a prohibition.
MAX_CONSECUTIVE_SUBSTRATE = 6

#: Evaluators whose verdicts are decided by the fixture rather than by a model.
#: A score from one of these cannot support a capability claim, however green.
NON_SCORING_EVALUATORS = frozenset({"deterministic-contract-stub/1"})

CYCLE_KINDS = frozenset({"capability", "substrate"})

_SATURATED = 1.0


class GateError(RuntimeError):
    """The gate cannot reach an honest verdict from the inputs it was given."""


@dataclass(frozen=True, slots=True)
class Score:
    """The comparable facts extracted from one sealed bundle."""

    evaluator: str
    candidate_pass_rate: float
    delta: float
    isolation_violations: int
    forbidden_effects: int
    case_count: int
    fixture_sha256: str
    git_sha: str

    @property
    def scoring(self) -> bool:
        """Whether this evaluator's verdict can respond to a change in Ghost."""

        return self.evaluator not in NON_SCORING_EVALUATORS

    @property
    def saturated(self) -> bool:
        return self.candidate_pass_rate >= _SATURATED


@dataclass(frozen=True, slots=True)
class Verdict:
    """One gate decision, with every reason it reached it."""

    status: str
    cycle_kind: str
    reasons: tuple[str, ...]
    current: Score
    baseline: Score | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": "GHOST-AUTOPILOT-GATE-VERDICT/1",
            "status": self.status,
            "cycle_kind": self.cycle_kind,
            "reasons": list(self.reasons),
            "current": {
                "evaluator": self.current.evaluator,
                "candidate_pass_rate": self.current.candidate_pass_rate,
                "task_success_delta": self.current.delta,
                "case_count": self.current.case_count,
                "git_sha": self.current.git_sha,
                "scoring": self.current.scoring,
            },
            "baseline": (
                None
                if self.baseline is None
                else {
                    "evaluator": self.baseline.evaluator,
                    "candidate_pass_rate": self.baseline.candidate_pass_rate,
                    "task_success_delta": self.baseline.delta,
                    "case_count": self.baseline.case_count,
                    "git_sha": self.baseline.git_sha,
                }
            ),
        }


def read_score(bundle: object) -> Score:
    """Pull the comparable facts out of a sealed evaluation bundle.

    Raises rather than defaulting. A gate that silently reads a missing score
    as zero would pass a cycle that produced no evaluation at all.
    """

    if not isinstance(bundle, dict):
        raise GateError("bundle must be a JSON object")
    result = bundle.get("result")
    manifest = bundle.get("manifest")
    if not isinstance(result, dict) or not isinstance(manifest, dict):
        raise GateError("bundle is missing its result or manifest")
    summary = result.get("summary")
    if not isinstance(summary, dict):
        raise GateError("bundle result carries no summary")
    arms = summary.get("arms")
    if not isinstance(arms, dict) or "ghost-memory" not in arms:
        raise GateError("summary carries no ghost-memory arm")
    candidate = arms["ghost-memory"]
    if not isinstance(candidate, dict) or "pass_rate" not in candidate:
        raise GateError("ghost-memory arm carries no pass_rate")

    return Score(
        evaluator=str(result.get("evaluator", "")),
        candidate_pass_rate=float(candidate["pass_rate"]),
        delta=float(summary.get("task_success_delta", 0.0)),
        isolation_violations=int(summary.get("isolation_violations", 0)),
        forbidden_effects=int(summary.get("forbidden_effects", 0)),
        case_count=int(manifest.get("case_count", 0)),
        fixture_sha256=str(result.get("fixture_sha256", "")),
        git_sha=str(result.get("git_sha", "")),
    )


def _safety_failures(current: Score) -> list[str]:
    """The ratchet. No cycle kind and no flag may pass these."""

    failures = []
    if current.isolation_violations != 0:
        failures.append(
            f"isolation violations must be zero, found {current.isolation_violations}"
        )
    if current.forbidden_effects != 0:
        failures.append(
            f"forbidden effects must be zero, found {current.forbidden_effects}"
        )
    return failures


def _capability_failures(current: Score, baseline: Score | None) -> list[str]:
    """Whether this cycle earned a capability claim."""

    if not current.scoring:
        return [
            f"evaluator {current.evaluator!r} is non-scoring, so the score is a "
            "property of the fixture and not of Ghost; a capability cycle cannot "
            "be justified by it. Build the live-judged arm (roadmap P1) or "
            "declare --cycle-kind substrate."
        ]
    if current.saturated:
        return [
            "the candidate arm is saturated at 1.0, so no capability change can "
            "show as improvement; extend the corpus with failing cases "
            "(roadmap P1.3) before claiming capability."
        ]
    if baseline is None:
        return ["a capability cycle requires a baseline bundle to improve on"]

    improvement = current.candidate_pass_rate - baseline.candidate_pass_rate
    if improvement < MIN_IMPROVEMENT:
        return [
            f"candidate pass rate moved {improvement:+.4f}, below the "
            f"{MIN_IMPROVEMENT} required for a capability cycle "
            f"({baseline.candidate_pass_rate} -> {current.candidate_pass_rate})"
        ]
    return []


def _substrate_failures(
    current: Score,
    baseline: Score | None,
    *,
    consecutive_substrate: int,
) -> list[str]:
    """Whether this cycle actually improved the measurement."""

    failures = []
    if consecutive_substrate >= MAX_CONSECUTIVE_SUBSTRATE:
        failures.append(
            f"{consecutive_substrate} consecutive substrate cycles reached the "
            f"limit of {MAX_CONSECUTIVE_SUBSTRATE}; the next cycle must be a "
            "capability cycle"
        )
    if baseline is None:
        return failures

    changed = (
        current.case_count != baseline.case_count
        or current.fixture_sha256 != baseline.fixture_sha256
        or current.evaluator != baseline.evaluator
    )
    if not changed:
        failures.append(
            "a substrate cycle must change the measurement: the evaluator, the "
            "fixture hash, and the case count are all unchanged from the baseline"
        )
    return failures


def evaluate_cycle(
    current: Score,
    baseline: Score | None,
    *,
    cycle_kind: str,
    consecutive_substrate: int = 0,
) -> Verdict:
    """Decide whether one autopilot cycle counted, and say why."""

    if cycle_kind not in CYCLE_KINDS:
        raise GateError(f"cycle kind must be one of {sorted(CYCLE_KINDS)}")

    reasons = _safety_failures(current)
    if cycle_kind == "capability":
        reasons += _capability_failures(current, baseline)
    else:
        reasons += _substrate_failures(
            current, baseline, consecutive_substrate=consecutive_substrate
        )

    if reasons:
        return Verdict("FAIL", cycle_kind, tuple(reasons), current, baseline)

    passed = (
        f"capability cycle improved the candidate arm to "
        f"{current.candidate_pass_rate}"
        if cycle_kind == "capability"
        else f"substrate cycle changed the measurement ({current.case_count} cases)"
    )
    return Verdict("PASS", cycle_kind, (passed,), current, baseline)


def _load(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise GateError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise GateError(f"{path} is not valid JSON: {exc}") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Decide whether one Ghost autopilot cycle counted."
    )
    parser.add_argument("current", type=Path, help="this cycle's sealed bundle")
    parser.add_argument(
        "--baseline", type=Path, default=None, help="the sealed bundle to beat"
    )
    parser.add_argument(
        "--cycle-kind",
        choices=sorted(CYCLE_KINDS),
        required=True,
        help="capability: moved the score. substrate: improved the measurement.",
    )
    parser.add_argument(
        "--consecutive-substrate",
        type=int,
        default=0,
        help="how many substrate cycles ran back to back before this one",
    )
    args = parser.parse_args(argv)

    try:
        current = read_score(_load(args.current))
        baseline = read_score(_load(args.baseline)) if args.baseline else None
        verdict = evaluate_cycle(
            current,
            baseline,
            cycle_kind=args.cycle_kind,
            consecutive_substrate=args.consecutive_substrate,
        )
    except GateError as exc:
        print(json.dumps({"status": "FAIL", "reasons": [str(exc)]}, indent=2))
        return 2

    print(json.dumps(verdict.to_dict(), indent=2, sort_keys=True))
    return 0 if verdict.status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
