"""Generate instrumentos/viola_art_harm.py from STE measured CSVs (mf only)."""

from __future__ import annotations

import sys
from pathlib import Path

STE_ROOT = Path(r"E:\PYTHON CODES\CÓDIGOS FINAIS - GIT HUB\Strings_Techniques_Extrapolation")
TD_ROOT = Path(__file__).resolve().parents[1]
OUT = TD_ROOT / "instrumentos" / "viola_art_harm.py"

sys.path.insert(0, str(STE_ROOT / "src"))

from string_technique_model.extrapolation.nonlinear.harmonic_source_resolver import (  # noqa: E402
    clear_harmonic_calibration_cache,
    load_raw_harmonic_calibration_table,
)
from string_technique_model.extrapolation.register_builder import resolve_note  # noqa: E402


def main() -> None:
    clear_harmonic_calibration_cache()
    raw = load_raw_harmonic_calibration_table()
    vla = raw[
        (raw["instrument"] == "vla")
        & (raw["technique"] == "artificial_harmonic")
        & (raw["dynamic"] == "mf")
    ]
    g = vla.groupby("note", as_index=False)["value"].mean()
    rows: list[tuple[int, str, float]] = []
    for _, r in g.iterrows():
        rn = resolve_note(str(r["note"]))
        midi = int(rn[1]) if rn else 0
        rows.append((midi, str(r["note"]), float(r["value"])))
    rows.sort()
    if len(rows) != 35:
        raise SystemExit(f"expected 35 unique viola art mf notes, got {len(rows)}")

    mf_lines = ["MF_MEASURED: dict[str, float] = {"]
    spec_lines = ["spectral_data = {"]
    for _midi, note, val in rows:
        mf_lines.append(f"    '{note}': {val:.6f},")
        spec_lines.append(f"    '{note}': {{'mf': {val:.6f}}},")
    mf_lines.append("}")
    spec_lines.append("}")
    lo, hi = rows[0][0], rows[-1][0]

    text = f'''# instrumentos/viola_art_harm.py
"""
Viola (arco artificial harmonic) instrument density module.

Acoustic calibration: same-instrument measured EWSD at dynamic **mf** only
(35 unique sounding pitches from STE viola measured tables; McGill + Orchidea
multi-collection mean per note).

pp/ff are **not** fabricated by copying mf. Cross-instrument transfer from
violin is forbidden. Unsupported dynamics remain unavailable at the lookup layer.
"""

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="external_acoustic_metadata",
    citation=(
        "Viola artificial_harmonic mf EWSD from Strings_techniques_extrapolation "
        "measured CSVs viola_orchidea_artificial_harmonic_mf.csv / "
        "viola_mcgill_artificial_harmonic_mf.csv (same-instrument measured; "
        "multi-collection mean per sounding pitch)."
    ),
    source_url_or_identifier="docs/instrument_acoustic_sources.md#viola-art-harm",
    extraction_method=(
        "Unique sounding pitches from STE harmonic calibration measured tables; "
        "value = mean across collections at mf; no violin transfer; pp/ff not fabricated."
    ),
    dynamic_levels=("mf",),
    pitch_range=({lo}, {hi}),
    uncertainty="high",
    version="2026-07-24",
    source_technique="arco_artificial_harmonic",
    table_supported_techniques=("arco_artificial_harmonic",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("viola_art_harm")

ACCEPTANCE_STATUS = "accepted_with_limited_coverage"
CALIBRATION_DYNAMIC = "mf"

PP_MEASURED: dict[str, float] = {{}}
{chr(10).join(mf_lines)}
FF_MEASURED: dict[str, float] = {{}}

{chr(10).join(spec_lines)}


def calcular_densidade(nota, dinamica):
    """Compute density from spectral CDM table (MIDI-space lookup, octave-safe)."""
    from instrumentos.spectral_lookup import lookup_spectral_density

    return lookup_spectral_density(
        spectral_data,
        nota,
        dinamica,
        logger=logger,
        preprocess=normalize_note_string,
    )


def predict_intermediate_dynamics(pitches, pp_values, mf_values, ff_values):
    """Predict intermediate dynamics using Gaussian Process Regression."""
    from instrumentos.gpr_dynamic_interpolation import predict_intermediate_dynamics_gpr

    return predict_intermediate_dynamics_gpr(pp_values, mf_values, ff_values, logger=logger)
'''
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT} ({len(rows)} notes, MIDI {lo}-{hi})")


if __name__ == "__main__":
    main()
