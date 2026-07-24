# instrumentos/viola_sordina.py
"""
Viola (arco sordina) instrument density module.

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
        "Viola con_sordino EWSD table from Strings_techniques_extrapolation "
        "workbooks Viola_pp.xlsx / Viola_mf.xlsx / Viola_ff.xlsx "
        "(assumption-based extrapolation; pp/mf/ff from estimate_mean)."
    ),
    source_url_or_identifier="docs/instrument_acoustic_sources.md#viola-sordina",
    extraction_method=(
        "estimate_mean from All_Results for dynamics pp, mf and ff; "
        "GPR interpolation by pitch/dynamic"
    ),
    dynamic_levels=("pp", "mf", "ff"),
    pitch_range=(48, 96),
    uncertainty="high",
    version="2026-07-24",
    source_technique="arco_sordina",
    table_supported_techniques=("arco_sordina",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("viola_sordina")

# Workbook pp / mf / ff anchors (49 chromatic rows, C3–C7).
PP_MEASURED: dict[str, float] = {
    'C3': 22.383522,
    'C#3': 20.230091,
    'D3': 18.455728,
    'D#3': 16.979976,
    'E3': 15.740708,
    'F3': 14.689309,
    'F#3': 13.787232,
    'G3': 13.003496,
    'G#3': 12.312865,
    'A3': 11.69453,
    'A#3': 11.131216,
    'B3': 10.611112,
    'C4': 10.127535,
    'C#4': 9.674909,
    'D4': 9.248387,
    'D#4': 8.843759,
    'E4': 8.457368,
    'F4': 8.086056,
    'F#4': 7.727111,
    'G4': 7.378231,
    'G#4': 7.037773,
    'A4': 6.7064,
    'A#4': 6.385522,
    'B4': 6.076281,
    'C5': 5.779571,
    'C#5': 5.496059,
    'D5': 5.226212,
    'D#5': 4.970319,
    'E5': 4.728517,
    'F5': 4.50081,
    'F#5': 4.286596,
    'G5': 4.08423,
    'G#5': 3.892132,
    'A5': 3.708933,
    'A#5': 3.533446,
    'B5': 3.364653,
    'C6': 3.201685,
    'C#6': 3.043811,
    'D6': 2.890424,
    'D#6': 2.740936,
    'E6': 2.593513,
    'F6': 2.445742,
    'F#6': 2.295843,
    'G6': 2.142689,
    'G#6': 1.985812,
    'A6': 1.82539,
    'A#6': 1.662217,
    'B6': 1.497651,
    'C7': 1.333525,
}

MF_MEASURED: dict[str, float] = {
    'C3': 25.850724,
    'C#3': 23.085242,
    'D3': 20.814383,
    'D#3': 18.93108,
    'E3': 17.35343,
    'F3': 16.018016,
    'F#3': 14.875134,
    'G3': 13.885363,
    'G#3': 13.017064,
    'A3': 12.244575,
    'A#3': 11.546956,
    'B3': 10.909809,
    'C4': 10.324615,
    'C#4': 9.784279,
    'D4': 9.282678,
    'D#4': 8.814514,
    'E4': 8.375203,
    'F4': 7.960776,
    'F#4': 7.5678,
    'G4': 7.19332,
    'G#4': 6.835026,
    'A4': 6.492533,
    'A#4': 6.166111,
    'B4': 5.855874,
    'C5': 5.561803,
    'C#5': 5.28376,
    'D5': 5.021509,
    'D#5': 4.774735,
    'E5': 4.543059,
    'F5': 4.326049,
    'F#5': 4.122824,
    'G5': 3.931675,
    'G#5': 3.75099,
    'A5': 3.579362,
    'A#5': 3.415567,
    'B5': 3.258542,
    'C6': 3.107373,
    'C#6': 2.961275,
    'D6': 2.819587,
    'D#6': 2.681654,
    'E6': 2.545462,
    'F6': 2.408344,
    'F#6': 2.26827,
    'G6': 2.12389,
    'G#6': 1.974543,
    'A6': 1.820267,
    'A#6': 1.66178,
    'B6': 1.50044,
    'C7': 1.338156,
}

FF_MEASURED: dict[str, float] = {
    'C3': 26.54959,
    'C#3': 23.657184,
    'D3': 21.288868,
    'D#3': 19.329637,
    'E3': 17.691871,
    'F3': 16.307977,
    'F#3': 15.125161,
    'G3': 14.10168,
    'G#3': 13.204133,
    'A3': 12.405507,
    'A#3': 11.683831,
    'B3': 11.02427,
    'C4': 10.418395,
    'C#4': 9.859208,
    'D4': 9.340649,
    'D#4': 8.857471,
    'E4': 8.405115,
    'F4': 7.979627,
    'F#4': 7.577575,
    'G4': 7.195985,
    'G#4': 6.832534,
    'A4': 6.486905,
    'A#4': 6.159436,
    'B4': 5.850272,
    'C5': 5.559383,
    'C#5': 5.286599,
    'D5': 5.031637,
    'D#5': 4.794123,
    'E5': 4.573618,
    'F5': 4.369633,
    'F#5': 4.181145,
    'G5': 4.006119,
    'G#5': 3.842625,
    'A5': 3.688968,
    'A#5': 3.543658,
    'B5': 3.405381,
    'C6': 3.272986,
    'C#6': 3.145459,
    'D6': 3.021917,
    'D#6': 2.901462,
    'E6': 2.781379,
    'F6': 2.657982,
    'F#6': 2.528285,
    'G6': 2.3901,
    'G#6': 2.242103,
    'A6': 2.083906,
    'A#6': 1.916097,
    'B6': 1.740232,
    'C7': 1.558766,
}

# GPR anchors: pp/mf/ff all from Excel estimate_mean.
spectral_data = {
    'C3': {'pp': 22.383522, 'mf': 25.850724, 'ff': 26.54959},
    'C#3': {'pp': 20.230091, 'mf': 23.085242, 'ff': 23.657184},
    'D3': {'pp': 18.455728, 'mf': 20.814383, 'ff': 21.288868},
    'D#3': {'pp': 16.979976, 'mf': 18.93108, 'ff': 19.329637},
    'E3': {'pp': 15.740708, 'mf': 17.35343, 'ff': 17.691871},
    'F3': {'pp': 14.689309, 'mf': 16.018016, 'ff': 16.307977},
    'F#3': {'pp': 13.787232, 'mf': 14.875134, 'ff': 15.125161},
    'G3': {'pp': 13.003496, 'mf': 13.885363, 'ff': 14.10168},
    'G#3': {'pp': 12.312865, 'mf': 13.017064, 'ff': 13.204133},
    'A3': {'pp': 11.69453, 'mf': 12.244575, 'ff': 12.405507},
    'A#3': {'pp': 11.131216, 'mf': 11.546956, 'ff': 11.683831},
    'B3': {'pp': 10.611112, 'mf': 10.909809, 'ff': 11.02427},
    'C4': {'pp': 10.127535, 'mf': 10.324615, 'ff': 10.418395},
    'C#4': {'pp': 9.674909, 'mf': 9.784279, 'ff': 9.859208},
    'D4': {'pp': 9.248387, 'mf': 9.282678, 'ff': 9.340649},
    'D#4': {'pp': 8.843759, 'mf': 8.814514, 'ff': 8.857471},
    'E4': {'pp': 8.457368, 'mf': 8.375203, 'ff': 8.405115},
    'F4': {'pp': 8.086056, 'mf': 7.960776, 'ff': 7.979627},
    'F#4': {'pp': 7.727111, 'mf': 7.5678, 'ff': 7.577575},
    'G4': {'pp': 7.378231, 'mf': 7.19332, 'ff': 7.195985},
    'G#4': {'pp': 7.037773, 'mf': 6.835026, 'ff': 6.832534},
    'A4': {'pp': 6.7064, 'mf': 6.492533, 'ff': 6.486905},
    'A#4': {'pp': 6.385522, 'mf': 6.166111, 'ff': 6.159436},
    'B4': {'pp': 6.076281, 'mf': 5.855874, 'ff': 5.850272},
    'C5': {'pp': 5.779571, 'mf': 5.561803, 'ff': 5.559383},
    'C#5': {'pp': 5.496059, 'mf': 5.28376, 'ff': 5.286599},
    'D5': {'pp': 5.226212, 'mf': 5.021509, 'ff': 5.031637},
    'D#5': {'pp': 4.970319, 'mf': 4.774735, 'ff': 4.794123},
    'E5': {'pp': 4.728517, 'mf': 4.543059, 'ff': 4.573618},
    'F5': {'pp': 4.50081, 'mf': 4.326049, 'ff': 4.369633},
    'F#5': {'pp': 4.286596, 'mf': 4.122824, 'ff': 4.181145},
    'G5': {'pp': 4.08423, 'mf': 3.931675, 'ff': 4.006119},
    'G#5': {'pp': 3.892132, 'mf': 3.75099, 'ff': 3.842625},
    'A5': {'pp': 3.708933, 'mf': 3.579362, 'ff': 3.688968},
    'A#5': {'pp': 3.533446, 'mf': 3.415567, 'ff': 3.543658},
    'B5': {'pp': 3.364653, 'mf': 3.258542, 'ff': 3.405381},
    'C6': {'pp': 3.201685, 'mf': 3.107373, 'ff': 3.272986},
    'C#6': {'pp': 3.043811, 'mf': 2.961275, 'ff': 3.145459},
    'D6': {'pp': 2.890424, 'mf': 2.819587, 'ff': 3.021917},
    'D#6': {'pp': 2.740936, 'mf': 2.681654, 'ff': 2.901462},
    'E6': {'pp': 2.593513, 'mf': 2.545462, 'ff': 2.781379},
    'F6': {'pp': 2.445742, 'mf': 2.408344, 'ff': 2.657982},
    'F#6': {'pp': 2.295843, 'mf': 2.26827, 'ff': 2.528285},
    'G6': {'pp': 2.142689, 'mf': 2.12389, 'ff': 2.3901},
    'G#6': {'pp': 1.985812, 'mf': 1.974543, 'ff': 2.242103},
    'A6': {'pp': 1.82539, 'mf': 1.820267, 'ff': 2.083906},
    'A#6': {'pp': 1.662217, 'mf': 1.66178, 'ff': 1.916097},
    'B6': {'pp': 1.497651, 'mf': 1.50044, 'ff': 1.740232},
    'C7': {'pp': 1.333525, 'mf': 1.338156, 'ff': 1.558766},
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
