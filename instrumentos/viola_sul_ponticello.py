# instrumentos/viola_sul_ponticello.py
"""
Viola (arco sul ponticello) instrument density module.

The ``spectral_data`` table stores a committed 10-dynamic Combined Density
Metric (CDM) ladder from the ``Results`` sheet of
``Viola_Dynamics10_sul_ponticello.xlsx``
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
        "Viola_Dynamics10_sul_ponticello.xlsx "
        "(dest Zenodo Viola_sul ponticello Media (IOWA+Orchidea average); Dynamics_predicter Results ladder)."
    ),
    source_url_or_identifier='docs/instrument_acoustic_sources.md#viola-sul-ponticello',
    extraction_method=(
        "Committed full dynamic ladder from Dynamics extrapolator v1.5.2.1 Results sheet "
        "(PCHIP interiors, tapered outers r=0.80) on measured pp/mf/ff anchors; "
        "interior cells clamped into their measured segment where the workbook "
        "marginally overshoots; pitch lookup via MIDI-space spectral_lookup"
    ),
    dynamic_levels=('pppp', 'ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', 'ffff'),
    pitch_range=(48, 93),
    uncertainty="high",
    version="2026-08-30",
    source_technique="arco_sul_ponticello",
    table_supported_techniques=("arco_sul_ponticello",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("viola_sul_ponticello")

# Full 10-dynamic CDM ladder (Results sheet). Anchors pp/mf/ff match measured
# workbook midpoints; other levels are workbook-committed.
spectral_data = {
    'C3': {'pppp': 34.315554, 'ppp': 35.691345, 'pp': 37.488908, 'p': 39.98296, 'mp': 42.123727, 'mf': 43.713792, 'f': 44.848868, 'ff': 45.550599, 'fff': 46.462631, 'ffff': 47.205387},
    'C#3': {'pppp': 48.806842, 'ppp': 50.058805, 'pp': 51.669016, 'p': 54.544957, 'mp': 56.434598, 'mf': 57.105852, 'f': 56.66973, 'ff': 55.205155, 'fff': 54.353343, 'ffff': 53.681366},
    'D3': {'pppp': 42.477143, 'ppp': 43.101316, 'pp': 43.894446, 'p': 44.47749, 'mp': 45.369066, 'mf': 46.473293, 'f': 47.956392, 'ff': 49.908793, 'fff': 51.613447, 'ffff': 53.018997},
    'D#3': {'pppp': 31.805993, 'ppp': 32.910807, 'pp': 34.345947, 'p': 36.963674, 'mp': 38.659268, 'mf': 39.250853, 'f': 38.739867, 'ff': 37.187108, 'fff': 36.251517, 'ffff': 35.520021},
    'E3': {'pppp': 36.804491, 'ppp': 38.133984, 'pp': 39.863589, 'p': 42.382637, 'mp': 44.465026, 'mf': 45.828104, 'f': 46.66775, 'ff': 47.05407, 'fff': 47.656894, 'ffff': 48.144708},
    'F3': {'pppp': 34.089113, 'ppp': 34.322171, 'pp': 34.615734, 'p': 34.717544, 'mp': 35.019323, 'mf': 35.517986, 'f': 38.208082, 'ff': 43.777229, 'fff': 48.408166, 'ffff': 52.463218},
    'F#3': {'pppp': 30.496077, 'ppp': 31.625588, 'pp': 33.096487, 'p': 35.947667, 'mp': 37.599809, 'mf': 38.113514, 'f': 37.136049, 'ff': 34.679617, 'fff': 33.148394, 'ffff': 31.972239},
    'G3': {'pppp': 37.059137, 'ppp': 38.034173, 'pp': 39.289121, 'p': 41.686057, 'mp': 43.064476, 'mf': 43.494451, 'f': 42.720886, 'ff': 40.730913, 'fff': 39.494259, 'ffff': 38.532024},
    'G#3': {'pppp': 53.942525, 'ppp': 54.027196, 'pp': 54.133222, 'p': 54.157313, 'mp': 54.231287, 'mf': 54.357806, 'f': 55.637397, 'ff': 58.240448, 'fff': 60.099983, 'ffff': 61.630269},
    'A3': {'pppp': 29.900673, 'ppp': 31.342004, 'pp': 33.24176, 'p': 36.95499, 'mp': 39.164738, 'mf': 39.86429, 'f': 38.597818, 'ff': 35.428222, 'fff': 33.46671, 'ffff': 31.975988},
    'A#3': {'pppp': 33.245164, 'ppp': 33.928958, 'pp': 34.803513, 'p': 36.131194, 'mp': 37.176078, 'mf': 37.762226, 'f': 38.021725, 'ff': 38.1321, 'fff': 38.317032, 'ffff': 38.465623},
    'B3': {'pppp': 32.756748, 'ppp': 34.003026, 'pp': 35.627762, 'p': 38.337888, 'mp': 40.443788, 'mf': 41.289676, 'f': 41.285183, 'ff': 41.253747, 'fff': 41.247731, 'ffff': 41.242919},
    'C4': {'pppp': 29.700332, 'ppp': 30.198617, 'pp': 30.833245, 'p': 31.499792, 'mp': 32.19791, 'mf': 32.926671, 'f': 33.690595, 'ff': 34.492498, 'fff': 35.254058, 'ffff': 35.875396},
    'C#4': {'pppp': 27.063305, 'ppp': 28.039351, 'pp': 29.309058, 'p': 31.336547, 'mp': 32.936245, 'mf': 33.710153, 'f': 33.898853, 'ff': 33.973088, 'fff': 34.106496, 'ffff': 34.213599},
    'D4': {'pppp': 23.621655, 'ppp': 24.205989, 'pp': 24.956775, 'p': 26.012763, 'mp': 26.887714, 'mf': 27.497887, 'f': 27.906364, 'ff': 28.133258, 'fff': 28.442509, 'ffff': 28.692356},
    'D#4': {'pppp': 40.861436, 'ppp': 41.237679, 'pp': 41.712859, 'p': 41.947781, 'mp': 42.499442, 'mf': 43.223192, 'f': 44.334853, 'ff': 45.939981, 'fff': 47.259297, 'ffff': 48.341979},
    'E4': {'pppp': 30.203029, 'ppp': 30.603346, 'pp': 31.11121, 'p': 31.969603, 'mp': 32.578353, 'mf': 32.808999, 'f': 32.782963, 'ff': 32.601286, 'fff': 32.527149, 'ffff': 32.467961},
    'F4': {'pppp': 24.739567, 'ppp': 25.473984, 'pp': 26.42274, 'p': 28.334879, 'mp': 29.330713, 'mf': 29.604102, 'f': 28.75837, 'ff': 26.764354, 'fff': 25.508588, 'ffff': 24.546533},
    'F#4': {'pppp': 22.716687, 'ppp': 22.652441, 'pp': 22.572389, 'p': 22.392997, 'mp': 22.251472, 'mf': 22.157528, 'f': 22.097144, 'ff': 22.065293, 'fff': 22.048113, 'ffff': 22.034379},
    'G4': {'pppp': 27.403334, 'ppp': 27.688098, 'pp': 28.048218, 'p': 28.646962, 'mp': 29.076443, 'mf': 29.240583, 'f': 29.227969, 'ff': 29.13982, 'fff': 29.114824, 'ffff': 29.094842},
    'G#4': {'pppp': 33.609338, 'ppp': 33.48381, 'pp': 33.327558, 'p': 32.937024, 'mp': 32.697819, 'mf': 32.61633, 'f': 32.678909, 'ff': 32.881935, 'fff': 33.01793, 'ffff': 33.12713},
    'A4': {'pppp': 28.482923, 'ppp': 28.196855, 'pp': 27.843307, 'p': 27.036191, 'mp': 26.726867, 'mf': 26.674153, 'f': 27.168903, 'ff': 28.350438, 'fff': 29.167914, 'ffff': 29.838834},
    'A#4': {'pppp': 30.983083, 'ppp': 30.586606, 'pp': 30.098137, 'p': 29.240145, 'mp': 28.642728, 'mf': 28.417964, 'f': 28.428956, 'ff': 28.506026, 'fff': 28.559848, 'ffff': 28.602978},
    'B4': {'pppp': 32.063711, 'ppp': 31.664259, 'pp': 31.171936, 'p': 30.712062, 'mp': 30.167706, 'mf': 29.566766, 'f': 28.883795, 'ff': 28.114976, 'fff': 27.480363, 'ffff': 26.983002},
    'C5': {'pppp': 19.447849, 'ppp': 19.805166, 'pp': 20.261059, 'p': 21.066834, 'mp': 21.597437, 'mf': 21.786995, 'f': 21.682683, 'ff': 21.308345, 'fff': 21.100685, 'ffff': 20.936015},
    'C#5': {'pppp': 17.211651, 'ppp': 17.233333, 'pp': 17.260474, 'p': 17.264483, 'mp': 17.276902, 'mf': 17.298332, 'f': 17.571806, 'ff': 18.128518, 'fff': 18.511612, 'ffff': 18.823908},
    'D5': {'pppp': 14.483904, 'ppp': 15.027189, 'pp': 15.735042, 'p': 16.957856, 'mp': 17.845006, 'mf': 18.184435, 'f': 18.132701, 'ff': 17.77466, 'fff': 17.588126, 'ffff': 17.44031},
    'D#5': {'pppp': 29.299673, 'ppp': 28.313274, 'pp': 27.126843, 'p': 25.017642, 'mp': 23.995676, 'mf': 23.713612, 'f': 24.439174, 'ff': 26.379153, 'fff': 27.769515, 'ffff': 28.934384},
    'E5': {'pppp': 17.732692, 'ppp': 17.813858, 'pp': 17.915837, 'p': 18.127095, 'mp': 18.205553, 'mf': 18.216789, 'f': 17.899737, 'ff': 17.229302, 'fff': 16.811624, 'ffff': 16.484784},
    'F5': {'pppp': 14.288558, 'ppp': 14.332051, 'pp': 14.386603, 'p': 14.477781, 'mp': 14.511518, 'mf': 14.516344, 'f': 14.454141, 'ff': 14.312616, 'fff': 14.24432, 'ffff': 14.189918},
    'F#5': {'pppp': 19.576765, 'ppp': 20.005201, 'pp': 20.553956, 'p': 21.250427, 'mp': 21.869559, 'mf': 22.393555, 'f': 22.827662, 'ff': 23.170852, 'fff': 23.548696, 'ffff': 23.855403},
    'G5': {'pppp': 17.80478, 'ppp': 18.060377, 'pp': 18.38504, 'p': 19.032137, 'mp': 19.358749, 'mf': 19.446811, 'f': 19.166389, 'ff': 18.490047, 'fff': 18.07079, 'ffff': 17.742241},
    'G#5': {'pppp': 18.487759, 'ppp': 18.532191, 'pp': 18.587882, 'p': 18.603986, 'mp': 18.651902, 'mf': 18.731149, 'f': 19.190466, 'ff': 20.08651, 'fff': 20.738569, 'ffff': 21.275425},
    'A5': {'pppp': 14.870503, 'ppp': 14.831134, 'pp': 14.78207, 'p': 14.645906, 'mp': 14.549729, 'mf': 14.513254, 'f': 14.515237, 'ff': 14.529125, 'fff': 14.549186, 'ffff': 14.565255},
    'A#5': {'pppp': 16.0954, 'ppp': 15.981685, 'pp': 15.84067, 'p': 15.543176, 'mp': 15.370307, 'mf': 15.313999, 'f': 15.378158, 'ff': 15.566162, 'fff': 15.686168, 'ffff': 15.782838},
    'B5': {'pppp': 16.298803, 'ppp': 16.187708, 'pp': 16.049904, 'p': 15.88878, 'mp': 15.719015, 'mf': 15.542648, 'f': 15.35774, 'ff': 15.163873, 'fff': 15.008518, 'ffff': 14.885382},
    'C6': {'pppp': 11.054327, 'ppp': 11.200793, 'pp': 11.386607, 'p': 11.732456, 'mp': 11.933478, 'mf': 11.997742, 'f': 11.902797, 'ff': 11.645386, 'fff': 11.494006, 'ffff': 11.37432},
    'C#6': {'pppp': 17.967184, 'ppp': 17.917932, 'pp': 17.856556, 'p': 17.822755, 'mp': 17.732013, 'mf': 17.6005, 'f': 17.295058, 'ff': 16.809528, 'fff': 16.480073, 'ffff': 16.221164},
    'D6': {'pppp': 18.160816, 'ppp': 17.857522, 'pp': 17.485517, 'p': 16.847966, 'mp': 16.426756, 'mf': 16.273744, 'f': 16.296631, 'ff': 16.457741, 'fff': 16.548735, 'ffff': 16.621892},
    'D#6': {'pppp': 18.40792, 'ppp': 17.908108, 'pp': 17.302384, 'p': 16.138227, 'mp': 15.63765, 'mf': 15.522559, 'f': 16.073006, 'ff': 17.472858, 'fff': 18.4965, 'ffff': 19.358427},
    'E6': {'pppp': 11.370439, 'ppp': 11.419502, 'pp': 11.481128, 'p': 11.502719, 'mp': 11.564665, 'mf': 11.662968, 'f': 12.036813, 'ff': 12.734164, 'fff': 13.264761, 'ffff': 13.705113},
    'F6': {'pppp': 8.46623, 'ppp': 8.484012, 'pp': 8.506292, 'p': 8.512071, 'mp': 8.529095, 'mf': 8.556931, 'f': 8.699293, 'ff': 8.970366, 'fff': 9.162292, 'ffff': 9.318784},
    'F#6': {'pppp': 8.868172, 'ppp': 8.90658, 'pp': 8.954824, 'p': 8.97145, 'mp': 9.019772, 'mf': 9.097664, 'f': 9.435096, 'ff': 10.081186, 'fff': 10.576903, 'ffff': 10.99097},
    'G6': {'pppp': 8.460342, 'ppp': 8.438047, 'pp': 8.410261, 'p': 8.335192, 'mp': 8.307704, 'mf': 8.303785, 'f': 8.526777, 'ff': 9.021014, 'fff': 9.373436, 'ffff': 9.665261},
    'G#6': {'pppp': 7.960556, 'ppp': 7.766379, 'pp': 7.530304, 'p': 7.042762, 'mp': 6.862145, 'mf': 6.832271, 'f': 7.12699, 'ff': 7.858365, 'fff': 8.406088, 'ffff': 8.871627},
    'A6': {'pppp': 7.925645, 'ppp': 7.872968, 'pp': 7.807614, 'p': 7.649263, 'mp': 7.591737, 'mf': 7.583554, 'f': 7.750056, 'ff': 8.13189, 'fff': 8.399835, 'ffff': 8.620534},
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
