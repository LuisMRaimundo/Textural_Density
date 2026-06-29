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
    version="2026-06-29",
    source_technique="arco_sul_ponticello",
    table_supported_techniques=("arco_sul_ponticello",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("violin_sul_ponticello")

# Measured mf anchor only (source data).
MF_MEASURED: dict[str, float] = {
    'G3': 47.829341,
    'G#3': 25.47046,
    'A3': 38.949341,
    'A#3': 38.060709,
    'B3': 34.745473,
    'C4': 24.794748,
    'C#4': 17.996875,
    'D4': 22.566453,
    'D#4': 28.079596,
    'E4': 24.384366,
    'F4': 19.671222,
    'F#4': 15.5584,
    'G4': 20.557578,
    'G#4': 13.419066,
    'A4': 14.663539,
    'A#4': 18.09879,
    'B4': 24.1738,
    'C5': 20.468627,
    'C#5': 14.907723,
    'D5': 17.860083,
    'D#5': 18.73179,
    'E5': 21.962632,
    'F5': 18.42943,
    'F#5': 18.728701,
    'G5': 13.968601,
    'G#5': 13.647852,
    'A5': 14.548303,
    'A#5': 13.368779,
    'B5': 15.197647,
    'C6': 12.420372,
    'C#6': 12.271476,
    'D6': 12.70586,
    'D#6': 12.957405,
    'E6': 12.403246,
    'F6': 10.113389,
    'F#6': 9.331383,
    'G6': 9.886641,
    'G#6': 7.891357,
    'A6': 7.737971,
    'A#6': 7.910347,
    'B6': 6.111945,
    'C7': 5.732009,
    'C#7': 4.350238,
    'D7': 3.206277,
    'D#7': 3.100384,
    'E7': 2.301219,
    'F7': 2.421042,
    'F#7': 2.451886,
    'G7': 1.569536,
}

# GPR anchors: mf measured; pp/ff extrapolated from violin arco dynamic ratios.
spectral_data = {
    'G3': {'pp': 44.518965, 'mf': 47.829341, 'ff': 54.783129},
    'G#3': {'pp': 23.760819, 'mf': 25.47046, 'ff': 27.271212},
    'A3': {'pp': 41.032102, 'mf': 38.949341, 'ff': 56.515695},
    'A#3': {'pp': 34.093952, 'mf': 38.060709, 'ff': 45.774523},
    'B3': {'pp': 35.352484, 'mf': 34.745473, 'ff': 31.548416},
    'C4': {'pp': 29.001114, 'mf': 24.794748, 'ff': 29.483823},
    'C#4': {'pp': 20.375819, 'mf': 17.996875, 'ff': 21.053117},
    'D4': {'pp': 17.152964, 'mf': 22.566453, 'ff': 24.206187},
    'D#4': {'pp': 23.028286, 'mf': 28.079596, 'ff': 26.613957},
    'E4': {'pp': 21.112223, 'mf': 24.384366, 'ff': 23.578008},
    'F4': {'pp': 19.6124, 'mf': 19.671222, 'ff': 23.355356},
    'F#4': {'pp': 13.995002, 'mf': 15.5584, 'ff': 15.488788},
    'G4': {'pp': 18.875401, 'mf': 20.557578, 'ff': 20.973096},
    'G#4': {'pp': 14.307387, 'mf': 13.419066, 'ff': 16.728441},
    'A4': {'pp': 16.918309, 'mf': 14.663539, 'ff': 18.967559},
    'A#4': {'pp': 20.064469, 'mf': 18.09879, 'ff': 23.062271},
    'B4': {'pp': 24.240322, 'mf': 24.1738, 'ff': 22.95631},
    'C5': {'pp': 20.133066, 'mf': 20.468627, 'ff': 20.36621},
    'C#5': {'pp': 18.789419, 'mf': 14.907723, 'ff': 17.200628},
    'D5': {'pp': 16.257062, 'mf': 17.860083, 'ff': 18.129369},
    'D#5': {'pp': 19.325319, 'mf': 18.73179, 'ff': 21.120787},
    'E5': {'pp': 20.231746, 'mf': 21.962632, 'ff': 24.080479},
    'F5': {'pp': 15.985929, 'mf': 18.42943, 'ff': 20.094381},
    'F#5': {'pp': 15.533615, 'mf': 18.728701, 'ff': 22.347515},
    'G5': {'pp': 12.914034, 'mf': 13.968601, 'ff': 14.586738},
    'G#5': {'pp': 12.621022, 'mf': 13.647852, 'ff': 13.211333},
    'A5': {'pp': 13.122103, 'mf': 14.548303, 'ff': 17.014939},
    'A#5': {'pp': 11.911236, 'mf': 13.368779, 'ff': 12.921333},
    'B5': {'pp': 13.906103, 'mf': 15.197647, 'ff': 15.125396},
    'C6': {'pp': 11.113792, 'mf': 12.420372, 'ff': 14.852089},
    'C#6': {'pp': 10.793729, 'mf': 12.271476, 'ff': 14.146593},
    'D6': {'pp': 9.437578, 'mf': 12.70586, 'ff': 14.913099},
    'D#6': {'pp': 11.327456, 'mf': 12.957405, 'ff': 16.80469},
    'E6': {'pp': 10.972197, 'mf': 12.403246, 'ff': 11.274081},
    'F6': {'pp': 9.380434, 'mf': 10.113389, 'ff': 9.567826},
    'F#6': {'pp': 9.022109, 'mf': 9.331383, 'ff': 10.128554},
    'G6': {'pp': 7.537495, 'mf': 9.886641, 'ff': 9.485839},
    'G#6': {'pp': 5.588611, 'mf': 7.891357, 'ff': 6.931011},
    'A6': {'pp': 7.32608, 'mf': 7.737971, 'ff': 9.394098},
    'A#6': {'pp': 6.695492, 'mf': 7.910347, 'ff': 8.286785},
    'B6': {'pp': 5.707018, 'mf': 6.111945, 'ff': 7.086571},
    'C7': {'pp': 3.901455, 'mf': 5.732009, 'ff': 4.306773},
    'C#7': {'pp': 3.088737, 'mf': 4.350238, 'ff': 3.96205},
    'D7': {'pp': 2.89607, 'mf': 3.206277, 'ff': 3.400467},
    'D#7': {'pp': 2.165692, 'mf': 3.100384, 'ff': 3.501924},
    'E7': {'pp': 1.936402, 'mf': 2.301219, 'ff': 1.817112},
    'F7': {'pp': 1.872048, 'mf': 2.421042, 'ff': 2.140379},
    'F#7': {'pp': 2.285753, 'mf': 2.451886, 'ff': 2.051317},
    'G7': {'pp': 1.102054, 'mf': 1.569536, 'ff': 1.187648},
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
