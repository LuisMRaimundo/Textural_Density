# instrumentos/viola_sul_ponticello.py
"""
Viola (arco sul ponticello) instrument density module.

The ``spectral_data`` table stores a committed 10-dynamic Combined Density
Metric (CDM) ladder from the ``Results`` sheet of
``Viola_Zenodo_collections_sul_ponticello_Dynamics10.xlsx``
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
        "Viola_Zenodo_collections_sul_ponticello_Dynamics10.xlsx "
        "(dest Zenodo Viola_sul ponticello Media (IOWA+Orchidea average); Dynamics_predicter Results ladder (CORDAS_4))."
    ),
    source_url_or_identifier='docs/instrument_acoustic_sources.md#viola-sul-ponticello',
    extraction_method=(
        "Committed full dynamic ladder from Dynamics extrapolator v1.5.2.1 Results sheet "
        "(PCHIP interiors, tapered outers r=0.80) on measured pp/mf/ff anchors; "
        "interior cells clamped into their measured segment where the workbook "
        "marginally overshoots; pitch lookup via MIDI-space spectral_lookup"
    ),
    dynamic_levels=('pppp', 'ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', 'ffff'),
    pitch_range=(48, 88),
    uncertainty="high",
    version="2026-09-18",
    source_technique="arco_sul_ponticello",
    table_supported_techniques=("arco_sul_ponticello",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("viola_sul_ponticello")

# Full 10-dynamic CDM ladder (Results sheet). Anchors pp/mf/ff match measured
# workbook midpoints; other levels are workbook-committed.
spectral_data = {
    'C3': {'pppp': 34.338448, 'ppp': 35.704572, 'pp': 37.488908, 'p': 39.98296, 'mp': 42.123727, 'mf': 43.713792, 'f': 44.848868, 'ff': 45.550599, 'fff': 46.439938, 'ffff': 47.163895},
    'C#3': {'pppp': 48.808329, 'ppp': 50.059652, 'pp': 51.669016, 'p': 54.544957, 'mp': 56.434598, 'mf': 57.105852, 'f': 56.66973, 'ff': 55.205155, 'fff': 54.366604, 'ffff': 53.704943},
    'D3': {'pppp': 42.45193, 'ppp': 43.087101, 'pp': 43.894446, 'p': 44.47749, 'mp': 45.369066, 'mf': 46.473293, 'f': 47.956392, 'ff': 49.908793, 'fff': 51.56136, 'ffff': 52.922725},
    'D#3': {'pppp': 31.820341, 'ppp': 32.919054, 'pp': 34.345947, 'p': 36.963674, 'mp': 38.659268, 'mf': 39.250853, 'f': 38.739867, 'ff': 37.187108, 'fff': 36.266024, 'ffff': 35.545611},
    'E3': {'pppp': 36.824579, 'ppp': 38.145546, 'pp': 39.863589, 'p': 42.382637, 'mp': 44.465026, 'mf': 45.828104, 'f': 46.66775, 'ff': 47.05407, 'fff': 47.638009, 'ffff': 48.110374},
    'F3': {'pppp': 34.067214, 'ppp': 34.309919, 'pp': 34.615734, 'p': 34.717544, 'mp': 35.019323, 'mf': 35.517986, 'f': 38.208082, 'ff': 43.777229, 'fff': 48.32183, 'ffff': 52.294915},
    'F#3': {'pppp': 30.510678, 'ppp': 31.633999, 'pp': 33.096487, 'p': 35.947667, 'mp': 37.599809, 'mf': 38.113514, 'f': 37.136049, 'ff': 34.679617, 'fff': 33.170693, 'ffff': 32.010964},
    'G3': {'pppp': 37.062146, 'ppp': 38.035888, 'pp': 39.289121, 'p': 41.686057, 'mp': 43.064476, 'mf': 43.494451, 'f': 42.720886, 'ff': 40.730913, 'fff': 39.515838, 'ffff': 38.569929},
    'G#3': {'pppp': 53.837814, 'ppp': 53.968907, 'pp': 54.133222, 'p': 54.157313, 'mp': 54.231287, 'mf': 54.357806, 'f': 55.637397, 'ff': 58.240448, 'fff': 60.02131, 'ffff': 61.485128},
    'A3': {'pppp': 29.92284, 'ppp': 31.354911, 'pp': 33.24176, 'p': 36.95499, 'mp': 39.164738, 'mf': 39.86429, 'f': 38.597818, 'ff': 35.428222, 'fff': 33.490918, 'ffff': 32.017632},
    'A#3': {'pppp': 33.232294, 'ppp': 33.921661, 'pp': 34.803513, 'p': 36.131194, 'mp': 37.176078, 'mf': 37.762226, 'f': 38.021725, 'ff': 38.1321, 'fff': 38.303731, 'ffff': 38.441591},
    'B3': {'pppp': 32.778804, 'ppp': 34.015743, 'pp': 35.627762, 'p': 38.337888, 'mp': 40.443788, 'mf': 41.289676, 'f': 41.285183, 'ff': 41.253747, 'fff': 41.242422, 'ffff': 41.233365},
    'C4': {'pppp': 29.684356, 'ppp': 30.189591, 'pp': 30.833245, 'p': 31.499792, 'mp': 32.19791, 'mf': 32.926671, 'f': 33.690595, 'ff': 34.492498, 'fff': 35.226816, 'ffff': 35.825511},
    'C#4': {'pppp': 27.078838, 'ppp': 28.04829, 'pp': 29.309058, 'p': 31.336547, 'mp': 32.936245, 'mf': 33.710153, 'f': 33.898853, 'ff': 33.973088, 'fff': 34.098837, 'ffff': 34.199772},
    'D4': {'pppp': 23.620752, 'ppp': 24.205475, 'pp': 24.956775, 'p': 26.012763, 'mp': 26.887714, 'mf': 27.497887, 'f': 27.906364, 'ff': 28.133258, 'fff': 28.429705, 'ffff': 28.669111},
    'D#4': {'pppp': 40.815648, 'ppp': 41.212001, 'pp': 41.712859, 'p': 41.947781, 'mp': 42.499442, 'mf': 43.223192, 'f': 44.334853, 'ff': 45.939981, 'fff': 47.210138, 'ffff': 48.251503},
    'E4': {'pppp': 30.166261, 'ppp': 30.582642, 'pp': 31.11121, 'p': 31.969603, 'mp': 32.578353, 'mf': 32.808999, 'f': 32.782963, 'ff': 32.601286, 'fff': 32.520986, 'ffff': 32.456888},
    'F4': {'pppp': 30.299001, 'ppp': 31.052711, 'pp': 32.021269, 'p': 34.011137, 'mp': 34.989345, 'mf': 35.238057, 'f': 34.266511, 'ff': 32.017529, 'fff': 30.619566, 'ffff': 29.545273},
    'F#4': {'pppp': 22.634532, 'ppp': 22.606892, 'pp': 22.572389, 'p': 22.392997, 'mp': 22.251472, 'mf': 22.157528, 'f': 22.097144, 'ff': 22.065293, 'fff': 22.037892, 'ffff': 22.015996},
    'G4': {'pppp': 27.356266, 'ppp': 27.661668, 'pp': 28.048218, 'p': 28.646962, 'mp': 29.076443, 'mf': 29.240583, 'f': 29.227969, 'ff': 29.13982, 'fff': 29.106169, 'ffff': 29.079276},
    'G#4': {'pppp': 33.493431, 'ppp': 33.419608, 'pp': 33.327558, 'p': 32.937024, 'mp': 32.697819, 'mf': 32.61633, 'f': 32.678909, 'ff': 32.881935, 'fff': 32.998131, 'ffff': 33.091383},
    'A4': {'pppp': 28.41699, 'ppp': 28.160575, 'pp': 27.843307, 'p': 27.036191, 'mp': 26.726867, 'mf': 26.674153, 'f': 27.168903, 'ff': 28.350438, 'fff': 29.138733, 'ffff': 29.785122},
    'A#4': {'pppp': 30.879359, 'ppp': 30.529677, 'pp': 30.098137, 'p': 29.240145, 'mp': 28.642728, 'mf': 28.417964, 'f': 28.428956, 'ff': 28.506026, 'fff': 28.55016, 'ffff': 28.585516},
    'B4': {'pppp': 31.984102, 'ppp': 31.620559, 'pp': 31.171936, 'p': 30.712062, 'mp': 30.167706, 'mf': 29.566766, 'f': 28.883795, 'ff': 28.114976, 'fff': 27.493665, 'ffff': 27.006516},
    'C5': {'pppp': 19.437776, 'ppp': 19.799467, 'pp': 20.261059, 'p': 21.066834, 'mp': 21.597437, 'mf': 21.786995, 'f': 21.682683, 'ff': 21.308345, 'fff': 21.102913, 'ffff': 20.939993},
    'C#5': {'pppp': 17.169849, 'ppp': 17.210068, 'pp': 17.260474, 'p': 17.264483, 'mp': 17.276902, 'mf': 17.298332, 'f': 17.571806, 'ff': 18.128518, 'fff': 18.490751, 'ffff': 18.785743},
    'D5': {'pppp': 14.492711, 'ppp': 15.032265, 'pp': 15.735042, 'p': 16.957856, 'mp': 17.845006, 'mf': 18.184435, 'f': 18.132701, 'ff': 17.77466, 'fff': 17.590036, 'ffff': 17.443719},
    'D#5': {'pppp': 29.236542, 'ppp': 28.279366, 'pp': 27.126843, 'p': 25.017642, 'mp': 23.995676, 'mf': 23.713612, 'f': 24.439174, 'ff': 26.379153, 'fff': 27.743542, 'ffff': 28.88569},
    'E5': {'pppp': 17.702166, 'ppp': 17.796815, 'pp': 17.915837, 'p': 18.127095, 'mp': 18.205553, 'mf': 18.216789, 'f': 17.899737, 'ff': 17.229302, 'fff': 16.821822, 'ffff': 16.502787},
    'F5': {'pppp': 14.244767, 'ppp': 14.307632, 'pp': 14.386603, 'p': 14.477781, 'mp': 14.511518, 'mf': 14.516344, 'f': 14.454141, 'ff': 14.312616, 'fff': 14.240104, 'ffff': 14.182359},
    'F#5': {'pppp': 19.57274, 'ppp': 20.002916, 'pp': 20.553956, 'p': 21.250427, 'mp': 21.869559, 'mf': 22.393555, 'f': 22.827662, 'ff': 23.170852, 'fff': 23.534803, 'ffff': 23.830076},
    'G5': {'pppp': 17.79203, 'ppp': 18.053191, 'pp': 18.38504, 'p': 19.032137, 'mp': 19.358749, 'mf': 19.446811, 'f': 19.166389, 'ff': 18.490047, 'fff': 18.079467, 'ffff': 17.757578},
    'G#5': {'pppp': 18.454249, 'ppp': 18.513522, 'pp': 18.587882, 'p': 18.603986, 'mp': 18.651902, 'mf': 18.731149, 'f': 19.190466, 'ff': 20.08651, 'fff': 20.711818, 'ffff': 21.226052},
    'A5': {'pppp': 14.815098, 'ppp': 14.80041, 'pp': 14.78207, 'p': 14.645906, 'mp': 14.549729, 'mf': 14.513254, 'f': 14.515237, 'ff': 14.529125, 'fff': 14.540616, 'ffff': 14.549815},
    'A#5': {'pppp': 16.045033, 'ppp': 15.953882, 'pp': 15.84067, 'p': 15.543176, 'mp': 15.370307, 'mf': 15.313999, 'f': 15.378158, 'ff': 15.566162, 'fff': 15.676666, 'ffff': 15.765633},
    'B5': {'pppp': 16.250902, 'ppp': 16.161261, 'pp': 16.049904, 'p': 15.88878, 'mp': 15.719015, 'mf': 15.542648, 'f': 15.35774, 'ff': 15.163873, 'fff': 15.010062, 'ffff': 14.888136},
    'C6': {'pppp': 11.043678, 'ppp': 11.194797, 'pp': 11.386607, 'p': 11.732456, 'mp': 11.933478, 'mf': 11.997742, 'f': 11.902797, 'ff': 11.645386, 'fff': 11.496431, 'ffff': 11.378639},
    'C#6': {'pppp': 17.921979, 'ppp': 17.892872, 'pp': 17.856556, 'p': 17.822755, 'mp': 17.732013, 'mf': 17.6005, 'f': 17.295058, 'ff': 16.809528, 'fff': 16.487593, 'ffff': 16.234491},
    'D6': {'pppp': 18.103876, 'ppp': 17.826395, 'pp': 17.485517, 'p': 16.847966, 'mp': 16.426756, 'mf': 16.273744, 'f': 16.296631, 'ff': 16.457741, 'fff': 16.54226, 'ffff': 16.610187},
    'D#6': {'pppp': 18.371145, 'ppp': 17.888223, 'pp': 17.302384, 'p': 16.138227, 'mp': 15.63765, 'mf': 15.522559, 'f': 16.073006, 'ff': 17.472858, 'fff': 18.476591, 'ffff': 19.320936},
    'E6': {'pppp': 11.354735, 'ppp': 11.410737, 'pp': 11.481128, 'p': 11.502719, 'mp': 11.564665, 'mf': 11.662968, 'f': 12.036813, 'ff': 12.734164, 'fff': 13.24671, 'ffff': 13.671562},
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
