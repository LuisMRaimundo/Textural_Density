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
        "monotone log-CDM ladder enforcement (2026-08-03): pp/mf/ff anchors isotonic-clamped then full DYNAMIC_LEVELS rebuilt via offline internal_default log-linear + adaptive tails; estimate_mean from All_Results for dynamics pp, mf and ff; "
        "duplicate sounding pitches averaged; GPR interpolation by pitch/dynamic"
    ),
    dynamic_levels=('pppp', 'ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', 'ffff'),
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
    'G5': {'pppp': 32.464304, 'ppp': 32.464304, 'pp': 32.464304, 'p': 32.464304, 'mp': 32.464304, 'mf': 32.464304, 'f': 32.464304, 'ff': 32.464304, 'fff': 32.464304, 'ffff': 32.464304},
    'G#5': {'pppp': 35.812839, 'ppp': 35.812839, 'pp': 35.812839, 'p': 35.812839, 'mp': 35.812839, 'mf': 35.812839, 'f': 35.812839, 'ff': 35.812839, 'fff': 35.812839, 'ffff': 35.812839},
    'A5': {'pppp': 31.141235, 'ppp': 31.141235, 'pp': 31.141235, 'p': 31.141235, 'mp': 31.141235, 'mf': 31.141235, 'f': 31.141235, 'ff': 31.141235, 'fff': 31.141235, 'ffff': 31.141235},
    'A#5': {'pppp': 20.990328, 'ppp': 20.990328, 'pp': 20.990328, 'p': 20.990328, 'mp': 20.990328, 'mf': 20.990328, 'f': 20.990328, 'ff': 20.990328, 'fff': 20.990328, 'ffff': 20.990328},
    'B5': {'pppp': 39.036522, 'ppp': 39.036522, 'pp': 39.036522, 'p': 39.036522, 'mp': 39.036522, 'mf': 39.036522, 'f': 39.036522, 'ff': 39.036522, 'fff': 39.036522, 'ffff': 39.036522},
    'C6': {'pppp': 35.657173, 'ppp': 35.657173, 'pp': 35.657173, 'p': 35.657173, 'mp': 35.657173, 'mf': 35.657173, 'f': 35.657173, 'ff': 35.657173, 'fff': 35.657173, 'ffff': 35.657173},
    'C#6': {'pppp': 27.701783, 'ppp': 27.701783, 'pp': 27.701783, 'p': 27.701783, 'mp': 27.701783, 'mf': 27.701783, 'f': 27.701783, 'ff': 27.701783, 'fff': 27.701783, 'ffff': 27.701783},
    'D6': {'pppp': 34.648456, 'ppp': 34.648456, 'pp': 34.648456, 'p': 34.648456, 'mp': 34.648456, 'mf': 34.648456, 'f': 34.648456, 'ff': 34.648456, 'fff': 34.648456, 'ffff': 34.648456},
    'D#6': {'pppp': 35.088779, 'ppp': 35.088779, 'pp': 35.088779, 'p': 35.088779, 'mp': 35.088779, 'mf': 35.088779, 'f': 35.088779, 'ff': 35.088779, 'fff': 35.088779, 'ffff': 35.088779},
    'E6': {'pppp': 36.725176, 'ppp': 36.725176, 'pp': 36.725176, 'p': 36.725176, 'mp': 36.725176, 'mf': 36.725176, 'f': 36.725176, 'ff': 36.725176, 'fff': 36.725176, 'ffff': 36.725176},
    'F6': {'pppp': 16.213369, 'ppp': 16.213369, 'pp': 16.213369, 'p': 16.213369, 'mp': 16.213369, 'mf': 16.213369, 'f': 16.213369, 'ff': 16.213369, 'fff': 16.213369, 'ffff': 16.213369},
    'F#6': {'pppp': 17.590889, 'ppp': 17.590889, 'pp': 17.590889, 'p': 17.590889, 'mp': 17.590889, 'mf': 17.590889, 'f': 17.590889, 'ff': 17.590889, 'fff': 17.590889, 'ffff': 17.590889},
    'G6': {'pppp': 12.000936, 'ppp': 12.000936, 'pp': 12.000936, 'p': 12.000936, 'mp': 12.000936, 'mf': 12.000936, 'f': 12.000936, 'ff': 12.000936, 'fff': 12.000936, 'ffff': 12.000936},
    'G#6': {'pppp': 12.16, 'ppp': 12.16, 'pp': 12.16, 'p': 12.16, 'mp': 12.16, 'mf': 12.16, 'f': 12.16, 'ff': 12.16, 'fff': 12.16, 'ffff': 12.16},
    'A6': {'pppp': 16.429103, 'ppp': 16.429103, 'pp': 16.429103, 'p': 16.429103, 'mp': 16.429103, 'mf': 16.429103, 'f': 16.429103, 'ff': 16.429103, 'fff': 16.429103, 'ffff': 16.429103},
    'A#6': {'pppp': 11.873774, 'ppp': 11.873774, 'pp': 11.873774, 'p': 11.873774, 'mp': 11.873774, 'mf': 11.873774, 'f': 11.873774, 'ff': 11.873774, 'fff': 11.873774, 'ffff': 11.873774},
    'B6': {'pppp': 10.572999, 'ppp': 10.572999, 'pp': 10.572999, 'p': 10.572999, 'mp': 10.572999, 'mf': 10.572999, 'f': 10.572999, 'ff': 10.572999, 'fff': 10.572999, 'ffff': 10.572999},
    'C7': {'pppp': 13.805565, 'ppp': 13.805565, 'pp': 13.805565, 'p': 13.805565, 'mp': 13.805565, 'mf': 13.805565, 'f': 13.805565, 'ff': 13.805565, 'fff': 13.805565, 'ffff': 13.805565},
    'C#7': {'pppp': 12.219019, 'ppp': 12.219019, 'pp': 12.219019, 'p': 12.219019, 'mp': 12.219019, 'mf': 12.219019, 'f': 12.219019, 'ff': 12.219019, 'fff': 12.219019, 'ffff': 12.219019},
    'D7': {'pppp': 12.123898, 'ppp': 12.123898, 'pp': 12.123898, 'p': 12.123898, 'mp': 12.123898, 'mf': 12.123898, 'f': 12.123898, 'ff': 12.123898, 'fff': 12.123898, 'ffff': 12.123898},
    'D#7': {'pppp': 9.109633, 'ppp': 9.109633, 'pp': 9.109633, 'p': 9.109633, 'mp': 9.109633, 'mf': 9.109633, 'f': 9.109633, 'ff': 9.109633, 'fff': 9.109633, 'ffff': 9.109633},
    'E7': {'pppp': 13.156565, 'ppp': 13.156565, 'pp': 13.156565, 'p': 13.156565, 'mp': 13.156565, 'mf': 13.156565, 'f': 13.156565, 'ff': 13.156565, 'fff': 13.156565, 'ffff': 13.156565},
    'F7': {'pppp': 12.787938, 'ppp': 12.787938, 'pp': 12.787938, 'p': 12.787938, 'mp': 12.787938, 'mf': 12.787938, 'f': 12.787938, 'ff': 12.787938, 'fff': 12.787938, 'ffff': 12.787938},
    'F#7': {'pppp': 13.863989, 'ppp': 13.863989, 'pp': 13.863989, 'p': 13.863989, 'mp': 13.863989, 'mf': 13.863989, 'f': 13.863989, 'ff': 13.863989, 'fff': 13.863989, 'ffff': 13.863989},
    'G7': {'pppp': 13.043966, 'ppp': 13.043966, 'pp': 13.043966, 'p': 13.043966, 'mp': 13.043966, 'mf': 13.043966, 'f': 13.043966, 'ff': 13.043966, 'fff': 13.043966, 'ffff': 13.043966},
    'G#7': {'pppp': 16.937995, 'ppp': 16.937995, 'pp': 16.937995, 'p': 16.937995, 'mp': 16.937995, 'mf': 16.937995, 'f': 16.937995, 'ff': 16.937995, 'fff': 16.937995, 'ffff': 16.937995},
    'A7': {'pppp': 6.012039, 'ppp': 6.012039, 'pp': 6.012039, 'p': 6.012039, 'mp': 6.012039, 'mf': 6.012039, 'f': 6.012039, 'ff': 6.012039, 'fff': 6.012039, 'ffff': 6.012039},
    'A#7': {'pppp': 5.863245, 'ppp': 5.863245, 'pp': 5.863245, 'p': 5.863245, 'mp': 5.863245, 'mf': 5.863245, 'f': 5.863245, 'ff': 5.863245, 'fff': 5.863245, 'ffff': 5.863245},
    'B7': {'pppp': 7.439221, 'ppp': 7.439221, 'pp': 7.439221, 'p': 7.439221, 'mp': 7.439221, 'mf': 7.439221, 'f': 7.439221, 'ff': 7.439221, 'fff': 7.439221, 'ffff': 7.439221},
    'C8': {'pppp': 7.439221, 'ppp': 7.439221, 'pp': 7.439221, 'p': 7.439221, 'mp': 7.439221, 'mf': 7.439221, 'f': 7.439221, 'ff': 7.439221, 'fff': 7.439221, 'ffff': 7.439221},
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
