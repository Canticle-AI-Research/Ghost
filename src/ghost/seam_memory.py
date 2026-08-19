"""Private SeamSDK adapter for Ghost's durable MIRL memory."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
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

    def complete_turn(
        self,
        turn: SeamTurn,
        *,
        user_input: str,
        assistant_output: str,
        thread_id: str,
        turn_id: str,
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
        run.finalize(
            "Ghost completed the user turn.",
            evidence_refs=turn.evidence_refs,
            knowledge_refs=stored_ids,
        )
        return stored_ids

    def close(self) -> None:
        if self._owns_sdk:
            self._sdk.close()

    def __enter__(self) -> SeamMemory:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()
