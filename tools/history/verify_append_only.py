"""Verify that ``HISTORY.md`` only appends to a prior Git revision."""

from __future__ import annotations

import argparse
import subprocess

from .model import HISTORY_PATH, ROOT, parse_history, validate_entries


def verify_append_only(base_text: str, current_text: str) -> None:
    """Fail when an existing history byte was changed, removed, or reordered."""

    base_entries = parse_history(base_text)
    current_entries = parse_history(current_text)
    validate_entries(base_entries, check_refs=False)
    validate_entries(current_entries, check_refs=False)
    if not current_text.startswith(base_text):
        raise ValueError(
            "HISTORY.md is not append-only: content from the base revision was "
            "changed, removed, or reordered"
        )
    if len(current_entries) < len(base_entries):
        raise ValueError("HISTORY.md removed entries from the base revision")


def _history_at(ref: str) -> str | None:
    commit = subprocess.run(  # noqa: S603
        ["git", "cat-file", "-e", f"{ref}^{{commit}}"],  # noqa: S607
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    if commit.returncode != 0:
        raise ValueError(f"base revision does not exist: {ref!r}")
    result = subprocess.run(  # noqa: S603
        ["git", "show", f"{ref}:HISTORY.md"],  # noqa: S607
        cwd=ROOT,
        capture_output=True,
        check=False,
        text=True,
    )
    return result.stdout if result.returncode == 0 else None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-ref", required=True, help="Git commit or ref to compare")
    args = parser.parse_args()
    current = HISTORY_PATH.read_text(encoding="utf-8")
    base = _history_at(args.base_ref)
    if base is None:
        validate_entries(parse_history(current))
        print(f"initialized append-only history; {args.base_ref} has no HISTORY.md")
    else:
        verify_append_only(base, current)
        print(f"append-only history verified against {args.base_ref}")


if __name__ == "__main__":
    main()
