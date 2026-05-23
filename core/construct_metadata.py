"""
Construct-level metadata hooks for systematic score-only symbolic analysis.

Maps ``density_subindices`` entries to canonical construct IDs with verification
status, composite inclusion flags, and documented component weights.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional

from core.composite import DOCUMENTED_COMPOSITE_WEIGHTS
from core.sensitivity import DEFAULT_WEIGHT_SETS

CONSTRUCT_MAP: dict[str, str] = {
    "event_count": "event_density",
    "interval_compactness": "interval_compactness",
    "registral": "registral_density",
    "orchestral_mass": "orchestration_mass",
    "timbral_heterogeneity": "timbral_orchestration_complexity",
    "temporal": "temporal_vertical_density",
    "composite": "composite_symbolic_density",
}

IN_COMPOSITE: frozenset[str] = frozenset(
    {
        "event_density",
        "interval_compactness",
        "registral_density",
        "orchestration_mass",
        "timbral_orchestration_complexity",
        "temporal_vertical_density",
    }
)


def _extract_value(entry: dict[str, Any]) -> Any:
    if "value" in entry:
        return entry["value"]
    raw = entry.get("raw")
    if isinstance(raw, dict):
        if "event_count" in raw:
            return raw.get("player_weighted_count", raw.get("event_count"))
        return raw
    return raw


def _extract_normalized(entry: dict[str, Any]) -> Optional[float]:
    if "normalized" in entry:
        return float(entry["normalized"])
    if "normalized_value" in entry:
        return float(entry["normalized_value"])
    return None


def build_construct_records(
    density_subindices: Mapping[str, Any],
    *,
    score_only_mode: bool = True,
) -> dict[str, dict[str, Any]]:
    """
    Build per-construct metadata records from ``density_subindices``.

    Each record includes construct_id, value, source_type, verification_status,
    included_in_composite, and component_weight where applicable.
    """
    baseline_weights = DEFAULT_WEIGHT_SETS["baseline"]
    records: dict[str, dict[str, Any]] = {}

    for sub_key, construct_id in CONSTRUCT_MAP.items():
        entry = density_subindices.get(sub_key)
        if not isinstance(entry, dict):
            continue

        raw = entry.get("raw")
        record: dict[str, Any] = {
            "construct_id": construct_id,
            "value": _extract_value(entry),
            "source_type": entry.get("source_type", "score_derived"),
            "verification_status": entry.get(
                "validation_status", entry.get("verification_status", "verified_by_tests")
            ),
            "assumptions": list(entry.get("assumptions", [])),
            "warnings": list(entry.get("warnings", [])),
            "included_in_composite": construct_id in IN_COMPOSITE,
        }

        if raw is not None and not isinstance(record["value"], (dict, list)):
            record["raw_value"] = raw if not isinstance(raw, dict) else raw
        elif isinstance(raw, dict):
            record["raw_value"] = raw

        norm = _extract_normalized(entry)
        if norm is not None:
            record["normalized_value"] = norm

        if construct_id in baseline_weights:
            record["component_weight"] = float(baseline_weights[construct_id])
        else:
            record["component_weight"] = None

        if construct_id == "composite_symbolic_density":
            record["included_in_composite"] = True
            record["documented_sensitivity_weights"] = dict(DOCUMENTED_COMPOSITE_WEIGHTS)
            if "components" in entry:
                record["components"] = entry["components"]

        records[construct_id] = record

    return records


def attach_construct_records(
    resultados: dict[str, Any],
    *,
    score_only_mode: bool = True,
) -> dict[str, Any]:
    """Add ``construct_records`` block derived from ``density_subindices``."""
    sub = resultados.get("density_subindices")
    if not isinstance(sub, dict):
        return resultados
    meta = resultados.get("metric_metadata", {})
    score_only = bool(meta.get("score_only_mode", score_only_mode))
    resultados["construct_records"] = build_construct_records(sub, score_only_mode=score_only)
    return resultados
