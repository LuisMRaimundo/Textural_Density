# instrumentos/trumpet.py
"""
Trumpet (Bb) instrument density module.

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
        "Median/midpoint summary of trumpet sustained-note Combined Density Metrics across IOWA and ORCH sound collections (pp, mf, ff)."
    ),
    source_url_or_identifier='D:\\METAIS\\Trumpet_Zenodo_collections_media.xlsx',
    extraction_method=(
        "Combined Density Metric midpoint of IOWA/ORCH collections (CDM midpoint pass-through; no rescaling); GPR interpolation by pitch/dynamic"
    ),
    dynamic_levels=("pp", "mf", "ff"),
    pitch_range=(52, 87),
    uncertainty="medium",
    version="2026-07-11",
    source_technique="ordinary_sustain",
    table_supported_techniques=("ordinary_sustain",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("trumpet")

# CDM medians: (IOWA + ORCH) / 2 per note at pp, mf, ff (sustains (ordinario)).
spectral_data = {
    'E3': {'pp': 32.438944, 'mf': 46.414616, 'ff': 114.646381},
    'F3': {'pp': 32.450831, 'mf': 45.513054, 'ff': 104.873930},
    'F#3': {'pp': 31.682840, 'mf': 45.384444, 'ff': 95.533161},
    'G3': {'pp': 30.578924, 'mf': 47.157859, 'ff': 98.648096},
    'G#3': {'pp': 23.689108, 'mf': 38.796385, 'ff': 70.349300},
    'A3': {'pp': 21.276720, 'mf': 30.204642, 'ff': 67.644764},
    'A#3': {'pp': 19.878389, 'mf': 30.893125, 'ff': 66.721079},
    'B3': {'pp': 20.759227, 'mf': 33.446236, 'ff': 51.143680},
    'C4': {'pp': 19.546937, 'mf': 31.649330, 'ff': 55.585461},
    'C#4': {'pp': 18.046234, 'mf': 32.219324, 'ff': 53.724940},
    'D4': {'pp': 17.606479, 'mf': 28.346052, 'ff': 47.730246},
    'D#4': {'pp': 17.965970, 'mf': 30.899544, 'ff': 40.618171},
    'E4': {'pp': 15.737618, 'mf': 27.583784, 'ff': 37.981762},
    'F4': {'pp': 14.660052, 'mf': 23.949086, 'ff': 34.459141},
    'F#4': {'pp': 14.138190, 'mf': 21.058538, 'ff': 36.358747},
    'G4': {'pp': 12.896852, 'mf': 23.100219, 'ff': 36.127025},
    'G#4': {'pp': 11.891756, 'mf': 21.141829, 'ff': 39.221104},
    'A4': {'pp': 11.892367, 'mf': 18.747277, 'ff': 37.614501},
    'A#4': {'pp': 11.695127, 'mf': 20.370647, 'ff': 37.775817},
    'B4': {'pp': 10.787306, 'mf': 19.073517, 'ff': 29.328791},
    'C5': {'pp': 8.049778, 'mf': 12.180896, 'ff': 23.241989},
    'C#5': {'pp': 7.356796, 'mf': 12.284252, 'ff': 18.973537},
    'D5': {'pp': 6.933087, 'mf': 11.674811, 'ff': 20.890838},
    'D#5': {'pp': 7.410795, 'mf': 10.899837, 'ff': 16.388274},
    'E5': {'pp': 8.235846, 'mf': 10.459737, 'ff': 17.705136},
    'F5': {'pp': 6.191983, 'mf': 10.609036, 'ff': 16.809704},
    'F#5': {'pp': 6.576007, 'mf': 10.373329, 'ff': 19.313608},
    'G5': {'pp': 6.327439, 'mf': 10.334344, 'ff': 16.740580},
    'G#5': {'pp': 6.701294, 'mf': 10.272295, 'ff': 14.696774},
    'A5': {'pp': 6.075068, 'mf': 9.944491, 'ff': 16.519243},
    'A#5': {'pp': 6.835218, 'mf': 9.777349, 'ff': 19.991531},
    'B5': {'pp': 5.941351, 'mf': 8.777226, 'ff': 15.461728},
    'C6': {'pp': 5.787870, 'mf': 8.791180, 'ff': 11.134150},
    'C#6': {'pp': 5.527210, 'mf': 8.346769, 'ff': 12.095545},
    'D6': {'pp': 6.471091, 'mf': 8.911979, 'ff': 11.369878},
    'D#6': {'pp': 5.262300, 'mf': 8.918069, 'ff': 10.259449},
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
