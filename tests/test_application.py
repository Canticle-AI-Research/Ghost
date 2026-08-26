from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ghost import application
from ghost.application import GhostAgent
from ghost.config import GhostSettings
from ghost.context import GhostTurnContext
from ghost.seam_memory import SeamTurn


@dataclass
class FakeMessage:
    content: str


class FakeGraph:
    def __init__(self) -> None:
        self.context: GhostTurnContext | None = None
        self.config: dict[str, Any] | None = None

    def invoke(self, input, *, context, config):
        self.context = context
        self.config = config
        assert input["messages"][-1]["content"] == "What do you remember?"
        return {"messages": [FakeMessage("A grounded answer.")]}


class FakeMemory:
    def __init__(self) -> None:
        self.completed: dict[str, Any] | None = None
        self.closed = False

    def begin_turn(self, user_input: str) -> SeamTurn:
        assert user_input == "What do you remember?"
        return SeamTurn("run-1", '{"record_id":"clm:1"}', ("clm:1",))

    def complete_turn(self, turn: SeamTurn, **kwargs: Any) -> tuple[str, ...]:
        self.completed = {"turn": turn, **kwargs}
        return ("raw:1", "clm:2")

    def close(self) -> None:
        self.closed = True


def test_agent_recall_invoke_and_persist_order() -> None:
    settings = GhostSettings(
        model="openai:test-model",
        seam_db=Path("unused.db"),
        namespace="ghost.test",
        scope="thread",
    )
    memory = FakeMemory()
    graph = FakeGraph()
    ghost = GhostAgent(settings, memory=memory, graph=graph)

    answer = ghost.invoke(
        " What do you remember? ",
        thread_id="thread-7",
        turn_id="turn-9",
    )

    assert answer == "A grounded answer."
    assert graph.context == GhostTurnContext(seam_memory='{"record_id":"clm:1"}')
    assert graph.config == {
        "configurable": {"thread_id": "thread-7"},
        "recursion_limit": 25,
    }
    assert memory.completed is not None
    assert memory.completed["assistant_output"] == answer
    assert memory.completed["thread_id"] == "thread-7"
    assert memory.completed["turn_id"] == "turn-9"


def test_agent_rejects_empty_input_before_recall() -> None:
    settings = GhostSettings(
        model="openai:test-model",
        seam_db=Path("unused.db"),
        namespace="ghost.test",
        scope="thread",
    )
    memory = FakeMemory()
    ghost = GhostAgent(settings, memory=memory, graph=FakeGraph())

    try:
        ghost.invoke("   ")
    except ValueError as exc:
        assert str(exc) == "user input is required"
    else:
        raise AssertionError("empty input should fail")


def test_openai_models_use_responses_api(monkeypatch) -> None:
    captured: dict[str, Any] = {}

    def fake_init(model: str, **kwargs: Any) -> object:
        captured.update(model=model, **kwargs)
        return object()

    monkeypatch.setattr(application, "init_chat_model", fake_init)
    settings = GhostSettings(
        model="openai:gpt-test",
        seam_db=Path("unused.db"),
        namespace="ghost.test",
        scope="thread",
    )

    application._init_model(settings)

    assert captured == {"model": "openai:gpt-test", "use_responses_api": True}
