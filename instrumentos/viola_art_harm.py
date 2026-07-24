# instrumentos/viola_art_harm.py
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
    pitch_range=(72, 107),
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

PP_MEASURED: dict[str, float] = {}
MF_MEASURED: dict[str, float] = {
    'C5': 35.440618,
    'C#5': 38.356544,
    'D5': 30.801953,
    'D#5': 32.007974,
    'E5': 27.040269,
    'F5': 23.407831,
    'F#5': 26.811268,
    'G5': 39.360046,
    'G#5': 41.629329,
    'A5': 32.400422,
    'A#5': 32.661063,
    'B5': 25.895024,
    'C6': 30.689386,
    'C#6': 36.663760,
    'D6': 34.913013,
    'D#6': 39.457440,
    'E6': 41.418318,
    'F6': 16.930697,
    'F#6': 17.387169,
    'G6': 17.801489,
    'G#6': 18.288071,
    'A6': 20.982103,
    'A#6': 20.731506,
    'B6': 16.824363,
    'C7': 10.403981,
    'C#7': 10.157961,
    'D7': 12.679000,
    'D#7': 16.130693,
    'E7': 16.598377,
    'F7': 10.874147,
    'G7': 10.301420,
    'G#7': 10.203305,
    'A7': 6.380502,
    'A#7': 6.585849,
    'B7': 5.965818,
}
FF_MEASURED: dict[str, float] = {}

spectral_data = {
    'C5': {'mf': 35.440618},
    'C#5': {'mf': 38.356544},
    'D5': {'mf': 30.801953},
    'D#5': {'mf': 32.007974},
    'E5': {'mf': 27.040269},
    'F5': {'mf': 23.407831},
    'F#5': {'mf': 26.811268},
    'G5': {'mf': 39.360046},
    'G#5': {'mf': 41.629329},
    'A5': {'mf': 32.400422},
    'A#5': {'mf': 32.661063},
    'B5': {'mf': 25.895024},
    'C6': {'mf': 30.689386},
    'C#6': {'mf': 36.663760},
    'D6': {'mf': 34.913013},
    'D#6': {'mf': 39.457440},
    'E6': {'mf': 41.418318},
    'F6': {'mf': 16.930697},
    'F#6': {'mf': 17.387169},
    'G6': {'mf': 17.801489},
    'G#6': {'mf': 18.288071},
    'A6': {'mf': 20.982103},
    'A#6': {'mf': 20.731506},
    'B6': {'mf': 16.824363},
    'C7': {'mf': 10.403981},
    'C#7': {'mf': 10.157961},
    'D7': {'mf': 12.679000},
    'D#7': {'mf': 16.130693},
    'E7': {'mf': 16.598377},
    'F7': {'mf': 10.874147},
    'G7': {'mf': 10.301420},
    'G#7': {'mf': 10.203305},
    'A7': {'mf': 6.380502},
    'A#7': {'mf': 6.585849},
    'B7': {'mf': 5.965818},
}


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
