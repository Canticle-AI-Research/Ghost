"""Verify HISTORY.md only appends to a prior Git revision."""

import argparse

from .model import HISTORY_PATH, history_at, parse_history, validate_entries


def verify_append_only(base: str, current: str) -> None:
    validate_entries(parse_history(base), check_refs=False)
    validate_entries(parse_history(current), check_refs=False)
    if not current.startswith(base):
        raise ValueError("HISTORY.md changed, removed, or reordered established bytes")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-ref", required=True)
    args = parser.parse_args()
    current = HISTORY_PATH.read_text(encoding="utf-8")
    base = history_at(args.base_ref)
    if base is None:
        validate_entries(parse_history(current))
        print(f"initialized append-only history; {args.base_ref} has no HISTORY.md")
    else:
        verify_append_only(base, current)
        print(f"append-only history verified against {args.base_ref}")


if __name__ == "__main__":
    main()
