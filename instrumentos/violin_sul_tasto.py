# instrumentos/violin_sul_tasto.py
"""
Violin (arco sul tasto) instrument density module.

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
        "Violin sul_tasto EWSD table from Strings_techniques_extrapolation "
        "workbooks Violin_mf.xlsx / Violin_ff.xlsx (assumption-based extrapolation); "
        "pp derived from violin arco pp/mf ratios."
    ),
    source_url_or_identifier="docs/instrument_acoustic_sources.md#violin-sul-tasto",
    extraction_method=(
        "estimate_mean from All_Results for dynamics mf and ff; "
        "pp via violin arco pp/mf ratio transfer; GPR interpolation by pitch/dynamic"
    ),
    dynamic_levels=("pp", "mf", "ff"),
    pitch_range=(55, 103),
    uncertainty="high",
    version="2026-07-24",
    source_technique="arco_sul_tasto",
    table_supported_techniques=("arco_sul_tasto",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("violin_sul_tasto")

# Workbook mf / ff anchors (49 chromatic rows, G3–G7).
MF_MEASURED: dict[str, float] = {
    'G3': 39.443424,
    'G#3': 36.192201,
    'A3': 33.55561,
    'A#3': 31.399188,
    'B3': 29.618852,
    'C4': 28.132473,
    'C#4': 26.873912,
    'D4': 25.788763,
    'D#4': 24.831341,
    'E4': 23.962562,
    'F4': 23.148771,
    'F#4': 22.370187,
    'G4': 21.621554,
    'G#4': 20.898955,
    'A4': 20.19889,
    'A#4': 19.518233,
    'B4': 18.854212,
    'C5': 18.204385,
    'C#5': 17.566619,
    'D5': 16.939077,
    'D#5': 16.320438,
    'E5': 15.711287,
    'F5': 15.112901,
    'F#5': 14.526412,
    'G5': 13.952806,
    'G#5': 13.392936,
    'A5': 12.847521,
    'A#5': 12.317158,
    'B5': 11.802325,
    'C6': 11.303395,
    'C#6': 10.820741,
    'D6': 10.354854,
    'D#6': 9.906111,
    'E6': 9.474755,
    'F6': 9.060908,
    'F#6': 8.664585,
    'G6': 8.285704,
    'G#6': 7.924103,
    'A6': 7.579545,
    'A#6': 7.251747,
    'B6': 6.940556,
    'C7': 6.645881,
    'C#7': 6.367548,
    'D7': 6.105316,
    'D#7': 5.858885,
    'E7': 5.627914,
    'F7': 5.412033,
    'F#7': 5.210851,
    'G7': 5.023967,
}

FF_MEASURED: dict[str, float] = {
    'G3': 46.252716,
    'G#3': 41.815439,
    'A3': 38.289676,
    'A#3': 35.462303,
    'B3': 33.173172,
    'C4': 31.299436,
    'C#4': 29.744734,
    'D4': 28.431669,
    'D#4': 27.296559,
    'E4': 26.28581,
    'F4': 25.353793,
    'F#4': 24.473161,
    'G4': 23.63537,
    'G#4': 22.833813,
    'A4': 22.0626,
    'A#4': 21.316488,
    'B4': 20.590828,
    'C5': 19.881526,
    'C#5': 19.185001,
    'D5': 18.498166,
    'D#5': 17.8187,
    'E5': 17.146813,
    'F5': 16.483693,
    'F#5': 15.830444,
    'G5': 15.188081,
    'G#5': 14.557529,
    'A5': 13.939629,
    'A#5': 13.33513,
    'B5': 12.744698,
    'C6': 12.168916,
    'C#6': 11.608299,
    'D6': 11.063308,
    'D#6': 10.534326,
    'E6': 10.021655,
    'F6': 9.52552,
    'F#6': 9.046072,
    'G6': 8.583395,
    'G#6': 8.137509,
    'A6': 7.708373,
    'A#6': 7.295779,
    'B6': 6.897873,
    'C7': 6.51196,
    'C#7': 6.135892,
    'D7': 5.768058,
    'D#7': 5.407343,
    'E7': 5.053089,
    'F7': 4.705061,
    'F#7': 4.363401,
    'G7': 4.028591,
}

# GPR anchors: mf/ff from Excel; pp extrapolated from violin arco dynamic ratios.
spectral_data = {
    'G3': {'pp': 36.713456, 'mf': 39.443424, 'ff': 46.252716},
    'G#3': {'pp': 33.76289, 'mf': 36.192201, 'ff': 41.815439},
    'A3': {'pp': 35.349949, 'mf': 33.55561, 'ff': 38.289676},
    'A#3': {'pp': 28.126707, 'mf': 31.399188, 'ff': 35.462303},
    'B3': {'pp': 30.1363, 'mf': 29.618852, 'ff': 33.173172},
    'C4': {'pp': 32.905076, 'mf': 28.132473, 'ff': 31.299436},
    'C#4': {'pp': 30.42628, 'mf': 26.873912, 'ff': 29.744734},
    'D4': {'pp': 19.602271, 'mf': 25.788763, 'ff': 28.431669},
    'D#4': {'pp': 20.364368, 'mf': 24.831341, 'ff': 27.296559},
    'E4': {'pp': 20.747021, 'mf': 23.962562, 'ff': 26.28581},
    'F4': {'pp': 23.079551, 'mf': 23.148771, 'ff': 25.353793},
    'F#4': {'pp': 20.122301, 'mf': 22.370187, 'ff': 24.473161},
    'G4': {'pp': 19.852314, 'mf': 21.621554, 'ff': 23.63537},
    'G#4': {'pp': 22.282433, 'mf': 20.898955, 'ff': 22.833813},
    'A4': {'pp': 23.304815, 'mf': 20.19889, 'ff': 22.0626},
    'A#4': {'pp': 21.638075, 'mf': 19.518233, 'ff': 21.316488},
    'B4': {'pp': 18.906095, 'mf': 18.854212, 'ff': 20.590828},
    'C5': {'pp': 17.905944, 'mf': 18.204385, 'ff': 19.881526},
    'C#5': {'pp': 22.140642, 'mf': 17.566619, 'ff': 19.185001},
    'D5': {'pp': 15.41872, 'mf': 16.939077, 'ff': 18.498166},
    'D#5': {'pp': 16.837562, 'mf': 16.320438, 'ff': 17.8187},
    'E5': {'pp': 14.473072, 'mf': 15.711287, 'ff': 17.146813},
    'F5': {'pp': 13.109129, 'mf': 15.112901, 'ff': 16.483693},
    'F#5': {'pp': 12.04823, 'mf': 14.526412, 'ff': 15.830444},
    'G5': {'pp': 12.899431, 'mf': 13.952806, 'ff': 15.188081},
    'G#5': {'pp': 12.385285, 'mf': 13.392936, 'ff': 14.557529},
    'A5': {'pp': 11.588052, 'mf': 12.847521, 'ff': 13.939629},
    'A#5': {'pp': 10.974268, 'mf': 12.317158, 'ff': 13.33513},
    'B5': {'pp': 10.799326, 'mf': 11.802325, 'ff': 12.744698},
    'C6': {'pp': 10.114317, 'mf': 11.303395, 'ff': 12.168916},
    'C#6': {'pp': 9.517694, 'mf': 10.820741, 'ff': 11.608299},
    'D6': {'pp': 7.691313, 'mf': 10.354854, 'ff': 11.063308},
    'D#6': {'pp': 8.659993, 'mf': 9.906111, 'ff': 10.534326},
    'E6': {'pp': 8.381586, 'mf': 9.474755, 'ff': 10.021655},
    'F6': {'pp': 8.40423, 'mf': 9.060908, 'ff': 9.52552},
    'F#6': {'pp': 8.377411, 'mf': 8.664585, 'ff': 9.046072},
    'G6': {'pp': 6.316954, 'mf': 8.285704, 'ff': 8.583395},
    'G#6': {'pp': 5.611802, 'mf': 7.924103, 'ff': 8.137509},
    'A6': {'pp': 7.176087, 'mf': 7.579545, 'ff': 7.708373},
    'A#6': {'pp': 6.138039, 'mf': 7.251747, 'ff': 7.295779},
    'B6': {'pp': 6.480732, 'mf': 6.940556, 'ff': 6.897873},
    'C7': {'pp': 4.523476, 'mf': 6.645881, 'ff': 6.51196},
    'C#7': {'pp': 4.521059, 'mf': 6.367548, 'ff': 6.135892},
    'D7': {'pp': 5.514627, 'mf': 6.105316, 'ff': 5.768058},
    'D#7': {'pp': 4.092571, 'mf': 5.858885, 'ff': 5.407343},
    'E7': {'pp': 4.73571, 'mf': 5.627914, 'ff': 5.053089},
    'F7': {'pp': 4.184804, 'mf': 5.412033, 'ff': 4.705061},
    'F#7': {'pp': 4.857777, 'mf': 5.210851, 'ff': 4.363401},
    'G7': {'pp': 3.527592, 'mf': 5.023967, 'ff': 4.028591},
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
