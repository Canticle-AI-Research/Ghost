"""Tests for the operator-facing terminal entry point.

`cli.main` is the only interface an operator actually touches, and it owns two
things nothing else covers: the exit codes a shell or supervisor branches on,
and the guarantee that the agent is closed -- and therefore the SEAM SDK
handle released -- on every path out, including Ctrl-C mid-answer.
"""

from __future__ import annotations

import pytest

from ghost import cli


class FakeGhost:
    """Stands in for GhostAgent, recording lifecycle and prompts."""

    instances: list[FakeGhost] = []

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


@pytest.fixture(autouse=True)
def _isolate(monkeypatch):
    """Never load a real .env, build a real agent, or touch a real MIRL store."""
    FakeGhost.instances = []
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
