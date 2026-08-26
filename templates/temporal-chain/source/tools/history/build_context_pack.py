"""Print a bounded, topic-aware subset of canonical history."""

import argparse

from .model import load_history


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--latest", type=int, default=5)
    parser.add_argument("--topics", nargs="*", default=())
    parser.add_argument("--token-budget", type=int, default=2000)
    args = parser.parse_args()
    if args.latest < 1 or args.token_budget < 100:
        raise SystemExit("latest must be positive and token budget at least 100")
    topics = {topic.lower() for topic in args.topics}
    entries = [e for e in load_history() if not topics or topics.intersection(e.topics)]
    output = "\n".join(entry.raw.rstrip() for entry in entries[-args.latest:])
    cap = args.token_budget * 4
    if len(output) > cap:
        output = "[context pack truncated]\n" + output[-cap:]
    print(output)


if __name__ == "__main__":
    main()
