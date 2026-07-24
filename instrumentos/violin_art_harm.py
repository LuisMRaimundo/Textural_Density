# instrumentos/violin_art_harm.py
"""
Violin (arco artificial harmonic) instrument density module.

Dynamic resolution chain (per note):

1. **Workbook anchors:** ``pp``, ``mf`` and ``ff`` imported from Strings Techniques
   Extrapolation Excel exports (``Violin_pp_hamro.xlsx`` / ``Violin_mf_harmo.xlsx`` /
   ``Violin_ff_harmo.xlsx``), column ``estimate_mean`` / ``All_Results``.
2. **GPR-modelled dynamics:** intermediate / extreme markings predicted by GPR
   on the pp/mf/ff triple.

These workbook values are calibrated / assumption-based harmonic descriptor
lookups from Strings Techniques Extrapolation (not Zenodo ordinary CDM rows).
Uncertainty is therefore high.

Runtime analysis does not ingest audio; it maps notated pitch + dynamic to these
pre-loaded tables.
"""

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="external_acoustic_metadata",
    citation=(
        "Violin artificial_harmonic EWSD table from Strings_techniques_extrapolation "
        "workbooks Violin_pp_hamro.xlsx / Violin_mf_harmo.xlsx / Violin_ff_harmo.xlsx "
        "(calibrated harmonic descriptor lookup / assumption-based dynamic transfer)."
    ),
    source_url_or_identifier="docs/instrument_acoustic_sources.md#violin-art-harm",
    extraction_method=(
        "estimate_mean from All_Results for dynamics pp, mf and ff; "
        "duplicate sounding pitches averaged; GPR interpolation by pitch/dynamic"
    ),
    dynamic_levels=("pp", "mf", "ff"),
    pitch_range=(79, 108),
    uncertainty="high",
    version="2026-07-24",
    source_technique="arco_artificial_harmonic",
    table_supported_techniques=("arco_artificial_harmonic",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("violin_art_harm")

# Workbook pp / mf / ff anchors (30 chromatic sounding rows, G5–C8).
PP_MEASURED: dict[str, float] = {
    'G5': 32.464304,
    'G#5': 35.812839,
    'A5': 31.141235,
    'A#5': 20.990328,
    'B5': 39.036522,
    'C6': 35.657173,
    'C#6': 27.701783,
    'D6': 34.648456,
    'D#6': 35.088779,
    'E6': 36.725176,
    'F6': 16.213369,
    'F#6': 17.590889,
    'G6': 12.000936,
    'G#6': 12.16,
    'A6': 16.429103,
    'A#6': 11.873774,
    'B6': 10.572999,
    'C7': 13.805565,
    'C#7': 12.219019,
    'D7': 12.123898,
    'D#7': 9.109633,
    'E7': 13.156565,
    'F7': 12.787938,
    'F#7': 13.863989,
    'G7': 13.043966,
    'G#7': 16.937995,
    'A7': 6.012039,
    'A#7': 5.863245,
    'B7': 7.439221,
    'C8': 7.439221,
}

MF_MEASURED: dict[str, float] = {
    'G5': 32.464304,
    'G#5': 35.812839,
    'A5': 31.141235,
    'A#5': 20.990328,
    'B5': 39.036522,
    'C6': 35.657173,
    'C#6': 27.701783,
    'D6': 34.648456,
    'D#6': 35.088779,
    'E6': 36.725176,
    'F6': 16.213369,
    'F#6': 17.590889,
    'G6': 12.000936,
    'G#6': 12.16,
    'A6': 16.429103,
    'A#6': 11.873774,
    'B6': 10.572999,
    'C7': 13.805565,
    'C#7': 12.219019,
    'D7': 12.123898,
    'D#7': 9.109633,
    'E7': 13.156565,
    'F7': 12.787938,
    'F#7': 13.863989,
    'G7': 13.043966,
    'G#7': 16.937995,
    'A7': 6.012039,
    'A#7': 5.863245,
    'B7': 7.439221,
    'C8': 7.439221,
}

FF_MEASURED: dict[str, float] = {
    'G5': 32.464304,
    'G#5': 35.812839,
    'A5': 31.141235,
    'A#5': 20.990328,
    'B5': 39.036522,
    'C6': 35.657173,
    'C#6': 27.701783,
    'D6': 34.648456,
    'D#6': 35.088779,
    'E6': 36.725176,
    'F6': 16.213369,
    'F#6': 17.590889,
    'G6': 12.000936,
    'G#6': 12.16,
    'A6': 16.429103,
    'A#6': 11.873774,
    'B6': 10.572999,
    'C7': 13.805565,
    'C#7': 12.219019,
    'D7': 12.123898,
    'D#7': 9.109633,
    'E7': 13.156565,
    'F7': 12.787938,
    'F#7': 13.863989,
    'G7': 13.043966,
    'G#7': 16.937995,
    'A7': 6.012039,
    'A#7': 5.863245,
    'B7': 7.439221,
    'C8': 7.439221,
}

# GPR anchors: pp/mf/ff from Excel harmonic workbooks.
spectral_data = {
    'G5': {'pp': 32.464304, 'mf': 32.464304, 'ff': 32.464304},
    'G#5': {'pp': 35.812839, 'mf': 35.812839, 'ff': 35.812839},
    'A5': {'pp': 31.141235, 'mf': 31.141235, 'ff': 31.141235},
    'A#5': {'pp': 20.990328, 'mf': 20.990328, 'ff': 20.990328},
    'B5': {'pp': 39.036522, 'mf': 39.036522, 'ff': 39.036522},
    'C6': {'pp': 35.657173, 'mf': 35.657173, 'ff': 35.657173},
    'C#6': {'pp': 27.701783, 'mf': 27.701783, 'ff': 27.701783},
    'D6': {'pp': 34.648456, 'mf': 34.648456, 'ff': 34.648456},
    'D#6': {'pp': 35.088779, 'mf': 35.088779, 'ff': 35.088779},
    'E6': {'pp': 36.725176, 'mf': 36.725176, 'ff': 36.725176},
    'F6': {'pp': 16.213369, 'mf': 16.213369, 'ff': 16.213369},
    'F#6': {'pp': 17.590889, 'mf': 17.590889, 'ff': 17.590889},
    'G6': {'pp': 12.000936, 'mf': 12.000936, 'ff': 12.000936},
    'G#6': {'pp': 12.16, 'mf': 12.16, 'ff': 12.16},
    'A6': {'pp': 16.429103, 'mf': 16.429103, 'ff': 16.429103},
    'A#6': {'pp': 11.873774, 'mf': 11.873774, 'ff': 11.873774},
    'B6': {'pp': 10.572999, 'mf': 10.572999, 'ff': 10.572999},
    'C7': {'pp': 13.805565, 'mf': 13.805565, 'ff': 13.805565},
    'C#7': {'pp': 12.219019, 'mf': 12.219019, 'ff': 12.219019},
    'D7': {'pp': 12.123898, 'mf': 12.123898, 'ff': 12.123898},
    'D#7': {'pp': 9.109633, 'mf': 9.109633, 'ff': 9.109633},
    'E7': {'pp': 13.156565, 'mf': 13.156565, 'ff': 13.156565},
    'F7': {'pp': 12.787938, 'mf': 12.787938, 'ff': 12.787938},
    'F#7': {'pp': 13.863989, 'mf': 13.863989, 'ff': 13.863989},
    'G7': {'pp': 13.043966, 'mf': 13.043966, 'ff': 13.043966},
    'G#7': {'pp': 16.937995, 'mf': 16.937995, 'ff': 16.937995},
    'A7': {'pp': 6.012039, 'mf': 6.012039, 'ff': 6.012039},
    'A#7': {'pp': 5.863245, 'mf': 5.863245, 'ff': 5.863245},
    'B7': {'pp': 7.439221, 'mf': 7.439221, 'ff': 7.439221},
    'C8': {'pp': 7.439221, 'mf': 7.439221, 'ff': 7.439221},
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
