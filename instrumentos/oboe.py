# instrumentos/oboe.py
"""
Oboe instrument density module.

The ``spectral_data`` table stores sparse Combined Density Metric (CDM) values
from **external acoustic sources** (IOWA + ORCH sustain collections,
midpoint summary at pp/mf/ff). Intermediate dynamics are interpolated via GPR.

Runtime analysis does not ingest audio; it maps notated pitch + dynamic to these
pre-loaded acoustic metadata tables.
"""

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="external_acoustic_metadata",
    citation=(
        "Median/midpoint summary of oboe sustained-note Combined Density Metrics across IOWA and ORCH sound collections (pp, mf, ff)."
    ),
    source_url_or_identifier='D:\\MADEIRAS\\Oboe_Zenodo_collections_media.xlsx',
    extraction_method=(
        "Combined Density Metric midpoint of IOWA/ORCH collections (CDM midpoint pass-through; no rescaling); GPR interpolation by pitch/dynamic"
    ),
    dynamic_levels=("pp", "mf", "ff"),
    pitch_range=(58, 93),
    uncertainty="medium",
    version="2026-06-21",
    source_technique="ordinary_sustain",
    table_supported_techniques=("ordinary_sustain",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("oboe")

# CDM medians: (IOWA + ORCH) / 2 per note at pp, mf, ff (sustains (ordinario)).
spectral_data = {
    'A#3': {'pp': 20.844437, 'mf': 21.132024, 'ff': 22.893716},
    'B3': {'pp': 20.283897, 'mf': 17.726558, 'ff': 20.16692},
    'C4': {'pp': 20.339505, 'mf': 18.939844, 'ff': 23.655352},
    'C#4': {'pp': 27.956977, 'mf': 16.659845, 'ff': 23.813667},
    'D4': {'pp': 18.022136, 'mf': 18.679609, 'ff': 20.777438},
    'D#4': {'pp': 15.482, 'mf': 17.248336, 'ff': 17.978634},
    'E4': {'pp': 16.19799, 'mf': 16.184374, 'ff': 17.931524},
    'F4': {'pp': 14.789418, 'mf': 17.902125, 'ff': 17.600163},
    'F#4': {'pp': 18.910898, 'mf': 16.310339, 'ff': 20.029988},
    'G4': {'pp': 17.429853, 'mf': 16.863416, 'ff': 25.17009},
    'G#4': {'pp': 15.407602, 'mf': 16.916487, 'ff': 23.176601},
    'A4': {'pp': 11.432839, 'mf': 15.842353, 'ff': 17.747469},
    'A#4': {'pp': 9.982581, 'mf': 13.833124, 'ff': 12.685675},
    'B4': {'pp': 11.344167, 'mf': 14.506929, 'ff': 16.782882},
    'C5': {'pp': 7.753775, 'mf': 10.5167, 'ff': 16.443205},
    'C#5': {'pp': 6.911579, 'mf': 9.034225, 'ff': 11.986729},
    'D5': {'pp': 6.182216, 'mf': 8.935851, 'ff': 9.546777},
    'D#5': {'pp': 5.49729, 'mf': 6.709331, 'ff': 8.268481},
    'E5': {'pp': 4.483334, 'mf': 6.79142, 'ff': 6.669166},
    'F5': {'pp': 6.834389, 'mf': 6.420876, 'ff': 6.797098},
    'F#5': {'pp': 6.331304, 'mf': 7.011412, 'ff': 10.510806},
    'G5': {'pp': 5.169126, 'mf': 6.375497, 'ff': 10.597217},
    'G#5': {'pp': 4.403686, 'mf': 6.152496, 'ff': 8.982725},
    'A5': {'pp': 5.733516, 'mf': 5.358714, 'ff': 7.480106},
    'A#5': {'pp': 5.01456, 'mf': 5.1876, 'ff': 7.064289},
    'B5': {'pp': 5.221377, 'mf': 6.998395, 'ff': 8.164667},
    'C6': {'pp': 5.099623, 'mf': 6.257006, 'ff': 6.925072},
    'C#6': {'pp': 4.595749, 'mf': 5.881672, 'ff': 8.013866},
    'D6': {'pp': 4.858473, 'mf': 5.422988, 'ff': 5.823865},
    'D#6': {'pp': 4.808858, 'mf': 5.934514, 'ff': 6.385965},
    'E6': {'pp': 3.403393, 'mf': 4.872698, 'ff': 6.357171},
    'F6': {'pp': 4.946564, 'mf': 4.201035, 'ff': 5.148317},
    'F#6': {'pp': 5.031815, 'mf': 5.474542, 'ff': 6.390392},
    'G6': {'pp': 5.290093, 'mf': 5.458185, 'ff': 7.00477},
    'G#6': {'pp': 3.086277, 'mf': 4.77891, 'ff': 4.725206},
    'A6': {'pp':  4.439842, 'mf': 5.873266, 'ff': 5.038772},
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
