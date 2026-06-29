# instrumentos/violin_sul_ponticello.py
"""
Violin (arco sul ponticello) instrument density module.

Dynamic resolution chain (per note):

1. **Measured (source data):** ``mf`` only — stored in ``MF_MEASURED``.
2. **Extrapolated GPR anchors:** ``pp`` and ``ff`` derived per note from mf using
   violin arco pp/mf and ff/mf ratios (``mf_anchor_dynamic_extrapolation``).
3. **GPR-modelled dynamics:** ``pppp``, ``ppp``, ``p``, ``mp``, ``f``, ``fff``,
   ``ffff`` (and any other non-anchor marking handled by orchestration) are
   predicted by Gaussian-process regression fitted on the three anchors above,
   using the same ordinal coordinates as all other GPR string modules.

Direct ``calcular_densidade`` calls collapse non-anchor markings to the nearest
table anchor (pp/mf/ff). The production pipeline (GUI / ``calculate_metrics``)
uses GPR for intermediate and extreme dynamics instead.

Runtime analysis does not ingest audio; it maps notated pitch + dynamic to these
pre-loaded acoustic metadata tables.
"""

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="external_acoustic_metadata",
    citation=(
        "Sparse violin arco sul ponticello CDM table with measured mf anchor only; "
        "pp/ff extrapolated from violin arco per-note dynamic ratios."
    ),
    source_url_or_identifier='docs/instrument_acoustic_sources.md#violin-sul-ponticello',
    extraction_method=(
        "Measured mf CDM rows; pp and ff extrapolated via violin arco pp/mf and ff/mf "
        "ratio transfer; GPR interpolation by pitch/dynamic"
    ),
    dynamic_levels=("pp", "mf", "ff"),
    pitch_range=(55, 103),
    uncertainty="high",
    version="2026-06-30",
    source_technique="arco_sul_ponticello",
    table_supported_techniques=("arco_sul_ponticello",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("violin_sul_ponticello")

# Measured mf anchor only (source data).
MF_MEASURED: dict[str, float] = {
    'G3': 57.652253,
    'G#3': 47.578577,
    'A3': 33.641299,
    'A#3': 35.484226,
    'B3': 42.456811,
    'C4': 45.433064,
    'C#4': 26.230773,
    'D4': 23.710172,
    'D#4': 32.63583,
    'E4': 32.663202,
    'F4': 28.123378,
    'F#4': 24.164889,
    'G4': 23.203351,
    'G#4': 25.105871,
    'A4': 22.040514,
    'A#4': 26.738352,
    'B4': 24.579877,
    'C5': 21.225696,
    'C#5': 16.591108,
    'D5': 13.089099,
    'D#5': 16.027738,
    'E5': 23.790111,
    'F5': 23.987978,
    'F#5': 18.15761,
    'G5': 16.549326,
    'G#5': 16.42402,
    'A5': 14.830077,
    'A#5': 16.883831,
    'B5': 16.158749,
    'C6': 14.044264,
    'C#6': 12.682653,
    'D6': 14.045441,
    'D#6': 13.660168,
    'E6': 18.117977,
    'F6': 10.444054,
    'F#6': 10.832464,
    'G6': 11.898137,
    'G#6': 9.031915,
    'A6': 9.60888,
    'A#6': 9.086601,
    'B6': 6.873202,
    'C7': 7.041356,
    'C#7': 5.945355,
    'D7': 3.386709,
    'D#7': 3.086786,
    'E7': 3.231493,
    'F7': 3.191603,
    'F#7': 2.744721,
    'G7': 2.395781,
}

# GPR anchors: mf measured; pp/ff extrapolated from violin arco dynamic ratios.
spectral_data = {
    'G3': {'pp': 53.662011, 'mf': 57.652253, 'ff': 66.03417},
    'G#3': {'pp': 44.384984, 'mf': 47.578577, 'ff': 50.942365},
    'A3': {'pp': 35.44022, 'mf': 33.641299, 'ff': 48.813699},
    'A#3': {'pp': 31.785995, 'mf': 35.484226, 'ff': 42.67586},
    'B3': {'pp': 43.198541, 'mf': 42.456811, 'ff': 38.550206},
    'C4': {'pp': 53.140669, 'mf': 45.433064, 'ff': 54.025168},
    'C#4': {'pp': 29.698127, 'mf': 26.230773, 'ff': 30.685302},
    'D4': {'pp': 18.022315, 'mf': 23.710172, 'ff': 25.433012},
    'D#4': {'pp': 26.764887, 'mf': 32.63583, 'ff': 30.932375},
    'E4': {'pp': 28.28012, 'mf': 32.663202, 'ff': 31.583074},
    'F4': {'pp': 28.039282, 'mf': 28.123378, 'ff': 33.390478},
    'F#4': {'pp': 21.736661, 'mf': 24.164889, 'ff': 24.056769},
    'G4': {'pp': 21.304677, 'mf': 23.203351, 'ff': 23.672346},
    'G#4': {'pp': 26.76784, 'mf': 25.105871, 'ff': 31.297415},
    'A4': {'pp': 25.42962, 'mf': 22.040514, 'ff': 28.509813},
    'A#4': {'pp': 29.642359, 'mf': 26.738352, 'ff': 34.071179},
    'B4': {'pp': 24.647516, 'mf': 24.579877, 'ff': 23.341936},
    'C5': {'pp': 20.877724, 'mf': 21.225696, 'ff': 21.119491},
    'C#5': {'pp': 20.911126, 'mf': 16.591108, 'ff': 19.142928},
    'D5': {'pp': 11.914295, 'mf': 13.089099, 'ff': 13.286451},
    'D#5': {'pp': 16.535587, 'mf': 16.027738, 'ff': 18.071868},
    'E5': {'pp': 21.9152, 'mf': 23.790111, 'ff': 26.084181},
    'F5': {'pp': 20.807487, 'mf': 23.987978, 'ff': 26.1551},
    'F#5': {'pp': 15.059951, 'mf': 18.15761, 'ff': 21.666076},
    'G5': {'pp': 15.299926, 'mf': 16.549326, 'ff': 17.281665},
    'G#5': {'pp': 15.188318, 'mf': 16.42402, 'ff': 15.898707},
    'A5': {'pp': 13.376254, 'mf': 14.830077, 'ff': 17.344487},
    'A#5': {'pp': 15.043056, 'mf': 16.883831, 'ff': 16.318739},
    'B5': {'pp': 14.785527, 'mf': 16.158749, 'ff': 16.081929},
    'C6': {'pp': 12.566856, 'mf': 14.044264, 'ff': 16.793914},
    'C#6': {'pp': 11.155392, 'mf': 12.682653, 'ff': 14.620599},
    'D6': {'pp': 10.432584, 'mf': 14.045441, 'ff': 16.48539},
    'D#6': {'pp': 11.941817, 'mf': 13.660168, 'ff': 17.716116},
    'E6': {'pp': 16.027579, 'mf': 18.117977, 'ff': 16.468556},
    'F6': {'pp': 9.687134, 'mf': 10.444054, 'ff': 9.880654},
    'F#6': {'pp': 10.47344, 'mf': 10.832464, 'ff': 11.757871},
    'G6': {'pp': 9.071044, 'mf': 11.898137, 'ff': 11.415789},
    'G#6': {'pp': 6.396348, 'mf': 9.031915, 'ff': 7.932767},
    'A6': {'pp': 9.097401, 'mf': 9.60888, 'ff': 11.66543},
    'A#6': {'pp': 7.6911, 'mf': 9.086601, 'ff': 9.519015},
    'B6': {'pp': 6.41784, 'mf': 6.873202, 'ff': 7.96922},
    'C7': {'pp': 4.792654, 'mf': 7.041356, 'ff': 5.290558},
    'C#7': {'pp': 4.221296, 'mf': 5.945355, 'ff': 5.414829},
    'D7': {'pp': 3.059045, 'mf': 3.386709, 'ff': 3.591827},
    'D#7': {'pp': 2.156194, 'mf': 3.086786, 'ff': 3.486565},
    'E7': {'pp': 2.719198, 'mf': 3.231493, 'ff': 2.551685},
    'F7': {'pp': 2.467877, 'mf': 3.191603, 'ff': 2.821612},
    'F#7': {'pp': 2.558746, 'mf': 2.744721, 'ff': 2.296311},
    'G7': {'pp': 1.682204, 'mf': 2.395781, 'ff': 1.812858},
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
