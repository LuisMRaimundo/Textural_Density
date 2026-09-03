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
    pitch_range=(48, 88),
    uncertainty="high",
    version="2026-09-03",
    source_technique="arco_sul_ponticello",
    table_supported_techniques=("arco_sul_ponticello",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("viola_sul_ponticello")

# Full 10-dynamic CDM ladder (Results sheet). Anchors pp/mf/ff match measured
# workbook midpoints; other levels are workbook-committed.
spectral_data = {
    'C3': {'pppp': 36.674282, 'ppp': 37.898558, 'pp': 39.486533, 'p': 42.159688, 'mp': 44.208709, 'mf': 45.024733, 'f': 45.009337, 'ff': 44.901716, 'fff': 44.883744, 'ffff': 44.869371},
    'C#3': {'pppp': 46.548459, 'ppp': 48.609962, 'pp': 51.315699, 'p': 56.492871, 'mp': 59.776597, 'mf': 60.891444, 'f': 59.589982, 'ff': 55.98405, 'fff': 53.900274, 'ffff': 52.289236},
    'D3': {'pppp': 44.479043, 'ppp': 45.741987, 'pp': 47.371214, 'p': 48.898982, 'mp': 50.725035, 'mf': 52.818383, 'f': 55.287895, 'ff': 58.208313, 'fff': 60.846767, 'ffff': 63.043382},
    'D#3': {'pppp': 35.518767, 'ppp': 37.154303, 'pp': 39.305033, 'p': 43.341457, 'mp': 46.022918, 'mf': 46.972687, 'f': 46.192299, 'ff': 43.804635, 'fff': 42.452164, 'ffff': 41.400314},
    'E3': {'pppp': 36.93201, 'ppp': 39.198776, 'pp': 42.228869, 'p': 47.5689, 'mp': 51.840052, 'mf': 53.582902, 'f': 53.538008, 'ff': 53.224801, 'fff': 53.08984, 'ffff': 52.982117},
    'F3': {'pppp': 36.389971, 'ppp': 36.679238, 'pp': 37.044058, 'p': 37.150604, 'mp': 37.449813, 'mf': 37.912512, 'f': 39.360013, 'ff': 41.986143, 'fff': 43.908958, 'ffff': 45.510421},
    'F#3': {'pppp': 26.757833, 'ppp': 28.579268, 'pp': 31.031395, 'p': 36.106817, 'mp': 39.173478, 'mf': 40.138379, 'f': 38.205323, 'ff': 33.584636, 'fff': 30.883098, 'ffff': 28.879191},
    'G3': {'pppp': 37.470467, 'ppp': 38.552094, 'pp': 39.948139, 'p': 42.86998, 'mp': 44.272402, 'mf': 44.612378, 'f': 43.086883, 'ff': 39.631756, 'fff': 37.579336, 'ffff': 36.014196},
    'G#3': {'pppp': 61.484103, 'ppp': 62.13612, 'pp': 62.960874, 'p': 63.471902, 'mp': 64.181997, 'mf': 65.032213, 'f': 66.113836, 'ff': 67.469137, 'fff': 68.558918, 'ffff': 69.443403},
    'A3': {'pppp': 34.7469, 'ppp': 36.232169, 'pp': 38.17835, 'p': 41.62565, 'mp': 44.149389, 'mf': 45.119714, 'f': 44.970164, 'ff': 43.937107, 'fff': 43.444249, 'ffff': 43.053945},
    'A#3': {'pppp': 36.757432, 'ppp': 37.740147, 'pp': 39.005568, 'p': 41.049221, 'mp': 42.619698, 'mf': 43.285725, 'f': 43.342527, 'ff': 43.363642, 'fff': 43.435903, 'ffff': 43.493799},
    'B3': {'pppp': 30.975149, 'ppp': 33.048199, 'pp': 35.835691, 'p': 40.336276, 'mp': 44.135609, 'mf': 46.359224, 'f': 47.353971, 'ff': 47.780384, 'fff': 48.472624, 'ffff': 49.03363},
    'C4': {'pppp': 30.299135, 'ppp': 30.901267, 'pp': 31.670788, 'p': 32.44114, 'mp': 33.256534, 'mf': 34.115549, 'f': 35.025612, 'ff': 35.991472, 'fff': 36.862474, 'ffff': 37.574427},
    'C#4': {'pppp': 27.023307, 'ppp': 28.39169, 'pp': 30.200015, 'p': 33.319268, 'mp': 35.80427, 'mf': 36.825192, 'f': 36.83643, 'ff': 36.840509, 'fff': 36.86967, 'ffff': 36.893016},
    'D4': {'pppp': 25.621671, 'ppp': 26.164362, 'pp': 26.858919, 'p': 27.731024, 'mp': 28.487925, 'mf': 29.098448, 'f': 29.579096, 'ff': 29.932645, 'fff': 30.321052, 'ffff': 30.635403},
    'D#4': {'pppp': 47.600376, 'ppp': 48.511113, 'pp': 49.674077, 'p': 50.470546, 'mp': 51.741626, 'mf': 53.338938, 'f': 55.536383, 'ff': 58.495632, 'fff': 60.97045, 'ffff': 63.025482},
    'E4': {'pppp': 32.43283, 'ppp': 33.350401, 'pp': 34.533955, 'p': 36.580339, 'mp': 38.012301, 'mf': 38.547012, 'f': 38.40597, 'ff': 37.687336, 'fff': 37.350551, 'ffff': 37.083292},
    'F4': {'pppp': 29.342193, 'ppp': 30.942117, 'pp': 33.065254, 'p': 37.311529, 'mp': 39.8983, 'mf': 40.73236, 'f': 39.320746, 'ff': 35.769989, 'fff': 33.682959, 'ffff': 32.101356},
    'F#4': {'pppp': 21.001262, 'ppp': 21.270153, 'pp': 21.611113, 'p': 22.017733, 'mp': 22.335626, 'mf': 22.521948, 'f': 22.616211, 'ff': 22.657338, 'fff': 22.740053, 'ffff': 22.806442},
    'G4': {'pppp': 24.60778, 'ppp': 25.07292, 'pp': 25.666729, 'p': 26.677316, 'mp': 27.314502, 'mf': 27.533877, 'f': 27.346127, 'ff': 26.766791, 'fff': 26.475562, 'ffff': 26.244861},
    'G#4': {'pppp': 36.517815, 'ppp': 36.904197, 'pp': 37.392929, 'p': 37.993199, 'mp': 38.385178, 'mf': 38.52501, 'f': 38.457916, 'ff': 38.201899, 'fff': 38.1334, 'ffff': 38.078689},
    'A4': {'pppp': 31.240182, 'ppp': 30.709325, 'pp': 30.058421, 'p': 28.604475, 'mp': 27.856986, 'mf': 27.63955, 'f': 28.101189, 'ff': 29.336105, 'fff': 30.131304, 'ffff': 30.782955},
    'A#4': {'pppp': 32.875822, 'ppp': 32.599183, 'pp': 32.256655, 'p': 31.775979, 'mp': 31.232767, 'mf': 30.646101, 'f': 29.999041, 'ff': 29.289061, 'fff': 28.765051, 'ffff': 28.3526},
    'B4': {'pppp': 33.075908, 'ppp': 32.872888, 'pp': 32.620863, 'p': 31.725377, 'mp': 31.376962, 'mf': 31.315323, 'f': 31.85466, 'ff': 33.143239, 'fff': 33.974651, 'ffff': 34.654772},
    'C5': {'pppp': 18.38534, 'ppp': 18.840538, 'pp': 19.425415, 'p': 20.437989, 'mp': 21.11935, 'mf': 21.36641, 'f': 21.24983, 'ff': 20.805509, 'fff': 20.586236, 'ffff': 20.412483},
    'C#5': {'pppp': 15.213319, 'ppp': 15.537692, 'pp': 15.952903, 'p': 16.300166, 'mp': 16.751731, 'mf': 17.286718, 'f': 17.95121, 'ff': 18.773181, 'fff': 19.482771, 'ffff': 20.069707},
    'D5': {'pppp': 12.746976, 'ppp': 13.317328, 'pp': 14.066289, 'p': 15.068721, 'mp': 15.972958, 'mf': 16.730596, 'f': 17.346951, 'ff': 17.815305, 'fff': 18.341517, 'ffff': 18.773655},
    'D#5': {'pppp': 24.735123, 'ppp': 24.727702, 'pp': 24.718428, 'p': 24.387182, 'mp': 24.266265, 'mf': 24.249041, 'f': 24.558822, 'ff': 25.264548, 'fff': 25.712239, 'ffff': 26.076097},
    'E5': {'pppp': 17.511333, 'ppp': 17.380469, 'pp': 17.218263, 'p': 16.870422, 'mp': 16.582666, 'mf': 16.359396, 'f': 16.188842, 'ff': 16.066141, 'fff': 15.966749, 'ffff': 15.887678},
    'F5': {'pppp': 14.585464, 'ppp': 14.725495, 'pp': 14.902426, 'p': 15.038474, 'mp': 15.164332, 'mf': 15.279797, 'f': 15.384523, 'ff': 15.478243, 'fff': 15.576416, 'ffff': 15.655403},
    'F#5': {'pppp': 20.201393, 'ppp': 20.955368, 'pp': 21.937532, 'p': 23.217226, 'mp': 24.373741, 'mf': 25.360445, 'f': 26.181092, 'ff': 26.827661, 'fff': 27.530749, 'ffff': 28.106463},
    'G5': {'pppp': 18.212386, 'ppp': 18.334783, 'pp': 18.488936, 'p': 18.511606, 'mp': 18.560305, 'mf': 18.622943, 'f': 18.715607, 'ff': 18.844439, 'fff': 18.956173, 'ffff': 19.046037},
    'G#5': {'pppp': 18.093138, 'ppp': 18.066836, 'pp': 18.034013, 'p': 17.846672, 'mp': 17.778144, 'mf': 17.768375, 'f': 18.728234, 'ff': 20.922505, 'fff': 22.514658, 'ffff': 23.875181},
    'A5': {'pppp': 15.798481, 'ppp': 15.609969, 'pp': 15.377489, 'p': 14.797496, 'mp': 14.495888, 'mf': 14.407526, 'f': 14.592015, 'ff': 15.083224, 'fff': 15.393875, 'ffff': 15.646997},
    'A#5': {'pppp': 14.821849, 'ppp': 14.765911, 'pp': 14.696286, 'p': 14.395056, 'mp': 14.28564, 'mf': 14.270077, 'f': 14.61335, 'ff': 15.399328, 'fff': 15.918475, 'ffff': 16.346365},
    'B5': {'pppp': 16.297398, 'ppp': 16.054321, 'pp': 15.755567, 'p': 15.170842, 'mp': 14.742449, 'mf': 14.519972, 'f': 14.432336, 'ff': 14.395996, 'fff': 14.358794, 'ffff': 14.329101},
    'C6': {'pppp': 11.121823, 'ppp': 11.1641, 'pp': 11.217172, 'p': 11.231207, 'mp': 11.236382, 'mf': 11.237121, 'f': 10.970613, 'ff': 10.435219, 'fff': 10.134828, 'ffff': 9.900753},
    'C#6': {'pppp': 19.236462, 'ppp': 19.026557, 'pp': 18.767393, 'p': 18.633012, 'mp': 18.280822, 'mf': 17.789138, 'f': 16.778687, 'ff': 15.291724, 'fff': 14.293962, 'ffff': 13.542835},
    'D6': {'pppp': 19.19684, 'ppp': 18.536301, 'pp': 17.742497, 'p': 16.322794, 'mp': 15.494313, 'mf': 15.21815, 'f': 15.409745, 'ff': 16.066333, 'fff': 16.473333, 'ffff': 16.806343},
    'D#6': {'pppp': 14.665478, 'ppp': 14.845334, 'pp': 15.073259, 'p': 15.155629, 'mp': 15.384868, 'mf': 15.736052, 'f': 16.741989, 'ff': 18.586766, 'fff': 20.04703, 'ffff': 21.297421},
    'E6': {'pppp': 10.35132, 'ppp': 10.344295, 'pp': 10.335522, 'p': 10.2732, 'mp': 10.250334, 'mf': 10.247072, 'f': 11.232871, 'ff': 13.605801, 'fff': 15.515236, 'ffff': 17.23399},
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
