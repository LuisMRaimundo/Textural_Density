# instrumentos/double_bass_sul_ponticello.py
"""
Double bass (arco sul ponticello) instrument density module.

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
        "Double bass sul_ponticello EWSD table from Strings_techniques_extrapolation "
        "workbooks Contrabass-pp.xlsx / Contrabass_mf.xlsx / Contrabass_ff.xlsx "
        "(assumption-based extrapolation; pp/mf/ff from estimate_mean)."
    ),
    source_url_or_identifier="docs/instrument_acoustic_sources.md#double-bass-sul-ponticello",
    extraction_method=(
        "estimate_mean from All_Results for dynamics pp, mf and ff; "
        "GPR interpolation by pitch/dynamic"
    ),
    dynamic_levels=("pp", "mf", "ff"),
    pitch_range=(28, 72),
    uncertainty="high",
    version="2026-07-24",
    source_technique="arco_sul_ponticello",
    table_supported_techniques=("arco_sul_ponticello",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("double_bass_sul_ponticello")

# Workbook pp / mf / ff anchors (45 chromatic rows, E1–C5).
PP_MEASURED: dict[str, float] = {
    'E1': 73.771918,
    'F1': 67.304806,
    'F#1': 62.247509,
    'G1': 58.277268,
    'G#1': 55.1516,
    'A1': 52.684056,
    'A#1': 50.727429,
    'B1': 49.161994,
    'C2': 47.887209,
    'C#2': 46.815968,
    'D2': 45.884718,
    'D#2': 45.066717,
    'E2': 44.341696,
    'F2': 43.69099,
    'F#2': 43.097235,
    'G2': 42.544121,
    'G#2': 42.016227,
    'A2': 41.498902,
    'A#2': 40.978311,
    'B2': 40.445454,
    'C3': 39.89713,
    'C#3': 39.330711,
    'D3': 38.743786,
    'D#3': 38.134175,
    'E3': 37.499944,
    'F3': 36.839418,
    'F#3': 36.151201,
    'G3': 35.433913,
    'G#3': 34.68256,
    'A3': 33.88988,
    'A#3': 33.049581,
    'B3': 32.156528,
    'C4': 31.206841,
    'C#4': 30.197998,
    'D4': 29.128921,
    'D#4': 28.000047,
    'E4': 26.81036,
    'F4': 25.53977,
    'F#4': 24.165792,
    'G4': 22.675316,
    'G#4': 21.065534,
    'A4': 19.344474,
    'A#4': 17.530942,
    'B4': 15.653664,
    'C5': 13.749525,
}

MF_MEASURED: dict[str, float] = {
    'E1': 87.08114,
    'F1': 79.451466,
    'F#1': 73.449092,
    'G1': 68.711994,
    'G#1': 64.967351,
    'A1': 62.005348,
    'A#1': 59.660845,
    'B1': 57.800396,
    'C2': 56.312948,
    'C#2': 55.103226,
    'D2': 54.096988,
    'D#2': 53.249133,
    'E2': 52.521346,
    'F2': 51.878028,
    'F#2': 51.285646,
    'G2': 50.712314,
    'G#2': 50.127575,
    'A2': 49.502383,
    'A#2': 48.809471,
    'B2': 48.031995,
    'C3': 47.165701,
    'C#3': 46.208135,
    'D3': 45.157968,
    'D#3': 44.015079,
    'E3': 42.78062,
    'F3': 41.457058,
    'F#3': 40.048204,
    'G3': 38.559079,
    'G#3': 36.994196,
    'A3': 35.358309,
    'A#3': 33.657943,
    'B3': 31.901348,
    'C4': 30.098378,
    'C#4': 28.260312,
    'D4': 26.39963,
    'D#4': 24.52974,
    'E4': 22.660801,
    'F4': 20.778252,
    'F#4': 18.867421,
    'G4': 16.927896,
    'G#4': 14.97261,
    'A4': 13.026067,
    'A#4': 11.121605,
    'B4': 9.297736,
    'C5': 7.59381,
}

FF_MEASURED: dict[str, float] = {
    'E1': 104.184679,
    'F1': 93.211037,
    'F#1': 84.681595,
    'G1': 78.002546,
    'G#1': 72.73885,
    'A1': 68.564896,
    'A#1': 65.231114,
    'B1': 62.541054,
    'C2': 60.335494,
    'C#2': 58.481474,
    'D2': 56.882516,
    'D#2': 55.492826,
    'E2': 54.277053,
    'F2': 53.203581,
    'F#2': 52.243764,
    'G2': 51.371336,
    'G#2': 50.561957,
    'A2': 49.792887,
    'A#2': 49.042916,
    'B2': 48.297725,
    'C3': 47.551065,
    'C#3': 46.797561,
    'D3': 46.032205,
    'D#3': 45.250369,
    'E3': 44.447818,
    'F3': 43.620731,
    'F#3': 42.765722,
    'G3': 41.879569,
    'G#3': 40.955282,
    'A3': 39.983593,
    'A#3': 38.956492,
    'B3': 37.867441,
    'C4': 36.711498,
    'C#4': 35.485445,
    'D4': 34.187895,
    'D#4': 32.81938,
    'E4': 31.377124,
    'F4': 29.824218,
    'F#4': 28.119292,
    'G4': 26.237604,
    'G#4': 24.173164,
    'A4': 21.940041,
    'A#4': 19.572264,
    'B4': 17.121802,
    'C5': 14.654389,
}

# GPR anchors: pp/mf/ff all from Excel estimate_mean.
spectral_data = {
    'E1': {'pp': 73.771918, 'mf': 87.08114, 'ff': 104.184679},
    'F1': {'pp': 67.304806, 'mf': 79.451466, 'ff': 93.211037},
    'F#1': {'pp': 62.247509, 'mf': 73.449092, 'ff': 84.681595},
    'G1': {'pp': 58.277268, 'mf': 68.711994, 'ff': 78.002546},
    'G#1': {'pp': 55.1516, 'mf': 64.967351, 'ff': 72.73885},
    'A1': {'pp': 52.684056, 'mf': 62.005348, 'ff': 68.564896},
    'A#1': {'pp': 50.727429, 'mf': 59.660845, 'ff': 65.231114},
    'B1': {'pp': 49.161994, 'mf': 57.800396, 'ff': 62.541054},
    'C2': {'pp': 47.887209, 'mf': 56.312948, 'ff': 60.335494},
    'C#2': {'pp': 46.815968, 'mf': 55.103226, 'ff': 58.481474},
    'D2': {'pp': 45.884718, 'mf': 54.096988, 'ff': 56.882516},
    'D#2': {'pp': 45.066717, 'mf': 53.249133, 'ff': 55.492826},
    'E2': {'pp': 44.341696, 'mf': 52.521346, 'ff': 54.277053},
    'F2': {'pp': 43.69099, 'mf': 51.878028, 'ff': 53.203581},
    'F#2': {'pp': 43.097235, 'mf': 51.285646, 'ff': 52.243764},
    'G2': {'pp': 42.544121, 'mf': 50.712314, 'ff': 51.371336},
    'G#2': {'pp': 42.016227, 'mf': 50.127575, 'ff': 50.561957},
    'A2': {'pp': 41.498902, 'mf': 49.502383, 'ff': 49.792887},
    'A#2': {'pp': 40.978311, 'mf': 48.809471, 'ff': 49.042916},
    'B2': {'pp': 40.445454, 'mf': 48.031995, 'ff': 48.297725},
    'C3': {'pp': 39.89713, 'mf': 47.165701, 'ff': 47.551065},
    'C#3': {'pp': 39.330711, 'mf': 46.208135, 'ff': 46.797561},
    'D3': {'pp': 38.743786, 'mf': 45.157968, 'ff': 46.032205},
    'D#3': {'pp': 38.134175, 'mf': 44.015079, 'ff': 45.250369},
    'E3': {'pp': 37.499944, 'mf': 42.78062, 'ff': 44.447818},
    'F3': {'pp': 36.839418, 'mf': 41.457058, 'ff': 43.620731},
    'F#3': {'pp': 36.151201, 'mf': 40.048204, 'ff': 42.765722},
    'G3': {'pp': 35.433913, 'mf': 38.559079, 'ff': 41.879569},
    'G#3': {'pp': 34.68256, 'mf': 36.994196, 'ff': 40.955282},
    'A3': {'pp': 33.88988, 'mf': 35.358309, 'ff': 39.983593},
    'A#3': {'pp': 33.049581, 'mf': 33.657943, 'ff': 38.956492},
    'B3': {'pp': 32.156528, 'mf': 31.901348, 'ff': 37.867441},
    'C4': {'pp': 31.206841, 'mf': 30.098378, 'ff': 36.711498},
    'C#4': {'pp': 30.197998, 'mf': 28.260312, 'ff': 35.485445},
    'D4': {'pp': 29.128921, 'mf': 26.39963, 'ff': 34.187895},
    'D#4': {'pp': 28.000047, 'mf': 24.52974, 'ff': 32.81938},
    'E4': {'pp': 26.81036, 'mf': 22.660801, 'ff': 31.377124},
    'F4': {'pp': 25.53977, 'mf': 20.778252, 'ff': 29.824218},
    'F#4': {'pp': 24.165792, 'mf': 18.867421, 'ff': 28.119292},
    'G4': {'pp': 22.675316, 'mf': 16.927896, 'ff': 26.237604},
    'G#4': {'pp': 21.065534, 'mf': 14.97261, 'ff': 24.173164},
    'A4': {'pp': 19.344474, 'mf': 13.026067, 'ff': 21.940041},
    'A#4': {'pp': 17.530942, 'mf': 11.121605, 'ff': 19.572264},
    'B4': {'pp': 15.653664, 'mf': 9.297736, 'ff': 17.121802},
    'C5': {'pp': 13.749525, 'mf': 7.59381, 'ff': 14.654389},
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
