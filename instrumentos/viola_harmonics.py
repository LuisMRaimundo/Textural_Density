# instrumentos/viola_harmonics.py
"""
Viola (arco harmonics) instrument density module.

The ``spectral_data`` table stores a committed 10-dynamic Combined Density
Metric (CDM) ladder from the ``Results`` sheet of
``Viola_Zenodo_collections_harmonics_Dynamics10.xlsx``
(measured pp/mf/ff anchors; remaining levels committed from that workbook —
no runtime dynamic extrapolation).

Runtime analysis does not ingest audio; it maps notated pitch + dynamic to
these pre-loaded acoustic metadata tables.
"""

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="external_acoustic_metadata",
    citation=(
        "Viola arco_harmonic CDM ladder: measured pp/mf/ff anchors with "
        "committed Results sheet values for all 10 dynamic levels from "
        "Viola_Zenodo_collections_harmonics_Dynamics10.xlsx "
        "(dest Zenodo Viola_harmonics Media (IOWA+Orchidea average); Dynamics_predicter Results ladder (CORDAS_4))."
    ),
    source_url_or_identifier='docs/instrument_acoustic_sources.md#viola-harmonics',
    extraction_method=(
        "Committed full dynamic ladder from Dynamics extrapolator v1.5.2.1 Results sheet "
        "(PCHIP interiors, tapered outers r=0.80) on measured pp/mf/ff anchors; "
        "interior cells clamped into their measured segment where the workbook "
        "marginally overshoots; pitch lookup via MIDI-space spectral_lookup"
    ),
    dynamic_levels=('pppp', 'ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', 'ffff'),
    pitch_range=(72, 94),
    uncertainty="high",
    version="2026-09-18",
    source_technique="arco_harmonic",
    table_supported_techniques=("arco_harmonic",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("viola_harmonics")

# Full 10-dynamic CDM ladder (Results sheet). Anchors pp/mf/ff match measured
# workbook midpoints; other levels are workbook-committed.
spectral_data = {
    'C5': {'pppp': 15.18262, 'ppp': 15.817456, 'pp': 16.648457, 'p': 18.273097, 'mp': 19.216505, 'mf': 19.50897, 'f': 18.934923, 'ff': 17.50901, 'fff': 16.615902, 'ffff': 15.934329},
    'C#5': {'pppp': 15.990015, 'ppp': 16.203397, 'pp': 16.474133, 'p': 16.957625, 'mp': 17.299537, 'mf': 17.428794, 'f': 17.412973, 'ff': 17.302631, 'fff': 17.255191, 'ffff': 17.217332},
    'D5': {'pppp': 12.763937, 'ppp': 13.25902, 'pp': 13.904965, 'p': 15.030925, 'mp': 15.839783, 'mf': 16.146812, 'f': 16.082592, 'ff': 15.707363, 'fff': 15.50471, 'ffff': 15.344471},
    'D#5': {'pppp': 18.390064, 'ppp': 17.835495, 'pp': 17.165741, 'p': 15.989722, 'mp': 15.408691, 'mf': 15.245443, 'f': 15.639486, 'ff': 16.692607, 'fff': 17.44197, 'ffff': 18.065609},
    'E5': {'pppp': 12.420076, 'ppp': 12.358137, 'pp': 12.281148, 'p': 12.214841, 'mp': 12.13362, 'mf': 12.041933, 'f': 11.934716, 'ff': 11.810535, 'fff': 11.720392, 'ffff': 11.648773},
    'F5': {'pppp': 11.65115, 'ppp': 11.888959, 'pp': 12.193058, 'p': 12.830853, 'mp': 13.133665, 'mf': 13.207073, 'f': 12.881302, 'ff': 12.130351, 'fff': 11.650266, 'ffff': 11.279914},
    'F#5': {'pppp': 11.961128, 'ppp': 12.407195, 'pp': 12.988244, 'p': 13.996757, 'mp': 14.72469, 'mf': 15.002138, 'f': 14.955784, 'ff': 14.641886, 'fff': 14.476237, 'ffff': 14.345068},
    'G5': {'pppp': 13.824313, 'ppp': 14.215853, 'pp': 14.720909, 'p': 15.755284, 'mp': 16.278888, 'mf': 16.41716, 'f': 15.932634, 'ff': 14.804988, 'fff': 14.087916, 'ffff': 13.539347},
    'G#5': {'pppp': 16.748742, 'ppp': 16.775515, 'pp': 16.809042, 'p': 16.823605, 'mp': 16.866936, 'mf': 16.938598, 'f': 17.35396, 'ff': 18.164253, 'fff': 18.764418, 'ffff': 19.258796},
    'A5': {'pppp': 16.941504, 'ppp': 16.863671, 'pp': 16.766882, 'p': 16.612435, 'mp': 16.503344, 'mf': 16.461971, 'f': 16.46422, 'ff': 16.479974, 'fff': 16.505165, 'ffff': 16.525345},
    'A#5': {'pppp': 16.535671, 'ppp': 16.397672, 'pp': 16.226791, 'p': 15.922045, 'mp': 15.744962, 'mf': 15.687282, 'f': 15.753005, 'ff': 15.945592, 'fff': 16.071706, 'ffff': 16.173314},
    'B5': {'pppp': 14.418466, 'ppp': 14.303191, 'pp': 14.160392, 'p': 14.018237, 'mp': 13.868458, 'mf': 13.712854, 'f': 13.549715, 'ff': 13.378671, 'fff': 13.239332, 'ffff': 13.128906},
    'C6': {'pppp': 13.832384, 'ppp': 14.007345, 'pp': 14.229161, 'p': 14.661347, 'mp': 14.912552, 'mf': 14.99286, 'f': 14.874213, 'ff': 14.552542, 'fff': 14.360564, 'ffff': 14.208806},
    'C#6': {'pppp': 15.58294, 'ppp': 15.523737, 'pp': 15.45005, 'p': 15.420805, 'mp': 15.342292, 'mf': 15.228503, 'f': 14.964224, 'ff': 14.544129, 'fff': 14.254066, 'ffff': 14.026185},
    'D6': {'pppp': 14.399989, 'ppp': 14.144288, 'pp': 13.831038, 'p': 13.326735, 'mp': 12.993559, 'mf': 12.872526, 'f': 12.89063, 'ff': 13.018068, 'fff': 13.091455, 'ffff': 13.150462},
    'D#6': {'pppp': 18.142296, 'ppp': 17.639738, 'pp': 17.031072, 'p': 15.885169, 'mp': 15.392442, 'mf': 15.279155, 'f': 15.820971, 'ff': 17.198872, 'fff': 18.214701, 'ffff': 19.070397},
    'E6': {'pppp': 13.415905, 'ppp': 13.465516, 'pp': 13.527787, 'p': 13.553227, 'mp': 13.626215, 'mf': 13.742042, 'f': 14.18253, 'ff': 15.004192, 'fff': 15.638618, 'ffff': 16.165419},
    'F6': {'pppp': 8.712683, 'ppp': 8.721754, 'pp': 8.733105, 'p': 8.739038, 'mp': 8.756517, 'mf': 8.785095, 'f': 8.931253, 'ff': 9.209554, 'fff': 9.410982, 'ffff': 9.575293},
    'F#6': {'pppp': 8.45932, 'ppp': 8.491282, 'pp': 8.531405, 'p': 8.547245, 'mp': 8.593281, 'mf': 8.66749, 'f': 8.988968, 'ff': 9.604507, 'fff': 10.083153, 'ffff': 10.483187},
    'G6': {'pppp': 8.60153, 'ppp': 8.572355, 'pp': 8.536024, 'p': 8.459832, 'mp': 8.431933, 'mf': 8.427955, 'f': 8.654282, 'ff': 9.155909, 'fff': 9.51918, 'ffff': 9.820148},
    'G#6': {'pppp': 10.869981, 'ppp': 10.599307, 'pp': 10.270423, 'p': 9.605474, 'mp': 9.359135, 'mf': 9.318391, 'f': 9.720352, 'ff': 10.717859, 'fff': 11.470795, 'ffff': 12.111053},
    'A6': {'pppp': 9.104231, 'ppp': 8.988486, 'pp': 8.845871, 'p': 8.558134, 'mp': 8.437342, 'mf': 8.411788, 'f': 8.565069, 'ff': 8.938414, 'fff': 9.199803, 'ffff': 9.414408},
    'A#6': {'pppp': 11.133252, 'ppp': 10.583482, 'pp': 9.934288, 'p': 8.903692, 'mp': 8.349597, 'mf': 8.176294, 'f': 8.38228, 'ff': 9.004915, 'fff': 9.43948, 'ffff': 9.802184},
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
