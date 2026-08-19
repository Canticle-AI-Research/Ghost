"""Command-line entry point for Ghost."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from dotenv import load_dotenv

from .application import GhostAgent
from .config import GhostSettings


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Ghost SEAM DeepAgent")
    parser.add_argument("prompt", nargs="*", help="one-shot prompt; omit for interactive mode")
    parser.add_argument("--thread-id", default="default", help="LangGraph conversation thread")
    return parser


def _terminal_approval(command: str) -> bool:
    """Ask the operator before Ghost runs a command.

    Written against the real terminal rather than stdin, so a piped prompt --
    ``echo "..." | ghost`` -- cannot answer its own approval prompt. If there
    is no terminal to ask, the answer is no: an unattended process must not
    silently inherit consent, and an operator who wants that sets
    ``GHOST_SHELL_APPROVAL=0`` deliberately.
    """

    print(f"\nghost wants to run:\n  {command}", file=sys.stderr)
    try:
        with open("/dev/tty") as tty:
            print("run it? [y/N] ", end="", file=sys.stderr, flush=True)
            answer = tty.readline().strip().lower()
    except OSError:
        print("  no terminal available to confirm; declining.", file=sys.stderr)
        return False
    return answer in {"y", "yes"}


def main(argv: Sequence[str] | None = None) -> int:
    load_dotenv(".env.local", override=False)
    args = _parser().parse_args(argv)
    settings = GhostSettings.from_env()

    if settings.enable_shell:
        where = settings.shell_workdir or "the current directory"
        gate = "asking before each command" if settings.shell_approval else (
            "WITHOUT asking -- GHOST_SHELL_APPROVAL is off"
        )
        print(f"shell enabled in {where}, {gate}.", file=sys.stderr)

    try:
        with GhostAgent(settings, approve=_terminal_approval) as ghost:
            if args.prompt:
                print(ghost.invoke(" ".join(args.prompt), thread_id=args.thread_id))
                return 0

            print("Ghost is ready. Type /exit to leave.")
            while True:
                try:
                    prompt = input("you> ").strip()
                except EOFError:
                    print()
                    return 0
                if prompt in {"/exit", "/quit"}:
                    return 0
                if not prompt:
                    continue
                print(f"ghost> {ghost.invoke(prompt, thread_id=args.thread_id)}")
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())

