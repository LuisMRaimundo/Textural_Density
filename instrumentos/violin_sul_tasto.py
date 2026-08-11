# instrumentos/violin_sul_tasto.py
"""
Violin (arco sul tasto) instrument density module.

The ``spectral_data`` table stores a committed 10-dynamic Combined Density
Metric (CDM) ladder from the ``Results`` sheet of
``OK_VIOLIN_sul_tasto_dynamics extrapolation.xlsx``
(measured pp/mf/ff anchors; remaining levels committed from that workbook —
no runtime dynamic extrapolation).

Runtime analysis does not ingest audio; it maps notated pitch + dynamic to
these pre-loaded acoustic metadata tables.
"""

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="external_acoustic_metadata",
    citation=(
        "Violin arco_sul_tasto CDM ladder: measured pp/mf/ff anchors with "
        "committed Results sheet values for all 10 dynamic levels from "
        "OK_VIOLIN_sul_tasto_dynamics extrapolation.xlsx "
        "(CDM Technique Extrapolator METApool, IOWA+ORCHIDEA collections)."
    ),
    source_url_or_identifier='docs/instrument_acoustic_sources.md#violin-sul-tasto',
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
    source_technique="arco_sul_tasto",
    table_supported_techniques=("arco_sul_tasto",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("violin_sul_tasto")

# Full 10-dynamic CDM ladder (Results sheet). Anchors pp/mf/ff match measured
# workbook midpoints; other levels are workbook-committed.
spectral_data = {
    'G3': {'pppp': 36.684078, 'ppp': 36.700972, 'pp': 36.7221, 'p': 36.275227, 'mp': 36.111963, 'mf': 36.0887, 'f': 37.773024, 'ff': 41.6008, 'fff': 44.360636, 'ffff': 46.699758},
    'G#3': {'pppp': 21.408636, 'ppp': 21.443429, 'pp': 21.487, 'p': 21.295797, 'mp': 21.225783, 'mf': 21.2158, 'f': 22.185242, 'ff': 24.3743, 'fff': 25.950826, 'ffff': 27.285154},
    'A3': {'pppp': 17.315638, 'ppp': 17.363893, 'pp': 17.4244, 'p': 17.32654, 'mp': 17.290625, 'mf': 17.2855, 'f': 18.058461, 'ff': 19.7923, 'fff': 21.039757, 'ffff': 22.094098},
    'A#3': {'pppp': 19.115257, 'ppp': 19.19069, 'pp': 19.2854, 'p': 19.240693, 'mp': 19.224248, 'mf': 19.2219, 'f': 20.062653, 'ff': 21.9356, 'fff': 23.282048, 'ffff': 24.418474},
    'B3': {'pppp': 23.203536, 'ppp': 23.320794, 'pp': 23.4682, 'p': 23.471548, 'mp': 23.482206, 'mf': 23.5011, 'f': 24.51215, 'ff': 26.7289, 'fff': 28.327647, 'ffff': 29.675226},
    'C4': {'pppp': 13.867057, 'ppp': 13.950981, 'pp': 14.0566, 'p': 14.065709, 'mp': 14.093914, 'mf': 14.1426, 'f': 14.749074, 'ff': 16.0311, 'fff': 16.967374, 'ffff': 17.755613},
    'C#4': {'pppp': 13.123171, 'ppp': 13.215753, 'pp': 13.3324, 'p': 13.348333, 'mp': 13.396404, 'mf': 13.4772, 'f': 14.052631, 'ff': 15.2256, 'fff': 16.093334, 'ffff': 16.822995},
    'D4': {'pppp': 20.384175, 'ppp': 20.548469, 'pp': 20.7557, 'p': 20.792696, 'mp': 20.901623, 'mf': 21.0799, 'f': 21.975012, 'ff': 23.7348, 'fff': 25.053981, 'ffff': 26.161924},
    'D#4': {'pppp': 19.195102, 'ppp': 19.36918, 'pp': 19.589, 'p': 19.636232, 'mp': 19.772129, 'mf': 19.9887, 'f': 20.831851, 'ff': 22.4307, 'fff': 23.645678, 'ffff': 24.664875},
    'E4': {'pppp': 21.319939, 'ppp': 21.534877, 'pp': 21.8066, 'p': 21.873783, 'mp': 22.062917, 'mf': 22.3564, 'f': 23.292041, 'ff': 25.0034, 'fff': 26.322277, 'ffff': 27.427295},
    'F4': {'pppp': 15.551919, 'ppp': 15.724491, 'pp': 15.9429, 'p': 16.003332, 'mp': 16.169992, 'mf': 16.4218, 'f': 17.102909, 'ff': 18.3046, 'fff': 19.244213, 'ffff': 20.030513},
    'F#4': {'pppp': 17.24139, 'ppp': 17.4503, 'pp': 17.715, 'p': 17.795466, 'mp': 18.013084, 'mf': 18.3332, 'f': 19.085827, 'ff': 20.3665, 'fff': 21.38302, 'ffff': 22.232646},
    'G4': {'pppp': 16.918549, 'ppp': 17.140833, 'pp': 17.4228, 'p': 17.515719, 'mp': 17.762405, 'mf': 18.1157, 'f': 18.850909, 'ff': 20.0574, 'fff': 21.030026, 'ffff': 21.841978},
    'G#4': {'pppp': 11.858345, 'ppp': 12.026303, 'pp': 12.2396, 'p': 12.315052, 'mp': 12.511878, 'mf': 12.7863, 'f': 13.298639, 'ff': 14.1093, 'fff': 14.773445, 'ffff': 15.327201},
    'A4': {'pppp': 14.083196, 'ppp': 14.297164, 'pp': 14.5692, 'p': 14.671723, 'mp': 14.93474, 'mf': 15.2917, 'f': 15.895853, 'ff': 16.8173, 'fff': 17.584986, 'ffff': 18.22429},
    'A#4': {'pppp': 12.082148, 'ppp': 12.27818, 'pp': 12.5277, 'p': 12.631762, 'mp': 12.881017, 'mf': 13.2109, 'f': 13.724849, 'ff': 14.4802, 'fff': 15.120606, 'ffff': 15.653264},
    'B4': {'pppp': 14.93476, 'ppp': 15.192526, 'pp': 15.521, 'p': 15.689168, 'mp': 16.018075, 'mf': 16.4445, 'f': 17.073563, 'ff': 17.9641, 'fff': 18.733036, 'ffff': 19.371816},
    'C5': {'pppp': 9.851958, 'ppp': 10.032223, 'pp': 10.2622, 'p': 10.399819, 'mp': 10.631073, 'mf': 10.924, 'f': 11.33427, 'ff': 11.8934, 'fff': 12.385522, 'ffff': 12.79384},
    'C#5': {'pppp': 9.085772, 'ppp': 9.261479, 'pp': 9.4859, 'p': 9.637978, 'mp': 9.864955, 'mf': 10.1452, 'f': 10.518698, 'ff': 11.0084, 'fff': 11.448188, 'ffff': 11.812635},
    'D5': {'pppp': 10.793888, 'ppp': 11.01393, 'pp': 11.2953, 'p': 11.506573, 'mp': 11.793188, 'mf': 12.1374, 'f': 12.574725, 'ff': 13.1259, 'fff': 13.631543, 'ffff': 14.050046},
    'D#5': {'pppp': 9.780913, 'ppp': 9.990539, 'pp': 10.2589, 'p': 10.478588, 'mp': 10.754208, 'mf': 11.0756, 'f': 11.465507, 'ff': 11.9375, 'fff': 12.380342, 'ffff': 12.746415},
    'E5': {'pppp': 13.743835, 'ppp': 14.052847, 'pp': 14.4489, 'p': 14.798203, 'mp': 15.208725, 'mf': 15.6727, 'f': 16.210795, 'ff': 16.8357, 'fff': 17.436209, 'ffff': 17.932001},
    'F5': {'pppp': 10.657101, 'ppp': 10.907937, 'pp': 11.2298, 'p': 11.532767, 'mp': 11.869736, 'mf': 12.2383, 'f': 12.6473, 'ff': 13.1024, 'fff': 13.551042, 'ffff': 13.920991},
    'F#5': {'pppp': 10.195055, 'ppp': 10.445791, 'pp': 10.7679, 'p': 11.089134, 'mp': 11.429981, 'mf': 11.7902, 'f': 12.17289, 'ff': 12.5802, 'fff': 12.992922, 'ffff': 13.332828},
    'G5': {'pppp': 10.132455, 'ppp': 10.392387, 'pp': 10.7267, 'p': 11.07778, 'mp': 11.435549, 'mf': 11.8004, 'f': 12.171637, 'ff': 12.5489, 'fff': 12.942666, 'ffff': 13.266557},
    'G#5': {'pppp': 8.395084, 'ppp': 8.619382, 'pp': 8.9082, 'p': 9.226025, 'mp': 9.538774, 'mf': 9.8461, 'f': 10.14559, 'ff': 10.4355, 'fff': 10.74801, 'ffff': 11.004742},
    'A5': {'pppp': 8.739185, 'ppp': 8.981988, 'pp': 9.295, 'p': 9.654425, 'mp': 9.997534, 'mf': 10.322, 'f': 10.624778, 'ff': 10.9032, 'fff': 11.21411, 'ffff': 11.469209},
    'A#5': {'pppp': 7.07577, 'ppp': 7.279915, 'pp': 7.5434, 'p': 7.858, 'mp': 8.150474, 'mf': 8.4163, 'f': 8.653712, 'ff': 8.8604, 'fff': 9.10038, 'ffff': 9.297035},
    'B5': {'pppp': 8.393112, 'ppp': 8.644264, 'pp': 8.9688, 'p': 9.370535, 'mp': 9.735453, 'mf': 10.0538, 'f': 10.325675, 'ff': 10.5488, 'fff': 10.819396, 'ffff': 11.040862},
    'C6': {'pppp': 8.635702, 'ppp': 8.903391, 'pp': 9.2497, 'p': 9.692998, 'mp': 10.087561, 'mf': 10.4175, 'f': 10.686612, 'ff': 10.8937, 'fff': 11.157514, 'ffff': 11.373158},
    'C#6': {'pppp': 6.936248, 'ppp': 7.158732, 'pp': 7.4469, 'p': 7.827472, 'mp': 8.160219, 'mf': 8.4266, 'f': 8.633794, 'ff': 8.7823, 'fff': 8.98242, 'ffff': 9.145794},
    'D6': {'pppp': 7.582479, 'ppp': 7.833887, 'pp': 8.1599, 'p': 8.603271, 'mp': 8.984875, 'mf': 9.2769, 'f': 9.493027, 'ff': 9.636, 'fff': 9.841731, 'ffff': 10.009474},
    'D#6': {'pppp': 7.143902, 'ppp': 7.388518, 'pp': 7.7061, 'p': 8.150077, 'mp': 8.526967, 'mf': 8.8023, 'f': 8.995704, 'ff': 9.1124, 'fff': 9.2939, 'ffff': 9.441699},
    'E6': {'pppp': 8.04681, 'ppp': 8.331088, 'pp': 8.7006, 'p': 9.230808, 'mp': 9.675468, 'mf': 9.9851, 'f': 10.190846, 'ff': 10.3022, 'fff': 10.492621, 'ffff': 10.64749},
    'F6': {'pppp': 5.415703, 'ppp': 5.612933, 'pp': 5.8696, 'p': 6.247098, 'mp': 6.560329, 'mf': 6.7679, 'f': 6.897837, 'ff': 6.9594, 'fff': 7.078046, 'ffff': 7.174418},
    'F#6': {'pppp': 4.967702, 'ppp': 5.154031, 'pp': 5.3968, 'p': 5.762341, 'mp': 6.062826, 'mf': 6.252, 'f': 6.359104, 'ff': 6.4073, 'fff': 6.507325, 'ffff': 6.588468},
    'G6': {'pppp': 4.873178, 'ppp': 5.061301, 'pp': 5.3067, 'p': 5.684562, 'mp': 5.99265, 'mf': 6.1766, 'f': 6.268594, 'ff': 6.3088, 'fff': 6.398236, 'ffff': 6.470696},
    'G#6': {'pppp': 5.784399, 'ppp': 6.014059, 'pp': 6.314, 'p': 6.785845, 'mp': 7.167833, 'mf': 7.3837, 'f': 7.476863, 'ff': 7.5164, 'fff': 7.61215, 'ffff': 7.689628},
    'A6': {'pppp': 4.596521, 'ppp': 4.784069, 'pp': 5.0293, 'p': 5.423041, 'mp': 5.73985, 'mf': 5.909, 'f': 5.969975, 'ff': 5.9951, 'fff': 6.062899, 'ffff': 6.11769},
    'A#6': {'pppp': 3.681521, 'ppp': 3.835812, 'pp': 4.0378, 'p': 4.368571, 'mp': 4.633304, 'mf': 4.7665, 'f': 4.804502, 'ff': 4.8197, 'fff': 4.867274, 'ffff': 4.905671},
    'B6': {'pppp': 4.031691, 'ppp': 4.205106, 'pp': 4.4324, 'p': 4.811738, 'mp': 5.113966, 'mf': 5.2569, 'f': 5.286294, 'ff': 5.2977, 'fff': 5.34237, 'ffff': 5.378377},
    'C7': {'pppp': 4.508819, 'ppp': 4.707749, 'pp': 4.9688, 'p': 5.412476, 'mp': 5.764622, 'mf': 5.9208, 'f': 5.939701, 'ff': 5.946817, 'fff': 5.988456, 'ffff': 6.021977},
    'C#7': {'pppp': 4.469374, 'ppp': 4.671559, 'pp': 4.9372, 'p': 5.396743, 'mp': 5.76032, 'mf': 5.911, 'f': 5.915387, 'ff': 5.916988, 'fff': 5.949893, 'ffff': 5.976349},
    'D7': {'pppp': 3.80647, 'ppp': 3.983118, 'pp': 4.2155, 'p': 4.621648, 'mp': 4.94135, 'mf': 5.0707, 'f': 5.069217, 'ff': 5.058852, 'fff': 5.079373, 'ffff': 5.095849},
    'D#7': {'pppp': 3.665118, 'ppp': 3.839588, 'pp': 4.0694, 'p': 4.473836, 'mp': 4.790366, 'mf': 4.9179, 'f': 4.914401, 'ff': 4.88998, 'fff': 4.902284, 'ffff': 4.91215},
    'E7': {'pppp': 3.496763, 'ppp': 3.667462, 'pp': 3.8926, 'p': 4.291435, 'mp': 4.601906, 'mf': 4.7265, 'f': 4.721146, 'ff': 4.68384, 'fff': 4.68835, 'ffff': 4.69196},
    'F7': {'pppp': 3.628186, 'ppp': 3.809693, 'pp': 4.0494, 'p': 4.476701, 'mp': 4.807679, 'mf': 4.94, 'f': 4.932339, 'ff': 4.87904, 'fff': 4.876193, 'ffff': 4.873916},
    'F#7': {'pppp': 3.559574, 'ppp': 3.741985, 'pp': 3.9832, 'p': 4.415764, 'mp': 4.749257, 'mf': 4.8821, 'f': 4.872479, 'ff': 4.805663, 'fff': 4.795383, 'ffff': 4.787176},
    'G7': {'pppp': 3.25526, 'ppp': 3.425877, 'pp': 3.651778, 'p': 4.059465, 'mp': 4.372415, 'mf': 4.496646, 'f': 4.485913, 'ff': 4.411499, 'fff': 4.395465, 'ffff': 4.382681},
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
