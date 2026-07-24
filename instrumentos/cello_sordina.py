# instrumentos/cello_sordina.py
"""
Cello (arco sordina) instrument density module.

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
        "Cello con_sordino EWSD table from Strings_techniques_extrapolation "
        "workbooks Cello_pp.xlsx / Cello_mf.xlsx / Cello_ff.xlsx "
        "(assumption-based extrapolation; pp/mf/ff from estimate_mean)."
    ),
    source_url_or_identifier="docs/instrument_acoustic_sources.md#cello-sordina",
    extraction_method=(
        "estimate_mean from All_Results for dynamics pp, mf and ff; "
        "GPR interpolation by pitch/dynamic"
    ),
    dynamic_levels=("pp", "mf", "ff"),
    pitch_range=(36, 84),
    uncertainty="high",
    version="2026-07-24",
    source_technique="arco_sordina",
    table_supported_techniques=("arco_sordina",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("cello_sordina")

# Workbook pp / mf / ff anchors (49 chromatic rows, C2–C6).
PP_MEASURED: dict[str, float] = {
    'C2': 54.072052,
    'C#2': 49.168436,
    'D2': 45.284304,
    'D#2': 42.186098,
    'E2': 39.697576,
    'F2': 37.682888,
    'F#2': 36.034836,
    'G2': 34.666635,
    'G#2': 33.506125,
    'A2': 32.491719,
    'A#2': 31.570027,
    'B2': 30.707892,
    'C3': 29.89361,
    'C#3': 29.117762,
    'D3': 28.371796,
    'D#3': 27.647946,
    'E3': 26.939161,
    'F3': 26.239066,
    'F#3': 25.541934,
    'G3': 24.842667,
    'G#3': 24.137203,
    'A3': 23.424958,
    'A#3': 22.706845,
    'B3': 21.983857,
    'C4': 21.257058,
    'C#4': 20.527575,
    'D4': 19.796589,
    'D#4': 19.065334,
    'E4': 18.335079,
    'F4': 17.607127,
    'F#4': 16.88247,
    'G4': 16.161459,
    'G#4': 15.44454,
    'A4': 14.732346,
    'A#4': 14.025686,
    'B4': 13.325524,
    'C5': 12.632963,
    'C#5': 11.949221,
    'D5': 11.275612,
    'D#5': 10.613002,
    'E5': 9.955103,
    'F5': 9.292416,
    'F#5': 8.618795,
    'G5': 7.931568,
    'G#5': 7.231456,
    'A5': 6.522383,
    'A#5': 5.811127,
    'B5': 5.106783,
    'C6': 4.42005,
}

MF_MEASURED: dict[str, float] = {
    'C2': 58.672456,
    'C#2': 54.238289,
    'D2': 50.629962,
    'D#2': 47.670062,
    'E2': 45.219622,
    'F2': 43.167592,
    'F#2': 41.423327,
    'G2': 39.91122,
    'G#2': 38.566877,
    'A2': 37.334469,
    'A#2': 36.165372,
    'B2': 35.031712,
    'C3': 33.927809,
    'C#3': 32.849822,
    'D3': 31.794333,
    'D#3': 30.758323,
    'E3': 29.73915,
    'F3': 28.734533,
    'F#3': 27.742538,
    'G3': 26.761559,
    'G#3': 25.790741,
    'A3': 24.832534,
    'A#3': 23.890476,
    'B3': 22.967668,
    'C4': 22.066789,
    'C#4': 21.190118,
    'D4': 20.339551,
    'D#4': 19.516636,
    'E4': 18.722591,
    'F4': 17.95833,
    'F#4': 17.222738,
    'G4': 16.51098,
    'G#4': 15.818407,
    'A4': 15.141074,
    'A#4': 14.475695,
    'B4': 13.819611,
    'C5': 13.170754,
    'C#5': 12.527623,
    'D5': 11.889258,
    'D#5': 11.254692,
    'E5': 10.616217,
    'F5': 9.963153,
    'F#5': 9.288427,
    'G5': 8.58882,
    'G#5': 7.864992,
    'A5': 7.121378,
    'A#5': 6.365879,
    'B5': 5.609303,
    'C6': 4.864553,
}

FF_MEASURED: dict[str, float] = {
    'C2': 58.007087,
    'C#2': 55.377223,
    'D2': 52.966574,
    'D#2': 50.743473,
    'E2': 48.680283,
    'F2': 46.752798,
    'F#2': 44.939761,
    'G2': 43.222465,
    'G#2': 41.584449,
    'A2': 40.01124,
    'A#2': 38.490234,
    'B2': 37.013136,
    'C3': 35.576092,
    'C#3': 34.175951,
    'D3': 32.80998,
    'D#3': 31.475836,
    'E3': 30.171542,
    'F3': 28.895463,
    'F#3': 27.646279,
    'G3': 26.422966,
    'G#3': 25.225246,
    'A3': 24.05633,
    'A#3': 22.920364,
    'B3': 21.820769,
    'C4': 20.76028,
    'C#4': 19.740999,
    'D4': 18.764459,
    'D#4': 17.831676,
    'E4': 16.94321,
    'F4': 16.099214,
    'F#4': 15.298355,
    'G4': 14.536819,
    'G#4': 13.810907,
    'A4': 13.117372,
    'A#4': 12.453373,
    'B4': 11.81643,
    'C5': 11.204394,
    'C#5': 10.615413,
    'D5': 10.047904,
    'D#5': 9.500173,
    'E5': 8.965781,
    'F5': 8.436076,
    'F#5': 7.904582,
    'G5': 7.367053,
    'G#5': 6.82143,
    'A5': 6.267786,
    'A#5': 5.708216,
    'B5': 5.146647,
    'C6': 4.588562,
}

# GPR anchors: pp/mf/ff all from Excel estimate_mean.
spectral_data = {
    'C2': {'pp': 54.072052, 'mf': 58.672456, 'ff': 58.007087},
    'C#2': {'pp': 49.168436, 'mf': 54.238289, 'ff': 55.377223},
    'D2': {'pp': 45.284304, 'mf': 50.629962, 'ff': 52.966574},
    'D#2': {'pp': 42.186098, 'mf': 47.670062, 'ff': 50.743473},
    'E2': {'pp': 39.697576, 'mf': 45.219622, 'ff': 48.680283},
    'F2': {'pp': 37.682888, 'mf': 43.167592, 'ff': 46.752798},
    'F#2': {'pp': 36.034836, 'mf': 41.423327, 'ff': 44.939761},
    'G2': {'pp': 34.666635, 'mf': 39.91122, 'ff': 43.222465},
    'G#2': {'pp': 33.506125, 'mf': 38.566877, 'ff': 41.584449},
    'A2': {'pp': 32.491719, 'mf': 37.334469, 'ff': 40.01124},
    'A#2': {'pp': 31.570027, 'mf': 36.165372, 'ff': 38.490234},
    'B2': {'pp': 30.707892, 'mf': 35.031712, 'ff': 37.013136},
    'C3': {'pp': 29.89361, 'mf': 33.927809, 'ff': 35.576092},
    'C#3': {'pp': 29.117762, 'mf': 32.849822, 'ff': 34.175951},
    'D3': {'pp': 28.371796, 'mf': 31.794333, 'ff': 32.80998},
    'D#3': {'pp': 27.647946, 'mf': 30.758323, 'ff': 31.475836},
    'E3': {'pp': 26.939161, 'mf': 29.73915, 'ff': 30.171542},
    'F3': {'pp': 26.239066, 'mf': 28.734533, 'ff': 28.895463},
    'F#3': {'pp': 25.541934, 'mf': 27.742538, 'ff': 27.646279},
    'G3': {'pp': 24.842667, 'mf': 26.761559, 'ff': 26.422966},
    'G#3': {'pp': 24.137203, 'mf': 25.790741, 'ff': 25.225246},
    'A3': {'pp': 23.424958, 'mf': 24.832534, 'ff': 24.05633},
    'A#3': {'pp': 22.706845, 'mf': 23.890476, 'ff': 22.920364},
    'B3': {'pp': 21.983857, 'mf': 22.967668, 'ff': 21.820769},
    'C4': {'pp': 21.257058, 'mf': 22.066789, 'ff': 20.76028},
    'C#4': {'pp': 20.527575, 'mf': 21.190118, 'ff': 19.740999},
    'D4': {'pp': 19.796589, 'mf': 20.339551, 'ff': 18.764459},
    'D#4': {'pp': 19.065334, 'mf': 19.516636, 'ff': 17.831676},
    'E4': {'pp': 18.335079, 'mf': 18.722591, 'ff': 16.94321},
    'F4': {'pp': 17.607127, 'mf': 17.95833, 'ff': 16.099214},
    'F#4': {'pp': 16.88247, 'mf': 17.222738, 'ff': 15.298355},
    'G4': {'pp': 16.161459, 'mf': 16.51098, 'ff': 14.536819},
    'G#4': {'pp': 15.44454, 'mf': 15.818407, 'ff': 13.810907},
    'A4': {'pp': 14.732346, 'mf': 15.141074, 'ff': 13.117372},
    'A#4': {'pp': 14.025686, 'mf': 14.475695, 'ff': 12.453373},
    'B4': {'pp': 13.325524, 'mf': 13.819611, 'ff': 11.81643},
    'C5': {'pp': 12.632963, 'mf': 13.170754, 'ff': 11.204394},
    'C#5': {'pp': 11.949221, 'mf': 12.527623, 'ff': 10.615413},
    'D5': {'pp': 11.275612, 'mf': 11.889258, 'ff': 10.047904},
    'D#5': {'pp': 10.613002, 'mf': 11.254692, 'ff': 9.500173},
    'E5': {'pp': 9.955103, 'mf': 10.616217, 'ff': 8.965781},
    'F5': {'pp': 9.292416, 'mf': 9.963153, 'ff': 8.436076},
    'F#5': {'pp': 8.618795, 'mf': 9.288427, 'ff': 7.904582},
    'G5': {'pp': 7.931568, 'mf': 8.58882, 'ff': 7.367053},
    'G#5': {'pp': 7.231456, 'mf': 7.864992, 'ff': 6.82143},
    'A5': {'pp': 6.522383, 'mf': 7.121378, 'ff': 6.267786},
    'A#5': {'pp': 5.811127, 'mf': 6.365879, 'ff': 5.708216},
    'B5': {'pp': 5.106783, 'mf': 5.609303, 'ff': 5.146647},
    'C6': {'pp': 4.42005, 'mf': 4.864553, 'ff': 4.588562},
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
