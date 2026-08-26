"""Credential-free checks for Ghost's declared license boundary.

These tests verify repository consistency. They do not interpret the license,
establish ownership, or replace legal review.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_polyform_shield_text_and_required_notices_are_present() -> None:
    license_text = _read("LICENSE")
    notice = _read("NOTICE")

    assert license_text.startswith("# PolyForm Shield License 1.0.0\n")
    assert "https://polyformproject.org/licenses/shield/1.0.0" in license_text
    assert "## Noncompete" in license_text
    assert "## No Liability" in license_text
    assert "Required Notice: Copyright 2026 Nicholas Thomas." in notice
    assert "Licensor Line of Business:" in notice


def test_package_metadata_matches_repository_license() -> None:
    metadata = tomllib.loads(_read("pyproject.toml"))["project"]

    assert metadata["license"] == "LicenseRef-PolyForm-Shield-1.0.0"
    assert set(metadata["license-files"]) == {"LICENSE", "NOTICE"}


def test_public_language_uses_source_available_not_open_source() -> None:
    readme = _read("README.md")
    structure = _read("docs/legal/LICENSING_STRUCTURE.md")

    assert "source-available under the" in readme
    assert "not an OSI-approved open-source license" in readme
    assert "Ghost | B" in structure
    assert "thin SEAM/Canticle client | A" in structure
    assert "private SEAM runtime/MIRL | C" in structure


def test_company_and_future_model_boundaries_are_not_overstated() -> None:
    structure = _read("docs/product/CANTICLE_PRODUCT_AND_LICENSING_STRUCTURE.md")
    status = _read("docs/status/CURRENT_STATE.md")

    for term in ("Ghost", "Canticle Core", "SEAM-U", "SEAM runtime"):
        assert term in structure
    assert "No model repository" in structure
    assert "No Canticle legal" in status
    assert "founder-to-company IP assignment" in status


def test_brand_assets_are_excluded_from_software_grant() -> None:
    notice = _read("NOTICE")

    assert "Files under branding/ and assets/" in notice
    assert "All Rights" in notice
    assert "does not grant permission to use them as a trademark" in notice
    assert "modified forks" in _read("TRADEMARKS.md")


def test_external_contributions_are_paused_pending_company_controls() -> None:
    contributing = _read("CONTRIBUTING.md")

    assert "not accepting external pull requests" in contributing
    assert "contributor agreement" in contributing
