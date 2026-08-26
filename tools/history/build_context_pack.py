"""Read a bounded subset of Ghost's canonical history."""

from __future__ import annotations

import argparse

from .model import HistoryEntry, load_history


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--latest", type=int, default=5, help="latest matching entries")
    parser.add_argument("--topics", nargs="*", default=(), help="match any topic")
    parser.add_argument("--entries", nargs="*", type=int, default=(), help="exact history IDs")
    parser.add_argument("--token-budget", type=int, default=2000, help="approximate output cap")
    return parser


def select_entries(
    entries: list[HistoryEntry],
    *,
    latest: int,
    topics: tuple[str, ...],
    ids: tuple[int, ...],
) -> list[HistoryEntry]:
    if latest < 1:
        raise ValueError("--latest must be positive")
    wanted_topics = {topic.lower() for topic in topics}
    wanted_ids = set(ids)
    matches = [
        entry
        for entry in entries
        if (not wanted_topics or wanted_topics.intersection(entry.topics))
        and (not wanted_ids or entry.id in wanted_ids)
    ]
    return matches[-latest:]


def main() -> None:
    args = _parser().parse_args()
    if args.token_budget < 100:
        raise SystemExit("--token-budget must be at least 100")
    selected = select_entries(
        load_history(),
        latest=args.latest,
        topics=tuple(args.topics),
        ids=tuple(args.entries),
    )
    budget_chars = args.token_budget * 4
    output = "\n".join(entry.raw.rstrip() for entry in selected)
    if len(output) > budget_chars:
        output = output[-budget_chars:]
        output = "[context pack truncated to requested budget]\n" + output
    print(output)


if __name__ == "__main__":
    main()
