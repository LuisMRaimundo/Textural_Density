"""Legacy dict → typed AnalysisRequest (compatibility only)."""

from __future__ import annotations

from typing import Any

from core.defaults import apply_research_defaults
from core.request import ALLOWED_REQUEST_KEYS, AnalysisRequest


def legacy_dict_to_request(data: dict[str, Any]) -> AnalysisRequest:
    """Convert legacy input dict after research defaults; rejects unknown keys."""
    normalized = apply_research_defaults(dict(data))
    analytical = {k: normalized[k] for k in ALLOWED_REQUEST_KEYS if k in normalized}
    for required in ("notes", "dynamics", "instruments", "num_instruments"):
        if required in normalized:
            analytical[required] = normalized[required]
    return AnalysisRequest.from_mapping(analytical)
