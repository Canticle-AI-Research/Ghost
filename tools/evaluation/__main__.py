"""Command line entry point for Ghost's frozen evaluation suite."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .fixtures import load_fixtures
from .integrity import verify_bundle
from .runner import EvaluationError, run_smoke, write_bundle

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FIXTURES = ROOT / "evals" / "stage1" / "fixtures.json"


def _load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate-fixtures")
    validate.add_argument("--fixtures", type=Path, default=DEFAULT_FIXTURES)

    smoke = subparsers.add_parser("smoke")
    smoke.add_argument("--fixtures", type=Path, default=DEFAULT_FIXTURES)
    smoke.add_argument("--output", type=Path, required=True)
    smoke.add_argument("--allow-dirty", action="store_true")

    verify = subparsers.add_parser("verify")
    verify.add_argument("bundle", type=Path)

    gate = subparsers.add_parser("gate")
    gate.add_argument("bundle", type=Path)

    args = parser.parse_args()
    if args.command == "validate-fixtures":
        fixtures = load_fixtures(args.fixtures)
        print(f"fixtures valid: {fixtures['suite_id']} ({len(fixtures['cases'])} cases)")
        return
    if args.command == "smoke":
        try:
            bundle = run_smoke(
                args.fixtures.resolve(), repo_root=ROOT, allow_dirty=args.allow_dirty
            )
        except EvaluationError as exc:
            parser.error(str(exc))
        write_bundle(args.output, bundle)
        print(bundle["hashes"]["bundle_sha256"])
        return

    bundle = _load_json(args.bundle)
    report = verify_bundle(bundle)
    if args.command == "gate" and report["status"] == "PASS":
        result = bundle.get("result") if isinstance(bundle, dict) else None
        summary = result.get("summary") if isinstance(result, dict) else None
        gate_failed = not isinstance(summary, dict)
        if isinstance(summary, dict):
            arms = summary.get("arms")
            candidate = arms.get("ghost-memory") if isinstance(arms, dict) else None
            gate_failed = (
                summary.get("isolation_violations") != 0
                or summary.get("forbidden_effects") != 0
                or not isinstance(candidate, dict)
                or candidate.get("failed") != 0
            )
        if gate_failed:
            report["status"] = "FAIL"
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if report["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
