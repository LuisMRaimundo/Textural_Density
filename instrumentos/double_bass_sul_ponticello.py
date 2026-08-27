# instrumentos/double_bass_sul_ponticello.py
"""
Double bass (arco sul ponticello) instrument density module.

The ``spectral_data`` table stores a committed 10-dynamic Combined Density
Metric (CDM) ladder from the ``Results`` sheet of
``DoubleBass_sul_ponticello_dynamics.xlsx``
(measured pp/mf/ff anchors; remaining levels committed from that workbook —
no runtime dynamic extrapolation).

Runtime analysis does not ingest audio; it maps notated pitch + dynamic to
these pre-loaded acoustic metadata tables.
"""

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="external_acoustic_metadata",
    citation=(
        "Double bass arco_sul_ponticello CDM ladder: measured pp/mf/ff anchors with "
        "committed Results sheet values for all 10 dynamic levels from "
        "DoubleBass_sul_ponticello_dynamics.xlsx "
        "(dest Zenodo DoubleBass_sul ponticello Media (IOWA+Orchidea average); Dynamics_predicter Results ladder)."
    ),
    source_url_or_identifier='docs/instrument_acoustic_sources.md#double-bass-sul-ponticello',
    extraction_method=(
        "Committed full dynamic ladder from Dynamics extrapolator v1.5.2.1 Results sheet "
        "(PCHIP interiors, tapered outers r=0.80) on measured pp/mf/ff anchors; "
        "interior cells clamped into their measured segment where the workbook "
        "marginally overshoots; pitch lookup via MIDI-space spectral_lookup"
    ),
    dynamic_levels=('pppp', 'ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', 'ffff'),
    pitch_range=(28, 67),
    uncertainty="high",
    version="2026-08-27",
    source_technique="arco_sul_ponticello",
    table_supported_techniques=("arco_sul_ponticello",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("double_bass_sul_ponticello")

# Full 10-dynamic CDM ladder (Results sheet). Anchors pp/mf/ff match measured
# workbook midpoints; other levels are workbook-committed.
spectral_data = {
    'E1': {'pppp': 67.174594, 'ppp': 66.064296, 'pp': 64.702195, 'p': 61.629419, 'mp': 60.534504, 'mf': 60.379684, 'f': 63.983294, 'ff': 72.68328, 'fff': 79.330979, 'ffff': 85.084304},
    'F1': {'pppp': 63.884079, 'ppp': 62.774845, 'pp': 61.415348, 'p': 58.36833, 'mp': 57.284258, 'mf': 57.131043, 'f': 60.677912, 'ff': 69.275675, 'fff': 75.883025, 'ffff': 81.619839},
    'F#1': {'pppp': 58.418075, 'ppp': 57.449082, 'pp': 56.260412, 'p': 53.588774, 'mp': 52.636793, 'mf': 52.502183, 'f': 55.838632, 'ff': 63.912734, 'fff': 70.138027, 'ffff': 75.552087},
    'G1': {'pppp': 41.568389, 'ppp': 43.345338, 'pp': 45.673723, 'p': 49.884633, 'mp': 52.874995, 'mf': 53.997813, 'f': 53.629198, 'ff': 51.971508, 'fff': 51.113926, 'ffff': 50.43806},
    'G#1': {'pppp': 42.636105, 'ppp': 41.978566, 'pp': 41.170884, 'p': 39.387793, 'mp': 38.621307, 'mf': 38.449607, 'f': 39.340952, 'ff': 41.549174, 'fff': 43.080042, 'ffff': 44.345249},
    'A1': {'pppp': 39.448831, 'ppp': 41.204997, 'pp': 43.510549, 'p': 48.353033, 'mp': 50.910145, 'mf': 51.607636, 'f': 49.333272, 'ff': 44.145267, 'fff': 41.026902, 'ffff': 38.691572},
    'A#1': {'pppp': 56.832013, 'ppp': 56.952824, 'pp': 57.1042, 'p': 57.182706, 'mp': 57.211657, 'mf': 57.215794, 'f': 56.414391, 'ff': 54.774656, 'fff': 53.961166, 'ffff': 53.319081},
    'B1': {'pppp': 52.600892, 'ppp': 53.275732, 'pp': 54.13147, 'p': 54.501243, 'mp': 55.478071, 'mf': 56.867278, 'f': 59.649637, 'ff': 64.197193, 'fff': 67.919438, 'ffff': 71.052035},
    'C2': {'pppp': 43.796616, 'ppp': 44.087546, 'pp': 44.453929, 'p': 44.591545, 'mp': 44.965801, 'mf': 45.520149, 'f': 46.88462, 'ff': 49.206635, 'fff': 50.990802, 'ffff': 52.464602},
    'C#2': {'pppp': 35.402189, 'ppp': 35.433842, 'pp': 35.473449, 'p': 35.316026, 'mp': 35.258204, 'mf': 35.249952, 'f': 35.441998, 'ff': 35.867456, 'fff': 36.218861, 'ffff': 36.502463},
    'D2': {'pppp': 32.544566, 'ppp': 34.850072, 'pp': 37.96297, 'p': 44.302459, 'mp': 48.261181, 'mf': 49.551583, 'f': 47.358546, 'ff': 41.947046, 'fff': 38.749266, 'ffff': 36.367476},
    'D#2': {'pppp': 41.505254, 'ppp': 40.136103, 'pp': 38.488001, 'p': 35.321377, 'mp': 33.926178, 'mf': 33.587404, 'f': 34.95746, 'ff': 38.518461, 'fff': 41.108127, 'ffff': 43.304667},
    'E2': {'pppp': 41.020087, 'ppp': 40.574117, 'pp': 40.023468, 'p': 38.810536, 'mp': 38.154095, 'mf': 37.953924, 'f': 38.297608, 'ff': 39.234457, 'fff': 39.870397, 'ffff': 40.386562},
    'F2': {'pppp': 28.718834, 'ppp': 30.800839, 'pp': 33.616868, 'p': 39.62572, 'mp': 43.07912, 'mf': 44.093523, 'f': 41.375428, 'ff': 35.258878, 'fff': 31.67513, 'ffff': 29.07223},
    'F#2': {'pppp': 34.257547, 'ppp': 34.53796, 'pp': 34.891707, 'p': 35.610158, 'mp': 35.905788, 'mf': 35.961679, 'f': 35.527945, 'ff': 34.536597, 'fff': 34.023815, 'ffff': 33.619076},
    'G2': {'pppp': 30.3591, 'ppp': 31.227307, 'pp': 32.347565, 'p': 34.66558, 'mp': 35.851191, 'mf': 36.168696, 'f': 35.103186, 'ff': 32.613805, 'fff': 31.119794, 'ffff': 29.974013},
    'G#2': {'pppp': 20.477892, 'ppp': 22.937177, 'pp': 26.43068, 'p': 34.93468, 'mp': 39.60993, 'mf': 40.783924, 'f': 35.428875, 'ff': 25.297089, 'fff': 20.029382, 'ffff': 16.616714},
    'A2': {'pppp': 46.014948, 'ppp': 44.146036, 'pp': 41.916276, 'p': 40.231448, 'mp': 38.007778, 'mf': 35.530544, 'f': 32.642589, 'ff': 29.40134, 'fff': 26.888383, 'ffff': 25.033567},
    'A#2': {'pppp': 34.43973, 'ppp': 33.900728, 'pp': 33.238823, 'p': 32.631525, 'mp': 31.86701, 'mf': 31.005433, 'f': 29.994946, 'ff': 28.831044, 'fff': 27.941816, 'ffff': 27.250221},
    'B2': {'pppp': 31.537159, 'ppp': 31.833576, 'pp': 32.208017, 'p': 32.358024, 'mp': 32.765223, 'mf': 33.367451, 'f': 34.817943, 'ff': 37.308795, 'fff': 39.282777, 'ffff': 40.9369},
    'C3': {'pppp': 39.394818, 'ppp': 37.658582, 'pp': 35.595495, 'p': 31.546648, 'mp': 30.055989, 'mf': 29.79121, 'f': 32.049282, 'ff': 37.988167, 'fff': 42.698943, 'ffff': 46.884808},
    'C#3': {'pppp': 30.466252, 'ppp': 30.86879, 'pp': 31.379451, 'p': 31.610821, 'mp': 32.206876, 'mf': 33.02144, 'f': 34.429677, 'ff': 36.601185, 'fff': 38.391439, 'ffff': 39.886487},
    'D3': {'pppp': 30.753676, 'ppp': 31.084453, 'pp': 31.502932, 'p': 31.671358, 'mp': 32.131049, 'mf': 32.816503, 'f': 34.522811, 'ff': 37.506091, 'fff': 39.907393, 'ffff': 41.938665},
    'D#3': {'pppp': 32.853066, 'ppp': 33.155816, 'pp': 33.538179, 'p': 33.96028, 'mp': 34.356522, 'mf': 34.726572, 'f': 35.068587, 'ff': 35.381341, 'fff': 35.737009, 'ffff': 36.024116},
    'E3': {'pppp': 34.601857, 'ppp': 34.624078, 'pp': 34.651874, 'p': 34.64765, 'mp': 34.634192, 'mf': 34.610329, 'f': 33.153577, 'ff': 30.344561, 'fff': 28.653453, 'ffff': 27.36868},
    'F3': {'pppp': 34.497207, 'ppp': 33.533149, 'pp': 32.365874, 'p': 30.145266, 'mp': 29.069701, 'mf': 28.774784, 'f': 29.564052, 'ff': 31.652661, 'fff': 33.111091, 'ffff': 34.326072},
    'F#3': {'pppp': 22.654492, 'ppp': 23.654532, 'pp': 24.966887, 'p': 27.525185, 'mp': 29.096685, 'mf': 29.613206, 'f': 28.863914, 'ff': 26.892828, 'fff': 25.726514, 'ffff': 24.829988},
    'G3': {'pppp': 22.360448, 'ppp': 23.062757, 'pp': 23.971744, 'p': 25.56079, 'mp': 26.728122, 'mf': 27.179538, 'f': 27.132323, 'ff': 26.804106, 'fff': 26.673191, 'ffff': 26.56892},
    'G#3': {'pppp': 22.306553, 'ppp': 22.514522, 'pp': 22.777212, 'p': 23.346064, 'mp': 23.559204, 'mf': 23.589811, 'f': 22.780357, 'ff': 21.110804, 'fff': 20.108023, 'ffff': 19.340204},
    'A3': {'pppp': 21.864474, 'ppp': 22.073613, 'pp': 22.337852, 'p': 22.913472, 'mp': 23.129261, 'mf': 23.160254, 'f': 22.674966, 'ff': 21.61899, 'fff': 21.011514, 'ffff': 20.537847},
    'A#3': {'pppp': 17.992454, 'ppp': 19.100682, 'pp': 20.582445, 'p': 23.589145, 'mp': 25.411987, 'mf': 25.992232, 'f': 24.916436, 'ff': 22.282502, 'fff': 20.716523, 'ffff': 19.543359},
    'B3': {'pppp': 22.855604, 'ppp': 22.910005, 'pp': 22.978188, 'p': 22.990584, 'mp': 23.028594, 'mf': 23.093527, 'f': 23.72998, 'ff': 25.029727, 'fff': 25.95703, 'ffff': 26.723547},
    'C4': {'pppp': 20.690988, 'ppp': 21.255625, 'pp': 21.983139, 'p': 22.667169, 'mp': 23.498391, 'mf': 24.459201, 'f': 25.606244, 'ff': 26.978025, 'fff': 28.253844, 'ffff': 29.317804},
    'C#4': {'pppp': 19.533768, 'ppp': 20.628833, 'pp': 22.084392, 'p': 24.858714, 'mp': 26.718419, 'mf': 27.378215, 'f': 26.800058, 'ff': 25.079141, 'fff': 24.080448, 'ffff': 23.310205},
    'D4': {'pppp': 26.483768, 'ppp': 25.876457, 'pp': 25.136864, 'p': 23.513382, 'mp': 22.942057, 'mf': 22.861581, 'f': 24.140555, 'ff': 27.294423, 'fff': 29.684155, 'ffff': 31.745729},
    'D#4': {'pppp': 22.3435, 'ppp': 21.793103, 'pp': 21.124133, 'p': 19.673976, 'mp': 19.150266, 'mf': 19.069272, 'f': 19.969777, 'ff': 22.210144, 'fff': 23.870731, 'ffff': 25.288157},
    'E4': {'pppp': 21.295393, 'ppp': 21.102334, 'pp': 20.86347, 'p': 20.279796, 'mp': 20.068898, 'mf': 20.03895, 'f': 20.961935, 'ff': 23.112377, 'fff': 24.699124, 'ffff': 26.046603},
    'F4': {'pppp': 18.79018, 'ppp': 18.98142, 'pp': 19.223209, 'p': 19.327324, 'mp': 19.5996, 'mf': 19.980631, 'f': 20.705141, 'ff': 21.854609, 'fff': 22.776886, 'ffff': 23.542653},
    'F#4': {'pppp': 23.746063, 'ppp': 23.203958, 'pp': 22.543698, 'p': 21.083533, 'mp': 20.569751, 'mf': 20.497383, 'f': 21.464483, 'ff': 23.853013, 'fff': 25.62339, 'ffff': 27.13384},
    'G4': {'pppp': 14.128795, 'ppp': 14.871678, 'pp': 15.855449, 'p': 17.618862, 'mp': 18.934358, 'mf': 19.44573, 'f': 19.370119, 'ff': 18.849009, 'fff': 18.594483, 'ffff': 18.393339},
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
