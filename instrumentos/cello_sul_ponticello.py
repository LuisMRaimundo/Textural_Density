# instrumentos/cello_sul_ponticello.py
"""
Cello (arco sul ponticello) instrument density module.

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
        "Cello sul_ponticello EWSD table from Strings_techniques_extrapolation "
        "workbooks Cello_pp.xlsx / Cello_mf.xlsx / Cello_ff.xlsx "
        "(assumption-based extrapolation; pp/mf/ff from estimate_mean)."
    ),
    source_url_or_identifier="docs/instrument_acoustic_sources.md#cello-sul-ponticello",
    extraction_method=(
        "estimate_mean from All_Results for dynamics pp, mf and ff; "
        "GPR interpolation by pitch/dynamic"
    ),
    dynamic_levels=("pp", "mf", "ff"),
    pitch_range=(36, 84),
    uncertainty="high",
    version="2026-07-24",
    source_technique="arco_sul_ponticello",
    table_supported_techniques=("arco_sul_ponticello",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("cello_sul_ponticello")

# Workbook pp / mf / ff anchors (49 chromatic rows, C2–C6).
PP_MEASURED: dict[str, float] = {
    'C2': 84.801858,
    'C#2': 77.111458,
    'D2': 71.019926,
    'D#2': 66.160972,
    'E2': 62.258192,
    'F2': 59.098533,
    'F#2': 56.513872,
    'G2': 54.368106,
    'G#2': 52.548063,
    'A2': 50.957159,
    'A#2': 49.511658,
    'B2': 48.159562,
    'C3': 46.882513,
    'C#3': 45.66574,
    'D3': 44.495834,
    'D#3': 43.36061,
    'E3': 42.249014,
    'F3': 41.151047,
    'F#3': 40.057726,
    'G3': 38.961058,
    'G#3': 37.85467,
    'A3': 36.737648,
    'A#3': 35.611422,
    'B3': 34.477551,
    'C4': 33.337703,
    'C#4': 32.193645,
    'D4': 31.047232,
    'D#4': 29.900395,
    'E4': 28.755128,
    'F4': 27.613472,
    'F#4': 26.476984,
    'G4': 25.346213,
    'G#4': 24.22186,
    'A4': 23.104917,
    'A#4': 21.996654,
    'B4': 20.898582,
    'C5': 19.81243,
    'C#5': 18.740109,
    'D5': 17.68368,
    'D#5': 16.6445,
    'E5': 15.612709,
    'F5': 14.573409,
    'F#5': 13.516961,
    'G5': 12.439174,
    'G#5': 11.341181,
    'A5': 10.229133,
    'A#5': 9.113661,
    'B5': 8.009031,
    'C6': 6.932019,
}

MF_MEASURED: dict[str, float] = {
    'C2': 92.016727,
    'C#2': 85.062569,
    'D2': 79.403586,
    'D#2': 74.76154,
    'E2': 70.918484,
    'F2': 67.70026,
    'F#2': 64.964709,
    'G2': 62.593252,
    'G#2': 60.484903,
    'A2': 58.552103,
    'A#2': 56.718593,
    'B2': 54.940661,
    'C3': 53.209396,
    'C#3': 51.518776,
    'D3': 49.86344,
    'D#3': 48.238652,
    'E3': 46.640271,
    'F3': 45.064719,
    'F#3': 43.508961,
    'G3': 41.97048,
    'G#3': 40.447933,
    'A3': 38.945166,
    'A#3': 37.467724,
    'B3': 36.020473,
    'C4': 34.607615,
    'C#4': 33.23272,
    'D4': 31.898766,
    'D#4': 30.608177,
    'E4': 29.362868,
    'F4': 28.164268,
    'F#4': 27.01063,
    'G4': 25.894371,
    'G#4': 24.808201,
    'A4': 23.74593,
    'A#4': 22.702409,
    'B4': 21.673464,
    'C5': 20.655853,
    'C#5': 19.647224,
    'D5': 18.646068,
    'D#5': 17.65087,
    'E5': 16.649543,
    'F5': 15.625334,
    'F#5': 14.567154,
    'G5': 13.469951,
    'G#5': 12.334762,
    'A5': 11.168544,
    'A#5': 9.983686,
    'B5': 8.797137,
    'C6': 7.629138,
}

FF_MEASURED: dict[str, float] = {
    'C2': 90.973221,
    'C#2': 86.848774,
    'D2': 83.068123,
    'D#2': 79.581606,
    'E2': 76.34588,
    'F2': 73.322983,
    'F#2': 70.479574,
    'G2': 67.786318,
    'G#2': 65.217397,
    'A2': 62.750116,
    'A#2': 60.364703,
    'B2': 58.048152,
    'C3': 55.794419,
    'C#3': 53.598561,
    'D3': 51.456291,
    'D#3': 49.363937,
    'E3': 47.318397,
    'F3': 45.317106,
    'F#3': 43.357996,
    'G3': 41.43946,
    'G#3': 39.561061,
    'A3': 37.727835,
    'A#3': 35.946287,
    'B3': 34.221779,
    'C4': 32.558599,
    'C#4': 30.960049,
    'D4': 29.42853,
    'D#4': 27.965635,
    'E4': 26.572243,
    'F4': 25.248593,
    'F#4': 23.992597,
    'G4': 22.79827,
    'G#4': 21.659813,
    'A4': 20.572135,
    'A#4': 19.530777,
    'B4': 18.531851,
    'C5': 17.571987,
    'C#5': 16.648281,
    'D5': 15.758251,
    'D#5': 14.899237,
    'E5': 14.061144,
    'F5': 13.230401,
    'F#5': 12.396852,
    'G5': 11.553839,
    'G#5': 10.698132,
    'A5': 9.829846,
    'A#5': 8.952265,
    'B5': 8.07155,
    'C6': 7.196297,
}

# GPR anchors: pp/mf/ff all from Excel estimate_mean.
spectral_data = {
    'C2': {'pp': 84.801858, 'mf': 92.016727, 'ff': 90.973221},
    'C#2': {'pp': 77.111458, 'mf': 85.062569, 'ff': 86.848774},
    'D2': {'pp': 71.019926, 'mf': 79.403586, 'ff': 83.068123},
    'D#2': {'pp': 66.160972, 'mf': 74.76154, 'ff': 79.581606},
    'E2': {'pp': 62.258192, 'mf': 70.918484, 'ff': 76.34588},
    'F2': {'pp': 59.098533, 'mf': 67.70026, 'ff': 73.322983},
    'F#2': {'pp': 56.513872, 'mf': 64.964709, 'ff': 70.479574},
    'G2': {'pp': 54.368106, 'mf': 62.593252, 'ff': 67.786318},
    'G#2': {'pp': 52.548063, 'mf': 60.484903, 'ff': 65.217397},
    'A2': {'pp': 50.957159, 'mf': 58.552103, 'ff': 62.750116},
    'A#2': {'pp': 49.511658, 'mf': 56.718593, 'ff': 60.364703},
    'B2': {'pp': 48.159562, 'mf': 54.940661, 'ff': 58.048152},
    'C3': {'pp': 46.882513, 'mf': 53.209396, 'ff': 55.794419},
    'C#3': {'pp': 45.66574, 'mf': 51.518776, 'ff': 53.598561},
    'D3': {'pp': 44.495834, 'mf': 49.86344, 'ff': 51.456291},
    'D#3': {'pp': 43.36061, 'mf': 48.238652, 'ff': 49.363937},
    'E3': {'pp': 42.249014, 'mf': 46.640271, 'ff': 47.318397},
    'F3': {'pp': 41.151047, 'mf': 45.064719, 'ff': 45.317106},
    'F#3': {'pp': 40.057726, 'mf': 43.508961, 'ff': 43.357996},
    'G3': {'pp': 38.961058, 'mf': 41.97048, 'ff': 41.43946},
    'G#3': {'pp': 37.85467, 'mf': 40.447933, 'ff': 39.561061},
    'A3': {'pp': 36.737648, 'mf': 38.945166, 'ff': 37.727835},
    'A#3': {'pp': 35.611422, 'mf': 37.467724, 'ff': 35.946287},
    'B3': {'pp': 34.477551, 'mf': 36.020473, 'ff': 34.221779},
    'C4': {'pp': 33.337703, 'mf': 34.607615, 'ff': 32.558599},
    'C#4': {'pp': 32.193645, 'mf': 33.23272, 'ff': 30.960049},
    'D4': {'pp': 31.047232, 'mf': 31.898766, 'ff': 29.42853},
    'D#4': {'pp': 29.900395, 'mf': 30.608177, 'ff': 27.965635},
    'E4': {'pp': 28.755128, 'mf': 29.362868, 'ff': 26.572243},
    'F4': {'pp': 27.613472, 'mf': 28.164268, 'ff': 25.248593},
    'F#4': {'pp': 26.476984, 'mf': 27.01063, 'ff': 23.992597},
    'G4': {'pp': 25.346213, 'mf': 25.894371, 'ff': 22.79827},
    'G#4': {'pp': 24.22186, 'mf': 24.808201, 'ff': 21.659813},
    'A4': {'pp': 23.104917, 'mf': 23.74593, 'ff': 20.572135},
    'A#4': {'pp': 21.996654, 'mf': 22.702409, 'ff': 19.530777},
    'B4': {'pp': 20.898582, 'mf': 21.673464, 'ff': 18.531851},
    'C5': {'pp': 19.81243, 'mf': 20.655853, 'ff': 17.571987},
    'C#5': {'pp': 18.740109, 'mf': 19.647224, 'ff': 16.648281},
    'D5': {'pp': 17.68368, 'mf': 18.646068, 'ff': 15.758251},
    'D#5': {'pp': 16.6445, 'mf': 17.65087, 'ff': 14.899237},
    'E5': {'pp': 15.612709, 'mf': 16.649543, 'ff': 14.061144},
    'F5': {'pp': 14.573409, 'mf': 15.625334, 'ff': 13.230401},
    'F#5': {'pp': 13.516961, 'mf': 14.567154, 'ff': 12.396852},
    'G5': {'pp': 12.439174, 'mf': 13.469951, 'ff': 11.553839},
    'G#5': {'pp': 11.341181, 'mf': 12.334762, 'ff': 10.698132},
    'A5': {'pp': 10.229133, 'mf': 11.168544, 'ff': 9.829846},
    'A#5': {'pp': 9.113661, 'mf': 9.983686, 'ff': 8.952265},
    'B5': {'pp': 8.009031, 'mf': 8.797137, 'ff': 8.07155},
    'C6': {'pp': 6.932019, 'mf': 7.629138, 'ff': 7.196297},
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
