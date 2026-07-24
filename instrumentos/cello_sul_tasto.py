# instrumentos/cello_sul_tasto.py
"""
Cello (arco sul tasto) instrument density module.

Dynamic resolution chain (per note):

1. **Workbook anchors:** ``pp``, ``mf`` and ``ff`` imported from Strings Techniques
   Extrapolation Excel exports (``Cello_pp.xlsx`` / ``Cello_mf.xlsx`` /
   ``Cello_ff.xlsx``), column ``estimate_mean`` / ``All_Results``.
2. **GPR-modelled dynamics:** intermediate / extreme markings predicted by GPR
   on the pp/mf/ff triple.

These workbook values are **assumption-based extrapolations**
(``value_kind=assumption_based_extrapolation``), not Zenodo-measured CDM rows.
Uncertainty is therefore high.

Runtime analysis does not ingest audio; it maps notated pitch + dynamic to these
pre-loaded tables.
"""

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="external_acoustic_metadata",
    citation=(
        "Cello sul_tasto EWSD table from Strings_techniques_extrapolation "
        "workbooks Cello_pp.xlsx / Cello_mf.xlsx / Cello_ff.xlsx "
        "(assumption-based extrapolation; pp/mf/ff from estimate_mean)."
    ),
    source_url_or_identifier="docs/instrument_acoustic_sources.md#cello-sul-tasto",
    extraction_method=(
        "estimate_mean from All_Results for dynamics pp, mf and ff; "
        "GPR interpolation by pitch/dynamic"
    ),
    dynamic_levels=("pp", "mf", "ff"),
    pitch_range=(36, 84),
    uncertainty="high",
    version="2026-07-24",
    source_technique="arco_sul_tasto",
    table_supported_techniques=("arco_sul_tasto",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("cello_sul_tasto")

# Workbook pp / mf / ff anchors (49 chromatic rows, C2–C6).
PP_MEASURED: dict[str, float] = {
    'C2': 61.578788,
    'C#2': 55.994411,
    'D2': 51.571051,
    'D#2': 48.042726,
    'E2': 45.208726,
    'F2': 42.914343,
    'F#2': 41.037494,
    'G2': 39.479348,
    'G#2': 38.157726,
    'A2': 37.002492,
    'A#2': 35.952843,
    'B2': 34.971019,
    'C3': 34.043692,
    'C#3': 33.160133,
    'D3': 32.310607,
    'D#3': 31.486265,
    'E3': 30.679081,
    'F3': 29.881793,
    'F#3': 29.087879,
    'G3': 28.291534,
    'G#3': 27.488132,
    'A3': 26.677008,
    'A#3': 25.8592,
    'B3': 25.035841,
    'C4': 24.208141,
    'C#4': 23.377385,
    'D4': 22.544918,
    'D#4': 21.712143,
    'E4': 20.880508,
    'F4': 20.051496,
    'F#4': 19.226236,
    'G4': 18.405128,
    'G#4': 17.58868,
    'A4': 16.777613,
    'A#4': 15.972849,
    'B4': 15.175485,
    'C5': 14.386777,
    'C#5': 13.608112,
    'D5': 12.840987,
    'D#5': 12.086387,
    'E5': 11.337154,
    'F5': 10.582467,
    'F#5': 9.815328,
    'G5': 9.032695,
    'G#5': 8.235388,
    'A5': 7.427875,
    'A#5': 6.617876,
    'B5': 5.81575,
    'C6': 5.033679,
}

MF_MEASURED: dict[str, float] = {
    'C2': 66.817858,
    'C#2': 61.768103,
    'D2': 57.658838,
    'D#2': 54.28802,
    'E2': 51.497389,
    'F2': 49.160479,
    'F#2': 47.174061,
    'G2': 45.45203,
    'G#2': 43.921054,
    'A2': 42.517554,
    'A#2': 41.186152,
    'B2': 39.895108,
    'C3': 38.637952,
    'C#3': 37.41031,
    'D3': 36.208289,
    'D#3': 35.028451,
    'E3': 33.867788,
    'F3': 32.723702,
    'F#3': 31.59399,
    'G3': 30.476823,
    'G#3': 29.371228,
    'A3': 28.279995,
    'A#3': 27.207152,
    'B3': 26.156232,
    'C4': 25.130286,
    'C#4': 24.131907,
    'D4': 23.163258,
    'D#4': 22.226099,
    'E4': 21.321818,
    'F4': 20.451456,
    'F#4': 19.613743,
    'G4': 18.803173,
    'G#4': 18.014451,
    'A4': 17.243084,
    'A#4': 16.485332,
    'B4': 15.738165,
    'C5': 14.999228,
    'C#5': 14.266813,
    'D5': 13.539825,
    'D#5': 12.817162,
    'E5': 12.090049,
    'F5': 11.346321,
    'F#5': 10.577925,
    'G5': 9.781192,
    'G#5': 8.956876,
    'A5': 8.110028,
    'A#5': 7.249644,
    'B5': 6.388033,
    'C6': 5.539891,
}

FF_MEASURED: dict[str, float] = {
    'C2': 66.060117,
    'C#2': 63.065154,
    'D2': 60.319838,
    'D#2': 57.788107,
    'E2': 55.438488,
    'F2': 53.243414,
    'F#2': 51.178675,
    'G2': 49.22297,
    'G#2': 47.35755,
    'A2': 45.565936,
    'A#2': 43.833771,
    'B2': 42.15161,
    'C3': 40.515064,
    'C#3': 38.920543,
    'D3': 37.364936,
    'D#3': 35.845575,
    'E3': 34.360208,
    'F3': 32.906973,
    'F#3': 31.484367,
    'G3': 30.091224,
    'G#3': 28.727226,
    'A3': 27.396031,
    'A#3': 26.102362,
    'B3': 24.850112,
    'C4': 23.642396,
    'C#4': 22.48161,
    'D4': 21.369499,
    'D#4': 20.307219,
    'E4': 19.295409,
    'F4': 18.334241,
    'F#4': 17.422201,
    'G4': 16.554942,
    'G#4': 15.728252,
    'A4': 14.938436,
    'A#4': 14.182255,
    'B4': 13.456886,
    'C5': 12.759882,
    'C#5': 12.089133,
    'D5': 11.442839,
    'D#5': 10.819067,
    'E5': 10.210486,
    'F5': 9.607243,
    'F#5': 9.001962,
    'G5': 8.389809,
    'G#5': 7.768438,
    'A5': 7.137933,
    'A#5': 6.500678,
    'B5': 5.861148,
    'C6': 5.225584,
}

# GPR anchors: pp/mf/ff all from Excel estimate_mean.
spectral_data = {
    'C2': {'pp': 61.578788, 'mf': 66.817858, 'ff': 66.060117},
    'C#2': {'pp': 55.994411, 'mf': 61.768103, 'ff': 63.065154},
    'D2': {'pp': 51.571051, 'mf': 57.658838, 'ff': 60.319838},
    'D#2': {'pp': 48.042726, 'mf': 54.28802, 'ff': 57.788107},
    'E2': {'pp': 45.208726, 'mf': 51.497389, 'ff': 55.438488},
    'F2': {'pp': 42.914343, 'mf': 49.160479, 'ff': 53.243414},
    'F#2': {'pp': 41.037494, 'mf': 47.174061, 'ff': 51.178675},
    'G2': {'pp': 39.479348, 'mf': 45.45203, 'ff': 49.22297},
    'G#2': {'pp': 38.157726, 'mf': 43.921054, 'ff': 47.35755},
    'A2': {'pp': 37.002492, 'mf': 42.517554, 'ff': 45.565936},
    'A#2': {'pp': 35.952843, 'mf': 41.186152, 'ff': 43.833771},
    'B2': {'pp': 34.971019, 'mf': 39.895108, 'ff': 42.15161},
    'C3': {'pp': 34.043692, 'mf': 38.637952, 'ff': 40.515064},
    'C#3': {'pp': 33.160133, 'mf': 37.41031, 'ff': 38.920543},
    'D3': {'pp': 32.310607, 'mf': 36.208289, 'ff': 37.364936},
    'D#3': {'pp': 31.486265, 'mf': 35.028451, 'ff': 35.845575},
    'E3': {'pp': 30.679081, 'mf': 33.867788, 'ff': 34.360208},
    'F3': {'pp': 29.881793, 'mf': 32.723702, 'ff': 32.906973},
    'F#3': {'pp': 29.087879, 'mf': 31.59399, 'ff': 31.484367},
    'G3': {'pp': 28.291534, 'mf': 30.476823, 'ff': 30.091224},
    'G#3': {'pp': 27.488132, 'mf': 29.371228, 'ff': 28.727226},
    'A3': {'pp': 26.677008, 'mf': 28.279995, 'ff': 27.396031},
    'A#3': {'pp': 25.8592, 'mf': 27.207152, 'ff': 26.102362},
    'B3': {'pp': 25.035841, 'mf': 26.156232, 'ff': 24.850112},
    'C4': {'pp': 24.208141, 'mf': 25.130286, 'ff': 23.642396},
    'C#4': {'pp': 23.377385, 'mf': 24.131907, 'ff': 22.48161},
    'D4': {'pp': 22.544918, 'mf': 23.163258, 'ff': 21.369499},
    'D#4': {'pp': 21.712143, 'mf': 22.226099, 'ff': 20.307219},
    'E4': {'pp': 20.880508, 'mf': 21.321818, 'ff': 19.295409},
    'F4': {'pp': 20.051496, 'mf': 20.451456, 'ff': 18.334241},
    'F#4': {'pp': 19.226236, 'mf': 19.613743, 'ff': 17.422201},
    'G4': {'pp': 18.405128, 'mf': 18.803173, 'ff': 16.554942},
    'G#4': {'pp': 17.58868, 'mf': 18.014451, 'ff': 15.728252},
    'A4': {'pp': 16.777613, 'mf': 17.243084, 'ff': 14.938436},
    'A#4': {'pp': 15.972849, 'mf': 16.485332, 'ff': 14.182255},
    'B4': {'pp': 15.175485, 'mf': 15.738165, 'ff': 13.456886},
    'C5': {'pp': 14.386777, 'mf': 14.999228, 'ff': 12.759882},
    'C#5': {'pp': 13.608112, 'mf': 14.266813, 'ff': 12.089133},
    'D5': {'pp': 12.840987, 'mf': 13.539825, 'ff': 11.442839},
    'D#5': {'pp': 12.086387, 'mf': 12.817162, 'ff': 10.819067},
    'E5': {'pp': 11.337154, 'mf': 12.090049, 'ff': 10.210486},
    'F5': {'pp': 10.582467, 'mf': 11.346321, 'ff': 9.607243},
    'F#5': {'pp': 9.815328, 'mf': 10.577925, 'ff': 9.001962},
    'G5': {'pp': 9.032695, 'mf': 9.781192, 'ff': 8.389809},
    'G#5': {'pp': 8.235388, 'mf': 8.956876, 'ff': 7.768438},
    'A5': {'pp': 7.427875, 'mf': 8.110028, 'ff': 7.137933},
    'A#5': {'pp': 6.617876, 'mf': 7.249644, 'ff': 6.500678},
    'B5': {'pp': 5.81575, 'mf': 6.388033, 'ff': 5.861148},
    'C6': {'pp': 5.033679, 'mf': 5.539891, 'ff': 5.225584},
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
