"""Package version and license metadata consistency."""

from __future__ import annotations

import re
from pathlib import Path

from core.version import PACKAGE_VERSION, get_package_version


ROOT = Path(__file__).resolve().parents[1]


def _pyproject_version() -> str:
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    assert match, "version not found in pyproject.toml"
    return match.group(1)


def test_package_version_matches_pyproject():
    assert PACKAGE_VERSION == _pyproject_version()


def test_get_package_version_matches_fallback():
    # Editable installs may resolve metadata; fallback must match pyproject when absent.
    assert get_package_version() in {PACKAGE_VERSION, _pyproject_version()}


def test_license_file_exists():
    license_path = ROOT / "LICENSE"
    assert license_path.is_file()
    content = license_path.read_text(encoding="utf-8")
    assert "MIT License" in content


def test_pyproject_declares_mit():
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'license = { file = "LICENSE" }' in text
