# instrumentos/violin_sul_ponticello.py
"""
Violin (arco sul ponticello) instrument density module.

Dynamic resolution chain (per note):

1. **Workbook anchors:** ``mf`` and ``ff`` imported from Strings Techniques
   Extrapolation Excel exports (``Violin_mf.xlsx`` / ``Violin_ff.xlsx``),
   column ``estimate_mean`` / ``All_Results``.
2. **Derived pp anchor:** per-note violin arco pp/mf ratio applied to the mf
   workbook value (``instrumentos.mf_anchor_dynamic_extrapolation`` style).
3. **GPR-modelled dynamics:** intermediate / extreme markings predicted by GPR
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
        "Violin sul_ponticello EWSD table from Strings_techniques_extrapolation "
        "workbooks Violin_mf.xlsx / Violin_ff.xlsx (assumption-based extrapolation); "
        "pp derived from violin arco pp/mf ratios."
    ),
    source_url_or_identifier="docs/instrument_acoustic_sources.md#violin-sul-ponticello",
    extraction_method=(
        "estimate_mean from All_Results for dynamics mf and ff; "
        "pp via violin arco pp/mf ratio transfer; GPR interpolation by pitch/dynamic"
    ),
    dynamic_levels=("pp", "mf", "ff"),
    pitch_range=(55, 103),
    uncertainty="high",
    version="2026-07-24",
    source_technique="arco_sul_ponticello",
    table_supported_techniques=("arco_sul_ponticello",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("violin_sul_ponticello")

# Workbook mf / ff anchors (49 chromatic rows, G3–G7).
MF_MEASURED: dict[str, float] = {
    'G3': 54.318634,
    'G#3': 49.841285,
    'A3': 46.210362,
    'A#3': 43.240694,
    'B3': 40.788943,
    'C4': 38.74201,
    'C#4': 37.00881,
    'D4': 35.514422,
    'D#4': 34.195929,
    'E4': 32.999509,
    'F4': 31.878815,
    'F#4': 30.806606,
    'G4': 29.775642,
    'G#4': 28.780532,
    'A4': 27.816452,
    'A#4': 26.879101,
    'B4': 25.964659,
    'C5': 25.069764,
    'C#5': 24.191479,
    'D5': 23.327274,
    'D#5': 22.475328,
    'E5': 21.63645,
    'F5': 20.812396,
    'F#5': 20.004725,
    'G5': 19.214797,
    'G#5': 18.443784,
    'A5': 17.692679,
    'A#5': 16.9623,
    'B5': 16.25331,
    'C6': 15.566219,
    'C#6': 14.901543,
    'D6': 14.259957,
    'D#6': 13.641981,
    'E6': 13.047948,
    'F6': 12.478028,
    'F#6': 11.93224,
    'G6': 11.410473,
    'G#6': 10.912502,
    'A6': 10.438001,
    'A#6': 9.986582,
    'B6': 9.558032,
    'C7': 9.152227,
    'C#7': 8.768928,
    'D7': 8.4078,
    'D#7': 8.068433,
    'E7': 7.750357,
    'F7': 7.453061,
    'F#7': 7.176007,
    'G7': 6.918644,
}

FF_MEASURED: dict[str, float] = {
    'G3': 63.695899,
    'G#3': 57.585202,
    'A3': 52.729776,
    'A#3': 48.836121,
    'B3': 45.683696,
    'C4': 43.103323,
    'C#4': 40.9623,
    'D4': 39.154041,
    'D#4': 37.590849,
    'E4': 36.198919,
    'F4': 34.915412,
    'F#4': 33.70267,
    'G4': 32.548924,
    'G#4': 31.445078,
    'A4': 30.383019,
    'A#4': 29.355527,
    'B4': 28.356201,
    'C5': 27.379401,
    'C#5': 26.420198,
    'D5': 25.474338,
    'D#5': 24.538627,
    'E5': 23.613353,
    'F5': 22.700152,
    'F#5': 21.800544,
    'G5': 20.915927,
    'G#5': 20.047578,
    'A5': 19.19665,
    'A#5': 18.364177,
    'B5': 17.551078,
    'C6': 16.758153,
    'C#6': 15.986111,
    'D6': 15.235588,
    'D#6': 14.507113,
    'E6': 13.8011,
    'F6': 13.117858,
    'F#6': 12.457597,
    'G6': 11.820432,
    'G#6': 11.206389,
    'A6': 10.615415,
    'A#6': 10.04722,
    'B6': 9.499252,
    'C7': 8.967801,
    'C#7': 8.449908,
    'D7': 7.943353,
    'D#7': 7.446602,
    'E7': 6.958749,
    'F7': 6.47947,
    'F#7': 6.008961,
    'G7': 5.547885,
}

# GPR anchors: mf/ff from Excel; pp extrapolated from violin arco dynamic ratios.
spectral_data = {
    'G3': {'pp': 50.559119, 'mf': 54.318634, 'ff': 63.695899},
    'G#3': {'pp': 46.495813, 'mf': 49.841285, 'ff': 57.585202},
    'A3': {'pp': 48.681396, 'mf': 46.210362, 'ff': 52.729776},
    'A#3': {'pp': 38.73407, 'mf': 43.240694, 'ff': 48.836121},
    'B3': {'pp': 41.501535, 'mf': 40.788943, 'ff': 45.683696},
    'C4': {'pp': 45.314494, 'mf': 38.74201, 'ff': 43.103323},
    'C#4': {'pp': 41.900875, 'mf': 37.00881, 'ff': 40.9623},
    'D4': {'pp': 26.994832, 'mf': 35.514422, 'ff': 39.154041},
    'D#4': {'pp': 28.044336, 'mf': 34.195929, 'ff': 37.590849},
    'E4': {'pp': 28.571298, 'mf': 32.999509, 'ff': 36.198919},
    'F4': {'pp': 31.78349, 'mf': 31.878815, 'ff': 34.915412},
    'F#4': {'pp': 27.71098, 'mf': 30.806606, 'ff': 33.70267},
    'G4': {'pp': 27.339173, 'mf': 29.775642, 'ff': 32.548924},
    'G#4': {'pp': 30.685758, 'mf': 28.780532, 'ff': 31.445078},
    'A4': {'pp': 32.093707, 'mf': 27.816452, 'ff': 30.383019},
    'A#4': {'pp': 29.798395, 'mf': 26.879101, 'ff': 29.355527},
    'B4': {'pp': 26.036109, 'mf': 25.964659, 'ff': 28.356201},
    'C5': {'pp': 24.658773, 'mf': 25.069764, 'ff': 27.379401},
    'C#5': {'pp': 30.490494, 'mf': 24.191479, 'ff': 26.420198},
    'D5': {'pp': 21.233548, 'mf': 23.327274, 'ff': 25.474338},
    'D#5': {'pp': 23.187473, 'mf': 22.475328, 'ff': 24.538627},
    'E5': {'pp': 19.93127, 'mf': 21.63645, 'ff': 23.613353},
    'F5': {'pp': 18.052945, 'mf': 20.812396, 'ff': 22.700152},
    'F#5': {'pp': 16.591951, 'mf': 20.004725, 'ff': 21.800544},
    'G5': {'pp': 17.764166, 'mf': 19.214797, 'ff': 20.915927},
    'G#5': {'pp': 17.05612, 'mf': 18.443784, 'ff': 20.047578},
    'A5': {'pp': 15.958229, 'mf': 17.692679, 'ff': 19.19665},
    'A#5': {'pp': 15.11297, 'mf': 16.9623, 'ff': 18.364177},
    'B5': {'pp': 14.872052, 'mf': 16.25331, 'ff': 17.551078},
    'C6': {'pp': 13.928707, 'mf': 15.566219, 'ff': 16.758153},
    'C#6': {'pp': 13.10708, 'mf': 14.901543, 'ff': 15.986111},
    'D6': {'pp': 10.59192, 'mf': 14.259957, 'ff': 15.235588},
    'D#6': {'pp': 11.925918, 'mf': 13.641981, 'ff': 14.507113},
    'E6': {'pp': 11.542515, 'mf': 13.047948, 'ff': 13.8011},
    'F6': {'pp': 11.573698, 'mf': 12.478028, 'ff': 13.117858},
    'F#6': {'pp': 11.536765, 'mf': 11.93224, 'ff': 12.457597},
    'G6': {'pp': 8.699253, 'mf': 11.410473, 'ff': 11.820432},
    'G#6': {'pp': 7.728168, 'mf': 10.912502, 'ff': 11.206389},
    'A6': {'pp': 9.882388, 'mf': 10.438001, 'ff': 10.615415},
    'A#6': {'pp': 8.452864, 'mf': 9.986582, 'ff': 10.04722},
    'B6': {'pp': 8.924796, 'mf': 9.558032, 'ff': 9.499252},
    'C7': {'pp': 6.229405, 'mf': 9.152227, 'ff': 8.967801},
    'C#7': {'pp': 6.226077, 'mf': 8.768928, 'ff': 8.449908},
    'D7': {'pp': 7.594345, 'mf': 8.4078, 'ff': 7.943353},
    'D#7': {'pp': 5.635993, 'mf': 8.068433, 'ff': 7.446602},
    'E7': {'pp': 6.521678, 'mf': 7.750357, 'ff': 6.958749},
    'F7': {'pp': 5.76301, 'mf': 7.453061, 'ff': 6.47947},
    'F#7': {'pp': 6.689779, 'mf': 7.176007, 'ff': 6.008961},
    'G7': {'pp': 4.857944, 'mf': 6.918644, 'ff': 5.547885},
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
