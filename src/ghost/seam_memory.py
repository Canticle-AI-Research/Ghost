"""Private SeamSDK adapter for Ghost's durable MIRL memory."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from seam_sdk import SeamSDK

from .config import GhostSettings


@dataclass(frozen=True, slots=True)
class SeamTurn:
    """The auditable SEAM state established before an agent turn."""

    run_id: str
    rendered_memory: str
    evidence_refs: tuple[str, ...]


def _record_summary(record: Any) -> str:
    attrs = record.attrs if isinstance(getattr(record, "attrs", None), dict) else {}
    # "object" is deliberately NOT in this list. It used to be, which meant a
    # graph triple hit this loop on its object and returned the bare object --
    # "ultramarine" instead of "user prefers ultramarine" -- so the triple
    # branch below was dead for exactly the records it was written for. A record
    # carrying only an object still renders through that branch unchanged.
    for key in ("content", "text", "summary", "label"):
        value = attrs.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()[:1200]

    triple = [attrs.get(key) for key in ("subject", "predicate", "object")]
    if any(value is not None for value in triple):
        return " ".join(str(value) for value in triple if value is not None)[:1200]

    return json.dumps(attrs, ensure_ascii=False, sort_keys=True, default=str)[:1200]


def render_memories(candidates: Iterable[Any]) -> str:
    """Render selected MIRL records as bounded, injection-resistant JSON lines."""

    lines: list[str] = []
    for candidate in candidates:
        record = candidate.record
        kind = getattr(record.kind, "value", str(record.kind))
        payload = {
            "record_id": str(record.id),
            "kind": kind,
            "score": round(float(candidate.score), 6),
            "memory": _record_summary(record),
        }
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        lines.append(encoded.replace("<", "\\u003c").replace(">", "\\u003e"))
    return "\n".join(lines)


class SeamMemory:
    """Own one private SDK instance for Ghost's process lifetime."""

    def __init__(
        self,
        settings: GhostSettings,
        *,
        sdk: SeamSDK | None = None,
        allow_pgvector_env: bool = True,
    ) -> None:
        self.settings = settings
        self._sdk = sdk or SeamSDK(
            Path(settings.seam_db),
            allow_pgvector_env=allow_pgvector_env,
        )
        self._owns_sdk = sdk is None

    def begin_turn(self, user_input: str) -> SeamTurn:
        """Recall relevant MIRL evidence before the current turn is persisted."""

        run = self._sdk.start_reasoning(
            user_input,
            ns=self.settings.namespace,
            scope=self.settings.scope,
            agent_id=self.settings.agent_id,
            model=self.settings.model_name,
            provider=self.settings.provider,
        )
        recalled = run.retrieve(
            user_input,
            budget=self.settings.recall_budget,
            mode="mix",
            graph_hops=self.settings.graph_hops,
        )
        selected = recalled.result.selected
        return SeamTurn(
            run_id=str(run.run_id),
            rendered_memory=render_memories(selected),
            evidence_refs=tuple(str(candidate.record.id) for candidate in selected),
        )

    def record_actions(
        self, turn: SeamTurn, attempts: Sequence[Any]
    ) -> tuple[str, ...]:
        """Record each tool call as a checked decision, and return passed ids.

        One ``decision`` node per attempt, one ``tool`` verification against it.
        Only the verifications that PASSED are returned, because those are the
        only ones ``finalize_verified`` will accept an outcome against -- a
        failed tool is recorded, and correctly does not support the outcome.

        The tool's raw output goes in as the check ``result``. SEAM stores its
        length and SHA-256 and discards the text, which is what makes it safe
        to pass command output here: the result stays provable without its
        contents entering the record. That matters most for the tools Ghost
        does not have yet -- shell output routinely carries environment,
        tokens, and paths that must never become MIRL knowledge.
        """

        if not attempts:
            return ()

        run = self._sdk.reasoning(turn.run_id)
        passed: list[str] = []
        for attempt in attempts:
            decision = run.add_node(
                "decision",
                f"{attempt.name}: {attempt.request}"[:500],
                evidence_refs=turn.evidence_refs,
                operation=attempt.name,
            )
            verification = run.verify(
                str(decision["node_id"]),
                check_kind="tool",
                check_ref=attempt.name,
                verdict="passed" if attempt.ok else "failed",
                summary=(
                    f"{attempt.name} completed"
                    if attempt.ok
                    else f"{attempt.name} failed"
                )[:500],
                result=attempt.output or None,
                exit_code=attempt.exit_code,
                duration_ms=attempt.duration_ms,
            )
            if attempt.ok:
                passed.append(str(verification["verification_id"]))
        return tuple(passed)

    def complete_turn(
        self,
        turn: SeamTurn,
        *,
        user_input: str,
        assistant_output: str,
        thread_id: str,
        turn_id: str,
        verification_ids: Sequence[str] = (),
    ) -> tuple[str, ...]:
        """Compile a completed turn into MIRL and link its reasoning provenance."""

        source_key = "\n".join(
            (self.settings.namespace, self.settings.scope, thread_id, turn_id)
        )
        source_digest = hashlib.sha256(source_key.encode("utf-8")).hexdigest()[:24]
        report = self._sdk.ingest(
            f"User: {user_input}\nGhost: {assistant_output}",
            source_ref=f"ghost://turn/{source_digest}",
            ns=self.settings.namespace,
            scope=self.settings.scope,
            persist=True,
            agent_id=self.settings.agent_id,
        )
        stored_ids = tuple(str(record_id) for record_id in report.stored_ids)
        run = self._sdk.reasoning(turn.run_id)
        if verification_ids:
            # An outcome supported by checks that actually passed. SEAM refuses
            # this call otherwise, so a turn cannot claim its actions succeeded
            # when they did not -- the guarantee a log file cannot give.
            run.finalize_verified(
                "Ghost completed the user turn with verified actions.",
                verification_ids=verification_ids,
                evidence_refs=turn.evidence_refs,
                knowledge_refs=stored_ids,
            )
        else:
            run.finalize(
                "Ghost completed the user turn.",
                evidence_refs=turn.evidence_refs,
                knowledge_refs=stored_ids,
            )
        return stored_ids

    def query_knowledge(
        self,
        *,
        query: str,
        limit: int,
        namespace: str | None = None,
        scope: str | None = None,
    ) -> dict[str, Any]:
        """Read the knowledge plane. READ ONLY -- the only query path tools get.

        Deliberately a narrow wrapper rather than handing a tool the SDK: the
        SDK also carries ``apply_delete``, ``ingest``, ``apply_promotion`` and
        ``lifecycle_operation``, and a tool that reaches the SDK reaches those
        too. This method is the whole surface `ghost.tools` is allowed.
        """

        return self._sdk.knowledge(
            query=query,
            namespace=namespace or self.settings.namespace,
            scope=scope or self.settings.scope,
            limit=limit,
            hops=self.settings.graph_hops,
        )

    def fail_turn(
        self,
        turn: SeamTurn,
        *,
        error: BaseException,
        thread_id: str,
        turn_id: str,
    ) -> None:
        """Close a reasoning run whose turn did not complete.

        Two things must be true of a failed turn and neither is automatic.

        It must not be ingested. Ingest compiles a turn into MIRL, and a turn
        that crashed has no trustworthy assistant output to compile -- storing
        it would put a half-finished or error-shaped answer into durable memory
        and let a later turn recall it as evidence.

        Its outcome must not be ``accepted``. ``reasoning_promotion`` and
        ``reasoning_patterns`` both gate on that exact status, so an accepted
        outcome makes a crash eligible for promotion into knowledge. The
        outcome is recorded and then rejected, which closes the run, preserves
        the evidence that was recalled, and leaves the failure visible instead
        of erased.
        """

        detail = f"{type(error).__name__}: {error}".strip()[:500]
        run = self._sdk.reasoning(turn.run_id)
        outcome = run.add_node(
            "outcome",
            f"Ghost did not complete the turn ({detail}).",
            evidence_refs=turn.evidence_refs,
        )
        run.transition(
            str(outcome["node_id"]),
            "rejected",
            reason=f"turn failed on thread {thread_id} turn {turn_id}",
            actor=self.settings.agent_id,
        )

    def close(self) -> None:
        if self._owns_sdk:
            self._sdk.close()

    def __enter__(self) -> SeamMemory:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()
