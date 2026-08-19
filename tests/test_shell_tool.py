"""The write tool, and everything that bounds it.

`run_command` is the only tool that can change the machine. A shell is exactly
as powerful as the account running Ghost and no wrapper changes that, so these
tests are not about making it safe -- they are about the two things that are
actually true of it:

* it cannot run unless the operator opted in, and
* every invocation is bounded and accountable.

There is deliberately no test for a "dangerous command denylist", because there
is deliberately no denylist. Pattern-matching shell strings is trivially
bypassable and implies a protection that does not exist; the real controls are
the opt-in, the approval hook, the timeout, and SEAM's refusal to accept an
outcome against a check that failed.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from ghost.application import _build_tools
from ghost.config import GhostSettings
from ghost.tools import (
    WRITE_TOOLS,
    ApprovalDenied,
    ToolError,
    make_run_command,
    shell_enabled,
)


def refusal(built, args: dict) -> str:
    """A tool's refusal, as the model receives it.

    `handle_tool_error` returns a raised `ToolError` to the model as the tool's
    result, so a declined or malformed command is something the agent can read
    and work around rather than an exception that ends the turn.
    """

    out = built.invoke(args)
    assert isinstance(out, str), f"expected a refusal string, got {out!r}"
    return out


@pytest.fixture
def shell_on(monkeypatch):
    monkeypatch.setenv("GHOST_ENABLE_SHELL", "1")


def _settings(tmp_path: Path, **kw) -> GhostSettings:
    base = dict(
        model="openai:test-model",
        seam_db=tmp_path / "g.db",
        namespace="ghost.test",
        scope="thread",
    )
    base.update(kw)
    return GhostSettings(**base)


class _StubMemory:
    def query_knowledge(self, **kwargs: object) -> dict[str, object]:
        return {"nodes": []}


# --- the opt-in ------------------------------------------------------------


def test_the_shell_refuses_to_run_when_not_enabled(monkeypatch, tmp_path: Path) -> None:
    """The single most important property: importing or running Ghost with
    defaults can never reach a shell."""
    monkeypatch.delenv("GHOST_ENABLE_SHELL", raising=False)
    tool = make_run_command(workdir=tmp_path)
    assert "GHOST_ENABLE_SHELL" in refusal(tool, {"command": "echo hello"})


@pytest.mark.parametrize("value", ["", "0", "false", "no", "off", "maybe"])
def test_only_an_explicit_yes_enables_the_shell(monkeypatch, value: str) -> None:
    """An unset or unrecognised flag must never read as enabled."""
    monkeypatch.setenv("GHOST_ENABLE_SHELL", value)
    assert not shell_enabled()


def test_the_tool_is_absent_from_the_agent_until_enabled(tmp_path: Path) -> None:
    names = [t.name for t in _build_tools(_settings(tmp_path), _StubMemory())]
    assert "run_command" not in names

    enabled = _settings(tmp_path, enable_shell=True)
    assert "run_command" in [t.name for t in _build_tools(enabled, _StubMemory())]


def test_run_command_is_declared_a_write_tool() -> None:
    """Classification is data so it cannot drift silently, and so a reviewer
    can see the whole write surface in one place."""
    assert WRITE_TOOLS == {"run_command"}


# --- what it does ----------------------------------------------------------


def test_it_runs_a_command_and_reports_the_exit_code(shell_on, tmp_path: Path) -> None:
    out = make_run_command(workdir=tmp_path).invoke({"command": "echo hello"})
    assert "exit=0" in out and "hello" in out


def test_a_failing_command_reports_its_real_exit_code(shell_on, tmp_path: Path) -> None:
    """The exit code is what SEAM turns into a verdict, so it must be real
    rather than flattened to success."""
    out = make_run_command(workdir=tmp_path).invoke({"command": "exit 3"})
    assert "exit=3" in out


def test_stderr_is_returned_not_swallowed(shell_on, tmp_path: Path) -> None:
    out = make_run_command(workdir=tmp_path).invoke({"command": "echo oops >&2"})
    assert "oops" in out


def test_it_runs_in_the_configured_working_directory(shell_on, tmp_path: Path) -> None:
    (tmp_path / "marker.txt").write_text("x")
    out = make_run_command(workdir=tmp_path).invoke({"command": "ls"})
    assert "marker.txt" in out


def test_an_empty_command_is_refused(shell_on, tmp_path: Path) -> None:
    assert "command is required" in refusal(
        make_run_command(workdir=tmp_path), {"command": "   "}
    )


# --- the bounds ------------------------------------------------------------


def test_a_hanging_command_is_killed(shell_on, tmp_path: Path) -> None:
    """Without this one `tail -f` ends the session."""
    tool = make_run_command(workdir=tmp_path, timeout=1)
    assert "exceeded 1s" in refusal(tool, {"command": "sleep 30"})


def test_the_operator_timeout_caps_the_model_request(shell_on, tmp_path: Path) -> None:
    """The model may narrow the timeout but never widen it past the cap."""
    tool = make_run_command(workdir=tmp_path, timeout=1)
    assert "exceeded 1s" in refusal(
        tool, {"command": "sleep 30", "timeout_seconds": 999}
    )


def test_output_is_capped_before_it_reaches_the_model(shell_on, tmp_path: Path) -> None:
    out = make_run_command(workdir=tmp_path).invoke(
        {"command": "head -c 400000 /dev/zero | tr '\\0' 'x'"}
    )
    assert "truncated" in out and len(out) < 30_000


# --- the approval hook -----------------------------------------------------


def test_a_declined_command_does_not_run(shell_on, tmp_path: Path) -> None:
    target = tmp_path / "should-not-exist"
    tool = make_run_command(workdir=tmp_path, approve=lambda _cmd: False)
    assert "declined" in refusal(tool, {"command": f"touch {target}"})
    assert not target.exists(), "a declined command still ran"


def test_an_approved_command_runs(shell_on, tmp_path: Path) -> None:
    target = tmp_path / "created"
    tool = make_run_command(workdir=tmp_path, approve=lambda _cmd: True)
    tool.invoke({"command": f"touch {target}"})
    assert target.exists()


def test_the_approver_sees_the_exact_command(shell_on, tmp_path: Path) -> None:
    """An operator cannot consent to something they were not shown."""
    seen: list[str] = []

    def approve(command: str) -> bool:
        seen.append(command)
        return True

    make_run_command(workdir=tmp_path, approve=approve).invoke({"command": "echo hi"})
    assert seen == ["echo hi"]


def test_declining_is_a_refusal_the_model_can_recover_from() -> None:
    """ApprovalDenied subclasses ToolError so the agent surfaces it as a tool
    failure and continues, rather than the turn dying."""
    assert issubclass(ApprovalDenied, ToolError)


def test_approval_is_wired_by_default_and_removable_only_by_config(tmp_path: Path) -> None:
    """`GHOST_SHELL_APPROVAL` defaults on whenever the shell is on."""
    settings = _settings(tmp_path, enable_shell=True)
    assert settings.shell_approval is True

    unattended = _settings(tmp_path, enable_shell=True, shell_approval=False)
    assert unattended.shell_approval is False


def test_the_agent_passes_the_approver_through_only_when_enabled(tmp_path: Path) -> None:
    """A settings flag must actually disconnect the hook, not just be advisory."""
    calls: list[str] = []

    def approve(command: str) -> bool:
        calls.append(command)
        return False

    os.environ["GHOST_ENABLE_SHELL"] = "1"
    try:
        gated = _build_tools(
            _settings(tmp_path, enable_shell=True), _StubMemory(), approve=approve
        )
        shell = next(t for t in gated if t.name == "run_command")
        assert "declined" in refusal(shell, {"command": "echo gated"})
        assert calls == ["echo gated"]

        unattended = _build_tools(
            _settings(tmp_path, enable_shell=True, shell_approval=False),
            _StubMemory(),
            approve=approve,
        )
        shell = next(t for t in unattended if t.name == "run_command")
        assert "exit=0" in shell.invoke({"command": "echo ungated"})
        assert calls == ["echo gated"], "the approver ran despite being disabled"
    finally:
        os.environ.pop("GHOST_ENABLE_SHELL", None)


def test_a_refusal_is_recoverable_rather_than_fatal(shell_on, tmp_path: Path) -> None:
    """The property that makes refusals useful instead of merely safe.

    Before `handle_tool_error`, a declined command raised out of the tool and
    killed the whole turn -- the operator said no to one command and lost the
    conversation. Now the refusal comes back as the tool's result, so the model
    reads it and can propose something else.
    """
    tool = make_run_command(workdir=tmp_path, approve=lambda _cmd: False)
    assert tool.handle_tool_error is True

    result = tool.invoke({"command": "rm -rf /"})
    assert isinstance(result, str) and "declined" in result

    # And the tool still works for the next call; a refusal is not terminal.
    allowed = make_run_command(workdir=tmp_path, approve=lambda _cmd: True)
    assert "exit=0" in allowed.invoke({"command": "echo still here"})
