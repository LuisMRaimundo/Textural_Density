# instrumentos/violin_art_harm.py
"""
Violin (arco artificial harmonics) instrument density module.

Dynamic resolution chain (per note):

1. **Measured (source data):** ``mf`` only — stored in ``MF_MEASURED``.
2. **Extrapolated GPR anchors:** ``pp`` and ``ff`` derived per note from mf using
   violin arco pp/mf and ff/mf ratios (``mf_anchor_dynamic_extrapolation``).
3. **GPR-modelled dynamics:** ``pppp``, ``ppp``, ``p``, ``mp``, ``f``, ``fff``,
   ``ffff`` are predicted by Gaussian-process regression on the three anchors.

Direct ``calcular_densidade`` calls collapse non-anchor markings to the nearest
table anchor (pp/mf/ff). The production pipeline uses GPR for other dynamics.

Runtime analysis does not ingest audio; it maps notated pitch + dynamic to these
pre-loaded acoustic metadata tables.
"""

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="external_acoustic_metadata",
    citation=(
        "Sparse violin arco artificial-harmonic CDM table with measured mf anchor only; "
        "pp/ff extrapolated from violin arco per-note dynamic ratios."
    ),
    source_url_or_identifier='docs/instrument_acoustic_sources.md#violin-art-harm',
    extraction_method=(
        "Measured mf CDM rows; pp and ff extrapolated via violin arco pp/mf and ff/mf "
        "ratio transfer; GPR interpolation by pitch/dynamic"
    ),
    dynamic_levels=("pp", "mf", "ff"),
    pitch_range=(79, 103),
    uncertainty="high",
    version="2026-06-29",
    source_technique="arco_artificial_harmonic",
    table_supported_techniques=("arco_artificial_harmonic",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("violin_art_harm")

# Measured mf anchor only (source data).
MF_MEASURED: dict[str, float] = {
    'G5': 12.974202,
    'G#5': 11.284534,
    'A5': 10.221026,
    'A#5': 8.60228,
    'B5': 10.500393,
    'C6': 8.102233,
    'C#6': 6.817026,
    'D6': 6.822602,
    'D#6': 8.455698,
    'E6': 7.698407,
    'F6': 7.633572,
    'F#6': 7.285399,
    'G6': 6.552264,
    'G#6': 6.752588,
    'A6': 8.292656,
    'A#6': 5.692625,
    'B6': 4.435892,
    'C7': 5.209404,
    'C#7': 5.480056,
    'D7': 3.2801,
    'D#7': 2.999644,
    'E7': 6.518378,
    'F7': 7.110205,
    'F#7': 6.825273,
    'G7': 5.525015,
}

# GPR anchors: mf measured; pp/ff extrapolated from violin arco dynamic ratios.
spectral_data = {
    'G5': {'pp': 11.994708, 'mf': 12.974202, 'ff': 13.548335},
    'G#5': {'pp': 10.435514, 'mf': 11.284534, 'ff': 10.923605},
    'A5': {'pp': 9.219038, 'mf': 10.221026, 'ff': 11.953981},
    'A#5': {'pp': 7.664408, 'mf': 8.60228, 'ff': 8.314366},
    'B5': {'pp': 9.608036, 'mf': 10.500393, 'ff': 10.450473},
    'C6': {'pp': 7.249906, 'mf': 8.102233, 'ff': 9.688525},
    'C#6': {'pp': 5.996111, 'mf': 6.817026, 'ff': 7.858687},
    'D6': {'pp': 5.067649, 'mf': 6.822602, 'ff': 8.007812},
    'D#6': {'pp': 7.392032, 'mf': 8.455698, 'ff': 10.966346},
    'E6': {'pp': 6.810188, 'mf': 7.698407, 'ff': 6.997561},
    'F6': {'pp': 7.080338, 'mf': 7.633572, 'ff': 7.221782},
    'F#6': {'pp': 7.043936, 'mf': 7.285399, 'ff': 7.907783},
    'G6': {'pp': 4.995393, 'mf': 6.552264, 'ff': 6.286637},
    'G#6': {'pp': 4.782142, 'mf': 6.752588, 'ff': 5.930825},
    'A6': {'pp': 7.851239, 'mf': 8.292656, 'ff': 10.0675},
    'A#6': {'pp': 4.818364, 'mf': 5.692625, 'ff': 5.963526},
    'B6': {'pp': 4.142006, 'mf': 4.435892, 'ff': 5.14325},
    'C7': {'pp': 3.545747, 'mf': 5.209404, 'ff': 3.914112},
    'C#7': {'pp': 3.890926, 'mf': 5.480056, 'ff': 4.99105},
    'D7': {'pp': 2.96275, 'mf': 3.2801, 'ff': 3.478761},
    'D#7': {'pp': 2.095323, 'mf': 2.999644, 'ff': 3.388137},
    'E7': {'pp': 5.485007, 'mf': 6.518378, 'ff': 5.147109},
    'F7': {'pp': 5.4979, 'mf': 7.110205, 'ff': 6.285945},
    'F#7': {'pp': 6.36281, 'mf': 6.825273, 'ff': 5.710216},
    'G7': {'pp': 3.879404, 'mf': 5.525015, 'ff': 4.18071},
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
