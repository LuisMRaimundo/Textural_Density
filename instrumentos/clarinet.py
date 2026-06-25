# instrumentos/clarinet.py
"""
Clarinet instrument density module.

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
        "Median/midpoint summary of clarinet sustained-note Combined Density Metrics across IOWA and ORCH sound collections (pp, mf, ff)."
    ),
    source_url_or_identifier='D:\\MADEIRAS\\Clarinet_Zenodo_collections_media.xlsx',
    extraction_method=(
        "Combined Density Metric midpoint of IOWA/ORCH collections (CDM midpoint pass-through; no rescaling); GPR interpolation by pitch/dynamic"
    ),
    dynamic_levels=("pp", "mf", "ff"),
    pitch_range=(50, 96),
    uncertainty="medium",
    version="2026-06-21",
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("clarinet")

# CDM medians: (IOWA + ORCH) / 2 per note at pp, mf, ff (sustains (ordinario)).
spectral_data = {
    'D3': {'pp': 11.903889, 'mf': 36.303041, 'ff': 42.864557},
    'D#3': {'pp': 15.312107, 'mf': 46.242576, 'ff': 47.969891},
    'E3': {'pp': 12.955682, 'mf': 42.30675, 'ff': 42.629695},
    'F3': {'pp': 11.828066, 'mf': 34.488982, 'ff': 44.845996},
    'F#3': {'pp': 10.411736, 'mf': 31.127683, 'ff': 45.702062},
    'G3': {'pp': 9.635438, 'mf': 26.358525, 'ff': 36.736956},
    'G#3': {'pp': 7.823748, 'mf': 18.837243, 'ff': 25.315938},
    'A3': {'pp': 8.626581, 'mf': 19.48731, 'ff': 25.191308},
    'A#3': {'pp': 7.45531, 'mf': 20.740353, 'ff': 22.113254},
    'B3': {'pp': 6.444599, 'mf': 18.55134, 'ff': 24.848007},
    'C4': {'pp': 5.297686, 'mf': 17.525757, 'ff': 26.949363},
    'C#4': {'pp': 5.360529, 'mf': 15.457444, 'ff': 21.814225},
    'D4': {'pp': 5.424456, 'mf': 17.389167, 'ff': 22.22991},
    'D#4': {'pp': 5.678017, 'mf': 14.628142, 'ff': 16.141993},
    'E4': {'pp': 6.392963, 'mf': 15.119309, 'ff': 15.091111},
    'F4': {'pp': 4.734192, 'mf': 12.982403, 'ff': 20.508392},
    'F#4': {'pp': 7.44362, 'mf': 13.331836, 'ff': 18.910568},
    'G4': {'pp': 6.221009, 'mf': 12.077698, 'ff': 15.583904},
    'G#4': {'pp': 6.381125, 'mf': 11.19551, 'ff': 14.144692},
    'A4': {'pp': 6.842638, 'mf': 9.92446, 'ff': 14.421695},
    'A#4': {'pp': 7.535291, 'mf': 11.824642, 'ff': 15.70528},
    'B4': {'pp': 6.861462, 'mf': 10.927506, 'ff': 14.199126},
    'C5': {'pp': 4.336489, 'mf': 7.857858, 'ff': 9.33885},
    'C#5': {'pp': 5.93285, 'mf': 8.563804, 'ff': 11.44536},
    'D5': {'pp': 6.321052, 'mf': 8.585646, 'ff': 8.970291},
    'D#5': {'pp': 5.779091, 'mf': 7.208623, 'ff': 7.769588},
    'E5': {'pp': 3.057712, 'mf': 6.962039, 'ff': 8.417246},
    'F5': {'pp': 4.189109, 'mf': 5.873598, 'ff': 7.224448},
    'F#5': {'pp': 4.049515, 'mf': 6.942169, 'ff': 8.315949},
    'G5': {'pp': 3.776513, 'mf': 6.870699, 'ff': 7.535695},
    'G#5': {'pp': 4.143959, 'mf': 5.391318, 'ff': 6.845354},
    'A5': {'pp': 3.878603, 'mf': 5.794484, 'ff': 7.337376},
    'A#5': {'pp': 3.669605, 'mf': 4.990902, 'ff': 6.596684},
    'B5': {'pp': 4.162225, 'mf': 5.625973, 'ff': 7.242145},
    'C6': {'pp': 4.008, 'mf': 6.928537, 'ff': 7.218995},
    'C#6': {'pp': 4.74413, 'mf': 5.692513, 'ff': 6.368469},
    'D6': {'pp': 3.387024, 'mf': 5.866964, 'ff': 6.298073},
    'D#6': {'pp': 3.673938, 'mf': 4.886739, 'ff': 5.716934},
    'E6': {'pp': 3.12203, 'mf': 4.014344, 'ff': 4.819832},
    'F6': {'pp': 2.93936, 'mf': 3.982764, 'ff': 4.408274},
    'F#6': {'pp': 1.754258, 'mf': 3.235531, 'ff': 4.173518},
    'G6': {'pp': 3.494253, 'mf': 2.866412, 'ff': 5.505037},
    'G#6': {'pp': 3.12221, 'mf': 2.889422, 'ff': 4.479782},
    'A6': {'pp': 3.323653, 'mf': 4.542583, 'ff': 4.646555},
    'A#6': {'pp': 2.877114, 'mf': 3.903432, 'ff': 4.306829},
    'B6': {'pp': 2.782129, 'mf': 3.790151, 'ff': 7.344033},
    'C7': {'pp': 2.695233, 'mf': 1.972507, 'ff': 5.09456},
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
