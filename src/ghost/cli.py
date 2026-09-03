"""Command-line entry point for Ghost."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

from dotenv import load_dotenv

from .application import GhostAgent
from .config import GhostSettings
from .lifeline import LifelineComponent, lifeline, touches_lifeline
from .operations import backup_checkpoint, restore_checkpoint, verify_checkpoint
from .seam_memory import SeamMemory, SeamTransportError


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Ghost SEAM DeepAgent")
    parser.add_argument("prompt", nargs="*", help="one-shot prompt; omit for interactive mode")
    parser.add_argument("--thread-id", default="default", help="LangGraph conversation thread")
    return parser


def _memory_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ghost memory",
        description="Inspect and mutate Ghost's durable SEAM memory",
    )
    commands = parser.add_subparsers(dest="memory_command", required=True)

    remember = commands.add_parser("remember", help="store one explicit memory")
    remember.add_argument("text")
    _add_memory_boundary_args(remember)

    recall = commands.add_parser("recall", help="search current or historical memory")
    recall.add_argument("query")
    recall.add_argument("--view", choices=("current", "history"), default="current")
    recall.add_argument("--limit", type=int, default=None)
    _add_memory_boundary_args(recall)

    correct = commands.add_parser("correct", help="supersede one memory")
    correct.add_argument("memory_id")
    correct.add_argument("text")
    correct.add_argument("--idempotency-key")
    _add_memory_boundary_args(correct)

    forget = commands.add_parser("forget", help="soft-delete one memory")
    forget.add_argument("memory_id")
    forget.add_argument(
        "--confirm",
        required=True,
        help="repeat the exact mem_ id to authorize forgetting",
    )
    forget.add_argument("--idempotency-key")
    _add_memory_boundary_args(forget)
    return parser


def _checkpoint_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ghost checkpoint",
        description="Back up, verify, and restore Ghost execution checkpoints",
    )
    commands = parser.add_subparsers(dest="checkpoint_command", required=True)
    backup = commands.add_parser("backup", help="write a consistent backup to a new path")
    backup.add_argument("destination")
    verify = commands.add_parser("verify", help="verify backup integrity and optional digest")
    verify.add_argument("backup")
    verify.add_argument("--sha256")
    restore = commands.add_parser("restore", help="restore a verified backup to a new path")
    restore.add_argument("backup")
    restore.add_argument("destination")
    restore.add_argument("--sha256", required=True)
    return parser


def _add_memory_boundary_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--thread-id", default="default", help="memory thread boundary")


def _operation_key(operation: str, *values: str) -> str:
    material = json.dumps(
        ["ghost-memory-operation/1", operation, *values],
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return f"ghost-{operation}-{hashlib.sha256(material).hexdigest()[:24]}"


def _run_memory_command(args: argparse.Namespace, settings: GhostSettings) -> int:
    if args.memory_command == "forget" and args.confirm != args.memory_id:
        print("forget confirmation must exactly match memory_id", file=sys.stderr)
        return 2
    try:
        with SeamMemory(settings) as memory:
            if args.memory_command == "remember":
                result = memory.remember(args.text, thread_id=args.thread_id)
            elif args.memory_command == "recall":
                result = memory.recall(
                    args.query,
                    thread_id=args.thread_id,
                    limit=args.limit,
                    view=args.view,
                )
            elif args.memory_command == "correct":
                key = args.idempotency_key or _operation_key(
                    "correct", args.memory_id, args.text
                )
                result = memory.correct(
                    args.memory_id,
                    args.text,
                    thread_id=args.thread_id,
                    idempotency_key=key,
                )
            else:
                key = args.idempotency_key or _operation_key(
                    "forget", args.memory_id
                )
                result = memory.forget(
                    args.memory_id,
                    thread_id=args.thread_id,
                    idempotency_key=key,
                )
    except SeamTransportError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def _run_checkpoint_command(args: argparse.Namespace, settings: GhostSettings) -> int:
    try:
        if args.checkpoint_command == "backup":
            manifest = backup_checkpoint(settings.checkpoints, Path(args.destination))
        elif args.checkpoint_command == "verify":
            manifest = verify_checkpoint(
                Path(args.backup), expected_sha256=args.sha256
            )
        else:
            manifest = restore_checkpoint(
                Path(args.backup),
                Path(args.destination),
                expected_sha256=args.sha256,
            )
    except FileExistsError as error:
        print(f"path already exists; refusing to overwrite: {error}", file=sys.stderr)
        return 1
    except (FileNotFoundError, ValueError, OSError) as error:
        print(str(error), file=sys.stderr)
        return 1
    print(json.dumps(manifest.to_dict(), indent=2, sort_keys=True))
    return 0


def _lifeline_approval(
    components: Sequence[LifelineComponent],
) -> Callable[[str], bool]:
    """Approval that says out loud when a command names Ghost's own substrate.

    The check is deliberately shallow -- see `ghost.lifeline.touches_lifeline`,
    which explains why anything deeper would be theatre. Its value is entirely
    in what the operator sees before answering: a command naming the SEAM store
    reads very differently from the same command with no annotation, and the
    operator is the boundary that actually holds.
    """

    def approve(command: str) -> bool:
        for component in touches_lifeline(command, components):
            print(
                f"\n  !! this command names Ghost's {component.name} "
                f"({component.severity}) at {component.path}\n"
                f"     losing it loses {component.loses}",
                file=sys.stderr,
            )
        return _terminal_approval(command)

    return approve


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
    raw_argv = list(argv) if argv is not None else sys.argv[1:]
    if raw_argv[:1] == ["memory"]:
        args = _memory_parser().parse_args(raw_argv[1:])
        return _run_memory_command(args, GhostSettings.from_env())
    if raw_argv[:1] == ["checkpoint"]:
        args = _checkpoint_parser().parse_args(raw_argv[1:])
        return _run_checkpoint_command(args, GhostSettings.from_env())
    args = _parser().parse_args(raw_argv)
    settings = GhostSettings.from_env()

    if settings.enable_shell:
        where = settings.shell_workdir or "the current directory"
        gate = "asking before each command" if settings.shell_approval else (
            "WITHOUT asking -- GHOST_SHELL_APPROVAL is off"
        )
        print(f"shell enabled in {where}, {gate}.", file=sys.stderr)

    try:
        with GhostAgent(
            settings, approve=_lifeline_approval(lifeline(settings))
        ) as ghost:
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
