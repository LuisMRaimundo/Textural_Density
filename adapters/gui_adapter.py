"""GUI state / loose dict → strict AnalysisRequest."""

from __future__ import annotations

from typing import Any

from core import calculate_metrics
from core.defaults import RESEARCH_ANALYSIS_DEFAULTS
from core.input_validation import strip_removed_gui_preference_keys
from core.request import ALLOWED_REQUEST_KEYS, AnalysisRequest

_GUI_ONLY_KEYS = frozenset({"save_results", "show_graphs"})


def build_analysis_request(raw: dict[str, Any]) -> AnalysisRequest:
    """
    Merge GUI options with research defaults, strip removed keys, build typed request.

    GUI-only keys (save_results, show_graphs) are dropped before strict validation.
    """
    cleaned, _stripped = strip_removed_gui_preference_keys(raw)
    merged = dict(RESEARCH_ANALYSIS_DEFAULTS)
    for key in ALLOWED_REQUEST_KEYS | _GUI_ONLY_KEYS:
        if key in cleaned:
            merged[key] = cleaned[key]
    analytical = {k: merged[k] for k in ALLOWED_REQUEST_KEYS if k in merged}
    if "notes" not in analytical:
        analytical["notes"] = cleaned.get("notes", [])
    if "dynamics" not in analytical:
        analytical["dynamics"] = cleaned.get("dynamics", [])
    if "instruments" not in analytical:
        analytical["instruments"] = cleaned.get("instruments", [])
    if "num_instruments" not in analytical:
        analytical["num_instruments"] = cleaned.get("num_instruments", [])
    return AnalysisRequest.from_mapping(analytical)


def calculate_from_gui_request(raw: dict[str, Any]):
    """GUI → AnalysisRequest → core.calculate_metrics."""
    request = build_analysis_request(raw)
    return calculate_metrics(request)
