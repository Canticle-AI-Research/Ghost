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


def main(argv: Sequence[str] | None = None) -> int:
    load_dotenv(".env.local", override=False)
    args = _parser().parse_args(argv)
    settings = GhostSettings.from_env()

    try:
        with GhostAgent(settings) as ghost:
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

