"""Shared pytest configuration for the Ghost test suite.

Strict no-skip enforcement, ported from the SEAM suite. A skip must never
silently mean "this test never ran". Ghost's suite currently has no legitimate
skip at all: every test either runs on the default SQLite MIRL store or is
deselected by path in the CI job that cannot provide its dependency. So the
allowlist below is deliberately empty -- the first entry added to it must
arrive with the justification for why that skip is unavoidable.

Default ON; opt out for ad-hoc local runs with ``GHOST_STRICT_NO_SKIP=0``.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager

import httpx
import pytest

# Reasons a skip is genuinely unavoidable in the current environment. Empty by
# design; see the module docstring before adding to it.
_ALLOWED_SKIP_SUBSTRINGS: tuple[str, ...] = ()

_observed_skips: list[tuple[str, str]] = []


class FakeSeamHTTP:
    """Stateful fake of only the opaque public routes Ghost is allowed to use."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, object]]] = []
        self.memories: list[dict[str, object]] = []
        self.turns: dict[str, str] = {}
        self.closed = False

    def _response(self, path: str, payload: dict[str, object]) -> httpx.Response:
        request = httpx.Request("POST", f"http://seam.test{path}")
        if path == "/v1/agent/turns/begin":
            turn_id = f"turn-{len(self.turns) + 1}"
            self.turns[turn_id] = "open"
            return httpx.Response(
                200,
                request=request,
                json={"turn_id": turn_id, "memories": list(self.memories)},
            )
        if path == "/v1/agent/turns/actions":
            attempts = payload.get("attempts")
            assert isinstance(attempts, list)
            ids = [f"verify-{index}" for index, _attempt in enumerate(attempts)]
            passed = [
                verification_id
                for verification_id, attempt in zip(ids, attempts, strict=True)
                if isinstance(attempt, dict) and attempt.get("ok") is True
            ]
            return httpx.Response(
                200,
                request=request,
                json={"verification_ids": ids, "passed_verification_ids": passed},
            )
        if path == "/v1/agent/turns/complete":
            turn_id = str(payload["turn_id"])
            receipt_id = f"receipt-{turn_id}"
            if self.turns.get(turn_id) != "accepted":
                text = f"{payload['user_input']} {payload['assistant_output']}"
                self.memories.append(
                    {
                        "id": f"memory-{len(self.memories) + 1}",
                        "text": text,
                        "score": 1.0,
                    }
                )
                self.turns[turn_id] = "accepted"
            return httpx.Response(
                200,
                request=request,
                json={"accepted": True, "receipt_id": receipt_id},
            )
        if path == "/v1/agent/turns/fail":
            self.turns[str(payload["turn_id"])] = "rejected"
            return httpx.Response(200, request=request, json={"status": "rejected"})
        if path == "/v1/memories/recall":
            return httpx.Response(
                200,
                request=request,
                json={"memories": list(self.memories)},
            )
        return httpx.Response(404, request=request, json={"detail": "not found"})

    def post(self, path: str, **kwargs: object) -> httpx.Response:
        payload = kwargs.get("json")
        assert isinstance(payload, dict)
        self.calls.append((path, payload))
        return self._response(path, payload)

    @contextmanager
    def stream(
        self, method: str, path: str, **kwargs: object
    ) -> Iterator[httpx.Response]:
        assert method == "POST"
        yield self.post(path, **kwargs)

    def close(self) -> None:
        self.closed = True


@pytest.fixture
def seam_http() -> FakeSeamHTTP:
    return FakeSeamHTTP()


def _strict_no_skip_enabled() -> bool:
    raw = os.environ.get("GHOST_STRICT_NO_SKIP", "1").strip().lower()
    return raw not in {"0", "false", "no", "off"}


def _skip_is_allowed(reason: str) -> bool:
    return any(substring in reason for substring in _ALLOWED_SKIP_SUBSTRINGS)


def pytest_runtest_logreport(report):
    # xfail also reports as "skipped" but is a deliberate outcome, not a test
    # that silently never ran -- leave it alone.
    if report.skipped and not hasattr(report, "wasxfail"):
        longrepr = getattr(report, "longrepr", None)
        # report.longrepr for a skip is (path, lineno, "Skipped: <reason>")
        if isinstance(longrepr, tuple) and len(longrepr) == 3:
            reason = str(longrepr[2])
        else:
            reason = str(longrepr)
        _observed_skips.append((report.nodeid, reason))


def pytest_sessionfinish(session, exitstatus):
    offenders = [(nid, r) for nid, r in _observed_skips if not _skip_is_allowed(r)]
    reporter = session.config.pluginmanager.get_plugin("terminalreporter")

    if not _strict_no_skip_enabled():
        # Disabling enforcement must never be silent: an unannounced opt-out
        # looks identical to a clean run, so a lane (or an agent) that inherits
        # GHOST_STRICT_NO_SKIP=0 would report green while tests quietly did not
        # run.
        if offenders and reporter is not None:
            reporter.write_sep(
                "=",
                f"STRICT NO-SKIP DISABLED (GHOST_STRICT_NO_SKIP=0): "
                f"{len(offenders)} unexplained skip(s) NOT enforced",
                yellow=True,
            )
            for nodeid, reason in offenders:
                reporter.write_line(f"  SKIPPED {nodeid}: {reason}")
        return

    if not offenders:
        return
    if reporter is not None:
        reporter.write_sep("=", "STRICT NO-SKIP: unexplained skips", red=True)
        for nodeid, reason in offenders:
            reporter.write_line(f"  SKIPPED {nodeid}: {reason}")
        reporter.write_line(
            "  Set GHOST_STRICT_NO_SKIP=0 only for ad-hoc local runs; CI must not skip."
        )
    session.exitstatus = 1
