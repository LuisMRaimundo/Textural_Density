"""
Split regression snapshots: numeric stability vs metadata/epistemic labels.

Metadata text may change after relabelling without implying formula drift.
"""

from __future__ import annotations

from typing import Any


def extract_numeric_snapshot(resultados: dict[str, Any]) -> dict[str, Any]:
    """Stable numeric density and subindex values only."""
    out: dict[str, Any] = {"density": dict(resultados.get("density", {}))}
    subindices: dict[str, Any] = {}
    for key, entry in (resultados.get("density_subindices") or {}).items():
        if not isinstance(entry, dict):
            continue
        snap: dict[str, Any] = {}
        if "normalized" in entry and isinstance(entry["normalized"], (int, float)):
            snap["normalized"] = float(entry["normalized"])
        raw = entry.get("raw")
        if isinstance(raw, (int, float)):
            snap["raw"] = float(raw)
        elif isinstance(raw, dict):
            snap["raw"] = {
                rk: float(rv)
                for rk, rv in raw.items()
                if isinstance(rv, (int, float))
            }
        subindices[key] = snap
    out["density_subindices"] = subindices
    return out


def extract_metadata_snapshot(resultados: dict[str, Any]) -> dict[str, Any]:
    """Epistemic labels, source types, and documented assumptions."""
    mm = resultados.get("metric_metadata") or {}
    metrics = mm.get("metrics") or {}
    inst = metrics.get("density.instrument") or {}
    interval = metrics.get("density.interval") or {}
    weighted = metrics.get("density.weighted") or {}
    orch = (resultados.get("density_subindices") or {}).get("orchestral_mass") or {}
    return {
        "score_only_mode": mm.get("score_only_mode"),
        "metric_schema_version": mm.get("metric_schema_version"),
        "density.interval.source_type": interval.get("source_type"),
        "density.instrument.source_type": inst.get("source_type"),
        "density.instrument.validation_status": inst.get("validation_status"),
        "density.weighted.source_type": weighted.get("source_type"),
        "density.instrument.assumptions": list(inst.get("assumptions") or []),
        "global_assumptions": list(mm.get("assumptions") or []),
        "orchestral_mass.assumptions": list(orch.get("assumptions") or []),
    }
