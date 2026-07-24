# instrumentos/viola_sul_ponticello.py
"""
Viola (arco sul ponticello) instrument density module.

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
        "Viola sul_ponticello EWSD table from Strings_techniques_extrapolation "
        "workbooks Viola_pp.xlsx / Viola_mf.xlsx / Viola_ff.xlsx "
        "(assumption-based extrapolation; pp/mf/ff from estimate_mean)."
    ),
    source_url_or_identifier="docs/instrument_acoustic_sources.md#viola-sul-ponticello",
    extraction_method=(
        "estimate_mean from All_Results for dynamics pp, mf and ff; "
        "GPR interpolation by pitch/dynamic"
    ),
    dynamic_levels=("pp", "mf", "ff"),
    pitch_range=(48, 96),
    uncertainty="high",
    version="2026-07-24",
    source_technique="arco_sul_ponticello",
    table_supported_techniques=("arco_sul_ponticello",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("viola_sul_ponticello")

# Workbook pp / mf / ff anchors (49 chromatic rows, C3–C7).
PP_MEASURED: dict[str, float] = {
    'C3': 68.673205,
    'C#3': 62.066426,
    'D3': 56.622634,
    'D#3': 52.094992,
    'E3': 48.292885,
    'F3': 45.067167,
    'F#3': 42.299574,
    'G3': 39.89505,
    'G#3': 37.776178,
    'A3': 35.879111,
    'A#3': 34.15085,
    'B3': 32.555158,
    'C4': 31.071531,
    'C#4': 29.682862,
    'D4': 28.374284,
    'D#4': 27.132873,
    'E4': 25.947416,
    'F4': 24.808221,
    'F#4': 23.706971,
    'G4': 22.636596,
    'G#4': 21.592063,
    'A4': 20.575404,
    'A#4': 19.590942,
    'B4': 18.642182,
    'C5': 17.731868,
    'C#5': 16.862046,
    'D5': 16.034149,
    'D#5': 15.249064,
    'E5': 14.50721,
    'F5': 13.808597,
    'F#5': 13.151385,
    'G5': 12.53052,
    'G#5': 11.941159,
    'A5': 11.379098,
    'A#5': 10.840701,
    'B5': 10.32284,
    'C6': 9.822851,
    'C#6': 9.338488,
    'D6': 8.867892,
    'D#6': 8.409261,
    'E6': 7.956961,
    'F6': 7.503597,
    'F#6': 7.043702,
    'G6': 6.573824,
    'G#6': 6.092522,
    'A6': 5.600341,
    'A#6': 5.099722,
    'B6': 4.594832,
    'C7': 4.091289,
}

MF_MEASURED: dict[str, float] = {
    'C3': 79.310669,
    'C#3': 70.8261,
    'D3': 63.859048,
    'D#3': 58.081027,
    'E3': 53.240758,
    'F3': 49.143673,
    'F#3': 45.637285,
    'G3': 42.60064,
    'G#3': 39.936678,
    'A3': 37.566662,
    'A#3': 35.426351,
    'B3': 33.471567,
    'C4': 31.676176,
    'C#4': 30.018412,
    'D4': 28.479488,
    'D#4': 27.04315,
    'E4': 25.695333,
    'F4': 24.423859,
    'F#4': 23.218201,
    'G4': 22.069286,
    'G#4': 20.970031,
    'A4': 19.919254,
    'A#4': 18.917782,
    'B4': 17.965969,
    'C5': 17.063752,
    'C#5': 16.210708,
    'D5': 15.406115,
    'D#5': 14.649007,
    'E5': 13.938219,
    'F5': 13.272426,
    'F#5': 12.648926,
    'G5': 12.062477,
    'G#5': 11.50813,
    'A5': 10.981572,
    'A#5': 10.479044,
    'B5': 9.997289,
    'C6': 9.533497,
    'C#6': 9.085265,
    'D6': 8.650563,
    'D#6': 8.227381,
    'E6': 7.80954,
    'F6': 7.388858,
    'F#6': 6.95911,
    'G6': 6.516148,
    'G#6': 6.057948,
    'A6': 5.584624,
    'A#6': 5.098383,
    'B6': 4.603388,
    'C7': 4.105497,
}

FF_MEASURED: dict[str, float] = {
    'C3': 81.454805,
    'C#3': 72.580832,
    'D3': 65.314779,
    'D#3': 59.30381,
    'E3': 54.279103,
    'F3': 50.033283,
    'F#3': 46.404374,
    'G3': 43.264306,
    'G#3': 40.510611,
    'A3': 38.060405,
    'A#3': 35.846287,
    'B3': 33.822735,
    'C4': 31.963898,
    'C#4': 30.248296,
    'D4': 28.657346,
    'D#4': 27.174941,
    'E4': 25.787102,
    'F4': 24.481695,
    'F#4': 23.248188,
    'G4': 22.077463,
    'G#4': 20.962385,
    'A4': 19.901985,
    'A#4': 18.897305,
    'B4': 17.948781,
    'C5': 17.056326,
    'C#5': 16.219419,
    'D5': 15.437189,
    'D#5': 14.70849,
    'E5': 14.031974,
    'F5': 13.406143,
    'F#5': 12.827857,
    'G5': 12.290873,
    'G#5': 11.78927,
    'A5': 11.317847,
    'A#5': 10.872031,
    'B5': 10.447795,
    'C6': 10.041602,
    'C#6': 9.650346,
    'D6': 9.271318,
    'D#6': 8.901757,
    'E6': 8.533339,
    'F6': 8.154754,
    'F#6': 7.756843,
    'G6': 7.332887,
    'G#6': 6.878828,
    'A6': 6.393476,
    'A#6': 5.878634,
    'B6': 5.339076,
    'C7': 4.782333,
}

# GPR anchors: pp/mf/ff all from Excel estimate_mean.
spectral_data = {
    'C3': {'pp': 68.673205, 'mf': 79.310669, 'ff': 81.454805},
    'C#3': {'pp': 62.066426, 'mf': 70.8261, 'ff': 72.580832},
    'D3': {'pp': 56.622634, 'mf': 63.859048, 'ff': 65.314779},
    'D#3': {'pp': 52.094992, 'mf': 58.081027, 'ff': 59.30381},
    'E3': {'pp': 48.292885, 'mf': 53.240758, 'ff': 54.279103},
    'F3': {'pp': 45.067167, 'mf': 49.143673, 'ff': 50.033283},
    'F#3': {'pp': 42.299574, 'mf': 45.637285, 'ff': 46.404374},
    'G3': {'pp': 39.89505, 'mf': 42.60064, 'ff': 43.264306},
    'G#3': {'pp': 37.776178, 'mf': 39.936678, 'ff': 40.510611},
    'A3': {'pp': 35.879111, 'mf': 37.566662, 'ff': 38.060405},
    'A#3': {'pp': 34.15085, 'mf': 35.426351, 'ff': 35.846287},
    'B3': {'pp': 32.555158, 'mf': 33.471567, 'ff': 33.822735},
    'C4': {'pp': 31.071531, 'mf': 31.676176, 'ff': 31.963898},
    'C#4': {'pp': 29.682862, 'mf': 30.018412, 'ff': 30.248296},
    'D4': {'pp': 28.374284, 'mf': 28.479488, 'ff': 28.657346},
    'D#4': {'pp': 27.132873, 'mf': 27.04315, 'ff': 27.174941},
    'E4': {'pp': 25.947416, 'mf': 25.695333, 'ff': 25.787102},
    'F4': {'pp': 24.808221, 'mf': 24.423859, 'ff': 24.481695},
    'F#4': {'pp': 23.706971, 'mf': 23.218201, 'ff': 23.248188},
    'G4': {'pp': 22.636596, 'mf': 22.069286, 'ff': 22.077463},
    'G#4': {'pp': 21.592063, 'mf': 20.970031, 'ff': 20.962385},
    'A4': {'pp': 20.575404, 'mf': 19.919254, 'ff': 19.901985},
    'A#4': {'pp': 19.590942, 'mf': 18.917782, 'ff': 18.897305},
    'B4': {'pp': 18.642182, 'mf': 17.965969, 'ff': 17.948781},
    'C5': {'pp': 17.731868, 'mf': 17.063752, 'ff': 17.056326},
    'C#5': {'pp': 16.862046, 'mf': 16.210708, 'ff': 16.219419},
    'D5': {'pp': 16.034149, 'mf': 15.406115, 'ff': 15.437189},
    'D#5': {'pp': 15.249064, 'mf': 14.649007, 'ff': 14.70849},
    'E5': {'pp': 14.50721, 'mf': 13.938219, 'ff': 14.031974},
    'F5': {'pp': 13.808597, 'mf': 13.272426, 'ff': 13.406143},
    'F#5': {'pp': 13.151385, 'mf': 12.648926, 'ff': 12.827857},
    'G5': {'pp': 12.53052, 'mf': 12.062477, 'ff': 12.290873},
    'G#5': {'pp': 11.941159, 'mf': 11.50813, 'ff': 11.78927},
    'A5': {'pp': 11.379098, 'mf': 10.981572, 'ff': 11.317847},
    'A#5': {'pp': 10.840701, 'mf': 10.479044, 'ff': 10.872031},
    'B5': {'pp': 10.32284, 'mf': 9.997289, 'ff': 10.447795},
    'C6': {'pp': 9.822851, 'mf': 9.533497, 'ff': 10.041602},
    'C#6': {'pp': 9.338488, 'mf': 9.085265, 'ff': 9.650346},
    'D6': {'pp': 8.867892, 'mf': 8.650563, 'ff': 9.271318},
    'D#6': {'pp': 8.409261, 'mf': 8.227381, 'ff': 8.901757},
    'E6': {'pp': 7.956961, 'mf': 7.80954, 'ff': 8.533339},
    'F6': {'pp': 7.503597, 'mf': 7.388858, 'ff': 8.154754},
    'F#6': {'pp': 7.043702, 'mf': 6.95911, 'ff': 7.756843},
    'G6': {'pp': 6.573824, 'mf': 6.516148, 'ff': 7.332887},
    'G#6': {'pp': 6.092522, 'mf': 6.057948, 'ff': 6.878828},
    'A6': {'pp': 5.600341, 'mf': 5.584624, 'ff': 6.393476},
    'A#6': {'pp': 5.099722, 'mf': 5.098383, 'ff': 5.878634},
    'B6': {'pp': 4.594832, 'mf': 4.603388, 'ff': 5.339076},
    'C7': {'pp': 4.091289, 'mf': 4.105497, 'ff': 4.782333},
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
