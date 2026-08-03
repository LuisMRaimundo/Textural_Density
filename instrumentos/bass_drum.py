# instrumentos/bass_drum.py
"""
Bass drum instrument density module.

The ``spectral_data`` table stores sparse Combined Density Metric (CDM)
proxy values from **NonTunPerc Analysis** metrical exports
(``replication/percussion_nontunperc/Analysis/density_profiles.csv``).

- **ff:** strike-phase ``composite_index`` from Analysis ``density_profiles.csv``
- **pp/mf:** NonTunPerc excitation-filtered strike indices, scaled so ff
  matches the Analysis metrical value exactly

Unpitched strokes use a flat chromatic table over the registry nominal MIDI
sounding range; intermediate dynamics are interpolated via GPR.

Runtime analysis does not ingest audio; it maps notated pitch + dynamic to
these pre-loaded acoustic metadata tables.
"""

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="literature_derived",
    citation=('NonTunPerc Analysis density_profiles.csv strike composite_index for bassdrum_82cm (ff CDM proxy); pp/mf from NonTunPerc excitation-filtered profiles scaled so ff matches the Analysis metrical export.'),
    source_url_or_identifier=(
        "replication/percussion_nontunperc/Analysis/density_profiles.csv"
    ),
    extraction_method=(
        "Analysis density_profiles.csv strike composite_index → ff; "
        "NonTunPerc generate_profile(stroke,dynamic) strike indices → pp/mf "
        "with scale so ff matches Analysis; flat chromatic CDM proxy; "
        "GPR interpolation by pitch/dynamic"
    ),
    dynamic_levels=("pp", "mf", "ff"),
    pitch_range=(28, 48),
    uncertainty="high",
    version="2026-08-03",
    source_technique="struck_membrane",
    table_supported_techniques=("struck_membrane",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("bass_drum")

# Flat CDM proxy across nominal sounding range (unpitched; note is metadata only).
spectral_data = {
    'E1': {'pp': 2.18772, 'mf': 3.703499, 'ff': 6.576554},
    'F1': {'pp': 2.18772, 'mf': 3.703499, 'ff': 6.576554},
    'F#1': {'pp': 2.18772, 'mf': 3.703499, 'ff': 6.576554},
    'G1': {'pp': 2.18772, 'mf': 3.703499, 'ff': 6.576554},
    'G#1': {'pp': 2.18772, 'mf': 3.703499, 'ff': 6.576554},
    'A1': {'pp': 2.18772, 'mf': 3.703499, 'ff': 6.576554},
    'A#1': {'pp': 2.18772, 'mf': 3.703499, 'ff': 6.576554},
    'B1': {'pp': 2.18772, 'mf': 3.703499, 'ff': 6.576554},
    'C2': {'pp': 2.18772, 'mf': 3.703499, 'ff': 6.576554},
    'C#2': {'pp': 2.18772, 'mf': 3.703499, 'ff': 6.576554},
    'D2': {'pp': 2.18772, 'mf': 3.703499, 'ff': 6.576554},
    'D#2': {'pp': 2.18772, 'mf': 3.703499, 'ff': 6.576554},
    'E2': {'pp': 2.18772, 'mf': 3.703499, 'ff': 6.576554},
    'F2': {'pp': 2.18772, 'mf': 3.703499, 'ff': 6.576554},
    'F#2': {'pp': 2.18772, 'mf': 3.703499, 'ff': 6.576554},
    'G2': {'pp': 2.18772, 'mf': 3.703499, 'ff': 6.576554},
    'G#2': {'pp': 2.18772, 'mf': 3.703499, 'ff': 6.576554},
    'A2': {'pp': 2.18772, 'mf': 3.703499, 'ff': 6.576554},
    'A#2': {'pp': 2.18772, 'mf': 3.703499, 'ff': 6.576554},
    'B2': {'pp': 2.18772, 'mf': 3.703499, 'ff': 6.576554},
    'C3': {'pp': 2.18772, 'mf': 3.703499, 'ff': 6.576554},
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

    return predict_intermediate_dynamics_gpr(
        pp_values, mf_values, ff_values, logger=logger
    )
