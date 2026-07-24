# instrumentos/viola_sul_tasto.py
"""
Viola (arco sul tasto) instrument density module.

Dynamic resolution chain (per note):

1. **Workbook anchors:** ``pp``, ``mf`` and ``ff`` imported from Strings Techniques
   Extrapolation Excel exports (``Viola_pp.xlsx`` / ``Viola_mf.xlsx`` /
   ``Viola_ff.xlsx``), column ``estimate_mean`` / ``All_Results``.
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
        "Viola sul_tasto EWSD table from Strings_techniques_extrapolation "
        "workbooks Viola_pp.xlsx / Viola_mf.xlsx / Viola_ff.xlsx "
        "(assumption-based extrapolation; pp/mf/ff from estimate_mean)."
    ),
    source_url_or_identifier="docs/instrument_acoustic_sources.md#viola-sul-tasto",
    extraction_method=(
        "estimate_mean from All_Results for dynamics pp, mf and ff; "
        "GPR interpolation by pitch/dynamic"
    ),
    dynamic_levels=("pp", "mf", "ff"),
    pitch_range=(48, 96),
    uncertainty="high",
    version="2026-07-24",
    source_technique="arco_sul_tasto",
    table_supported_techniques=("arco_sul_tasto",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("viola_sul_tasto")

# Workbook pp / mf / ff anchors (49 chromatic rows, C3–C7).
PP_MEASURED: dict[str, float] = {
    'C3': 49.866981,
    'C#3': 45.069476,
    'D3': 41.116471,
    'D#3': 37.828728,
    'E3': 35.067832,
    'F3': 32.72548,
    'F#3': 30.715795,
    'G3': 28.969752,
    'G#3': 27.431136,
    'A3': 26.053582,
    'A#3': 24.798607,
    'B3': 23.639897,
    'C4': 22.562562,
    'C#4': 21.554182,
    'D4': 20.603959,
    'D#4': 19.70251,
    'E4': 18.841691,
    'F4': 18.014466,
    'F#4': 17.214794,
    'G4': 16.437543,
    'G#4': 15.679056,
    'A4': 14.94081,
    'A#4': 14.225943,
    'B4': 13.537003,
    'C5': 12.875979,
    'C#5': 12.244359,
    'D5': 11.643182,
    'D#5': 11.073093,
    'E5': 10.534396,
    'F5': 10.027099,
    'F#5': 9.549866,
    'G5': 9.099025,
    'G#5': 8.671061,
    'A5': 8.262921,
    'A#5': 7.871965,
    'B5': 7.495921,
    'C6': 7.132854,
    'C#6': 6.781134,
    'D6': 6.439411,
    'D#6': 6.106377,
    'E6': 5.77794,
    'F6': 5.44873,
    'F#6': 5.114778,
    'G6': 4.773576,
    'G#6': 4.424079,
    'A6': 4.066682,
    'A#6': 3.703158,
    'B6': 3.336533,
    'C7': 2.970885,
}

MF_MEASURED: dict[str, float] = {
    'C3': 57.591366,
    'C#3': 51.430304,
    'D3': 46.371186,
    'D#3': 42.175482,
    'E3': 38.660725,
    'F3': 35.685631,
    'F#3': 33.13947,
    'G3': 30.934414,
    'G#3': 28.999981,
    'A3': 27.278996,
    'A#3': 25.72481,
    'B3': 24.305346,
    'C4': 23.001624,
    'C#4': 21.797841,
    'D4': 20.680352,
    'D#4': 19.637358,
    'E4': 18.658642,
    'F4': 17.735362,
    'F#4': 16.859874,
    'G4': 16.025591,
    'G#4': 15.227368,
    'A4': 14.464347,
    'A#4': 13.737129,
    'B4': 13.045971,
    'C5': 12.390827,
    'C#5': 11.77139,
    'D5': 11.187136,
    'D#5': 10.637363,
    'E5': 10.121224,
    'F5': 9.637759,
    'F#5': 9.185006,
    'G5': 8.759156,
    'G#5': 8.356618,
    'A5': 7.974258,
    'A#5': 7.609348,
    'B5': 7.259522,
    'C6': 6.92274,
    'C#6': 6.597257,
    'D6': 6.281598,
    'D#6': 5.974305,
    'E6': 5.67089,
    'F6': 5.365412,
    'F#6': 5.053351,
    'G6': 4.731695,
    'G#6': 4.398973,
    'A6': 4.055269,
    'A#6': 3.702186,
    'B6': 3.342746,
    'C7': 2.981203,
}

FF_MEASURED: dict[str, float] = {
    'C3': 59.148328,
    'C#3': 52.704501,
    'D3': 47.428264,
    'D#3': 43.063404,
    'E3': 39.414719,
    'F3': 36.33162,
    'F#3': 33.696491,
    'G3': 31.416334,
    'G#3': 29.416741,
    'A3': 27.637527,
    'A#3': 26.029746,
    'B3': 24.560346,
    'C4': 23.210553,
    'C#4': 21.964771,
    'D4': 20.809504,
    'D#4': 19.733057,
    'E4': 18.72528,
    'F4': 17.777359,
    'F#4': 16.881649,
    'G4': 16.031528,
    'G#4': 15.221816,
    'A4': 14.451808,
    'A#4': 13.72226,
    'B4': 13.03349,
    'C5': 12.385435,
    'C#5': 11.777715,
    'D5': 11.2097,
    'D#5': 10.680556,
    'E5': 10.189304,
    'F5': 9.734858,
    'F#5': 9.314936,
    'G5': 8.925006,
    'G#5': 8.560767,
    'A5': 8.218444,
    'A#5': 7.894714,
    'B5': 7.586656,
    'C6': 7.291699,
    'C#6': 7.007589,
    'D6': 6.732359,
    'D#6': 6.464003,
    'E6': 6.196476,
    'F6': 5.921567,
    'F#6': 5.632624,
    'G6': 5.324769,
    'G#6': 4.995054,
    'A6': 4.642617,
    'A#6': 4.268764,
    'B6': 3.876965,
    'C7': 3.472686,
}

# GPR anchors: pp/mf/ff all from Excel estimate_mean.
spectral_data = {
    'C3': {'pp': 49.866981, 'mf': 57.591366, 'ff': 59.148328},
    'C#3': {'pp': 45.069476, 'mf': 51.430304, 'ff': 52.704501},
    'D3': {'pp': 41.116471, 'mf': 46.371186, 'ff': 47.428264},
    'D#3': {'pp': 37.828728, 'mf': 42.175482, 'ff': 43.063404},
    'E3': {'pp': 35.067832, 'mf': 38.660725, 'ff': 39.414719},
    'F3': {'pp': 32.72548, 'mf': 35.685631, 'ff': 36.33162},
    'F#3': {'pp': 30.715795, 'mf': 33.13947, 'ff': 33.696491},
    'G3': {'pp': 28.969752, 'mf': 30.934414, 'ff': 31.416334},
    'G#3': {'pp': 27.431136, 'mf': 28.999981, 'ff': 29.416741},
    'A3': {'pp': 26.053582, 'mf': 27.278996, 'ff': 27.637527},
    'A#3': {'pp': 24.798607, 'mf': 25.72481, 'ff': 26.029746},
    'B3': {'pp': 23.639897, 'mf': 24.305346, 'ff': 24.560346},
    'C4': {'pp': 22.562562, 'mf': 23.001624, 'ff': 23.210553},
    'C#4': {'pp': 21.554182, 'mf': 21.797841, 'ff': 21.964771},
    'D4': {'pp': 20.603959, 'mf': 20.680352, 'ff': 20.809504},
    'D#4': {'pp': 19.70251, 'mf': 19.637358, 'ff': 19.733057},
    'E4': {'pp': 18.841691, 'mf': 18.658642, 'ff': 18.72528},
    'F4': {'pp': 18.014466, 'mf': 17.735362, 'ff': 17.777359},
    'F#4': {'pp': 17.214794, 'mf': 16.859874, 'ff': 16.881649},
    'G4': {'pp': 16.437543, 'mf': 16.025591, 'ff': 16.031528},
    'G#4': {'pp': 15.679056, 'mf': 15.227368, 'ff': 15.221816},
    'A4': {'pp': 14.94081, 'mf': 14.464347, 'ff': 14.451808},
    'A#4': {'pp': 14.225943, 'mf': 13.737129, 'ff': 13.72226},
    'B4': {'pp': 13.537003, 'mf': 13.045971, 'ff': 13.03349},
    'C5': {'pp': 12.875979, 'mf': 12.390827, 'ff': 12.385435},
    'C#5': {'pp': 12.244359, 'mf': 11.77139, 'ff': 11.777715},
    'D5': {'pp': 11.643182, 'mf': 11.187136, 'ff': 11.2097},
    'D#5': {'pp': 11.073093, 'mf': 10.637363, 'ff': 10.680556},
    'E5': {'pp': 10.534396, 'mf': 10.121224, 'ff': 10.189304},
    'F5': {'pp': 10.027099, 'mf': 9.637759, 'ff': 9.734858},
    'F#5': {'pp': 9.549866, 'mf': 9.185006, 'ff': 9.314936},
    'G5': {'pp': 9.099025, 'mf': 8.759156, 'ff': 8.925006},
    'G#5': {'pp': 8.671061, 'mf': 8.356618, 'ff': 8.560767},
    'A5': {'pp': 8.262921, 'mf': 7.974258, 'ff': 8.218444},
    'A#5': {'pp': 7.871965, 'mf': 7.609348, 'ff': 7.894714},
    'B5': {'pp': 7.495921, 'mf': 7.259522, 'ff': 7.586656},
    'C6': {'pp': 7.132854, 'mf': 6.92274, 'ff': 7.291699},
    'C#6': {'pp': 6.781134, 'mf': 6.597257, 'ff': 7.007589},
    'D6': {'pp': 6.439411, 'mf': 6.281598, 'ff': 6.732359},
    'D#6': {'pp': 6.106377, 'mf': 5.974305, 'ff': 6.464003},
    'E6': {'pp': 5.77794, 'mf': 5.67089, 'ff': 6.196476},
    'F6': {'pp': 5.44873, 'mf': 5.365412, 'ff': 5.921567},
    'F#6': {'pp': 5.114778, 'mf': 5.053351, 'ff': 5.632624},
    'G6': {'pp': 4.773576, 'mf': 4.731695, 'ff': 5.324769},
    'G#6': {'pp': 4.424079, 'mf': 4.398973, 'ff': 4.995054},
    'A6': {'pp': 4.066682, 'mf': 4.055269, 'ff': 4.642617},
    'A#6': {'pp': 3.703158, 'mf': 3.702186, 'ff': 4.268764},
    'B6': {'pp': 3.336533, 'mf': 3.342746, 'ff': 3.876965},
    'C7': {'pp': 2.970885, 'mf': 2.981203, 'ff': 3.472686},
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
