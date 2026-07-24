# instrumentos/double_bass_sul_tasto.py
"""
Double bass (arco sul tasto) instrument density module.

Dynamic resolution chain (per note):

1. **Workbook anchors:** ``pp``, ``mf`` and ``ff`` imported from Strings Techniques
   Extrapolation Excel exports (``Contrabass-pp.xlsx`` / ``Contrabass_mf.xlsx`` /
   ``Contrabass_ff.xlsx``), column ``estimate_mean`` / ``All_Results``.
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
        "Double bass sul_tasto EWSD table from Strings_techniques_extrapolation "
        "workbooks Contrabass-pp.xlsx / Contrabass_mf.xlsx / Contrabass_ff.xlsx "
        "(assumption-based extrapolation; pp/mf/ff from estimate_mean)."
    ),
    source_url_or_identifier="docs/instrument_acoustic_sources.md#double-bass-sul-tasto",
    extraction_method=(
        "estimate_mean from All_Results for dynamics pp, mf and ff; "
        "GPR interpolation by pitch/dynamic"
    ),
    dynamic_levels=("pp", "mf", "ff"),
    pitch_range=(28, 72),
    uncertainty="high",
    version="2026-07-24",
    source_technique="arco_sul_tasto",
    table_supported_techniques=("arco_sul_tasto",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("double_bass_sul_tasto")

# Workbook pp / mf / ff anchors (45 chromatic rows, E1–C5).
PP_MEASURED: dict[str, float] = {
    'E1': 53.569407,
    'F1': 48.87332,
    'F#1': 45.200968,
    'G1': 42.317982,
    'G#1': 40.048281,
    'A1': 38.256476,
    'A#1': 36.835674,
    'B1': 35.698934,
    'C2': 34.77325,
    'C#2': 33.99537,
    'D2': 33.319144,
    'D#2': 32.725153,
    'E2': 32.19868,
    'F2': 31.72617,
    'F#2': 31.295015,
    'G2': 30.893373,
    'G#2': 30.510043,
    'A2': 30.134388,
    'A#2': 29.756361,
    'B2': 29.369428,
    'C3': 28.971263,
    'C#3': 28.559958,
    'D3': 28.133763,
    'D#3': 27.691094,
    'E3': 27.230548,
    'F3': 26.750908,
    'F#3': 26.251159,
    'G3': 25.730302,
    'G#3': 25.184708,
    'A3': 24.609104,
    'A#3': 23.998921,
    'B3': 23.350431,
    'C4': 22.660818,
    'C#4': 21.928247,
    'D4': 21.151938,
    'D#4': 20.332207,
    'E4': 19.468317,
    'F4': 18.545679,
    'F#4': 17.547966,
    'G4': 16.465659,
    'G#4': 15.296717,
    'A4': 14.046971,
    'A#4': 12.730077,
    'B4': 11.366893,
    'C5': 9.984205,
}

MF_MEASURED: dict[str, float] = {
    'E1': 63.233886,
    'F1': 57.693605,
    'F#1': 53.334987,
    'G1': 49.895148,
    'G#1': 47.17598,
    'A1': 45.025124,
    'A#1': 43.322665,
    'B1': 41.971702,
    'C2': 40.891593,
    'C#2': 40.013154,
    'D2': 39.282476,
    'D#2': 38.666807,
    'E2': 38.138325,
    'F2': 37.67118,
    'F#2': 37.241022,
    'G2': 36.824698,
    'G#2': 36.40009,
    'A2': 35.946108,
    'A#2': 35.44295,
    'B2': 34.878387,
    'C3': 34.249328,
    'C#3': 33.553992,
    'D3': 32.791415,
    'D#3': 31.961508,
    'E3': 31.065106,
    'F3': 30.104003,
    'F#3': 29.080965,
    'G3': 27.999638,
    'G#3': 26.8633,
    'A3': 25.675402,
    'A#3': 24.440683,
    'B3': 23.165133,
    'C4': 21.855908,
    'C#4': 20.521198,
    'D4': 19.170066,
    'D#4': 17.812247,
    'E4': 16.455119,
    'F4': 15.088108,
    'F#4': 13.700559,
    'G4': 12.292175,
    'G#4': 10.872347,
    'A4': 9.458866,
    'A#4': 8.075943,
    'B4': 6.751542,
    'C5': 5.514238,
}

FF_MEASURED: dict[str, float] = {
    'E1': 75.653605,
    'F1': 67.685105,
    'F#1': 61.491459,
    'G1': 56.641474,
    'G#1': 52.819246,
    'A1': 49.788333,
    'A#1': 47.367511,
    'B1': 45.414126,
    'C2': 43.812561,
    'C#2': 42.466266,
    'D2': 41.305184,
    'D#2': 40.296062,
    'E2': 39.41323,
    'F2': 38.633729,
    'F#2': 37.936759,
    'G2': 37.303246,
    'G#2': 36.715516,
    'A2': 36.157057,
    'A#2': 35.612466,
    'B2': 35.071346,
    'C3': 34.52916,
    'C#3': 33.982004,
    'D3': 33.426241,
    'D#3': 32.858512,
    'E3': 32.27574,
    'F3': 31.675152,
    'F#3': 31.054288,
    'G3': 30.410809,
    'G#3': 29.739639,
    'A3': 29.034048,
    'A#3': 28.288219,
    'B3': 27.497406,
    'C4': 26.658019,
    'C#4': 25.767722,
    'D4': 24.825507,
    'D#4': 23.831761,
    'E4': 22.784468,
    'F4': 21.656827,
    'F#4': 20.418797,
    'G4': 19.052411,
    'G#4': 17.55332,
    'A4': 15.93174,
    'A#4': 14.212381,
    'B4': 12.43298,
    'C5': 10.641271,
}

# GPR anchors: pp/mf/ff all from Excel estimate_mean.
spectral_data = {
    'E1': {'pp': 53.569407, 'mf': 63.233886, 'ff': 75.653605},
    'F1': {'pp': 48.87332, 'mf': 57.693605, 'ff': 67.685105},
    'F#1': {'pp': 45.200968, 'mf': 53.334987, 'ff': 61.491459},
    'G1': {'pp': 42.317982, 'mf': 49.895148, 'ff': 56.641474},
    'G#1': {'pp': 40.048281, 'mf': 47.17598, 'ff': 52.819246},
    'A1': {'pp': 38.256476, 'mf': 45.025124, 'ff': 49.788333},
    'A#1': {'pp': 36.835674, 'mf': 43.322665, 'ff': 47.367511},
    'B1': {'pp': 35.698934, 'mf': 41.971702, 'ff': 45.414126},
    'C2': {'pp': 34.77325, 'mf': 40.891593, 'ff': 43.812561},
    'C#2': {'pp': 33.99537, 'mf': 40.013154, 'ff': 42.466266},
    'D2': {'pp': 33.319144, 'mf': 39.282476, 'ff': 41.305184},
    'D#2': {'pp': 32.725153, 'mf': 38.666807, 'ff': 40.296062},
    'E2': {'pp': 32.19868, 'mf': 38.138325, 'ff': 39.41323},
    'F2': {'pp': 31.72617, 'mf': 37.67118, 'ff': 38.633729},
    'F#2': {'pp': 31.295015, 'mf': 37.241022, 'ff': 37.936759},
    'G2': {'pp': 30.893373, 'mf': 36.824698, 'ff': 37.303246},
    'G#2': {'pp': 30.510043, 'mf': 36.40009, 'ff': 36.715516},
    'A2': {'pp': 30.134388, 'mf': 35.946108, 'ff': 36.157057},
    'A#2': {'pp': 29.756361, 'mf': 35.44295, 'ff': 35.612466},
    'B2': {'pp': 29.369428, 'mf': 34.878387, 'ff': 35.071346},
    'C3': {'pp': 28.971263, 'mf': 34.249328, 'ff': 34.52916},
    'C#3': {'pp': 28.559958, 'mf': 33.553992, 'ff': 33.982004},
    'D3': {'pp': 28.133763, 'mf': 32.791415, 'ff': 33.426241},
    'D#3': {'pp': 27.691094, 'mf': 31.961508, 'ff': 32.858512},
    'E3': {'pp': 27.230548, 'mf': 31.065106, 'ff': 32.27574},
    'F3': {'pp': 26.750908, 'mf': 30.104003, 'ff': 31.675152},
    'F#3': {'pp': 26.251159, 'mf': 29.080965, 'ff': 31.054288},
    'G3': {'pp': 25.730302, 'mf': 27.999638, 'ff': 30.410809},
    'G#3': {'pp': 25.184708, 'mf': 26.8633, 'ff': 29.739639},
    'A3': {'pp': 24.609104, 'mf': 25.675402, 'ff': 29.034048},
    'A#3': {'pp': 23.998921, 'mf': 24.440683, 'ff': 28.288219},
    'B3': {'pp': 23.350431, 'mf': 23.165133, 'ff': 27.497406},
    'C4': {'pp': 22.660818, 'mf': 21.855908, 'ff': 26.658019},
    'C#4': {'pp': 21.928247, 'mf': 20.521198, 'ff': 25.767722},
    'D4': {'pp': 21.151938, 'mf': 19.170066, 'ff': 24.825507},
    'D#4': {'pp': 20.332207, 'mf': 17.812247, 'ff': 23.831761},
    'E4': {'pp': 19.468317, 'mf': 16.455119, 'ff': 22.784468},
    'F4': {'pp': 18.545679, 'mf': 15.088108, 'ff': 21.656827},
    'F#4': {'pp': 17.547966, 'mf': 13.700559, 'ff': 20.418797},
    'G4': {'pp': 16.465659, 'mf': 12.292175, 'ff': 19.052411},
    'G#4': {'pp': 15.296717, 'mf': 10.872347, 'ff': 17.55332},
    'A4': {'pp': 14.046971, 'mf': 9.458866, 'ff': 15.93174},
    'A#4': {'pp': 12.730077, 'mf': 8.075943, 'ff': 14.212381},
    'B4': {'pp': 11.366893, 'mf': 6.751542, 'ff': 12.43298},
    'C5': {'pp': 9.984205, 'mf': 5.514238, 'ff': 10.641271},
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
