"""Opaque HTTP adapter for Ghost's durable SEAM memory."""

from __future__ import annotations

import json
import math
from collections.abc import Iterable, Mapping, Sequence
from contextlib import AbstractContextManager
from contextvars import ContextVar, Token
from dataclasses import dataclass
from typing import Any, Protocol

import httpx

from .config import GhostSettings, validate_dimension
from .memory_policy import MemoryAdmission

MAX_SEAM_RESPONSE_BYTES = 8 * 1024 * 1024


@dataclass(frozen=True, slots=True)
class SeamTurn:
    """The auditable SEAM state established before an agent turn."""

    run_id: str
    rendered_memory: str
    evidence_refs: tuple[str, ...]
    session_id: str = "default"


class HTTPClient(Protocol):
    """The tiny httpx surface used by ``SeamMemory`` and its contract fakes."""

    def stream(
        self, method: str, url: str, **kwargs: Any
    ) -> AbstractContextManager[Any]: ...

    def close(self) -> None: ...


class SeamTransportError(RuntimeError):
    """The configured SEAM service could not honor the public contract."""


def _record_summary(record: Any) -> str:
    if isinstance(record, Mapping):
        for key in ("text", "memory", "content", "summary", "label"):
            value = record.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()[:1200]
        return json.dumps(dict(record), ensure_ascii=False, sort_keys=True, default=str)[
            :1200
        ]

    attrs = record.attrs if isinstance(getattr(record, "attrs", None), dict) else {}
    for key in ("content", "text", "summary", "label"):
        value = attrs.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()[:1200]

    triple = [attrs.get(key) for key in ("subject", "predicate", "object")]
    if any(value is not None for value in triple):
        return " ".join(str(value) for value in triple if value is not None)[:1200]

    return json.dumps(attrs, ensure_ascii=False, sort_keys=True, default=str)[:1200]


def _validated_score(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SeamTransportError("SEAM memory response has an invalid score")
    score = float(value)
    if not math.isfinite(score):
        raise SeamTransportError("SEAM memory response has an invalid score")
    return score


def render_memories(candidates: Iterable[Any]) -> str:
    """Render selected public memory records as injection-resistant JSON lines."""

    lines: list[str] = []
    for candidate in candidates:
        if isinstance(candidate, Mapping):
            record_id = candidate.get("id") or candidate.get("record_id") or ""
            kind = candidate.get("kind") or "memory"
            score = _validated_score(candidate.get("score", 0.0))
            record = candidate
        else:
            record = candidate.record
            record_id = getattr(record, "id", "")
            kind_value = getattr(record, "kind", "memory")
            kind = getattr(kind_value, "value", str(kind_value))
            score = _validated_score(getattr(candidate, "score", 0.0))
        payload = {
            "record_id": str(record_id),
            "kind": str(kind),
            "score": round(float(score), 6),
            "memory": _record_summary(record),
        }
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        lines.append(encoded.replace("<", "\\u003c").replace(">", "\\u003e"))
    return "\n".join(lines)


class SeamMemory:
    """Own one public SEAM HTTP client for Ghost's process lifetime."""

    def __init__(
        self,
        settings: GhostSettings,
        *,
        client: HTTPClient | None = None,
    ) -> None:
        self.settings = settings
        headers = {"Accept": "application/json"}
        if settings.seam_api_token:
            headers["Authorization"] = f"Bearer {settings.seam_api_token}"
        self._client = client or httpx.Client(
            base_url=settings.seam_base_url.rstrip("/"),
            headers=headers,
            timeout=settings.seam_timeout,
        )
        self._owns_client = client is None
        self._active_session: ContextVar[str | None] = ContextVar(
            "ghost_seam_session", default=None
        )
        self._session_tokens: dict[str, Token[str | None]] = {}

    def _dimensions(self, session_id: str | None = None) -> dict[str, object]:
        resolved_session = session_id or self._active_session.get() or "default"
        dimensions: dict[str, object] = {
            "namespace": self.settings.namespace,
            "scope": self.settings.scope,
            "workspace": self.settings.workspace,
            "project": self.settings.project,
        }
        if self.settings.scope == "thread":
            dimensions["session_id"] = validate_dimension(
                resolved_session, "thread_id"
            )
        return dimensions

    def _post(self, path: str, payload: dict[str, object]) -> dict[str, Any]:
        detail = ""
        try:
            with self._client.stream("POST", path, json=payload) as response:
                chunks: list[bytes] = []
                received = 0
                for chunk in response.iter_bytes():
                    received += len(chunk)
                    if received > MAX_SEAM_RESPONSE_BYTES:
                        raise SeamTransportError(
                            f"SEAM request {path} exceeded the "
                            f"{MAX_SEAM_RESPONSE_BYTES}-byte response limit"
                        )
                    chunks.append(chunk)
                raw = b"".join(chunks)
                if response.is_error:
                    try:
                        candidate = json.loads(raw).get("detail")
                        if isinstance(candidate, str):
                            detail = f": {candidate[:300]}"
                    except (AttributeError, UnicodeDecodeError, ValueError):
                        pass
                    response.raise_for_status()
                body = json.loads(raw)
        except SeamTransportError:
            raise
        except (httpx.HTTPError, ValueError) as exc:
            raise SeamTransportError(f"SEAM request {path} failed{detail}") from exc
        if not isinstance(body, dict):
            raise SeamTransportError(f"SEAM request {path} returned a non-object")
        return body

    def begin_turn(self, user_input: str, *, thread_id: str = "default") -> SeamTurn:
        """Recall relevant evidence while opening its server-side reasoning run."""

        payload = {
            **self._dimensions(thread_id),
            "query": user_input,
            "limit": self.settings.recall_budget,
            "graph_hops": self.settings.graph_hops,
            "agent_id": self.settings.agent_id,
            "model": self.settings.model_name,
            "provider": self.settings.provider,
        }
        body = self._post("/v1/agent/turns/begin", payload)
        turn_id = body.get("turn_id")
        memories = body.get("memories")
        if not isinstance(turn_id, str) or not turn_id:
            raise SeamTransportError("SEAM begin response has no turn_id")
        if not isinstance(memories, list) or not all(
            isinstance(item, dict) for item in memories
        ):
            raise SeamTransportError("SEAM begin response has invalid memories")
        evidence_refs = tuple(
            str(item["id"])
            for item in memories
            if isinstance(item.get("id"), str) and item["id"]
        )
        token = self._active_session.set(thread_id)
        self._session_tokens[turn_id] = token
        return SeamTurn(
            run_id=turn_id,
            rendered_memory=render_memories(memories),
            evidence_refs=evidence_refs,
            session_id=thread_id,
        )

    def record_actions(
        self, turn: SeamTurn, attempts: Sequence[Any]
    ) -> tuple[str, ...]:
        """Record tool decisions and return only the checks that passed."""

        if not attempts:
            return ()
        serialized = [attempt.to_payload() for attempt in attempts]
        body = self._post(
            "/v1/agent/turns/actions",
            {
                **self._dimensions(turn.session_id),
                "turn_id": turn.run_id,
                "attempts": serialized,
            },
        )
        passed = body.get("passed_verification_ids")
        if not isinstance(passed, list) or not all(
            isinstance(item, str) and item for item in passed
        ):
            raise SeamTransportError("SEAM actions response has invalid check ids")
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
        admission: MemoryAdmission | None = None,
    ) -> tuple[str, ...]:
        """Compile a completed turn and finalize its server-side outcome.

        ``thread_id``, client ``turn_id``, and ``verification_ids`` remain in
        the interface for lifecycle compatibility. The service owns the
        authoritative run identity and passed-check set, so callers cannot
        forge either over HTTP.
        """

        del thread_id, turn_id, verification_ids
        try:
            body = self._post(
                "/v1/agent/turns/complete",
                {
                    **self._dimensions(turn.session_id),
                    "turn_id": turn.run_id,
                    "user_input": user_input,
                    "assistant_output": assistant_output,
                    "memory_admission": (
                        admission
                        or MemoryAdmission("admit", "conversation", "legacy_auto")
                    ).to_payload(),
                },
            )
            receipt_id = body.get("receipt_id")
            if body.get("accepted") is not True or not isinstance(receipt_id, str):
                raise SeamTransportError("SEAM completion response was not accepted")
            return (receipt_id,)
        finally:
            self._restore_session(turn)

    def query_knowledge(
        self,
        *,
        query: str,
        limit: int,
        namespace: str | None = None,
        scope: str | None = None,
        view: str = "current",
        thread_id: str | None = None,
    ) -> dict[str, Any]:
        """Read opaque public memories and adapt them to Ghost's tool shape."""

        body = self._post(
            "/v1/memories/recall",
            {
                **self._dimensions(thread_id),
                "query": query,
                "namespace": namespace or self.settings.namespace,
                "scope": scope or self.settings.scope,
                "limit": limit,
                "view": view,
            },
        )
        memories = body.get("memories")
        if not isinstance(memories, list) or not all(
            isinstance(item, dict) for item in memories
        ):
            raise SeamTransportError("SEAM recall response has invalid memories")
        return {
            "nodes": [
                {
                    "id": str(item.get("id") or ""),
                    "kind": "memory",
                    "label": str(item.get("text") or ""),
                    "status": str(item.get("status") or "unknown"),
                    "created_at": item.get("created_at"),
                }
                for item in memories[:limit]
            ]
        }

    def fail_turn(
        self,
        turn: SeamTurn,
        *,
        error: BaseException,
        thread_id: str,
        turn_id: str,
    ) -> None:
        """Reject a failed run without sending exception text or ingesting it."""

        del thread_id, turn_id
        try:
            self._post(
                "/v1/agent/turns/fail",
                {
                    **self._dimensions(turn.session_id),
                    "turn_id": turn.run_id,
                    "error_type": type(error).__name__,
                },
            )
        finally:
            self._restore_session(turn)

    def _restore_session(self, turn: SeamTurn) -> None:
        token = self._session_tokens.pop(turn.run_id, None)
        if token is not None:
            self._active_session.reset(token)

    def remember(self, text: str, *, thread_id: str) -> dict[str, Any]:
        """Explicitly admit one operator-authored memory."""

        return self._post(
            "/v1/memories",
            {**self._dimensions(thread_id), "text": text, "agent_id": self.settings.agent_id},
        )

    def recall(
        self,
        query: str,
        *,
        thread_id: str,
        limit: int | None = None,
        view: str = "current",
    ) -> dict[str, Any]:
        """Recall the current view or the retained historical view."""

        return self._post(
            "/v1/memories/recall",
            {
                **self._dimensions(thread_id),
                "query": query,
                "limit": self.settings.recall_budget if limit is None else limit,
                "view": view,
            },
        )

    def correct(
        self,
        memory_id: str,
        text: str,
        *,
        thread_id: str,
        idempotency_key: str,
    ) -> dict[str, Any]:
        """Replace a memory additively while retaining its historical record."""

        return self._post(
            "/v1/memories/correct",
            {
                **self._dimensions(thread_id),
                "memory_ids": [memory_id],
                "text": text,
                "idempotency_key": idempotency_key,
            },
        )

    def forget(
        self,
        memory_id: str,
        *,
        thread_id: str,
        idempotency_key: str,
    ) -> dict[str, Any]:
        """Soft-delete one opaque memory through SEAM's lifecycle engine."""

        return self._post(
            "/v1/memories/delete",
            {
                **self._dimensions(thread_id),
                "memory_ids": [memory_id],
                "idempotency_key": idempotency_key,
            },
        )

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> SeamMemory:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()


__all__ = [
    "MAX_SEAM_RESPONSE_BYTES",
    "SeamMemory",
    "SeamTransportError",
    "SeamTurn",
    "render_memories",
]
