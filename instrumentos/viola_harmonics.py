# instrumentos/viola_harmonics.py
"""
Viola (arco harmonics) instrument density module.

The ``spectral_data`` table stores a committed 10-dynamic Combined Density
Metric (CDM) ladder from the ``Results`` sheet of
``Viola_Dynamics10_harmonics.xlsx``
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
        "Viola_Dynamics10_harmonics.xlsx "
        "(dest Zenodo Viola_harmonics Media (IOWA+Orchidea average); Dynamics_predicter Results ladder)."
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
    version="2026-08-30",
    source_technique="arco_harmonic",
    table_supported_techniques=("arco_harmonic",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("viola_harmonics")

# Full 10-dynamic CDM ladder (Results sheet). Anchors pp/mf/ff match measured
# workbook midpoints; other levels are workbook-committed.
spectral_data = {
    'C5': {'pppp': 18.785677, 'ppp': 19.134703, 'pp': 19.580118, 'p': 20.358813, 'mp': 20.871583, 'mf': 21.05477, 'f': 20.953964, 'ff': 20.592207, 'fff': 20.383046, 'ffff': 20.217248},
    'C#5': {'pppp': 18.27816, 'ppp': 18.2905, 'pp': 18.305937, 'p': 18.310188, 'mp': 18.323359, 'mf': 18.346088, 'f': 18.636126, 'ff': 19.226557, 'fff': 19.650712, 'ffff': 19.996762},
    'D5': {'pppp': 12.897375, 'ppp': 13.388543, 'pp': 14.028889, 'p': 15.119113, 'mp': 15.910069, 'mf': 16.212694, 'f': 16.166569, 'ff': 15.847351, 'fff': 15.676462, 'ffff': 15.541079},
    'D#5': {'pppp': 19.178408, 'ppp': 18.518998, 'pp': 17.726528, 'p': 16.348232, 'mp': 15.680409, 'mf': 15.49609, 'f': 15.970221, 'ff': 17.237936, 'fff': 18.160801, 'ffff': 18.934541},
    'E5': {'pppp': 11.376599, 'ppp': 11.425057, 'pp': 11.485919, 'p': 11.621357, 'mp': 11.671657, 'mf': 11.678861, 'f': 11.475597, 'ff': 11.045779, 'fff': 10.7664, 'ffff': 10.547993},
    'F5': {'pppp': 14.012639, 'ppp': 14.044526, 'pp': 14.084486, 'p': 14.173749, 'mp': 14.206778, 'mf': 14.211502, 'f': 14.150606, 'ff': 14.012052, 'fff': 13.939749, 'ffff': 13.882176},
    'F#5': {'pppp': 14.078023, 'ppp': 14.390092, 'pp': 14.789925, 'p': 15.291082, 'mp': 15.736588, 'mf': 16.113638, 'f': 16.426006, 'ff': 16.672954, 'fff': 16.95134, 'ffff': 17.177391},
    'G5': {'pppp': 15.740204, 'ppp': 15.967254, 'pp': 16.255679, 'p': 16.827829, 'mp': 17.116612, 'mf': 17.194475, 'f': 16.946532, 'ff': 16.348524, 'fff': 15.96519, 'ffff': 15.665005},
    'G#5': {'pppp': 16.732894, 'ppp': 16.766695, 'pp': 16.809042, 'p': 16.823605, 'mp': 16.866936, 'mf': 16.938598, 'f': 17.35396, 'ff': 18.164253, 'fff': 18.774984, 'ffff': 19.278321},
    'A5': {'pppp': 16.912024, 'ppp': 16.847362, 'pp': 16.766882, 'p': 16.612435, 'mp': 16.503344, 'mf': 16.461971, 'f': 16.46422, 'ff': 16.479974, 'fff': 16.502726, 'ffff': 16.52095},
    'A#5': {'pppp': 16.52413, 'ppp': 16.391313, 'pp': 16.226791, 'p': 15.922045, 'mp': 15.744962, 'mf': 15.687282, 'f': 15.753005, 'ff': 15.945592, 'fff': 16.072685, 'ffff': 16.175088},
    'B5': {'pppp': 14.40913, 'ppp': 14.298045, 'pp': 14.160392, 'p': 14.018237, 'mp': 13.868458, 'mf': 13.712854, 'f': 13.549715, 'ff': 13.378671, 'fff': 13.23395, 'ffff': 13.119301},
    'C6': {'pppp': 13.812988, 'ppp': 13.99643, 'pp': 14.229161, 'p': 14.661347, 'mp': 14.912552, 'mf': 14.99286, 'f': 14.874213, 'ff': 14.552542, 'fff': 14.355091, 'ffff': 14.199061},
    'C#6': {'pppp': 15.569766, 'ppp': 15.516445, 'pp': 15.45005, 'p': 15.420805, 'mp': 15.342292, 'mf': 15.228503, 'f': 14.964224, 'ff': 14.544129, 'fff': 14.245107, 'ffff': 14.010322},
    'D6': {'pppp': 14.399722, 'ppp': 14.144143, 'pp': 13.831038, 'p': 13.326735, 'mp': 12.993559, 'mf': 12.872526, 'f': 12.89063, 'ff': 13.018068, 'fff': 13.091455, 'ffff': 13.150462},
    'D#6': {'pppp': 18.146493, 'ppp': 17.642005, 'pp': 17.031072, 'p': 15.885169, 'mp': 15.392442, 'mf': 15.279155, 'f': 15.820971, 'ff': 17.198872, 'fff': 18.223313, 'ffff': 19.08663},
    'E6': {'pppp': 13.404756, 'ppp': 13.459298, 'pp': 13.527787, 'p': 13.553227, 'mp': 13.626215, 'mf': 13.742042, 'f': 14.18253, 'ff': 15.004192, 'fff': 15.648217, 'ffff': 16.183284},
    'F6': {'pppp': 8.70206, 'ppp': 8.715844, 'pp': 8.733105, 'p': 8.739038, 'mp': 8.756517, 'mf': 8.785095, 'f': 8.931253, 'ff': 9.209554, 'fff': 9.414931, 'ffff': 9.582526},
    'F#6': {'pppp': 8.453004, 'ppp': 8.487759, 'pp': 8.531405, 'p': 8.547245, 'mp': 8.593281, 'mf': 8.66749, 'f': 8.988968, 'ff': 9.604507, 'fff': 10.089885, 'ffff': 10.495789},
    'G6': {'pppp': 8.596392, 'ppp': 8.56951, 'pp': 8.536024, 'p': 8.459832, 'mp': 8.431933, 'mf': 8.427955, 'f': 8.654282, 'ff': 9.155909, 'fff': 9.524937, 'ffff': 9.83084},
    'G#6': {'pppp': 10.871791, 'ppp': 10.600287, 'pp': 10.270423, 'p': 9.605474, 'mp': 9.359135, 'mf': 9.318391, 'f': 9.720352, 'ff': 10.717859, 'fff': 11.477073, 'ffff': 12.122987},
    'A6': {'pppp': 9.280078, 'ppp': 9.439144, 'pp': 9.641815, 'p': 10.095422, 'mp': 10.267868, 'mf': 10.292742, 'f': 9.852896, 'ff': 8.938414, 'fff': 8.346696, 'ffff': 7.901652},
    'A#6': {'pppp': 11.853478, 'ppp': 11.391831, 'pp': 10.839973, 'p': 10.139094, 'mp': 9.618589, 'mf': 9.295552, 'f': 9.099616, 'ff': 9.004915, 'fff': 8.868679, 'ffff': 8.761176},
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
