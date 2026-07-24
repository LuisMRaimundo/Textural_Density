# instrumentos/double_bass_sordina.py
"""
Double bass (arco sordina) instrument density module.

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
        "Double bass con_sordino EWSD table from Strings_techniques_extrapolation "
        "workbooks Contrabass-pp.xlsx / Contrabass_mf.xlsx / Contrabass_ff.xlsx "
        "(assumption-based extrapolation; pp/mf/ff from estimate_mean)."
    ),
    source_url_or_identifier="docs/instrument_acoustic_sources.md#double-bass-sordina",
    extraction_method=(
        "estimate_mean from All_Results for dynamics pp, mf and ff; "
        "GPR interpolation by pitch/dynamic"
    ),
    dynamic_levels=("pp", "mf", "ff"),
    pitch_range=(28, 72),
    uncertainty="high",
    version="2026-07-24",
    source_technique="arco_sordina",
    table_supported_techniques=("arco_sordina",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("double_bass_sordina")

# Workbook pp / mf / ff anchors (45 chromatic rows, E1–C5).
PP_MEASURED: dict[str, float] = {
    'E1': 47.039052,
    'F1': 42.915439,
    'F#1': 39.690764,
    'G1': 37.159226,
    'G#1': 35.166213,
    'A1': 33.592837,
    'A#1': 32.345237,
    'B1': 31.347071,
    'C2': 30.534232,
    'C#2': 29.851179,
    'D2': 29.257388,
    'D#2': 28.735808,
    'E2': 28.273513,
    'F2': 27.858605,
    'F#2': 27.48001,
    'G2': 27.127329,
    'G#2': 26.790729,
    'A2': 26.460868,
    'A#2': 26.128925,
    'B2': 25.78916,
    'C3': 25.439533,
    'C#3': 25.078368,
    'D3': 24.704128,
    'D#3': 24.315423,
    'E3': 23.91102,
    'F3': 23.48985,
    'F#3': 23.051023,
    'G3': 22.59366,
    'G#3': 22.114577,
    'A3': 21.609141,
    'A#3': 21.073343,
    'B3': 20.503907,
    'C4': 19.89836,
    'C#4': 19.255094,
    'D4': 18.57342,
    'D#4': 17.853618,
    'E4': 17.095041,
    'F4': 16.284876,
    'F#4': 15.408789,
    'G4': 14.45842,
    'G#4': 13.431977,
    'A4': 12.334581,
    'A#4': 11.178222,
    'B4': 9.981217,
    'C5': 8.767084,
}

MF_MEASURED: dict[str, float] = {
    'E1': 55.525387,
    'F1': 50.660491,
    'F#1': 46.833209,
    'G1': 43.812702,
    'G#1': 41.425012,
    'A1': 39.536355,
    'A#1': 38.041434,
    'B1': 36.855159,
    'C2': 35.906721,
    'C#2': 35.135368,
    'D2': 34.493763,
    'D#2': 33.953146,
    'E2': 33.489089,
    'F2': 33.078891,
    'F#2': 32.701172,
    'G2': 32.335599,
    'G#2': 31.962753,
    'A2': 31.564113,
    'A#2': 31.122293,
    'B2': 30.626552,
    'C3': 30.074179,
    'C#3': 29.463607,
    'D3': 28.793991,
    'D#3': 28.065254,
    'E3': 27.278128,
    'F3': 26.434187,
    'F#3': 25.535862,
    'G3': 24.586354,
    'G#3': 23.588541,
    'A3': 22.545453,
    'A#3': 21.461252,
    'B3': 20.341197,
    'C4': 19.191573,
    'C#4': 18.019571,
    'D4': 16.833147,
    'D#4': 15.640853,
    'E4': 14.449165,
    'F4': 13.248799,
    'F#4': 12.030399,
    'G4': 10.793703,
    'G#4': 9.546958,
    'A4': 8.305787,
    'A#4': 7.091449,
    'B4': 5.928499,
    'C5': 4.842027,
}

FF_MEASURED: dict[str, float] = {
    'E1': 66.431085,
    'F1': 59.433981,
    'F#1': 53.995369,
    'G1': 49.736619,
    'G#1': 46.380338,
    'A1': 43.718908,
    'A#1': 41.593195,
    'B1': 39.877937,
    'C2': 38.47161,
    'C#2': 37.289434,
    'D2': 36.269893,
    'D#2': 35.383788,
    'E2': 34.608577,
    'F2': 33.924101,
    'F#2': 33.312095,
    'G2': 32.75581,
    'G#2': 32.239727,
    'A2': 31.749347,
    'A#2': 31.271144,
    'B2': 30.795989,
    'C3': 30.319898,
    'C#3': 29.839442,
    'D3': 29.35143,
    'D#3': 28.852909,
    'E3': 28.34118,
    'F3': 27.813806,
    'F#3': 27.268628,
    'G3': 26.703592,
    'G#3': 26.114241,
    'A3': 25.494665,
    'A#3': 24.839756,
    'B3': 24.145346,
    'C4': 23.408285,
    'C#4': 22.626519,
    'D4': 21.799164,
    'D#4': 20.926561,
    'E4': 20.006937,
    'F4': 19.016761,
    'F#4': 17.929652,
    'G4': 16.729835,
    'G#4': 15.41349,
    'A4': 13.989588,
    'A#4': 12.479827,
    'B4': 10.917343,
    'C5': 9.344051,
}

# GPR anchors: pp/mf/ff all from Excel estimate_mean.
spectral_data = {
    'E1': {'pp': 47.039052, 'mf': 55.525387, 'ff': 66.431085},
    'F1': {'pp': 42.915439, 'mf': 50.660491, 'ff': 59.433981},
    'F#1': {'pp': 39.690764, 'mf': 46.833209, 'ff': 53.995369},
    'G1': {'pp': 37.159226, 'mf': 43.812702, 'ff': 49.736619},
    'G#1': {'pp': 35.166213, 'mf': 41.425012, 'ff': 46.380338},
    'A1': {'pp': 33.592837, 'mf': 39.536355, 'ff': 43.718908},
    'A#1': {'pp': 32.345237, 'mf': 38.041434, 'ff': 41.593195},
    'B1': {'pp': 31.347071, 'mf': 36.855159, 'ff': 39.877937},
    'C2': {'pp': 30.534232, 'mf': 35.906721, 'ff': 38.47161},
    'C#2': {'pp': 29.851179, 'mf': 35.135368, 'ff': 37.289434},
    'D2': {'pp': 29.257388, 'mf': 34.493763, 'ff': 36.269893},
    'D#2': {'pp': 28.735808, 'mf': 33.953146, 'ff': 35.383788},
    'E2': {'pp': 28.273513, 'mf': 33.489089, 'ff': 34.608577},
    'F2': {'pp': 27.858605, 'mf': 33.078891, 'ff': 33.924101},
    'F#2': {'pp': 27.48001, 'mf': 32.701172, 'ff': 33.312095},
    'G2': {'pp': 27.127329, 'mf': 32.335599, 'ff': 32.75581},
    'G#2': {'pp': 26.790729, 'mf': 31.962753, 'ff': 32.239727},
    'A2': {'pp': 26.460868, 'mf': 31.564113, 'ff': 31.749347},
    'A#2': {'pp': 26.128925, 'mf': 31.122293, 'ff': 31.271144},
    'B2': {'pp': 25.78916, 'mf': 30.626552, 'ff': 30.795989},
    'C3': {'pp': 25.439533, 'mf': 30.074179, 'ff': 30.319898},
    'C#3': {'pp': 25.078368, 'mf': 29.463607, 'ff': 29.839442},
    'D3': {'pp': 24.704128, 'mf': 28.793991, 'ff': 29.35143},
    'D#3': {'pp': 24.315423, 'mf': 28.065254, 'ff': 28.852909},
    'E3': {'pp': 23.91102, 'mf': 27.278128, 'ff': 28.34118},
    'F3': {'pp': 23.48985, 'mf': 26.434187, 'ff': 27.813806},
    'F#3': {'pp': 23.051023, 'mf': 25.535862, 'ff': 27.268628},
    'G3': {'pp': 22.59366, 'mf': 24.586354, 'ff': 26.703592},
    'G#3': {'pp': 22.114577, 'mf': 23.588541, 'ff': 26.114241},
    'A3': {'pp': 21.609141, 'mf': 22.545453, 'ff': 25.494665},
    'A#3': {'pp': 21.073343, 'mf': 21.461252, 'ff': 24.839756},
    'B3': {'pp': 20.503907, 'mf': 20.341197, 'ff': 24.145346},
    'C4': {'pp': 19.89836, 'mf': 19.191573, 'ff': 23.408285},
    'C#4': {'pp': 19.255094, 'mf': 18.019571, 'ff': 22.626519},
    'D4': {'pp': 18.57342, 'mf': 16.833147, 'ff': 21.799164},
    'D#4': {'pp': 17.853618, 'mf': 15.640853, 'ff': 20.926561},
    'E4': {'pp': 17.095041, 'mf': 14.449165, 'ff': 20.006937},
    'F4': {'pp': 16.284876, 'mf': 13.248799, 'ff': 19.016761},
    'F#4': {'pp': 15.408789, 'mf': 12.030399, 'ff': 17.929652},
    'G4': {'pp': 14.45842, 'mf': 10.793703, 'ff': 16.729835},
    'G#4': {'pp': 13.431977, 'mf': 9.546958, 'ff': 15.41349},
    'A4': {'pp': 12.334581, 'mf': 8.305787, 'ff': 13.989588},
    'A#4': {'pp': 11.178222, 'mf': 7.091449, 'ff': 12.479827},
    'B4': {'pp': 9.981217, 'mf': 5.928499, 'ff': 10.917343},
    'C5': {'pp': 8.767084, 'mf': 4.842027, 'ff': 9.344051},
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
