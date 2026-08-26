"""Credential-free integrity for Ghost evaluation bundles.

This is an independently authored implementation of the proof properties Ghost
adopts from SEAM: canonical JSON, exact input/case/result hashes, explicit BIL
level, exact source identity, and volatile timing excluded from result hashes.
"""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any

BUNDLE_VERSION = "GHOST-EVAL-BUNDLE/1"
VERIFY_VERSION = "GHOST-EVAL-BUNDLE-VERIFY/1"
SMOKE_LEVEL = "BIL-0"
VOLATILE_KEYS = {"created_at", "elapsed_ms", "started_at"}


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def sha256_canonical(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def stable_result(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: stable_result(item)
            for key, item in value.items()
            if key not in VOLATILE_KEYS
        }
    if isinstance(value, list):
        return [stable_result(item) for item in value]
    return copy.deepcopy(value)


def case_hashes(fixtures: dict[str, Any]) -> dict[str, str]:
    return {
        str(case["id"]): sha256_canonical(case)
        for case in fixtures.get("cases", [])
    }


def _bundle_hash_input(bundle: dict[str, Any]) -> dict[str, Any]:
    value = copy.deepcopy(bundle)
    value.setdefault("hashes", {})["bundle_sha256"] = None
    return value


def seal_bundle(*, result: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    bundle = {
        "version": BUNDLE_VERSION,
        "integrity": {
            "level": SMOKE_LEVEL,
            "sealed": True,
            "claim_boundary": "provider-free deterministic contract smoke only",
        },
        "manifest": copy.deepcopy(manifest),
        "result": copy.deepcopy(result),
        "hashes": {
            "manifest_sha256": sha256_canonical(manifest),
            "result_sha256": sha256_canonical(stable_result(result)),
            "bundle_sha256": None,
        },
    }
    bundle["hashes"]["bundle_sha256"] = sha256_canonical(_bundle_hash_input(bundle))
    return bundle


def verify_bundle(bundle: object) -> dict[str, Any]:
    checks: list[dict[str, str]] = []
    if not isinstance(bundle, dict):
        return _failed("bundle must be an object")
    checks.append(_check("bundle_version", bundle.get("version") == BUNDLE_VERSION))
    integrity = bundle.get("integrity")
    checks.append(
        _check(
            "integrity_level",
            isinstance(integrity, dict)
            and integrity.get("level") == SMOKE_LEVEL
            and integrity.get("sealed") is True,
        )
    )
    manifest = bundle.get("manifest")
    result = bundle.get("result")
    hashes = bundle.get("hashes")
    valid_shapes = all(isinstance(item, dict) for item in (manifest, result, hashes))
    checks.append(_check("payload_shapes", valid_shapes))
    if valid_shapes:
        checks.append(
            _check(
                "manifest_hash",
                hashes.get("manifest_sha256") == sha256_canonical(manifest),
            )
        )
        checks.append(
            _check(
                "result_hash",
                hashes.get("result_sha256") == sha256_canonical(stable_result(result)),
            )
        )
        checks.append(
            _check(
                "bundle_hash",
                hashes.get("bundle_sha256")
                == sha256_canonical(_bundle_hash_input(bundle)),
            )
        )
        checks.extend(_cross_checks(manifest, result))
    status = "PASS" if all(check["status"] == "PASS" for check in checks) else "FAIL"
    return {
        "version": VERIFY_VERSION,
        "status": status,
        "integrity_level": SMOKE_LEVEL,
        "checks": checks,
    }


def _cross_checks(manifest: dict[str, Any], result: dict[str, Any]) -> list[dict[str, str]]:
    results = result.get("cases")
    result_ids = (
        sorted(str(item.get("case_id")) for item in results if isinstance(item, dict))
        if isinstance(results, list)
        else []
    )
    return [
        _check("suite_identity", manifest.get("suite_id") == result.get("suite_id")),
        _check("git_identity", manifest.get("git_sha") == result.get("git_sha")),
        _check("fixture_identity", manifest.get("fixture_sha256") == result.get("fixture_sha256")),
        _check("case_count", manifest.get("case_count") * 2 == len(result_ids)),
        _check(
            "case_ids",
            sorted(case_id for case_id in manifest.get("case_ids", []) for _ in range(2))
            == result_ids,
        ),
    ]


def _check(identifier: str, passed: bool) -> dict[str, str]:
    return {
        "id": identifier,
        "status": "PASS" if passed else "FAIL",
        "message": "" if passed else f"{identifier} check failed",
    }


def _failed(message: str) -> dict[str, Any]:
    return {
        "version": VERIFY_VERSION,
        "status": "FAIL",
        "integrity_level": "BIL-0",
        "checks": [{"id": "bundle_shape", "status": "FAIL", "message": message}],
    }
