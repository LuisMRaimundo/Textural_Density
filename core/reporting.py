"""
Interpretability and reporting helpers (Phase 9).

Provides plain-language slice explanations and robustness (sensitivity) analysis.
Sensitivity output is explicitly not empirical validation.
"""

from __future__ import annotations

from copy import deepcopy
from itertools import combinations
from typing import Any, Optional

from config import COMPOSITE_HARMONIC_DAMPING, MAX_DENS_GLOBAL, USE_LOG_COMPRESSION
from microtonal import note_to_midi


def explain_score_slice(resultados: dict[str, Any]) -> str:
    """
    Score-only explanation of why a vertical slice is dense in symbolic terms.

    Does not use hearing, loudness, masking, or perception language.
    """
    lines: list[str] = []
    meta = resultados.get("metric_metadata", {})
    sub = resultados.get("density_subindices", {})
    density = resultados.get("density", {})

    score_only = meta.get("score_only_mode", True)
    lines.append("=== Score-only vertical slice explanation ===")
    lines.append(
        f"score_only_mode={score_only}."
    )
    lines.append(f"validation_status={meta.get('validation_status', 'verified_only')}.")
    lines.append("")

    total = float(density.get("total", 0.0))
    lines.append(f"Composite symbolic vertical density: {total:.4f}")
    lines.append("")

    composite = sub.get("composite", {})
    dominant = composite.get("dominant_factors", [])
    if dominant:
        lines.append(
            "Dominant score-derived factors: " + ", ".join(dominant) + "."
        )

    drivers: list[str] = []
    ec = sub.get("event_count", {}).get("raw", {})
    if isinstance(ec, dict) and ec.get("event_count", 0) >= 3:
        drivers.append("many simultaneous symbolic events")
    ic = float(density.get("interval", 0))
    if ic > float(density.get("instrument", 0)):
        drivers.append("tight interval compactness in pitch space")
    registral = sub.get("registral", {}).get("raw", {})
    span = registral.get("pitch_span_semitones") if isinstance(registral, dict) else None
    if span is not None and float(span) < 5:
        drivers.append("register compression (narrow pitch span)")
    elif span is not None and float(span) > 12:
        drivers.append("wide registral spread (reduces cohesion)")
    mass = float(density.get("sonic_mass", 0))
    if mass > 1.5:
        drivers.append("symbolic orchestration mass (written dynamics, player counts)")

    if drivers:
        lines.append("This slice appears dense in score terms because of: " + "; ".join(drivers) + ".")
    else:
        lines.append("Density drivers are moderate across event count, intervals, register, and orchestration metadata.")
    lines.append("")

    lines.append("## What is not claimed")
    lines.append(
        "- No audio waveform analysis; no measured spectra; no auditory perception model."
    )
    lines.append(
        "- Written dynamics are symbolic score markings, not SPL or loudness."
    )
    lines.append(
        "- Instrument density uses externally sourced acoustic metadata (GPR tables) where available; "
        "not live audio analysis."
    )

    lines.append("")
    lines.append(
        "Strictly symbolic mode: score input only; instrument density applies pre-loaded "
        "external acoustic metadata where GPR modules exist."
    )

    return "\n".join(lines)


def explain_vertical_slice(resultados: dict[str, Any]) -> str:
    """
    Explain why a vertical slice received its density score.

    Args:
        resultados: Output dict from ``calculate_metrics`` (includes ``metric_metadata``,
            ``density_subindices`` when Phase 3+ pipeline ran).

    Returns:
        Multi-paragraph plain-language explanation string.
    """
    lines: list[str] = []
    density = resultados.get("density", {})
    sub = resultados.get("density_subindices", {})
    meta = resultados.get("metric_metadata", {})
    input_data = resultados.get("input_data", {})

    total = float(density.get("total", 0.0))
    lines.append(f"Composite density (total): {total:.4f}")
    lines.append("")

    # --- Primary drivers ---
    lines.append("## Primary contributors")
    composite = sub.get("composite", {})
    dominant = composite.get("dominant_factors", [])
    if dominant:
        lines.append(
            "The composite score is most influenced by: "
            + ", ".join(f"`{f}`" for f in dominant)
            + "."
        )
    else:
        lines.append(
            "Composite drivers: refined density, cohesion (register span), "
            "complexity, harmonic adjustment, and dynamic boost."
        )

    drivers: list[str] = []
    ic = float(density.get("interval", 0))
    inst = float(density.get("instrument", 0))
    mass = float(density.get("sonic_mass", 0))
    if ic >= inst:
        drivers.append("pitch compactness (interval density)")
    else:
        drivers.append("orchestral/instrument density")
    if mass > 1.5:
        drivers.append("symbolic dynamics and player counts (sonic mass)")
    registral = sub.get("registral", {}).get("raw", {})
    span = registral.get("pitch_span_semitones")
    if span is not None and float(span) > 12:
        drivers.append("wide registral spread (reduces cohesion)")
    elif span is not None and float(span) < 5:
        drivers.append("narrow registral clustering")
    lines.append("This vertical appears dense mainly because of: " + "; ".join(drivers) + ".")
    lines.append("")

    # --- Interval pairs ---
    notes = input_data.get("notes", [])
    if len(notes) >= 2:
        lines.append("## Interval compactness (not sensory dissonance)")
        pairs = _top_interval_pairs(notes, top_n=3)
        for n1, n2, w in pairs:
            st = abs(note_to_midi(n1) - note_to_midi(n2))
            lines.append(f"- Pair {n1}–{n2} ({st:.1f} st): decay weight ≈ {w:.4f}")
        lines.append("")

    # --- Orchestral mass ---
    instruments = input_data.get("instruments", [])
    numeros = input_data.get("num_instruments", [])
    dynamics = input_data.get("dynamics", [])
    if instruments:
        lines.append("## Orchestral mass contributors")
        contrib = []
        for inst, num, dyn in zip(instruments, numeros, dynamics):
            contrib.append(f"{inst} ×{num} ({dyn})")
        lines.append("Events: " + "; ".join(contrib))
        lines.append("Dynamics are symbolic score markings — not SPL measurements.")
        lines.append("")

    # --- Register ---
    occ = registral.get("register_band_occupancy")
    if occ:
        lines.append("## Register occupancy")
        for band, frac in sorted(occ.items(), key=lambda kv: -kv[1]):
            lines.append(f"- {band}: {float(frac):.0%}")
        lines.append("")

    # --- Metadata proxies ---
    lines.append("## Metadata proxies and options")
    low_conf = [
        k
        for k, v in meta.get("metrics", {}).items()
        if v.get("confidence") == "low"
    ]
    if low_conf:
        lines.append("Low-confidence metrics: " + ", ".join(low_conf) + ".")
    lines.append("Non-notated virtual pitches are not generated (removed feature).")
    lines.append("")

    # --- Warnings and limitations ---
    warnings = list(meta.get("warnings", [])) + list(composite.get("warnings", []))
    if warnings:
        lines.append("## Warnings")
        for w in warnings[:8]:
            lines.append(f"- {w}")
        if len(warnings) > 8:
            lines.append(f"- … and {len(warnings) - 8} more.")
        lines.append("")

    lines.append("## Limitations")
    lines.extend(
        [
            "- Score/information analysis only — no measured audio spectra.",
            "- Some instruments lack GPR acoustic tables and use coarse register/dynamic fallbacks.",
            "- Composite density is a heuristic index, not validated perceptual density.",
            f"- Normalization: MAX_DENS_GLOBAL={MAX_DENS_GLOBAL}, "
            f"log compression={'on' if USE_LOG_COMPRESSION else 'off'}.",
        ]
    )

    return "\n".join(lines)


def format_interpretability_report(resultados: dict[str, Any]) -> str:
    """
    Extended text report: legacy density block + metadata + subindices + explanation.
    """
    from core.formatting import format_output_string

    sections = [
        format_output_string(resultados),
        "",
        "=" * 20 + " METRIC METADATA " + "=" * 20,
        _format_metadata_summary(resultados.get("metric_metadata", {})),
        "",
        "=" * 20 + " DENSITY SUBINDICES " + "=" * 20,
        _format_subindices_summary(resultados.get("density_subindices", {})),
        "",
        "=" * 20 + " INTERPRETATION " + "=" * 20,
        explain_vertical_slice(resultados),
    ]
    return "\n".join(sections)


def run_sensitivity_analysis(
    input_data: dict[str, Any],
    *,
    include_lambda: bool = False,
) -> dict[str, Any]:
    """
    Robustness analysis: vary parameters and report total-density changes.

    This is sensitivity analysis, not empirical validation.
    """
    from core.pipeline import calculate_metrics

    baseline, _, _ = calculate_metrics(input_data)
    base_total = float(baseline["density"]["total"])
    variations: list[dict[str, Any]] = []

    def _record(parameter: str, label: str, data: dict[str, Any]) -> None:
        resultados, _, _ = calculate_metrics(data)
        total = float(resultados["density"]["total"])
        delta = total - base_total
        variations.append(
            {
                "parameter": parameter,
                "label": label,
                "total_density": total,
                "delta": delta,
                "delta_percent": (100.0 * delta / base_total) if base_total else 0.0,
            }
        )

    # Weight factor extremes
    for wf, label in ((0.0, "interval_only"), (1.0, "instrument_only")):
        data = deepcopy(input_data)
        data["weight_factor"] = wf
        _record("weight_factor", label, data)

    # Dynamics: all loud
    if input_data.get("notes"):
        loud = deepcopy(input_data)
        loud["dynamics"] = ["ff"] * len(loud["notes"])
        _record("dynamics", "all_ff", loud)

    # Player count doubling
    if input_data.get("num_instruments"):
        doubled = deepcopy(input_data)
        doubled["num_instruments"] = [max(1, int(n) * 2) for n in doubled["num_instruments"]]
        _record("num_instruments", "doubled", doubled)

    # Lambda (optional; patches calibrated loader)
    if include_lambda:
        import densidade_intervalar as di

        original_load = di.load_calibrated_parameters
        for lamb, label in ((0.03, "lambda_0.03"), (0.08, "lambda_0.08")):
            data = deepcopy(input_data)

            def _load(_l=lamb, _orig=original_load):
                return _l

            di.load_calibrated_parameters = _load
            try:
                _record("lambda", label, data)
            finally:
                di.load_calibrated_parameters = original_load

    return {
        "baseline_total_density": base_total,
        "variations": variations,
        "disclaimer": (
            "Robustness/sensitivity analysis only — not empirical validation. "
            "Shows how heuristic outputs respond to parameter changes."
        ),
        "normalization": {
            "MAX_DENS_GLOBAL": MAX_DENS_GLOBAL,
            "COMPOSITE_HARMONIC_DAMPING": COMPOSITE_HARMONIC_DAMPING,
            "USE_LOG_COMPRESSION": USE_LOG_COMPRESSION,
        },
    }


def format_sensitivity_report(sensitivity: dict[str, Any]) -> str:
    """Format sensitivity analysis as readable text."""
    lines = [
        "=== SENSITIVITY ANALYSIS (robustness, not validation) ===",
        sensitivity.get("disclaimer", ""),
        "",
        f"Baseline total density: {sensitivity['baseline_total_density']:.4f}",
        "",
        "Variations:",
    ]
    for var in sensitivity.get("variations", []):
        lines.append(
            f"- {var['parameter']} ({var['label']}): "
            f"total={var['total_density']:.4f}, "
            f"Δ={var['delta']:+.4f} ({var['delta_percent']:+.1f}%)"
        )
    return "\n".join(lines)


def _top_interval_pairs(
    notes: list[str],
    top_n: int = 3,
) -> list[tuple[str, str, float]]:
    from densidade_intervalar import load_calibrated_parameters, modified_exponential_decay

    lamb = load_calibrated_parameters()
    pairs: list[tuple[str, str, float]] = []
    for i, j in combinations(range(len(notes)), 2):
        delta_st = abs(note_to_midi(notes[i]) - note_to_midi(notes[j]))
        delta = delta_st * 2.0
        weight = float(modified_exponential_decay(delta, lamb))
        pairs.append((notes[i], notes[j], weight))
    pairs.sort(key=lambda p: p[2], reverse=True)
    return pairs[:top_n]


def _format_metadata_summary(meta: dict[str, Any]) -> str:
    if not meta:
        return "(metric_metadata not present)"
    lines = []
    for key, payload in meta.get("metrics", {}).items():
        lines.append(
            f"{key}: value={payload.get('value')} "
            f"source={payload.get('source_type')} "
            f"status={payload.get('validation_status')} "
            f"confidence={payload.get('confidence')}"
        )
    norm = meta.get("normalization", {})
    if norm:
        lines.append(f"Normalization constants: {norm}")
    return "\n".join(lines) if lines else "(empty)"


def _format_subindices_summary(sub: dict[str, Any]) -> str:
    if not sub:
        return "(density_subindices not present)"
    lines = []
    for name, payload in sub.items():
        if name == "composite":
            lines.append(
                f"composite: {payload.get('value')} "
                f"(components: {list(payload.get('components', {}).keys())})"
            )
        elif isinstance(payload, dict) and "raw" in payload:
            lines.append(
                f"{name}: raw={payload.get('raw')} "
                f"source={payload.get('source_type')} "
                f"confidence={payload.get('confidence')}"
            )
    return "\n".join(lines) if lines else "(empty)"
