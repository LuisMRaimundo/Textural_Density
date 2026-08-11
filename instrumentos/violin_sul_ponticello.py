# instrumentos/violin_sul_ponticello.py
"""
Violin (arco sul ponticello) instrument density module.

The ``spectral_data`` table stores a committed 10-dynamic Combined Density
Metric (CDM) ladder from the ``Results`` sheet of
``OK_VIOLIN_sul_ponticello_dynamics extrapolation.xlsx``
(measured pp/mf/ff anchors; remaining levels committed from that workbook —
no runtime dynamic extrapolation).

Runtime analysis does not ingest audio; it maps notated pitch + dynamic to
these pre-loaded acoustic metadata tables.
"""

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="external_acoustic_metadata",
    citation=(
        "Violin arco_sul_ponticello CDM ladder: measured pp/mf/ff anchors with "
        "committed Results sheet values for all 10 dynamic levels from "
        "OK_VIOLIN_sul_ponticello_dynamics extrapolation.xlsx "
        "(CDM Technique Extrapolator METApool, IOWA+ORCHIDEA collections)."
    ),
    source_url_or_identifier='docs/instrument_acoustic_sources.md#violin-sul-ponticello',
    extraction_method=(
        "Committed full dynamic ladder from Dynamics extrapolator v1.5.2.1 Results sheet "
        "(PCHIP interiors, tapered outers r=0.80) on measured pp/mf/ff anchors; "
        "interior cells clamped into their measured segment where the workbook "
        "marginally overshoots; pitch lookup via MIDI-space spectral_lookup"
    ),
    dynamic_levels=('pppp', 'ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', 'ffff'),
    pitch_range=(55, 103),
    uncertainty="high",
    version="2026-08-11",
    source_technique="arco_sul_ponticello",
    table_supported_techniques=("arco_sul_ponticello",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("violin_sul_ponticello")

# Full 10-dynamic CDM ladder (Results sheet). Anchors pp/mf/ff match measured
# workbook midpoints; other levels are workbook-committed.
spectral_data = {
    'G3': {'pppp': 49.295121, 'ppp': 49.323724, 'pp': 49.3595, 'p': 48.758824, 'mp': 48.53937, 'mf': 48.5081, 'f': 50.772056, 'ff': 55.9171, 'fff': 59.617136, 'ffff': 62.752681},
    'G#3': {'pppp': 40.595307, 'ppp': 40.666249, 'pp': 40.7551, 'p': 40.392434, 'mp': 40.259636, 'mf': 40.2407, 'f': 42.079434, 'ff': 46.2314, 'fff': 49.213538, 'ffff': 51.737165},
    'A3': {'pppp': 29.645976, 'ppp': 29.732318, 'pp': 29.8406, 'p': 29.673061, 'mp': 29.611574, 'mf': 29.6028, 'f': 30.926502, 'ff': 33.8957, 'fff': 36.025958, 'ffff': 37.826162},
    'A#3': {'pppp': 28.851573, 'ppp': 28.969108, 'pp': 29.1167, 'p': 29.049182, 'mp': 29.024346, 'mf': 29.0208, 'f': 30.290154, 'ff': 33.1179, 'fff': 35.144761, 'ffff': 36.855205},
    'B3': {'pppp': 33.297246, 'ppp': 33.469822, 'pp': 33.6868, 'p': 33.691604, 'mp': 33.706894, 'mf': 33.734, 'f': 35.185292, 'ff': 38.3673, 'fff': 40.655185, 'ffff': 42.583339},
    'C4': {'pppp': 29.071129, 'ppp': 29.250822, 'pp': 29.477, 'p': 29.496107, 'mp': 29.555273, 'mf': 29.6574, 'f': 30.929193, 'ff': 33.6176, 'fff': 35.574885, 'ffff': 37.22245},
    'C#4': {'pppp': 19.994354, 'ppp': 20.137952, 'pp': 20.3189, 'p': 20.343172, 'mp': 20.416407, 'mf': 20.5395, 'f': 21.416453, 'ff': 23.2041, 'fff': 24.52238, 'ffff': 25.630727},
    'D4': {'pppp': 21.81597, 'ppp': 21.99458, 'pp': 22.2199, 'p': 22.259509, 'mp': 22.376132, 'mf': 22.567, 'f': 23.525236, 'ff': 25.4091, 'fff': 26.81678, 'ffff': 27.998871},
    'D#4': {'pppp': 25.750767, 'ppp': 25.987553, 'pp': 26.2866, 'p': 26.349986, 'mp': 26.532362, 'mf': 26.823, 'f': 27.954396, 'ff': 30.0998, 'fff': 31.724818, 'ffff': 33.087775},
    'E4': {'pppp': 26.261462, 'ppp': 26.529501, 'pp': 26.8684, 'p': 26.951174, 'mp': 27.184203, 'mf': 27.5458, 'f': 28.698643, 'ff': 30.8073, 'fff': 32.426978, 'ffff': 33.78382},
    'F4': {'pppp': 22.766225, 'ppp': 23.021709, 'pp': 23.3451, 'p': 23.433612, 'mp': 23.677708, 'mf': 24.0465, 'f': 25.043846, 'ff': 26.8034, 'fff': 28.174603, 'ffff': 29.321902},
    'F#4': {'pppp': 20.488531, 'ppp': 20.739308, 'pp': 21.0571, 'p': 21.152743, 'mp': 21.411404, 'mf': 21.7919, 'f': 22.686512, 'ff': 24.2088, 'fff': 25.41295, 'ffff': 26.419253},
    'G4': {'pppp': 20.287015, 'ppp': 20.556065, 'pp': 20.8974, 'p': 21.008868, 'mp': 21.304796, 'mf': 21.7286, 'f': 22.610438, 'ff': 24.0575, 'fff': 25.220003, 'ffff': 26.190322},
    'G#4': {'pppp': 18.707031, 'ppp': 18.974273, 'pp': 19.3137, 'p': 19.432765, 'mp': 19.743361, 'mf': 20.1764, 'f': 20.984841, 'ff': 22.264, 'fff': 23.308235, 'ffff': 24.178778},
    'A4': {'pppp': 18.774068, 'ppp': 19.06155, 'pp': 19.4271, 'p': 19.563788, 'mp': 19.914461, 'mf': 20.3904, 'f': 21.196021, 'ff': 22.4248, 'fff': 23.44478, 'ffff': 24.294067},
    'A#4': {'pppp': 17.823778, 'ppp': 18.115118, 'pp': 18.486, 'p': 18.639593, 'mp': 19.007411, 'mf': 19.4942, 'f': 20.252567, 'ff': 21.3671, 'fff': 22.308525, 'ffff': 23.091443},
    'B4': {'pppp': 20.14885, 'ppp': 20.499019, 'pp': 20.9453, 'p': 21.172273, 'mp': 21.616139, 'mf': 22.1916, 'f': 23.040492, 'ff': 24.2422, 'fff': 25.275875, 'ffff': 26.134459},
    'C5': {'pppp': 14.459898, 'ppp': 14.726207, 'pp': 15.066, 'p': 15.268081, 'mp': 15.607619, 'mf': 16.0377, 'f': 16.640039, 'ff': 17.4609, 'fff': 18.180574, 'ffff': 18.777613},
    'C#5': {'pppp': 12.33148, 'ppp': 12.571411, 'pp': 12.8779, 'p': 13.084373, 'mp': 13.392527, 'mf': 13.773, 'f': 14.280072, 'ff': 14.9449, 'fff': 15.539573, 'ffff': 16.032304},
    'D5': {'pppp': 10.829324, 'ppp': 11.051352, 'pp': 11.3353, 'p': 11.547329, 'mp': 11.834964, 'mf': 12.1804, 'f': 12.619276, 'ff': 13.1724, 'fff': 13.677745, 'ffff': 14.095945},
    'D#5': {'pppp': 11.975467, 'ppp': 12.233511, 'pp': 12.5639, 'p': 12.832957, 'mp': 13.170504, 'mf': 13.5641, 'f': 14.041594, 'ff': 14.6196, 'fff': 15.159621, 'ffff': 15.605965},
    'E5': {'pppp': 18.553707, 'ppp': 18.972972, 'pp': 19.5104, 'p': 19.982022, 'mp': 20.536318, 'mf': 21.1628, 'f': 21.88938, 'ff': 22.7332, 'fff': 23.540533, 'ffff': 24.206995},
    'F5': {'pppp': 16.777761, 'ppp': 17.174568, 'pp': 17.6838, 'p': 18.160904, 'mp': 18.691534, 'mf': 19.2719, 'f': 19.915918, 'ff': 20.6325, 'fff': 21.335757, 'ffff': 21.915582},
    'F#5': {'pppp': 13.957598, 'ppp': 14.302441, 'pp': 14.7455, 'p': 15.185369, 'mp': 15.652113, 'mf': 16.1454, 'f': 16.66948, 'ff': 17.2273, 'fff': 17.78989, 'ffff': 18.253162},
    'G5': {'pppp': 13.564258, 'ppp': 13.913747, 'pp': 14.3633, 'p': 14.833393, 'mp': 15.312451, 'mf': 15.801, 'f': 16.29811, 'ff': 16.8033, 'fff': 17.328046, 'ffff': 17.759617},
    'G#5': {'pppp': 12.061287, 'ppp': 12.384877, 'pp': 12.8016, 'p': 13.258327, 'mp': 13.707759, 'mf': 14.1494, 'f': 14.579783, 'ff': 14.9964, 'fff': 15.443254, 'ffff': 15.810305},
    'A5': {'pppp': 10.825743, 'ppp': 11.127692, 'pp': 11.517, 'p': 11.962287, 'mp': 12.38738, 'mf': 12.7894, 'f': 13.164575, 'ff': 13.5096, 'fff': 13.892864, 'ffff': 14.207289},
    'A#5': {'pppp': 10.587196, 'ppp': 10.893812, 'pp': 11.2896, 'p': 11.760428, 'mp': 12.198148, 'mf': 12.596, 'f': 12.951337, 'ff': 13.2607, 'fff': 13.61794, 'ffff': 13.910649},
    'B5': {'pppp': 11.752873, 'ppp': 12.105843, 'pp': 12.562, 'p': 13.124691, 'mp': 13.635813, 'mf': 14.0817, 'f': 14.462492, 'ff': 14.775, 'fff': 15.151858, 'ffff': 15.460254},
    'C6': {'pppp': 11.110406, 'ppp': 11.456022, 'pp': 11.9032, 'p': 12.47369, 'mp': 12.981471, 'mf': 13.4061, 'f': 13.752457, 'ff': 14.019, 'fff': 14.356525, 'ffff': 14.632386},
    'C#6': {'pppp': 9.427272, 'ppp': 9.730677, 'pp': 10.1237, 'p': 10.641102, 'mp': 11.093474, 'mf': 11.4556, 'f': 11.737249, 'ff': 11.9391, 'fff': 12.209433, 'ffff': 12.4301},
    'D6': {'pppp': 10.461617, 'ppp': 10.8096, 'pp': 11.2609, 'p': 11.872761, 'mp': 12.399387, 'mf': 12.8024, 'f': 13.100676, 'ff': 13.298, 'fff': 13.58006, 'ffff': 13.810009},
    'D#6': {'pppp': 9.840368, 'ppp': 10.178351, 'pp': 10.6172, 'p': 11.228904, 'mp': 11.74817, 'mf': 12.1275, 'f': 12.393945, 'ff': 12.5547, 'fff': 12.802998, 'ffff': 13.005167},
    'E6': {'pppp': 12.207955, 'ppp': 12.640502, 'pp': 13.2028, 'p': 14.007331, 'mp': 14.682055, 'mf': 15.1519, 'f': 15.464114, 'ff': 15.6331, 'fff': 15.919911, 'ffff': 16.153143},
    'F6': {'pppp': 7.155618, 'ppp': 7.41696, 'pp': 7.7571, 'p': 8.256025, 'mp': 8.67, 'mf': 8.9443, 'f': 9.115984, 'ff': 9.1973, 'fff': 9.352812, 'ffff': 9.479112},
    'F#6': {'pppp': 6.99608, 'ppp': 7.259217, 'pp': 7.6021, 'p': 8.11702, 'mp': 8.540304, 'mf': 8.8068, 'f': 8.957697, 'ff': 9.0256, 'fff': 9.165298, 'ffff': 9.278612},
    'G6': {'pppp': 6.933894, 'ppp': 7.202273, 'pp': 7.5524, 'p': 8.09014, 'mp': 8.528591, 'mf': 8.7904, 'f': 8.92136, 'ff': 8.9786, 'fff': 9.104709, 'ffff': 9.20687},
    'G#6': {'pppp': 5.78313, 'ppp': 6.013327, 'pp': 6.314, 'p': 6.785845, 'mp': 7.167833, 'mf': 7.3837, 'f': 7.476863, 'ff': 7.5164, 'fff': 7.611158, 'ffff': 7.687824},
    'A6': {'pppp': 4.595522, 'ppp': 4.783491, 'pp': 5.0293, 'p': 5.423041, 'mp': 5.73985, 'mf': 5.909, 'f': 5.969975, 'ff': 5.9951, 'fff': 6.062116, 'ffff': 6.116267},
    'A#6': {'pppp': 3.680729, 'ppp': 3.835353, 'pp': 4.0378, 'p': 4.368571, 'mp': 4.633304, 'mf': 4.7665, 'f': 4.804502, 'ff': 4.8197, 'fff': 4.866651, 'ffff': 4.90454},
    'B6': {'pppp': 4.030831, 'ppp': 4.204607, 'pp': 4.4324, 'p': 4.811738, 'mp': 5.113966, 'mf': 5.2569, 'f': 5.286294, 'ff': 5.2977, 'fff': 5.341692, 'ffff': 5.377149},
    'C7': {'pppp': 4.507866, 'ppp': 4.707196, 'pp': 4.9688, 'p': 5.412476, 'mp': 5.764622, 'mf': 5.9208, 'f': 5.939701, 'ff': 5.946817, 'fff': 5.987703, 'ffff': 6.020615},
    'C#7': {'pppp': 4.468438, 'ppp': 4.671015, 'pp': 4.9372, 'p': 5.396743, 'mp': 5.76032, 'mf': 5.911, 'f': 5.915387, 'ff': 5.916988, 'fff': 5.949152, 'ffff': 5.975009},
    'D7': {'pppp': 3.805691, 'ppp': 3.982665, 'pp': 4.2155, 'p': 4.621648, 'mp': 4.94135, 'mf': 5.0707, 'f': 5.069217, 'ff': 5.058852, 'fff': 5.078755, 'ffff': 5.094735},
    'D#7': {'pppp': 3.664391, 'ppp': 3.839165, 'pp': 4.0694, 'p': 4.473836, 'mp': 4.790366, 'mf': 4.9179, 'f': 4.914401, 'ff': 4.88998, 'fff': 4.901706, 'ffff': 4.911107},
    'E7': {'pppp': 3.49609, 'ppp': 3.66707, 'pp': 3.8926, 'p': 4.291435, 'mp': 4.601906, 'mf': 4.7265, 'f': 4.721146, 'ff': 4.68384, 'fff': 4.687813, 'ffff': 4.690994},
    'F7': {'pppp': 3.618196, 'ppp': 3.799518, 'pp': 4.039, 'p': 4.465195, 'mp': 4.795319, 'mf': 4.9273, 'f': 4.919661, 'ff': 4.866515, 'fff': 4.863142, 'ffff': 4.860446},
    'F#7': {'pppp': 3.636027, 'ppp': 3.822668, 'pp': 4.0695, 'p': 4.511444, 'mp': 4.852173, 'mf': 4.9879, 'f': 4.978074, 'ff': 4.90983, 'fff': 4.898809, 'ffff': 4.89001},
    'G7': {'pppp': 3.842799, 'ppp': 4.044759, 'pp': 4.3122, 'p': 4.793833, 'mp': 5.163541, 'mf': 5.3103, 'f': 5.297605, 'ff': 5.209582, 'fff': 5.189765, 'ffff': 5.173966},
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
