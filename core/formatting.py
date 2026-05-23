"""
Human-readable formatting for analysis results (GUI-independent).
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


def _fmt(v: float) -> str:
    return f"{max(0.0, float(v)):.4f}"


def format_output_string(resultados: dict[str, Any]) -> str:
    """Format results dict for display in a text field."""
    try:
        dens = resultados["density"]
        agg = resultados.get("pitch_aggregation") or {}
        event_count = int(agg.get("event_count", len(resultados.get("input_data", {}).get("notes", []))))
        distinct_pitch = int(agg.get("distinct_pitch_count", event_count))
        pitch_polyphony = int(agg.get("pitch_polyphony", distinct_pitch))
        event_doubling = int(agg.get("event_doubling_count", agg.get("doubling_count", 0)))
        player_doubling = int(agg.get("player_doubling_count", 0))
        total_players = int(agg.get("player_count", agg.get("total_player_count", event_count)))
        has_pitch_structure = distinct_pitch >= 2

        pitch_structure_val = float(dens.get("pitch_structure", dens.get("refined", 0)))
        composite_val = float(dens["total"])
        sonic_mass = float(dens.get("sonic_mass", 0))
        instrument_sum = float(dens["instrument"])
        weighted_pitch = float(dens.get("weighted_pitch", 0))
        weighted_orch = float(dens.get("weighted_orchestral", dens.get("weighted", 0)))

        moments = resultados["spectral_moments"]
        spectral_entropy = max(0.0, float(moments.get("spectral_entropy", 0)))
        complexity = max(0.0, float(resultados["additional_metrics"].get("complexity", 0)))

        lines = [
            "==================== PITCH STRUCTURE ====================",
            f"Event Count: {event_count}",
            f"Player Count: {total_players}",
            f"Distinct Pitch Count: {distinct_pitch}",
            f"Pitch Polyphony: {pitch_polyphony}",
            f"Event Doubling Count: {event_doubling}",
            f"Player Doubling Count: {player_doubling}",
        ]
        if not has_pitch_structure:
            lines.append(
                "Note: unison / single pitch — no vertical pitch-structure diversity."
            )
        lines.extend(
            [
                f"Interval Compactness (distinct pitches): {_fmt(dens['interval'])}",
                f"Pitch-Structure Density: {_fmt(pitch_structure_val)}",
                f"Composite Vertical Density: {_fmt(composite_val)}",
                "",
                "================== ORCHESTRAL MASS =====================",
                f"Sonic / Orchestral Mass (linear Qty): {_fmt(sonic_mass)}",
                f"Instrument Density, pressure-equiv (RSS): {_fmt(instrument_sum)}",
                f"Weighted Orchestral Component: {_fmt(weighted_orch)}",
                f"Weighted Pitch Component: {_fmt(weighted_pitch)}",
                "",
                "================ SPECTRAL (distinct pitch bins) ===============",
                f"Centroid: {moments['centroid']['frequency']:.2f} Hz, Note: {moments['centroid']['note']}",
                f"Spread: ±{moments['spread']['deviation']:.2f} Hz",
                f"Entropy: {_fmt(spectral_entropy)}",
                "",
                "=============== ADVANCED METRICS ===============",
                f"Spectral Complexity: {_fmt(complexity)}",
                f"Harmonic Ratio: {resultados['additional_metrics'].get('harmonic_ratio', 0):.4f}",
                "",
                "================== TEXTURE ======================",
            ]
        )

        output_string = "\n".join(lines) + "\n"
        for k, v in resultados["texture"].items():
            if isinstance(v, (int, float)) and np.isfinite(v):
                output_string += f"{k.capitalize()}: {v:.4f}\n"

        output_string += "\n================== TIMBRE ======================\n"
        for k, v in resultados["timbre"].items():
            if k != "family_contributions" and isinstance(v, (int, float)) and np.isfinite(v):
                output_string += f"{k.capitalize()}: {v:.4f}\n"

        output_string += "\n================ ORCHESTRATION ===================\n"
        for k, v in resultados["orchestration"].items():
            if k != "register_distribution" and isinstance(v, (int, float)) and np.isfinite(v):
                output_string += f"{k.capitalize()}: {v:.4f}\n"

        return output_string

    except Exception as e:
        logger.error("Error formatting results: %s", e)
        return f"Error formatting results: {e}"
