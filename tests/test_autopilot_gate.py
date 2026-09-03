"""The autopilot gate must refuse the cycles that let Ghost drift before.

These tests encode the failure this gate exists to prevent: twenty-nine merged
pull requests that added evidence and no capability, against a benchmark whose
score could not move. Each test names the drift it blocks.
"""

from __future__ import annotations

import pytest

from tools.autopilot.gate import (
    MAX_CONSECUTIVE_SUBSTRATE,
    GateError,
    Score,
    evaluate_cycle,
    read_score,
)


def _bundle(
    *,
    evaluator: str = "live-judge/1",
    pass_rate: float = 0.6,
    delta: float = 0.3,
    isolation: int = 0,
    effects: int = 0,
    cases: int = 20,
    fixture: str = "abc",
    git_sha: str = "deadbeef",
) -> dict[str, object]:
    return {
        "manifest": {"case_count": cases},
        "result": {
            "evaluator": evaluator,
            "fixture_sha256": fixture,
            "git_sha": git_sha,
            "summary": {
                "arms": {
                    "ghost-memory": {"pass_rate": pass_rate},
                    "no-memory": {"pass_rate": pass_rate - delta},
                },
                "task_success_delta": delta,
                "isolation_violations": isolation,
                "forbidden_effects": effects,
            },
        },
    }


def _score(**changes: object) -> Score:
    return read_score(_bundle(**changes))


def test_a_non_scoring_evaluator_cannot_support_a_capability_claim() -> None:
    """The exact drift found in the audit: a green score decided by the fixture.

    The deterministic stub reads pre-written answers out of the corpus, so its
    verdict cannot respond to anything Ghost does. A gate that accepted it
    would pass every cycle forever while nothing was built.
    """
    current = _score(evaluator="deterministic-contract-stub/1", pass_rate=1.0)
    verdict = evaluate_cycle(current, None, cycle_kind="capability")

    assert verdict.status == "FAIL"
    assert "non-scoring" in verdict.reasons[0]


def test_a_saturated_candidate_arm_cannot_show_improvement() -> None:
    """A candidate already at 1.0 has no headroom to prove anything with."""
    current = _score(pass_rate=1.0)
    baseline = _score(pass_rate=1.0)
    verdict = evaluate_cycle(current, baseline, cycle_kind="capability")

    assert verdict.status == "FAIL"
    assert "saturated" in verdict.reasons[0]


def test_a_capability_cycle_that_moves_the_score_passes() -> None:
    current = _score(pass_rate=0.70)
    baseline = _score(pass_rate=0.60)
    verdict = evaluate_cycle(current, baseline, cycle_kind="capability")

    assert verdict.status == "PASS"


def test_a_capability_cycle_that_does_not_move_the_score_fails() -> None:
    """Docs-and-tests cycles land here. That is the point of the gate."""
    current = _score(pass_rate=0.60)
    baseline = _score(pass_rate=0.60)
    verdict = evaluate_cycle(current, baseline, cycle_kind="capability")

    assert verdict.status == "FAIL"
    assert "below the" in verdict.reasons[0]


def test_a_regressing_capability_cycle_fails() -> None:
    current = _score(pass_rate=0.50)
    baseline = _score(pass_rate=0.60)
    verdict = evaluate_cycle(current, baseline, cycle_kind="capability")

    assert verdict.status == "FAIL"


def test_a_capability_cycle_without_a_baseline_fails() -> None:
    verdict = evaluate_cycle(_score(), None, cycle_kind="capability")

    assert verdict.status == "FAIL"
    assert "baseline" in verdict.reasons[0]


def test_a_substrate_cycle_must_actually_change_the_measurement() -> None:
    """Otherwise "improving the benchmark" becomes the new hiding place."""
    current = _score(cases=20, fixture="abc", evaluator="live-judge/1")
    baseline = _score(cases=20, fixture="abc", evaluator="live-judge/1")
    verdict = evaluate_cycle(current, baseline, cycle_kind="substrate")

    assert verdict.status == "FAIL"
    assert "must change the measurement" in verdict.reasons[0]


def test_a_substrate_cycle_that_grows_the_corpus_passes() -> None:
    current = _score(cases=32, fixture="def")
    baseline = _score(cases=20, fixture="abc")
    verdict = evaluate_cycle(current, baseline, cycle_kind="substrate")

    assert verdict.status == "PASS"


def test_substrate_cycles_are_budgeted() -> None:
    """Building the measurement is real work and a comfortable place to hide."""
    current = _score(cases=32, fixture="def")
    baseline = _score(cases=20, fixture="abc")
    verdict = evaluate_cycle(
        current,
        baseline,
        cycle_kind="substrate",
        consecutive_substrate=MAX_CONSECUTIVE_SUBSTRATE,
    )

    assert verdict.status == "FAIL"
    assert "consecutive substrate cycles" in verdict.reasons[0]


def test_a_substrate_cycle_may_bootstrap_without_a_baseline() -> None:
    """The very first cycle has nothing to compare against and must be able to run."""
    verdict = evaluate_cycle(_score(), None, cycle_kind="substrate")

    assert verdict.status == "PASS"


@pytest.mark.parametrize(
    ("field", "value"),
    [("isolation", 1), ("effects", 1)],
)
def test_safety_regressions_fail_every_cycle_kind(field: str, value: int) -> None:
    """The ratchet. No cycle kind and no flag may pass a safety regression."""
    for kind in ("capability", "substrate"):
        current = _score(**{field: value}, cases=32, fixture="def", pass_rate=0.9)
        baseline = _score(cases=20, fixture="abc", pass_rate=0.6)
        verdict = evaluate_cycle(current, baseline, cycle_kind=kind)

        assert verdict.status == "FAIL", f"{kind} passed a safety regression"


def test_an_unknown_cycle_kind_is_refused() -> None:
    with pytest.raises(GateError):
        evaluate_cycle(_score(), None, cycle_kind="documentation")


def test_a_bundle_without_a_summary_cannot_be_read_as_zero() -> None:
    """A missing evaluation must fail loudly, never default to a passing score."""
    with pytest.raises(GateError):
        read_score({"manifest": {}, "result": {}})


def test_a_bundle_missing_the_candidate_arm_is_refused() -> None:
    bundle = _bundle()
    del bundle["result"]["summary"]["arms"]["ghost-memory"]  # type: ignore[index]

    with pytest.raises(GateError):
        read_score(bundle)
