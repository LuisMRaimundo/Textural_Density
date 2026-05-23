"""
Composite weight sensitivity — diagnostic only, not validation.

Varies documented weight sets over normalized subindex values without changing
the default composite formula in ``calculate_metrics``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional


DEFAULT_WEIGHT_SETS: dict[str, dict[str, float]] = {
    "baseline": {
        "event_density": 0.20,
        "interval_compactness": 0.20,
        "registral_density": 0.15,
        "orchestration_mass": 0.15,
        "timbral_orchestration_complexity": 0.15,
        "temporal_vertical_density": 0.15,
    },
    "event_density_emphasis": {
        "event_density": 0.45,
        "interval_compactness": 0.15,
        "registral_density": 0.10,
        "orchestration_mass": 0.10,
        "timbral_orchestration_complexity": 0.10,
        "temporal_vertical_density": 0.10,
    },
    "interval_compactness_emphasis": {
        "event_density": 0.10,
        "interval_compactness": 0.45,
        "registral_density": 0.10,
        "orchestration_mass": 0.10,
        "timbral_orchestration_complexity": 0.10,
        "temporal_vertical_density": 0.15,
    },
    "registral_density_emphasis": {
        "event_density": 0.10,
        "interval_compactness": 0.10,
        "registral_density": 0.45,
        "orchestration_mass": 0.10,
        "timbral_orchestration_complexity": 0.10,
        "temporal_vertical_density": 0.15,
    },
    "orchestration_mass_emphasis": {
        "event_density": 0.10,
        "interval_compactness": 0.10,
        "registral_density": 0.10,
        "orchestration_mass": 0.45,
        "timbral_orchestration_complexity": 0.10,
        "temporal_vertical_density": 0.15,
    },
    "balanced_equal_weights": {
        "event_density": 1 / 6,
        "interval_compactness": 1 / 6,
        "registral_density": 1 / 6,
        "orchestration_mass": 1 / 6,
        "timbral_orchestration_complexity": 1 / 6,
        "temporal_vertical_density": 1 / 6,
    },
}

_SUBINDEX_KEYS = {
    "event_density": "event_count",
    "interval_compactness": "interval_compactness",
    "registral_density": "registral",
    "orchestration_mass": "orchestral_mass",
    "timbral_orchestration_complexity": "timbral_heterogeneity",
    "temporal_vertical_density": "temporal",
}


@dataclass
class SensitivityResult:
    baseline_composite: float
    baseline_weight_set: str
    alternatives: list[dict[str, Any]]
    weight_sets_used: dict[str, dict[str, float]]
    warnings: list[str] = field(default_factory=list)
    disclaimer: str = (
        "Composite weight sensitivity is diagnostic only — not empirical validation. "
        "Does not change the default composite formula in calculate_metrics."
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "baseline_composite": self.baseline_composite,
            "baseline_weight_set": self.baseline_weight_set,
            "alternatives": self.alternatives,
            "weight_sets_used": self.weight_sets_used,
            "warnings": self.warnings,
            "disclaimer": self.disclaimer,
        }


def _extract_normalized(subindices: dict[str, Any], construct: str) -> Optional[float]:
    key = _SUBINDEX_KEYS.get(construct, construct)
    block = subindices.get(key)
    if not isinstance(block, dict):
        return None
    if "normalized" in block and block["normalized"] is not None:
        return float(block["normalized"])
    raw = block.get("raw")
    if isinstance(raw, (int, float)):
        return float(raw)
    if isinstance(raw, dict):
        for candidate in ("player_weighted_count", "event_count", "duration_weighted_event_count"):
            if candidate in raw and raw[candidate] is not None:
                return float(raw[candidate])
    return None


def _weighted_sum(subindices: dict[str, Any], weights: Mapping[str, float]) -> tuple[float, list[str]]:
    warnings: list[str] = []
    total = 0.0
    weight_sum = 0.0
    for construct, w in weights.items():
        val = _extract_normalized(subindices, construct)
        if val is None:
            warnings.append(f"Missing normalized subindex for construct: {construct}")
            continue
        total += float(w) * val
        weight_sum += float(w)
    if weight_sum > 0:
        total /= weight_sum
    return total, warnings


def analyze_composite_weight_sensitivity_from_subindices(
    subindices: dict[str, Any],
    weight_sets: Optional[dict[str, dict[str, float]]] = None,
    *,
    baseline_set: str = "baseline",
) -> SensitivityResult:
    """
    Diagnostic sensitivity over documented weight sets using existing subindices.

    Does not re-run the analytical pipeline or alter default composite output.
    """
    sets = weight_sets or DEFAULT_WEIGHT_SETS
    if baseline_set not in sets:
        raise ValueError(f"Unknown baseline weight set: {baseline_set}")

    baseline_val, base_warnings = _weighted_sum(subindices, sets[baseline_set])
    all_warnings = list(base_warnings)
    alternatives: list[dict[str, Any]] = []

    for name, weights in sets.items():
        if name == baseline_set:
            continue
        val, warns = _weighted_sum(subindices, weights)
        all_warnings.extend(warns)
        delta = val - baseline_val
        alternatives.append(
            {
                "weight_set": name,
                "diagnostic_composite": val,
                "delta_from_baseline": delta,
                "weights": dict(weights),
            }
        )

    alternatives.sort(key=lambda x: abs(x["delta_from_baseline"]), reverse=True)
    ranked = [a["weight_set"] for a in alternatives]

    return SensitivityResult(
        baseline_composite=baseline_val,
        baseline_weight_set=baseline_set,
        alternatives=alternatives,
        weight_sets_used={k: dict(v) for k, v in sets.items()},
        warnings=sorted(set(all_warnings)),
        disclaimer=(
            "Composite weight sensitivity is diagnostic only — not empirical validation. "
            f"Most influential weight sets (by |delta|): {ranked[:3] or 'n/a'}."
        ),
    )


def analyze_composite_weight_sensitivity(
    resultados: dict[str, Any],
    weight_sets: Optional[dict[str, dict[str, float]]] = None,
    *,
    baseline_set: str = "baseline",
) -> SensitivityResult:
    """Convenience wrapper using ``density_subindices`` from a calculate_metrics result."""
    sub = resultados.get("density_subindices", {})
    if not sub:
        return SensitivityResult(
            baseline_composite=0.0,
            baseline_weight_set=baseline_set,
            alternatives=[],
            weight_sets_used=weight_sets or DEFAULT_WEIGHT_SETS,
            warnings=["density_subindices missing from result"],
        )
    return analyze_composite_weight_sensitivity_from_subindices(
        sub, weight_sets=weight_sets, baseline_set=baseline_set
    )
