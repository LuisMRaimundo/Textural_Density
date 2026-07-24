# instrumentos/violin_sordina.py
"""
Violin (arco sordina) instrument density module.

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
        "Violin con_sordino EWSD table from Strings_techniques_extrapolation "
        "workbooks Violin_mf.xlsx / Violin_ff.xlsx (assumption-based extrapolation); "
        "pp derived from violin arco pp/mf ratios."
    ),
    source_url_or_identifier="docs/instrument_acoustic_sources.md#violin-sordina",
    extraction_method=(
        "estimate_mean from All_Results for dynamics mf and ff; "
        "pp via violin arco pp/mf ratio transfer; GPR interpolation by pitch/dynamic"
    ),
    dynamic_levels=("pp", "mf", "ff"),
    pitch_range=(55, 103),
    uncertainty="high",
    version="2026-07-24",
    source_technique="arco_sordina",
    table_supported_techniques=("arco_sordina",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("violin_sordina")

# Workbook mf / ff anchors (49 chromatic rows, G3–G7).
MF_MEASURED: dict[str, float] = {
    'G3': 11.170946,
    'G#3': 10.250153,
    'A3': 9.503432,
    'A#3': 8.892702,
    'B3': 8.388486,
    'C4': 7.967522,
    'C#4': 7.611079,
    'D4': 7.303749,
    'D#4': 7.032593,
    'E4': 6.786543,
    'F4': 6.556065,
    'F#4': 6.335559,
    'G4': 6.123535,
    'G#4': 5.918885,
    'A4': 5.720617,
    'A#4': 5.527845,
    'B4': 5.339784,
    'C5': 5.155744,
    'C#5': 4.97512,
    'D5': 4.797391,
    'D#5': 4.622183,
    'E5': 4.449663,
    'F5': 4.280191,
    'F#5': 4.114089,
    'G5': 3.951636,
    'G#5': 3.793072,
    'A5': 3.638603,
    'A#5': 3.488397,
    'B5': 3.342589,
    'C6': 3.201284,
    'C#6': 3.06459,
    'D6': 2.932644,
    'D#6': 2.805553,
    'E6': 2.683387,
    'F6': 2.56618,
    'F#6': 2.453935,
    'G6': 2.346631,
    'G#6': 2.24422,
    'A6': 2.146636,
    'A#6': 2.053799,
    'B6': 1.965665,
    'C7': 1.882209,
    'C#7': 1.803381,
    'D7': 1.729113,
    'D#7': 1.659321,
    'E7': 1.593906,
    'F7': 1.532766,
    'F#7': 1.475788,
    'G7': 1.42286,
}

FF_MEASURED: dict[str, float] = {
    'G3': 13.099435,
    'G#3': 11.842735,
    'A3': 10.844188,
    'A#3': 10.043435,
    'B3': 9.39512,
    'C4': 8.864451,
    'C#4': 8.424137,
    'D4': 8.052258,
    'D#4': 7.730779,
    'E4': 7.44452,
    'F4': 7.180559,
    'F#4': 6.931152,
    'G4': 6.693877,
    'G#4': 6.466865,
    'A4': 6.248446,
    'A#4': 6.037136,
    'B4': 5.831619,
    'C5': 5.630734,
    'C#5': 5.433469,
    'D5': 5.238947,
    'D#5': 5.046513,
    'E5': 4.856225,
    'F5': 4.668419,
    'F#5': 4.48341,
    'G5': 4.301483,
    'G#5': 4.122902,
    'A5': 3.947904,
    'A#5': 3.776701,
    'B5': 3.609482,
    'C6': 3.446412,
    'C#6': 3.287637,
    'D6': 3.133288,
    'D#6': 2.983473,
    'E6': 2.838277,
    'F6': 2.697764,
    'F#6': 2.561978,
    'G6': 2.430941,
    'G#6': 2.30466,
    'A6': 2.183122,
    'A#6': 2.06627,
    'B6': 1.953577,
    'C7': 1.844281,
    'C#7': 1.737773,
    'D7': 1.633597,
    'D#7': 1.531437,
    'E7': 1.431108,
    'F7': 1.332541,
    'F#7': 1.235778,
    'G7': 1.140955,
}

# GPR anchors: mf/ff from Excel; pp extrapolated from violin arco dynamic ratios.
spectral_data = {
    'G3': {'pp': 10.39778, 'mf': 11.170946, 'ff': 13.099435},
    'G#3': {'pp': 9.562137, 'mf': 10.250153, 'ff': 11.842735},
    'A3': {'pp': 10.011615, 'mf': 9.503432, 'ff': 10.844188},
    'A#3': {'pp': 7.965888, 'mf': 8.892702, 'ff': 10.043435},
    'B3': {'pp': 8.535035, 'mf': 8.388486, 'ff': 9.39512},
    'C4': {'pp': 9.319192, 'mf': 7.967522, 'ff': 8.864451},
    'C#4': {'pp': 8.617161, 'mf': 7.611079, 'ff': 8.424137},
    'D4': {'pp': 5.551645, 'mf': 7.303749, 'ff': 8.052258},
    'D#4': {'pp': 5.767482, 'mf': 7.032593, 'ff': 7.730779},
    'E4': {'pp': 5.875855, 'mf': 6.786543, 'ff': 7.44452},
    'F4': {'pp': 6.536461, 'mf': 6.556065, 'ff': 7.180559},
    'F#4': {'pp': 5.698925, 'mf': 6.335559, 'ff': 6.931152},
    'G4': {'pp': 5.622461, 'mf': 6.123535, 'ff': 6.693877},
    'G#4': {'pp': 6.310706, 'mf': 5.918885, 'ff': 6.466865},
    'A4': {'pp': 6.60026, 'mf': 5.720617, 'ff': 6.248446},
    'A#4': {'pp': 6.128215, 'mf': 5.527845, 'ff': 6.037136},
    'B4': {'pp': 5.354478, 'mf': 5.339784, 'ff': 5.831619},
    'C5': {'pp': 5.071221, 'mf': 5.155744, 'ff': 5.630734},
    'C#5': {'pp': 6.270549, 'mf': 4.97512, 'ff': 5.433469},
    'D5': {'pp': 4.366804, 'mf': 4.797391, 'ff': 5.238947},
    'D#5': {'pp': 4.76864, 'mf': 4.622183, 'ff': 5.046513},
    'E5': {'pp': 4.098983, 'mf': 4.449663, 'ff': 4.856225},
    'F5': {'pp': 3.712694, 'mf': 4.280191, 'ff': 4.668419},
    'F#5': {'pp': 3.412232, 'mf': 4.114089, 'ff': 4.48341},
    'G5': {'pp': 3.653305, 'mf': 3.951636, 'ff': 4.301483},
    'G#5': {'pp': 3.507691, 'mf': 3.793072, 'ff': 4.122902},
    'A5': {'pp': 3.281903, 'mf': 3.638603, 'ff': 3.947904},
    'A#5': {'pp': 3.108071, 'mf': 3.488397, 'ff': 3.776701},
    'B5': {'pp': 3.058525, 'mf': 3.342589, 'ff': 3.609482},
    'C6': {'pp': 2.86452, 'mf': 3.201284, 'ff': 3.446412},
    'C#6': {'pp': 2.695548, 'mf': 3.06459, 'ff': 3.287637},
    'D6': {'pp': 2.178291, 'mf': 2.932644, 'ff': 3.133288},
    'D#6': {'pp': 2.452635, 'mf': 2.805553, 'ff': 2.983473},
    'E6': {'pp': 2.373786, 'mf': 2.683387, 'ff': 2.838277},
    'F6': {'pp': 2.380199, 'mf': 2.56618, 'ff': 2.697764},
    'F#6': {'pp': 2.372603, 'mf': 2.453935, 'ff': 2.561978},
    'G6': {'pp': 1.789053, 'mf': 2.346631, 'ff': 2.430941},
    'G#6': {'pp': 1.589343, 'mf': 2.24422, 'ff': 2.30466},
    'A6': {'pp': 2.032371, 'mf': 2.146636, 'ff': 2.183122},
    'A#6': {'pp': 1.738381, 'mf': 2.053799, 'ff': 2.06627},
    'B6': {'pp': 1.835436, 'mf': 1.965665, 'ff': 1.953577},
    'C7': {'pp': 1.281114, 'mf': 1.882209, 'ff': 1.844281},
    'C#7': {'pp': 1.280429, 'mf': 1.803381, 'ff': 1.737773},
    'D7': {'pp': 1.561821, 'mf': 1.729113, 'ff': 1.633597},
    'D#7': {'pp': 1.159075, 'mf': 1.659321, 'ff': 1.531437},
    'E7': {'pp': 1.341221, 'mf': 1.593906, 'ff': 1.431108},
    'F7': {'pp': 1.185197, 'mf': 1.532766, 'ff': 1.332541},
    'F#7': {'pp': 1.375792, 'mf': 1.475788, 'ff': 1.235778},
    'G7': {'pp': 0.999065, 'mf': 1.42286, 'ff': 1.140955},
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
