"""The recorded-fact audit must catch stale claims, not just pass.

An audit that only ever returns clean is indistinguishable from no audit. Each
test here injects the specific drift the extractor exists to catch, and the
ground-truth test checks Ghost's own documents against the real suite rather
than against each other.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

from tools.history.recorded_fact_audit import (
    TEST_COUNT,
    audit_recorded_facts,
    main,
)

ROOT = Path(__file__).resolve().parents[1]


def _repo(tmp_path: Path, files: dict[str, str]) -> Path:
    """A throwaway tree carrying only the documents under test."""
    for relative, text in files.items():
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return tmp_path


def test_ghost_recorded_facts_are_currently_clean() -> None:
    assert [issue.format() for issue in audit_recorded_facts()] == []


def test_disagreeing_test_counts_are_caught(tmp_path: Path) -> None:
    """The exact drift that shipped: two status authorities, two numbers."""
    repo = _repo(
        tmp_path,
        {
            "PROJECT_STATUS.md": "The current tree passes 196 provider-free tests.\n",
            "docs/status/CURRENT_STATE.md": "```text\nuv run pytest\n  184 passed\n```\n",
        },
    )
    issues = audit_recorded_facts(repo)
    assert [issue.kind for issue in issues] == ["test_count"]
    assert "196" in issues[0].message and "184" in issues[0].message


def test_agreeing_test_counts_pass(tmp_path: Path) -> None:
    repo = _repo(
        tmp_path,
        {
            "PROJECT_STATUS.md": "The current tree passes 196 provider-free tests.\n",
            "docs/status/CURRENT_STATE.md": "```text\n  196 passed\n```\n",
        },
    )
    assert audit_recorded_facts(repo) == []


def test_superseded_count_is_a_record_not_a_claim(tmp_path: Path) -> None:
    """Past-tense language keeps an old number readable without lying."""
    repo = _repo(
        tmp_path,
        {
            "PROJECT_STATUS.md": "The current tree passes 196 provider-free tests.\n",
            "docs/status/CURRENT_STATE.md": (
                "```text\n  196 passed\n```\n\n"
                "The earlier recorded `184 passed` predated the slices that added tests.\n"
            ),
        },
    )
    assert audit_recorded_facts(repo) == []


def test_both_claim_word_orders_are_extracted() -> None:
    """Matching only one word order makes disagreement undetectable."""
    orders = [
        "the tree passes 196 provider-free tests",
        "196 provider-free tests pass",
        "196 passed, 8 deselected",
    ]
    for text in orders:
        match = TEST_COUNT.search(text)
        assert match is not None, f"unmatched claim form: {text}"
        raw = match.group("count") or match.group("after") or match.group("bare")
        assert raw == "196", text


def test_deselected_count_is_not_read_as_a_claim() -> None:
    """`8 deselected` must not be mistaken for a passing total."""
    matches = [
        m.group("count") or m.group("after") or m.group("bare")
        for m in TEST_COUNT.finditer("196 passed, 8 deselected")
    ]
    assert matches == ["196"]


def test_stale_module_line_count_is_caught(tmp_path: Path) -> None:
    repo = _repo(
        tmp_path,
        {
            "sample.py": "one\ntwo\nthree\n",
            "docs/roadmap/R.md": "Split `sample.py` (99 lines) along its seams.\n",
        },
    )
    issues = audit_recorded_facts(repo)
    assert [issue.kind for issue in issues] == ["module_lines"]
    assert "is 3 lines, not 99" in issues[0].message


def test_accurate_module_line_count_passes(tmp_path: Path) -> None:
    repo = _repo(
        tmp_path,
        {
            "sample.py": "one\ntwo\nthree\n",
            "docs/roadmap/R.md": "Split `sample.py` (3 lines) along its seams.\n",
        },
    )
    assert audit_recorded_facts(repo) == []


def test_module_line_claim_for_missing_file_is_caught(tmp_path: Path) -> None:
    repo = _repo(tmp_path, {"docs/roadmap/R.md": "See `gone.py` (12 lines).\n"})
    issues = audit_recorded_facts(repo)
    assert [issue.kind for issue in issues] == ["module_lines"]
    assert "missing module" in issues[0].message


def test_any_documented_current_count_matches_the_real_suite() -> None:
    """Ground truth: a current count, when asserted, must match collection.

    Cross-document agreement alone cannot catch every authority being equally
    wrong, so an asserted count is compared against real collection. Omitting a
    volatile count is valid and preferable to publishing a stale one.
    """
    status = (ROOT / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    match = TEST_COUNT.search(status)
    if match is None:
        return

    # Not -q: the "N/M tests collected" total line only appears in the default
    # reporter's output.
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    collected = re.search(r"(?P<selected>\d+)(?:/\d+)? tests? collected", result.stdout)
    assert collected is not None, (
        "pytest reported no collection total; the reporter format changed:\n"
        + result.stdout[-500:]
    )
    actual = int(collected.group("selected"))
    claimed = int(match.group("count") or match.group("after") or match.group("bare"))
    assert claimed == actual, (
        f"PROJECT_STATUS.md claims {claimed} tests; pytest collects {actual}"
    )


def test_cli_reports_success_on_a_clean_repository(capsys: pytest.CaptureFixture[str]) -> None:
    main()
    assert "recorded facts verified" in capsys.readouterr().out
