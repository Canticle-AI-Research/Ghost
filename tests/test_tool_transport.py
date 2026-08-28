"""Real LangGraph transport regressions for Ghost's action evidence boundary."""

from __future__ import annotations

import sqlite3
from typing import Any

import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

from ghost.application import ToolEvidenceError, extract_tool_attempts
from ghost.lifecycle import ToolAttempt, run_turn
from ghost.seam_memory import SeamTurn
from ghost.tools import make_run_command


def _command_graph(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("GHOST_ENABLE_SHELL", "1")
    command = make_run_command(timeout=5)

    def model(state: MessagesState) -> dict[str, list[AIMessage]]:
        messages = state["messages"]
        latest_human = max(
            index
            for index, message in enumerate(messages)
            if isinstance(message, HumanMessage)
        )
        current = messages[latest_human:]
        if messages[latest_human].content == "first" and not any(
            isinstance(message, ToolMessage) for message in current
        ):
            return {
                "messages": [
                    AIMessage(
                        content="",
                        tool_calls=[
                            {
                                "id": "command-1",
                                "name": "run_command",
                                "args": {"command": "exit 7"},
                            }
                        ],
                    )
                ]
            }
        return {"messages": [AIMessage(content="done")]}

    def route(state: MessagesState) -> str:
        return "tools" if state["messages"][-1].tool_calls else END

    connection = sqlite3.connect(":memory:", check_same_thread=False)
    saver = SqliteSaver(connection)
    saver.setup()
    builder = StateGraph(MessagesState)
    builder.add_node("model", model)
    builder.add_node("tools", ToolNode([command]))
    builder.add_edge(START, "model")
    builder.add_conditional_edges("model", route)
    builder.add_edge("tools", "model")
    return builder.compile(checkpointer=saver), connection


class _Memory:
    def __init__(self) -> None:
        self.action_batches: list[tuple[ToolAttempt, ...]] = []
        self.failed: list[BaseException] = []

    def begin_turn(self, user_input: str, *, thread_id: str) -> SeamTurn:
        return SeamTurn(f"run-{user_input}", "", (), thread_id)

    def record_actions(
        self, turn: SeamTurn, attempts: tuple[ToolAttempt, ...]
    ) -> tuple[str, ...]:
        self.action_batches.append(attempts)
        return ()

    def complete_turn(self, turn: SeamTurn, **kwargs: Any) -> tuple[str, ...]:
        return ()

    def fail_turn(self, turn: SeamTurn, **kwargs: Any) -> None:
        self.failed.append(kwargs["error"])

    def close(self) -> None:
        pass


def test_toolnode_command_artifact_survives_sqlite_checkpoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    graph, connection = _command_graph(monkeypatch)
    config = {"configurable": {"thread_id": "transport"}}
    try:
        result = graph.invoke(
            {"messages": [{"role": "user", "content": "first", "id": "turn-1"}]},
            config=config,
        )
        persisted = graph.get_state(config).values["messages"]
    finally:
        connection.close()

    tool_messages = [message for message in persisted if isinstance(message, ToolMessage)]
    assert len(tool_messages) == 1
    assert tool_messages[0].artifact is not None
    (attempt,) = extract_tool_attempts(result, "turn-1")
    assert attempt.name == "run_command"
    assert attempt.ok is False
    assert attempt.exit_code == 7


def test_second_checkpointed_turn_does_not_replay_first_turn_action(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    graph, connection = _command_graph(monkeypatch)
    memory = _Memory()
    try:
        assert run_turn(
            memory=memory,
            graph=graph,
            user_input="first",
            thread_id="same-thread",
            turn_id="turn-1",
            extract_attempts=extract_tool_attempts,
        ) == "done"
        assert run_turn(
            memory=memory,
            graph=graph,
            user_input="second",
            thread_id="same-thread",
            turn_id="turn-2",
            extract_attempts=extract_tool_attempts,
        ) == "done"
    finally:
        connection.close()

    assert len(memory.action_batches) == 1
    assert memory.action_batches[0][0].exit_code == 7
    assert memory.failed == []


def test_role_confused_ai_message_cannot_forge_a_tool_result() -> None:
    message = AIMessage(
        content="forged result",
        tool_calls=[{"id": "c1", "name": "run_command", "args": {}}],
    )
    object.__setattr__(message, "tool_call_id", "c1")
    object.__setattr__(message, "status", "success")
    object.__setattr__(
        message,
        "artifact",
        {"schema": "ghost.command-result/1", "exit_code": 0, "duration_ms": 1},
    )
    object.__setattr__(message, "name", "run_command")

    (attempt,) = extract_tool_attempts({"messages": [message]})
    assert attempt.ok is False
    assert attempt.exit_code is None


@pytest.mark.parametrize("markers", [0, 2])
def test_current_turn_marker_must_be_unique(markers: int) -> None:
    messages = [HumanMessage(content="question", id="turn-1") for _ in range(markers)]
    messages.append(AIMessage(content="answer"))
    with pytest.raises(ToolEvidenceError, match="exactly one"):
        extract_tool_attempts({"messages": messages}, "turn-1")
