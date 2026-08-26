from __future__ import annotations

import json

from ghost.specialists import (
    DelegationEnvelope,
    SpecialistBudget,
    SpecialistCancelled,
    SpecialistEvidence,
    SpecialistOutcome,
    SpecialistScope,
    execute_delegation,
)


def _envelope() -> DelegationEnvelope:
    return DelegationEnvelope(
        delegation_id="dlg-001",
        parent_turn_id="turn-001",
        role="verifier",
        objective="Verify the named evidence bundle.",
        budget=SpecialistBudget(max_steps=8, timeout_seconds=30, max_output_chars=200),
        scope=SpecialistScope(
            tools=frozenset({"seam_recall"}),
            roots=("/workspace/reports",),
            namespace="ghost.default",
            workspace="acme",
            project="launch",
        ),
    )


def test_delegation_preserves_explicit_scope_budget_and_provenance() -> None:
    envelope = _envelope()
    events = []

    def runner(received: DelegationEnvelope) -> SpecialistOutcome:
        assert received is envelope
        return SpecialistOutcome(
            status="succeeded",
            summary="Bundle verified.",
            steps_used=3,
            evidence=(SpecialistEvidence("bundle:sha256:abc", "artifact"),),
            error_type="adapter-controlled-value",
        )

    outcome = execute_delegation(envelope, runner, observe=events.append)

    assert outcome.status == "succeeded"
    assert outcome.error_type is None
    assert outcome.evidence[0].ref == "bundle:sha256:abc"
    assert [event.kind for event in events] == ["specialist.started", "specialist.finished"]
    assert events[-1].attributes == {"status": "succeeded", "steps_used": 3}


def test_delegation_fails_closed_when_runner_exceeds_budget() -> None:
    envelope = _envelope()

    def runner(_received: DelegationEnvelope) -> SpecialistOutcome:
        return SpecialistOutcome(status="succeeded", summary="x", steps_used=9)

    outcome = execute_delegation(envelope, runner)

    assert outcome.status == "failed"
    assert outcome.error_type == "BudgetExceeded"
    assert outcome.summary == "specialist outcome rejected"


def test_failure_and_cancellation_do_not_expose_exception_text() -> None:
    secret = "provider-token-that-must-not-escape"
    events = []

    def failed(_received: DelegationEnvelope) -> SpecialistOutcome:
        raise RuntimeError(secret)

    failed_outcome = execute_delegation(_envelope(), failed, observe=events.append)
    assert failed_outcome.status == "failed"
    assert failed_outcome.error_type == "RunnerError"
    assert secret not in repr(failed_outcome)

    def cancelled(_received: DelegationEnvelope) -> SpecialistOutcome:
        raise SpecialistCancelled(secret)

    cancelled_outcome = execute_delegation(_envelope(), cancelled, observe=events.append)
    assert cancelled_outcome.status == "cancelled"
    assert cancelled_outcome.error_type == "SpecialistCancelled"
    assert secret not in repr(cancelled_outcome)

    def reported_failure(_received: DelegationEnvelope) -> SpecialistOutcome:
        return SpecialistOutcome(status="failed", summary=secret, error_type=secret)

    reported = execute_delegation(_envelope(), reported_failure, observe=events.append)
    assert reported.summary == "specialist outcome rejected"
    assert reported.error_type == "SpecialistFailed"
    assert secret not in repr(reported)
    rendered_events = json.dumps(
        [{"kind": event.kind, "attributes": event.attributes} for event in events],
        sort_keys=True,
    )
    assert secret not in rendered_events


def test_observability_failure_never_changes_specialist_outcome() -> None:
    def broken_observer(_event) -> None:
        raise RuntimeError("telemetry backend unavailable")

    outcome = execute_delegation(
        _envelope(),
        lambda _envelope: SpecialistOutcome(status="succeeded", summary="ok"),
        observe=broken_observer,
    )
    assert outcome.status == "succeeded"


def test_scope_rejects_implicit_authority_and_traversal() -> None:
    for kwargs in (
        {"tools": frozenset({"run_command", ""})},
        {"roots": ("relative/path",)},
        {"roots": ("/workspace/../private",)},
    ):
        try:
            SpecialistScope(**kwargs)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid specialist authority should be rejected")


def test_budget_rejects_unbounded_values() -> None:
    for kwargs in (
        {"max_steps": 0},
        {"timeout_seconds": 0},
        {"max_output_chars": 0},
    ):
        try:
            SpecialistBudget(**kwargs)
        except ValueError:
            pass
        else:
            raise AssertionError("unbounded specialist budget should be rejected")
