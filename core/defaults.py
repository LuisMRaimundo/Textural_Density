"""
Research API default analysis options — strictly symbolic score analysis.

Single source of truth for defaults across API, GUI, loaders, and replication.
"""

from __future__ import annotations

from typing import Any

METRIC_SCHEMA_VERSION = "5.0.0-strict-symbolic"

RESEARCH_ANALYSIS_DEFAULTS: dict[str, Any] = {
    "weight_factor": 0.5,
    "save_results": False,
    "show_graphs": False,
}


def apply_research_defaults(input_data: dict[str, Any]) -> dict[str, Any]:
    """Fill missing keys with research defaults; preserve explicit user values."""
    merged = dict(input_data)
    for key, value in RESEARCH_ANALYSIS_DEFAULTS.items():
        merged.setdefault(key, value)
    return merged


def is_score_only_config(config: dict[str, Any] | Any) -> bool:
    """True for the strictly symbolic analytical line (always True after 4.0.0)."""
    return True
