# instrumentos/viola_sul_ponticello.py
"""
Viola (arco sul ponticello) instrument density module.

The ``spectral_data`` table stores a committed 10-dynamic Combined Density
Metric (CDM) ladder from the ``Results`` sheet of
``OK_VIOLA_sul ponticello_dynamics extrapolation.xlsx``
(measured pp/mf/ff anchors; remaining levels committed from that workbook —
no runtime dynamic extrapolation).

Runtime analysis does not ingest audio; it maps notated pitch + dynamic to
these pre-loaded acoustic metadata tables.
"""

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="external_acoustic_metadata",
    citation=(
        "Viola arco_sul_ponticello CDM ladder: measured pp/mf/ff anchors with "
        "committed Results sheet values for all 10 dynamic levels from "
        "OK_VIOLA_sul ponticello_dynamics extrapolation.xlsx "
        "(CDM Technique Extrapolator METApool, IOWA+ORCHIDEA collections)."
    ),
    source_url_or_identifier='docs/instrument_acoustic_sources.md#viola-sul-ponticello',
    extraction_method=(
        "Committed full dynamic ladder from Dynamics extrapolator v1.5.2.1 Results sheet "
        "(PCHIP interiors, tapered outers r=0.80) on measured pp/mf/ff anchors; "
        "interior cells clamped into their measured segment where the workbook "
        "marginally overshoots; pitch lookup via MIDI-space spectral_lookup"
    ),
    dynamic_levels=('pppp', 'ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', 'ffff'),
    pitch_range=(48, 96),
    uncertainty="high",
    version="2026-08-11",
    source_technique="arco_sul_ponticello",
    table_supported_techniques=("arco_sul_ponticello",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("viola_sul_ponticello")

# Full 10-dynamic CDM ladder (Results sheet). Anchors pp/mf/ff match measured
# workbook midpoints; other levels are workbook-committed.
spectral_data = {
    'C3': {'pppp': 50.661604, 'ppp': 50.691014, 'pp': 50.7278, 'p': 50.110474, 'mp': 49.884937, 'mf': 49.8528, 'f': 52.17952, 'ff': 57.4672, 'fff': 61.269809, 'ffff': 64.492278},
    'C#3': {'pppp': 49.65917, 'ppp': 49.745977, 'pp': 49.8547, 'p': 49.411097, 'mp': 49.248661, 'mf': 49.2255, 'f': 51.474787, 'ff': 56.5538, 'fff': 60.201784, 'ffff': 63.288881},
    'D3': {'pppp': 42.739278, 'ppp': 42.863772, 'pp': 43.0199, 'p': 42.778385, 'mp': 42.689747, 'mf': 42.6771, 'f': 44.585429, 'ff': 48.866, 'fff': 51.937103, 'ffff': 54.532382},
    'D#3': {'pppp': 38.324898, 'ppp': 38.481035, 'pp': 38.6771, 'p': 38.587404, 'mp': 38.554411, 'mf': 38.5497, 'f': 40.235821, 'ff': 43.992, 'fff': 46.684336, 'ffff': 48.956366},
    'E3': {'pppp': 38.372839, 'ppp': 38.571733, 'pp': 38.8218, 'p': 38.827336, 'mp': 38.844959, 'mf': 38.8762, 'f': 40.548727, 'ff': 44.2158, 'fff': 46.852449, 'ffff': 49.074529},
    'F3': {'pppp': 35.953667, 'ppp': 36.17589, 'pp': 36.4556, 'p': 36.479219, 'mp': 36.552355, 'mf': 36.6786, 'f': 38.251473, 'ff': 41.5764, 'fff': 43.99708, 'ffff': 46.034713},
    'F#3': {'pppp': 35.892973, 'ppp': 36.15076, 'pp': 36.4756, 'p': 36.519171, 'mp': 36.650635, 'mf': 36.8716, 'f': 38.445874, 'ff': 41.655, 'fff': 44.02153, 'ffff': 46.011197},
    'G3': {'pppp': 34.979438, 'ppp': 35.265821, 'pp': 35.6271, 'p': 35.690604, 'mp': 35.877583, 'mf': 36.1836, 'f': 37.720021, 'ff': 40.7406, 'fff': 42.997661, 'ffff': 44.893014},
    'G#3': {'pppp': 28.835586, 'ppp': 29.100734, 'pp': 29.4356, 'p': 29.506572, 'mp': 29.710774, 'mf': 30.0362, 'f': 31.303138, 'ff': 33.7056, 'fff': 35.525313, 'ffff': 37.051568},
    'A3': {'pppp': 25.37584, 'ppp': 25.634835, 'pp': 25.9623, 'p': 26.042275, 'mp': 26.267425, 'mf': 26.6168, 'f': 27.730752, 'ff': 29.7683, 'fff': 31.33335, 'ffff': 32.644428},
    'A#3': {'pppp': 22.381712, 'ppp': 22.632877, 'pp': 22.9508, 'p': 23.03781, 'mp': 23.277763, 'mf': 23.6403, 'f': 24.620781, 'ff': 26.3506, 'fff': 27.698624, 'ffff': 28.826529},
    'B3': {'pppp': 25.671327, 'ppp': 25.985531, 'pp': 26.3837, 'p': 26.503524, 'mp': 26.827588, 'mf': 27.3043, 'f': 28.425239, 'ff': 30.3327, 'fff': 31.841509, 'ffff': 33.102417},
    'C4': {'pppp': 21.574688, 'ppp': 21.860808, 'pp': 22.2238, 'p': 22.342333, 'mp': 22.657021, 'mf': 23.1077, 'f': 24.045527, 'ff': 25.5845, 'fff': 26.820827, 'ffff': 27.852767},
    'C#4': {'pppp': 19.772484, 'ppp': 20.054944, 'pp': 20.4137, 'p': 20.539539, 'mp': 20.867811, 'mf': 21.3255, 'f': 22.180013, 'ff': 23.5321, 'fff': 24.635858, 'ffff': 25.556024},
    'D4': {'pppp': 22.802386, 'ppp': 23.151579, 'pp': 23.5956, 'p': 23.761637, 'mp': 24.187597, 'mf': 24.7657, 'f': 25.744158, 'ff': 27.2365, 'fff': 28.47528, 'ffff': 29.506749},
    'D#4': {'pppp': 21.012327, 'ppp': 21.35578, 'pp': 21.793, 'p': 21.974025, 'mp': 22.407631, 'mf': 22.9815, 'f': 23.875575, 'ff': 25.1896, 'fff': 26.299511, 'ffff': 27.22255},
    'E4': {'pppp': 19.902065, 'ppp': 20.247962, 'pp': 20.6888, 'p': 20.913031, 'mp': 21.351476, 'mf': 21.9199, 'f': 22.758375, 'ff': 23.9453, 'fff': 24.966275, 'ffff': 25.81431},
    'F4': {'pppp': 19.877628, 'ppp': 20.243707, 'pp': 20.7108, 'p': 20.988571, 'mp': 21.455303, 'mf': 22.0465, 'f': 22.874499, 'ff': 24.0029, 'fff': 24.9922, 'ffff': 25.812918},
    'F#4': {'pppp': 14.704851, 'ppp': 14.990987, 'pp': 15.3565, 'p': 15.602772, 'mp': 15.970272, 'mf': 16.424, 'f': 17.028662, 'ff': 17.8214, 'fff': 18.530505, 'ffff': 19.118051},
    'G4': {'pppp': 16.702859, 'ppp': 17.045282, 'pp': 17.4832, 'p': 17.810135, 'mp': 18.25373, 'mf': 18.7865, 'f': 19.463451, 'ff': 20.3167, 'fff': 21.096207, 'ffff': 21.741293},
    'G#4': {'pppp': 17.288219, 'ppp': 17.66074, 'pp': 18.1377, 'p': 18.526103, 'mp': 19.013391, 'mf': 19.5816, 'f': 20.270939, 'ff': 21.1054, 'fff': 21.885014, 'ffff': 22.52939},
    'A4': {'pppp': 17.672798, 'ppp': 18.07217, 'pp': 18.5841, 'p': 19.03336, 'mp': 19.561355, 'mf': 20.1581, 'f': 20.850174, 'ff': 21.6539, 'fff': 22.422885, 'ffff': 23.057689},
    'A#4': {'pppp': 13.492382, 'ppp': 13.811486, 'pp': 14.221, 'p': 14.604664, 'mp': 15.03138, 'mf': 15.4981, 'f': 16.016017, 'ff': 16.5923, 'fff': 17.157861, 'ffff': 17.624158},
    'B4': {'pppp': 15.621063, 'ppp': 16.007018, 'pp': 16.5029, 'p': 16.995209, 'mp': 17.5176, 'mf': 18.0697, 'f': 18.656267, 'ff': 19.2806, 'fff': 19.910268, 'ffff': 20.428776},
    'C5': {'pppp': 12.067306, 'ppp': 12.378241, 'pp': 12.7782, 'p': 13.19644, 'mp': 13.62265, 'mf': 14.0573, 'f': 14.499559, 'ff': 14.949, 'fff': 15.415842, 'ffff': 15.799791},
    'C#5': {'pppp': 10.412859, 'ppp': 10.692227, 'pp': 11.052, 'p': 11.446297, 'mp': 11.834306, 'mf': 12.2156, 'f': 12.587186, 'ff': 12.9469, 'fff': 13.33271, 'ffff': 13.649619},
    'D5': {'pppp': 11.046223, 'ppp': 11.35434, 'pp': 11.7516, 'p': 12.206007, 'mp': 12.639788, 'mf': 13.05, 'f': 13.432795, 'ff': 13.7848, 'fff': 14.17584, 'ffff': 14.496645},
    'D#5': {'pppp': 11.306198, 'ppp': 11.633636, 'pp': 12.0563, 'p': 12.559106, 'mp': 13.026547, 'mf': 13.4514, 'f': 13.83084, 'ff': 14.161175, 'fff': 14.542647, 'ffff': 14.85521},
    'E5': {'pppp': 9.515401, 'ppp': 9.801179, 'pp': 10.1705, 'p': 10.626083, 'mp': 11.039906, 'mf': 11.4009, 'f': 11.709182, 'ff': 11.96217, 'fff': 12.267265, 'ffff': 12.516935},
    'F5': {'pppp': 7.389995, 'ppp': 7.619872, 'pp': 7.9173, 'p': 8.296746, 'mp': 8.634479, 'mf': 8.9169, 'f': 9.147258, 'ff': 9.324527, 'fff': 9.549013, 'ffff': 9.732486},
    'F#5': {'pppp': 9.737817, 'ppp': 10.051222, 'pp': 10.4572, 'p': 10.991665, 'mp': 11.458949, 'mf': 11.833, 'f': 12.123914, 'ff': 12.332393, 'fff': 12.611618, 'ffff': 12.839542},
    'G5': {'pppp': 9.183411, 'ppp': 9.488904, 'pp': 9.8851, 'p': 10.422277, 'mp': 10.884613, 'mf': 11.2384, 'f': 11.500222, 'ff': 11.673405, 'fff': 11.920985, 'ffff': 12.122825},
    'G#5': {'pppp': 7.954113, 'ppp': 8.227293, 'pp': 8.582, 'p': 9.076395, 'mp': 9.496088, 'mf': 9.8027, 'f': 10.018085, 'ff': 10.148052, 'fff': 10.348773, 'ffff': 10.512205},
    'A5': {'pppp': 7.507062, 'ppp': 7.773039, 'pp': 8.1188, 'p': 8.613503, 'mp': 9.02839, 'mf': 9.3173, 'f': 9.509285, 'ff': 9.6132, 'fff': 9.789568, 'ffff': 9.932989},
    'A#5': {'pppp': 7.401289, 'ppp': 7.671594, 'pp': 8.0234, 'p': 8.539413, 'mp': 8.967575, 'mf': 9.2513, 'f': 9.428902, 'ff': 9.513044, 'fff': 9.67392, 'ffff': 9.804578},
    'B5': {'pppp': 6.485792, 'ppp': 6.729732, 'pp': 7.0476, 'p': 7.524947, 'mp': 7.917345, 'mf': 8.1644, 'f': 8.304295, 'ff': 8.367249, 'fff': 8.496761, 'ffff': 8.601813},
    'C6': {'pppp': 5.873116, 'ppp': 6.100437, 'pp': 6.397, 'p': 6.852468, 'mp': 7.223839, 'mf': 7.4456, 'f': 7.556535, 'ff': 7.605022, 'fff': 7.711845, 'ffff': 7.798383},
    'C#6': {'pppp': 7.520467, 'ppp': 7.81981, 'pp': 8.2108, 'p': 8.82435, 'mp': 9.321065, 'mf': 9.6018, 'f': 9.723, 'ff': 9.77444, 'fff': 9.897697, 'ffff': 9.997421},
    'D6': {'pppp': 6.054245, 'ppp': 6.301873, 'pp': 6.6257, 'p': 7.144417, 'mp': 7.561778, 'mf': 7.7846, 'f': 7.864904, 'ff': 7.897993, 'fff': 7.986267, 'ffff': 8.057595},
    'D#6': {'pppp': 6.367696, 'ppp': 6.635179, 'pp': 6.98539, 'p': 7.557576, 'mp': 8.015525, 'mf': 8.245939, 'f': 8.311685, 'ff': 8.337978, 'fff': 8.419206, 'ffff': 8.484758},
    'E6': {'pppp': 5.978085, 'ppp': 6.235812, 'pp': 6.573651, 'p': 7.136223, 'mp': 7.584443, 'mf': 7.796456, 'f': 7.840099, 'ff': 7.857035, 'fff': 7.922309, 'ffff': 7.974919},
    'F6': {'pppp': 2.853749, 'ppp': 2.979942, 'pp': 3.14556, 'p': 3.426451, 'mp': 3.649394, 'mf': 3.748261, 'f': 3.760214, 'ff': 3.764714, 'fff': 3.790591, 'ffff': 3.81142},
    'F#6': {'pppp': 3.545351, 'ppp': 3.706066, 'pp': 3.917244, 'p': 4.281805, 'mp': 4.570237, 'mf': 4.689792, 'f': 4.693298, 'ff': 4.694578, 'fff': 4.720113, 'ffff': 4.740641},
    'G6': {'pppp': 3.012744, 'ppp': 3.152837, 'pp': 3.337148, 'p': 3.658651, 'mp': 3.911722, 'mf': 4.014114, 'f': 4.01294, 'ff': 4.004732, 'fff': 4.020488, 'ffff': 4.033138},
    'G#6': {'pppp': 2.747595, 'ppp': 2.878652, 'pp': 3.051298, 'p': 3.354577, 'mp': 3.591934, 'mf': 3.687568, 'f': 3.684942, 'ff': 3.666609, 'fff': 3.67539, 'ffff': 3.682431},
    'A6': {'pppp': 3.609297, 'ppp': 3.785806, 'pp': 4.01863, 'p': 4.430356, 'mp': 4.750867, 'mf': 4.879491, 'f': 4.873968, 'ff': 4.835483, 'fff': 4.8396, 'ffff': 4.842896},
    'A#6': {'pppp': 2.54037, 'ppp': 2.667681, 'pp': 2.83583, 'p': 3.135079, 'mp': 3.366869, 'mf': 3.459537, 'f': 3.45417, 'ff': 3.416835, 'fff': 3.414457, 'ffff': 3.412556},
    'B6': {'pppp': 2.210184, 'ppp': 2.323638, 'pp': 2.473681, 'p': 2.742329, 'mp': 2.94945, 'mf': 3.031954, 'f': 3.02598, 'ff': 2.984486, 'fff': 2.977781, 'ffff': 2.972428},
    'C7': {'pppp': 2.226639, 'ppp': 2.343661, 'pp': 2.498624, 'p': 2.777694, 'mp': 2.991916, 'mf': 3.076955, 'f': 3.069602, 'ff': 3.018622, 'fff': 3.007151, 'ffff': 2.998006},
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
