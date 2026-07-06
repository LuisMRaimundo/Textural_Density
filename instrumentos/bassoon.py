# instrumentos/bassoon.py
"""
Bassoon instrument density module.

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
        "Median/midpoint summary of bassoon sustained-note Combined Density Metrics across IOWA and ORCH sound collections (pp, mf, ff)."
    ),
    source_url_or_identifier='D:\\MADEIRAS\\Bassoon_Zenodo_collections_media.xlsx',
    extraction_method=(
        "Combined Density Metric midpoint of IOWA/ORCH collections (CDM midpoint pass-through; no rescaling); GPR interpolation by pitch/dynamic"
    ),
    dynamic_levels=("pp", "mf", "ff"),
    pitch_range=(34, 75),
    uncertainty="medium",
    version="2026-07-06",
    source_technique="ordinary_sustain",
    table_supported_techniques=("ordinary_sustain",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("bassoon")

# CDM medians: (IOWA + ORCH) / 2 per note at pp, mf, ff (sustains (ordinario)).
spectral_data = {
    'A#1': {'pp': 60.112884, 'mf': 82.082187, 'ff': 115.200631},
    'B1': {'pp': 67.334597, 'mf': 70.608465, 'ff': 108.404336},
    'C2': {'pp': 61.50509, 'mf': 63.451659, 'ff': 93.431898},
    'C#2': {'pp': 44.632087, 'mf': 45.327772, 'ff': 54.145859},
    'D2': {'pp': 47.045754, 'mf': 50.818887, 'ff': 51.268523},
    'D#2': {'pp': 38.161244, 'mf': 45.023381, 'ff': 56.127555},
    'E2': {'pp': 30.491994, 'mf': 36.698836, 'ff': 46.101874},
    'F2': {'pp': 37.191381, 'mf': 42.582053, 'ff': 44.376113},
    'F#2': {'pp': 31.660461, 'mf': 37.079685, 'ff': 41.069527},
    'G2': {'pp': 22.673724, 'mf': 30.906966, 'ff': 32.645658},
    'G#2': {'pp': 29.183647, 'mf': 29.203203, 'ff': 34.50579},
    'A2': {'pp': 24.588876, 'mf': 29.069409, 'ff': 32.445937},
    'A#2': {'pp': 24.010092, 'mf': 29.111408, 'ff': 30.666221},
    'B2': {'pp': 22.619395, 'mf': 27.063989, 'ff': 32.944671},
    'C3': {'pp': 22.650121, 'mf': 25.560195, 'ff': 31.029659},
    'C#3': {'pp': 16.38565, 'mf': 24.344905, 'ff': 30.834523},
    'D3': {'pp': 18.670381, 'mf': 24.890236, 'ff': 25.890483},
    'D#3': {'pp': 18.991454, 'mf': 23.770827, 'ff': 30.881352},
    'E3': {'pp': 13.079968, 'mf': 17.560663, 'ff': 25.459988},
    'F3': {'pp': 19.217275, 'mf': 23.505008, 'ff': 31.891148},
    'F#3': {'pp': 16.472004, 'mf': 19.165129, 'ff': 21.822608},
    'G3': {'pp': 15.658701, 'mf': 17.8718, 'ff': 22.791335},
    'G#3': {'pp': 17.443661, 'mf': 19.382364, 'ff': 20.958858},
    'A3': {'pp': 15.104971, 'mf': 15.356676, 'ff': 17.945941},
    'A#3': {'pp': 10.820228, 'mf': 12.96143, 'ff': 13.752958},
    'B3': {'pp': 9.855421, 'mf': 11.679629, 'ff': 12.261966},
    'C4': {'pp': 13.073926, 'mf': 13.852624, 'ff': 14.201543},
    'C#4': {'pp': 9.396726, 'mf': 9.331062, 'ff': 11.634741},
    'D4': {'pp': 8.994419, 'mf': 9.833251, 'ff': 10.521924},
    'D#4': {'pp': 9.566457, 'mf': 13.481235, 'ff': 13.420602},
    'E4': {'pp': 9.516094, 'mf': 9.967572, 'ff': 10.610339},
    'F4': {'pp': 14.362144, 'mf': 12.928177, 'ff': 18.309567},
    'F#4': {'pp': 10.266545, 'mf': 7.977475, 'ff': 9.269676},
    'G4': {'pp': 13.694737, 'mf': 13.580782, 'ff': 16.414992},
    'G#4': {'pp': 12.215962, 'mf': 14.026172, 'ff': 11.106307},
    'A4': {'pp': 14.831893, 'mf': 7.473162, 'ff': 14.710054},
    'A#4': {'pp': 6.697716, 'mf': 6.946417, 'ff': 11.142307},
    'B4': {'pp': 6.281922, 'mf': 7.618266, 'ff': 10.2809},
    'C5': {'pp': 7.063705, 'mf': 5.596543, 'ff': 8.65714},
    'C#5': {'pp': 7.082404, 'mf': 3.747398, 'ff': 4.723837},
    'D5': {'pp': 4.112753, 'mf': 4.800128, 'ff': 6.540951},
    'D#5': {'pp': 5.943685, 'mf': 5.788072, 'ff': 6.890604},
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
