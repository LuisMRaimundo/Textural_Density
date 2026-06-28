"""Read-only diagnostics comparing violin arco vs arco con sordina density tables."""

from __future__ import annotations

from typing import Any

from config import DYNAMIC_LEVELS
from instrumentos.registry import resolve_profile

SORDINA_INPUT_KEYWORDS: tuple[str, ...] = (
    "sordina",
    "sordino",
    "muted",
    "con_sordina",
    "con sordina",
)

AUDIT_FLAG_HIGH = "sordina_gt_arco_high"
AUDIT_FLAG_CRITICAL = "sordina_gt_arco_critical"

HIGH_RATIO_THRESHOLD = 1.15
CRITICAL_RATIO_THRESHOLD = 1.50

ANCHOR_DYNAMICS: tuple[str, ...] = ("pp", "mf", "ff")


def input_implies_violin_sordina(instrument_name: str) -> bool:
    """Return True when the raw instrument label suggests muted/sordina violin."""
    normalized = instrument_name.strip().lower()
    normalized_key = normalized.replace("-", "_").replace(" ", "_")
    for keyword in SORDINA_INPUT_KEYWORDS:
        key = keyword.replace(" ", "_")
        if keyword in normalized or key in normalized_key:
            return True
    return False


def _audit_flag_for_ratio(ratio: float | None, sordina_gt_arco: bool) -> str | None:
    if ratio is None or not sordina_gt_arco:
        return None
    if ratio > CRITICAL_RATIO_THRESHOLD:
        return AUDIT_FLAG_CRITICAL
    if ratio > HIGH_RATIO_THRESHOLD:
        return AUDIT_FLAG_HIGH
    return None


def _density_relation_to_arco(sordina_value: float, arco_value: float) -> str:
    if sordina_value > arco_value:
        return "sordina_gt_arco"
    if sordina_value < arco_value:
        return "sordina_lt_arco"
    return "sordina_eq_arco"


def compare_violin_sordina_to_arco() -> list[dict[str, Any]]:
    """
    Compare committed sparse tables for violin arco vs violin sordina.

    Returns one row per shared note and anchor dynamic (pp/mf/ff).
    Diagnostic only — does not modify lookup values.
    """
    from instrumentos import violin, violin_sordina

    rows: list[dict[str, Any]] = []
    shared_notes = sorted(
        set(violin.spectral_data.keys()) & set(violin_sordina.spectral_data.keys())
    )
    for note in shared_notes:
        for dynamic in ANCHOR_DYNAMICS:
            arco_row = violin.spectral_data.get(note, {})
            sordina_row = violin_sordina.spectral_data.get(note, {})
            if dynamic not in arco_row or dynamic not in sordina_row:
                continue
            arco_value = float(arco_row[dynamic])
            sordina_value = float(sordina_row[dynamic])
            ratio = sordina_value / arco_value if arco_value else None
            sordina_gt_arco = sordina_value > arco_value
            rows.append(
                {
                    "note": note,
                    "dynamic": dynamic,
                    "arco_value": arco_value,
                    "sordina_value": sordina_value,
                    "sordina_arco_ratio": ratio,
                    "sordina_gt_arco": sordina_gt_arco,
                    "density_relation_to_arco": _density_relation_to_arco(
                        sordina_value, arco_value
                    ),
                    "audit_flag": _audit_flag_for_ratio(ratio, sordina_gt_arco),
                }
            )
    return rows


def compare_violin_sordina_to_arco_dataframe():
    """Return the table comparison as a pandas DataFrame."""
    import pandas as pd

    return pd.DataFrame(compare_violin_sordina_to_arco())


def _normalize_dynamic(dynamic: str | None, known_dynamics: tuple[str, ...]) -> str:
    dyn = (dynamic or "mf").strip().lower()
    return dyn if dyn in known_dynamics else "mf"


def lookup_module_one_player_density(
    module: Any,
    note: str,
    dynamic: str | None,
    known_dynamics: tuple[str, ...] | None = None,
) -> float:
    """Mirror orchestration lookup without changing production code paths."""
    known = known_dynamics or tuple(DYNAMIC_LEVELS) if DYNAMIC_LEVELS else ANCHOR_DYNAMICS
    dyn_norm = _normalize_dynamic(dynamic, known)
    if dyn_norm in ANCHOR_DYNAMICS:
        return float(module.calcular_densidade(note, dyn_norm))
    pp = module.calcular_densidade(note, "pp")
    mf = module.calcular_densidade(note, "mf")
    ff = module.calcular_densidade(note, "ff")
    return float(
        module.predict_intermediate_dynamics([note], [pp], [mf], [ff])[dyn_norm][0]
    )


def build_event_arco_reference(
    *,
    note: str,
    dynamic: str | None,
    module_name: str | None,
    known_dynamics: tuple[str, ...] | None = None,
) -> tuple[float | None, float | None, str | None]:
    """
    Return (arco_density, ratio, relation) for a resolved lookup event.

    For non-sordina modules, arco_density mirrors the selected module density
    and ratio is 1.0.
    """
    from instrumentos import get_instrument_module

    known = known_dynamics or tuple(DYNAMIC_LEVELS) if DYNAMIC_LEVELS else ANCHOR_DYNAMICS
    selected_module = get_instrument_module(module_name or "violino")
    selected_density = lookup_module_one_player_density(
        selected_module, note, dynamic, known
    )

    if module_name != "violin_sordina":
        return selected_density, 1.0, None

    arco_module = get_instrument_module("violino")
    arco_density = lookup_module_one_player_density(arco_module, note, dynamic, known)
    ratio = selected_density / arco_density if arco_density else None
    relation = _density_relation_to_arco(selected_density, arco_density)
    return arco_density, ratio, relation


def build_event_lookup_trace_row(
    *,
    event: Any,
    one_player_density: float,
    known_dynamics: tuple[str, ...] | None = None,
) -> dict[str, Any]:
    """Build one per-event diagnostic row for analysis trace output."""
    profile = resolve_profile(event.instrument_name)
    resolved_profile_id = profile.instrument_id if profile is not None else "unknown"
    module_name = profile.module_name if profile is not None else None
    note = event.sounding_pitch.note_name or ""
    dynamic = event.dynamic or "mf"

    arco_density, ratio, relation = build_event_arco_reference(
        note=note,
        dynamic=dynamic,
        module_name=module_name,
        known_dynamics=known_dynamics,
    )

    row: dict[str, Any] = {
        "event_id": event.event_id,
        "note": note,
        "dynamic": dynamic,
        "instrument": event.instrument_name,
        "resolved_profile_id": resolved_profile_id,
        "module_name": module_name,
        "one_player_density": float(one_player_density),
        "corresponding_arco_density": arco_density,
        "sordina_arco_ratio": ratio,
        "density_relation_to_arco": relation if module_name == "violin_sordina" else "",
    }

    if module_name == "violin_sordina" and ratio is not None and arco_density is not None:
        row["audit_flag"] = _audit_flag_for_ratio(
            ratio,
            float(one_player_density) > float(arco_density),
        )
    else:
        row["audit_flag"] = None

    return row


def summarize_compare_flags(rows: list[dict[str, Any]] | None = None) -> dict[str, int]:
    """Count audit flags from ``compare_violin_sordina_to_arco`` output."""
    source = rows if rows is not None else compare_violin_sordina_to_arco()
    summary = {
        AUDIT_FLAG_HIGH: 0,
        AUDIT_FLAG_CRITICAL: 0,
        "sordina_gt_arco": 0,
    }
    for row in source:
        if row.get("sordina_gt_arco"):
            summary["sordina_gt_arco"] += 1
        flag = row.get("audit_flag")
        if flag in summary:
            summary[flag] += 1
    return summary
