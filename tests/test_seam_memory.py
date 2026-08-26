from __future__ import annotations

from pathlib import Path

import httpx
import pytest

from ghost.config import GhostSettings
from ghost.lifecycle import ToolAttempt
from ghost.memory_policy import MemoryAdmission
from ghost.seam_memory import MAX_SEAM_RESPONSE_BYTES, SeamMemory, SeamTransportError


def _settings() -> GhostSettings:
    return GhostSettings(
        model="openai:test-model",
        seam_db=Path("unused.db"),
        namespace="ghost.test",
        scope="thread",
        recall_budget=8,
        graph_hops=1,
    )


def test_public_api_compiles_and_recalls_memory(seam_http) -> None:
    with SeamMemory(_settings(), client=seam_http) as memory:
        first = memory.begin_turn("What color does the user prefer?", thread_id="thread-a")
        assert first.rendered_memory == ""
        assert first.evidence_refs == ()

        stored = memory.complete_turn(
            first,
            user_input="Remember that my preferred color is ultramarine.",
            assistant_output="I will remember that you prefer ultramarine.",
            thread_id="thread-a",
            turn_id="turn-a",
            admission=MemoryAdmission("admit", "preference", "explicit_remember"),
        )
        recalled = memory.begin_turn(
            "What is the user's preferred color?", thread_id="thread-a"
        )

    assert stored == ("receipt-turn-1",)
    assert recalled.evidence_refs == ("memory-1",)
    assert "ultramarine" in recalled.rendered_memory.lower()
    assert "record_id" in recalled.rendered_memory
    assert not seam_http.closed, "an injected shared client must not be closed"


def test_client_identity_cannot_forge_server_checks_or_receipts(seam_http) -> None:
    with SeamMemory(_settings(), client=seam_http) as memory:
        turn = memory.begin_turn("Do the work", thread_id="forged-thread")
        checks = memory.record_actions(
            turn,
            [ToolAttempt(name="read_file", request="{}", output="ok", ok=True)],
        )
        receipt = memory.complete_turn(
            turn,
            user_input="Do the work",
            assistant_output="Done",
            thread_id="forged-thread",
            turn_id="forged-turn",
            verification_ids=("forged-check",),
            admission=MemoryAdmission("reject", "none", "no_durable_intent"),
        )

    complete_payload = next(
        payload
        for path, payload in seam_http.calls
        if path == "/v1/agent/turns/complete"
    )
    assert checks == ("verify-0",)
    assert receipt == ("receipt-turn-1",)
    assert "verification_ids" not in complete_payload
    assert "thread_id" not in complete_payload
    assert complete_payload["turn_id"] == "turn-1"


def test_failure_sends_only_exception_class_not_sensitive_text(seam_http) -> None:
    with SeamMemory(_settings(), client=seam_http) as memory:
        turn = memory.begin_turn("fail safely", thread_id="thread-a")
        memory.fail_turn(
            turn,
            error=RuntimeError("secret provider response"),
            thread_id="thread-a",
            turn_id="turn-a",
        )

    path, payload = seam_http.calls[-1]
    assert path == "/v1/agent/turns/fail"
    assert payload["error_type"] == "RuntimeError"
    assert "secret provider response" not in str(payload)


def test_malformed_public_memory_score_fails_closed(seam_http) -> None:
    seam_http.memories.append(
        {
            "id": "memory-1",
            "text": "hello",
            "score": None,
            "_dimensions": (
                "ghost.test",
                "thread",
                "default",
                "default",
                "thread-a",
            ),
        }
    )
    with SeamMemory(_settings(), client=seam_http) as memory, pytest.raises(
        SeamTransportError, match="invalid score"
    ):
        memory.begin_turn("hello", thread_id="thread-a")


def test_http_failures_are_redacted_and_wrapped() -> None:
    def fail(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            500,
            request=request,
            json={"detail": "bounded public error"},
        )

    client = httpx.Client(transport=httpx.MockTransport(fail), base_url="http://seam.test")
    try:
        with SeamMemory(_settings(), client=client) as memory, pytest.raises(
            SeamTransportError,
            match="SEAM request /v1/agent/turns/begin failed: bounded public error",
        ):
            memory.begin_turn("hello", thread_id="thread-a")
    finally:
        client.close()


def test_failed_completion_restores_the_previous_thread_context(
    seam_http, monkeypatch
) -> None:
    original_response = seam_http._response

    def fail_completion(path, payload):
        if path == "/v1/agent/turns/complete":
            request = httpx.Request("POST", f"http://seam.test{path}")
            return httpx.Response(
                500, request=request, json={"detail": "completion failed"}
            )
        return original_response(path, payload)

    monkeypatch.setattr(seam_http, "_response", fail_completion)
    with SeamMemory(_settings(), client=seam_http) as memory:
        turn = memory.begin_turn("hello", thread_id="failed-thread")
        with pytest.raises(SeamTransportError, match="completion failed"):
            memory.complete_turn(
                turn,
                user_input="hello",
                assistant_output="answer",
                thread_id="failed-thread",
                turn_id="client-turn",
            )
        memory.query_knowledge(query="probe", limit=1)

    recall_payload = seam_http.calls[-1][1]
    assert recall_payload["session_id"] == "default"


def test_chunked_response_without_content_length_is_bounded() -> None:
    class OversizedStream(httpx.SyncByteStream):
        def __iter__(self):
            chunk = b"x" * (1024 * 1024)
            for _index in range(9):
                yield chunk

    def oversized(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, stream=OversizedStream())

    client = httpx.Client(
        transport=httpx.MockTransport(oversized), base_url="http://seam.test"
    )
    try:
        with SeamMemory(_settings(), client=client) as memory, pytest.raises(
            SeamTransportError,
            match=f"exceeded the {MAX_SEAM_RESPONSE_BYTES}-byte response limit",
        ):
            memory.begin_turn("hello")
    finally:
        client.close()


def test_owned_client_uses_configured_bearer_token(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class CapturingClient:
        def __init__(self, **kwargs: object) -> None:
            captured.update(kwargs)

        def stream(self, method: str, url: str, **kwargs: object) -> object:
            raise AssertionError("no request expected")

        def close(self) -> None:
            captured["closed"] = True

    monkeypatch.setattr("ghost.seam_memory.httpx.Client", CapturingClient)
    token_value = "".join(("test", "-token"))
    settings = GhostSettings(
        model="openai:test-model",
        seam_db=Path("unused.db"),
        namespace="ghost.test",
        scope="thread",
        seam_base_url="https://seam.example/v1/..",
        seam_api_token=token_value,
        seam_timeout=12.5,
    )
    memory = SeamMemory(settings)
    memory.close()

    assert captured["base_url"] == "https://seam.example/v1/.."
    assert captured["headers"] == {
        "Accept": "application/json",
        "Authorization": "Bearer test-token",
    }
    assert captured["timeout"] == 12.5
    assert captured["closed"] is True


def test_thread_scope_is_forwarded_and_prevents_cross_thread_recall(seam_http) -> None:
    with SeamMemory(_settings(), client=seam_http) as memory:
        turn = memory.begin_turn("seed", thread_id="thread-a")
        memory.complete_turn(
            turn,
            user_input="Remember the thread marker is amber.",
            assistant_output="Remembered.",
            thread_id="thread-a",
            turn_id="turn-a",
            admission=MemoryAdmission("admit", "event", "explicit_remember"),
        )
        own = memory.recall("amber", thread_id="thread-a")
        crossed = memory.recall("amber", thread_id="thread-b")

    assert own["memories"]
    assert crossed["memories"] == []
    for _path, payload in seam_http.calls:
        assert payload["workspace"] == "default"
        assert payload["project"] == "default"
        assert payload["session_id"] in {"thread-a", "thread-b"}


def test_explicit_zero_recall_limit_is_not_replaced_by_the_default(seam_http) -> None:
    with SeamMemory(_settings(), client=seam_http) as memory:
        memory.recall("probe", thread_id="thread-a", limit=0)

    assert seam_http.calls[-1][1]["limit"] == 0


@pytest.mark.parametrize("thread_id", ["bad/thread", "-leading", "has space"])
def test_invalid_thread_id_fails_before_an_http_request(seam_http, thread_id) -> None:
    with SeamMemory(_settings(), client=seam_http) as memory, pytest.raises(ValueError):
        memory.begin_turn("hello", thread_id=thread_id)
    assert seam_http.calls == []


def test_explicit_memory_operations_preserve_current_and_history_views(seam_http) -> None:
    with SeamMemory(_settings(), client=seam_http) as memory:
        remembered = memory.remember(
            "The release captain is Alice.", thread_id="operations"
        )
        assert remembered["accepted"] is True
        original = memory.recall("release captain", thread_id="operations")
        memory_id = original["memories"][0]["id"]

        corrected = memory.correct(
            memory_id,
            "The release captain is Bob.",
            thread_id="operations",
            idempotency_key="release-captain-correction",
        )
        assert corrected["accepted"] is True
        current = memory.recall("release captain", thread_id="operations")
        history = memory.recall(
            "release captain", thread_id="operations", view="history"
        )
        assert [item["text"] for item in current["memories"]] == [
            "The release captain is Bob."
        ]
        assert {item["status"] for item in history["memories"]} == {
            "asserted",
            "deleted_soft",
        }

        replacement_id = current["memories"][0]["id"]
        forgotten = memory.forget(
            replacement_id,
            thread_id="operations",
            idempotency_key="release-captain-forget",
        )
        assert forgotten["status"] == "deleted"
        assert memory.recall("release captain", thread_id="operations")[
            "memories"
        ] == []


def test_recall_tool_exposes_opaque_status_and_timestamp(seam_http) -> None:
    with SeamMemory(_settings(), client=seam_http) as memory:
        memory.remember("Provenance marker.", thread_id="provenance")
        graph = memory.query_knowledge(
            query="marker", limit=3, thread_id="provenance"
        )
    assert graph["nodes"][0] == {
        "id": "memory-1",
        "kind": "memory",
        "label": "Provenance marker.",
        "status": "asserted",
        "created_at": "2026-08-25T00:00:00+00:00",
    }
