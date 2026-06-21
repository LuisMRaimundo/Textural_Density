"""
Package version — single runtime fallback aligned with pyproject.toml.
"""

from __future__ import annotations

# Keep in sync with [project].version in pyproject.toml
PACKAGE_VERSION = "1.1.2"

# User-facing product name (documentation, error messages). PyPI id remains densidade-vertical.
PRODUCT_DISPLAY_NAME = "Textural Density"


def get_package_version() -> str:
    """Return installed distribution version, or PACKAGE_VERSION when running from source."""
    try:
        from importlib.metadata import version as pkg_version

        return pkg_version("densidade-vertical")
    except Exception:
        return PACKAGE_VERSION


__version__ = get_package_version()
