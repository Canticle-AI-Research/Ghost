"""Deterministic admission policy for Ghost's durable SEAM memory.

The policy is intentionally provider-free and inspectable. It decides whether
a completed turn is eligible for durable storage; SEAM remains the only owner
of the resulting memory record and its lifecycle.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

ADMISSION_MODES = frozenset({"all", "explicit", "off"})

_REMEMBER_RE = re.compile(
    r"\b(remember|save this|store this|keep (?:this )?in mind|note that|"
    r"do not forget|don't forget)\b",
    re.IGNORECASE,
)
_RECALL_QUESTION_RE = re.compile(
    r"\b(what|where|when|why|how)\b.{0,80}\bremember\b|\bdo you remember\b",
    re.IGNORECASE,
)
_MUTATION_RE = re.compile(
    r"\b(forget|delete|erase|remove|correct|replace|update)\b.{0,80}\b(memory|remembered|fact|preference|record)\b",
    re.IGNORECASE,
)
_PREFERENCE_RE = re.compile(
    r"\b(i|we)\s+(prefer|like|want|always use|never use)\b|\bmy\s+preferred\b",
    re.IGNORECASE,
)
_DECISION_RE = re.compile(
    r"\b(we decided|decision is|approved direction|chosen approach)\b",
    re.IGNORECASE,
)
_PROCEDURE_RE = re.compile(
    r"\b(always|every time|procedure|workflow|runbook|how we)\b",
    re.IGNORECASE,
)
_TASK_STATE_RE = re.compile(
    r"\b(blocked on|in progress|next step|remaining task|deadline|due date)\b",
    re.IGNORECASE,
)
_PROJECT_RE = re.compile(
    r"\b(project|repository|repo|architecture|service|deployment|release)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class MemoryAdmission:
    """One auditable admission decision sent to SEAM with a completed turn."""

    decision: str
    kind: str
    reason_code: str

    def to_payload(self) -> dict[str, str]:
        return {
            "decision": self.decision,
            "kind": self.kind,
            "reason_code": self.reason_code,
        }


def classify_memory_candidate(
    user_input: str,
    assistant_output: str = "",
    *,
    mode: str = "explicit",
) -> MemoryAdmission:
    """Classify a completed turn without calling a model or reading memory.

    ``assistant_output`` is accepted so future policies can evaluate the whole
    exchange, but the current policy trusts only the operator's input when
    deciding durability. Model-authored text can never promote itself.
    """

    del assistant_output
    if mode not in ADMISSION_MODES:
        raise ValueError("memory admission mode must be all, explicit, or off")
    text = user_input.strip()
    if mode == "off":
        return MemoryAdmission("reject", "none", "admission_disabled")
    if mode == "all":
        return MemoryAdmission("admit", _durable_kind(text), "operator_store_all")
    if _MUTATION_RE.search(text):
        return MemoryAdmission("reject", "none", "operator_mutation_required")
    if _REMEMBER_RE.search(text) and not _RECALL_QUESTION_RE.search(text):
        return MemoryAdmission("admit", _durable_kind(text), "explicit_remember")
    if any(
        pattern.search(text)
        for pattern in (
            _PREFERENCE_RE,
            _DECISION_RE,
            _PROCEDURE_RE,
            _TASK_STATE_RE,
            _PROJECT_RE,
        )
    ):
        return MemoryAdmission("review", "none", "durable_candidate_unconfirmed")
    return MemoryAdmission("reject", "none", "no_durable_intent")


def _durable_kind(text: str) -> str:
    if _PREFERENCE_RE.search(text):
        return "preference"
    if _DECISION_RE.search(text):
        return "decision"
    if _PROCEDURE_RE.search(text):
        return "procedure"
    if _TASK_STATE_RE.search(text):
        return "task_state"
    if _PROJECT_RE.search(text):
        return "project_fact"
    return "event"


__all__ = [
    "ADMISSION_MODES",
    "MemoryAdmission",
    "classify_memory_candidate",
]
