"""Tests for the operator-facing terminal entry point.

`cli.main` is the only interface an operator actually touches, and it owns two
things nothing else covers: the exit codes a shell or supervisor branches on,
and the guarantee that the agent is closed -- and therefore the SEAM SDK
handle released -- on every path out, including Ctrl-C mid-answer.
"""

from __future__ import annotations

import json
from typing import ClassVar

import pytest

from ghost import cli


class FakeGhost:
    """Stands in for GhostAgent, recording lifecycle and prompts."""

    # ClassVar is the point, not an annotation nicety: every FakeGhost appends
    # to one shared list and the fixture resets it per test.
    instances: ClassVar[list[FakeGhost]] = []

    def __init__(self, settings=None, **_: object) -> None:
        self.settings = settings
        self.prompts: list[tuple[str, str]] = []
        self.closed = False
        self.raises: BaseException | None = None
        FakeGhost.instances.append(self)

    def invoke(self, user_input: str, *, thread_id: str = "default") -> str:
        if self.raises is not None:
            raise self.raises
        self.prompts.append((user_input, thread_id))
        return f"answer to {user_input!r}"

    def close(self) -> None:
        self.closed = True

    def __enter__(self) -> FakeGhost:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


class FakeOperatorMemory:
    instances: ClassVar[list[FakeOperatorMemory]] = []

    def __init__(self, settings) -> None:
        self.settings = settings
        self.calls: list[tuple[str, tuple[object, ...], dict[str, object]]] = []
        self.closed = False
        FakeOperatorMemory.instances.append(self)

    def __enter__(self):
        return self

    def __exit__(self, *exc: object) -> None:
        self.closed = True

    def _call(self, name: str, *args: object, **kwargs: object) -> dict[str, object]:
        self.calls.append((name, args, kwargs))
        return {"accepted": True, "operation": name}

    def remember(self, *args: object, **kwargs: object):
        return self._call("remember", *args, **kwargs)

    def recall(self, *args: object, **kwargs: object):
        return self._call("recall", *args, **kwargs)

    def correct(self, *args: object, **kwargs: object):
        return self._call("correct", *args, **kwargs)

    def forget(self, *args: object, **kwargs: object):
        return self._call("forget", *args, **kwargs)


@pytest.fixture(autouse=True)
def _isolate(monkeypatch):
    """Never load a real .env, build a real agent, or touch a real MIRL store."""
    FakeGhost.instances = []
    FakeOperatorMemory.instances = []
    monkeypatch.setattr(cli, "load_dotenv", lambda *a, **k: False)
    monkeypatch.setattr(cli, "GhostAgent", FakeGhost)
    monkeypatch.setenv("GHOST_SEAM_DB", "/nonexistent/ghost-cli-test.db")
    yield


def test_one_shot_prompt_joins_argv_and_prints_the_answer(capsys) -> None:
    assert cli.main(["what", "do", "you", "remember?"]) == 0
    assert capsys.readouterr().out == "answer to 'what do you remember?'\n"
    assert FakeGhost.instances[0].prompts == [("what do you remember?", "default")]


def test_thread_id_flag_reaches_the_agent() -> None:
    assert cli.main(["--thread-id", "local-demo", "hello"]) == 0
    assert FakeGhost.instances[0].prompts == [("hello", "local-demo")]


def test_agent_is_closed_after_a_one_shot_run() -> None:
    cli.main(["hello"])
    assert FakeGhost.instances[0].closed, "SEAM handle leaked on the one-shot path"


@pytest.mark.parametrize("command", ["/exit", "/quit"])
def test_interactive_session_exits_cleanly_on_command(monkeypatch, capsys, command) -> None:
    monkeypatch.setattr("builtins.input", lambda _prompt="": command)
    assert cli.main([]) == 0
    assert "Ghost is ready" in capsys.readouterr().out
    assert FakeGhost.instances[0].closed


def test_interactive_session_skips_blank_lines_without_calling_the_agent(
    monkeypatch, capsys
) -> None:
    replies = iter(["", "   ", "hello", "/exit"])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(replies))

    assert cli.main([]) == 0
    # A blank line must not open a SEAM reasoning run or write a MIRL turn.
    assert FakeGhost.instances[0].prompts == [("hello", "default")]
    assert "ghost> answer to 'hello'" in capsys.readouterr().out


def test_eof_ends_the_session_cleanly(monkeypatch) -> None:
    """Ctrl-D / a closed pipe is a normal exit, not a crash."""

    def raise_eof(_prompt: str = "") -> str:
        raise EOFError

    monkeypatch.setattr("builtins.input", raise_eof)
    assert cli.main([]) == 0
    assert FakeGhost.instances[0].closed


def test_keyboard_interrupt_reports_130_and_still_closes(monkeypatch, capsys) -> None:
    """130 is the shell convention for SIGINT; a supervisor branches on it."""
    monkeypatch.setattr("builtins.input", lambda _prompt="": "hello")
    cli.GhostAgent = FakeGhost

    def build(settings=None, **kwargs):
        agent = FakeGhost(settings, **kwargs)
        agent.raises = KeyboardInterrupt()
        return agent

    monkeypatch.setattr(cli, "GhostAgent", build)

    assert cli.main([]) == 130
    assert "Interrupted." in capsys.readouterr().err
    assert FakeGhost.instances[0].closed, "SEAM handle leaked on Ctrl-C"


def test_parser_defaults_to_the_default_thread() -> None:
    args = cli._parser().parse_args([])
    assert args.prompt == [] and args.thread_id == "default"


def test_memory_remember_uses_the_operator_boundary(monkeypatch, capsys) -> None:
    monkeypatch.setattr(cli, "SeamMemory", FakeOperatorMemory)
    assert cli.main(
        ["memory", "remember", "The release code is violet.", "--thread-id", "t-7"]
    ) == 0
    instance = FakeOperatorMemory.instances[0]
    assert instance.calls == [
        ("remember", ("The release code is violet.",), {"thread_id": "t-7"})
    ]
    assert instance.closed is True
    assert json.loads(capsys.readouterr().out)["operation"] == "remember"


def test_memory_recall_selects_history_view(monkeypatch) -> None:
    monkeypatch.setattr(cli, "SeamMemory", FakeOperatorMemory)
    assert cli.main(
        [
            "memory",
            "recall",
            "release code",
            "--view",
            "history",
            "--limit",
            "12",
            "--thread-id",
            "t-7",
        ]
    ) == 0
    assert FakeOperatorMemory.instances[0].calls == [
        (
            "recall",
            ("release code",),
            {"thread_id": "t-7", "limit": 12, "view": "history"},
        )
    ]


def test_memory_correction_gets_a_stable_default_idempotency_key(monkeypatch) -> None:
    monkeypatch.setattr(cli, "SeamMemory", FakeOperatorMemory)
    argv = ["memory", "correct", "mem_abc", "New fact", "--thread-id", "t-7"]
    assert cli.main(argv) == 0
    first_key = FakeOperatorMemory.instances[-1].calls[0][2]["idempotency_key"]
    assert cli.main(argv) == 0
    second_key = FakeOperatorMemory.instances[-1].calls[0][2]["idempotency_key"]
    assert first_key == second_key
    assert str(first_key).startswith("ghost-correct-")


def test_memory_forget_requires_exact_confirmation(monkeypatch, capsys) -> None:
    monkeypatch.setattr(cli, "SeamMemory", FakeOperatorMemory)
    assert cli.main(
        ["memory", "forget", "mem_abc", "--confirm", "mem_wrong"]
    ) == 2
    assert FakeOperatorMemory.instances == []
    assert "exactly match" in capsys.readouterr().err


def test_memory_forget_forwards_an_explicit_idempotency_key(monkeypatch) -> None:
    monkeypatch.setattr(cli, "SeamMemory", FakeOperatorMemory)
    assert cli.main(
        [
            "memory",
            "forget",
            "mem_abc",
            "--confirm",
            "mem_abc",
            "--idempotency-key",
            "operator-key-1",
        ]
    ) == 0
    assert FakeOperatorMemory.instances[0].calls[0] == (
        "forget",
        ("mem_abc",),
        {"thread_id": "default", "idempotency_key": "operator-key-1"},
    )
