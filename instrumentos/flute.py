# instrumentos/flute.py
"""
Flute instrument density module.

The ``spectral_data`` table stores a committed 10-dynamic Combined Density
Metric (CDM) ladder from the Dynamics_predicter ``Results`` sheet
(IOWA + ORCH ordinary sustain anchors at pp/mf/ff; remaining levels
committed from that workbook — no runtime dynamic extrapolation).

Runtime analysis does not ingest audio; it maps notated pitch + dynamic to
these pre-loaded acoustic metadata tables.
"""

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="external_acoustic_metadata",
    citation=(
        "Flute CDM ladder: IOWA+ORCH measured pp/mf/ff anchors with "
        "committed Dynamics_predicter Results sheet values for all 10 "
        "dynamic levels (not re-extrapolated at runtime)."
    ),
    source_url_or_identifier='docs/instrument_acoustic_sources.md#flute',
    extraction_method=(
        "monotone log-CDM ladder enforcement (2026-08-03): pp/mf/ff anchors isotonic-clamped then full DYNAMIC_LEVELS rebuilt via offline internal_default log-linear + adaptive tails; Committed full dynamic ladder from Flute_iowa_orchidea_dynamics.xlsx / sheet 'Results'; "
        "pitch lookup via MIDI-space spectral_lookup"
    ),
    dynamic_levels=('pppp', 'ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', 'ffff'),
    pitch_range=(59, 98),
    uncertainty="medium",
    version="2026-08-03",
    source_technique="ordinary_sustain",
    table_supported_techniques=("ordinary_sustain",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("flute")

# Full 10-dynamic CDM ladder (Results sheet). Anchors pp/mf/ff match measured
# IOWA+ORCH midpoints; other levels are workbook-committed.
spectral_data = {
    'B3': {'pppp': 7.0926961, 'ppp': 7.6417211, 'pp': 8.870556, 'p': 13.8748985, 'mp': 17.3527897, 'mf': 21.7024513, 'f': 24.238714, 'ff': 27.0713776, 'fff': 28.6095316, 'ffff': 29.4110781},
    'C4': {'pppp': 10.5126727, 'ppp': 11.1655485, 'pp': 12.5954564, 'p': 18.0807084, 'mp': 21.6628808, 'mf': 25.9547576, 'f': 25.9547576, 'ff': 25.9547576, 'fff': 25.9547576, 'ffff': 25.9547576},
    'C#4': {'pppp': 15.3109348, 'ppp': 15.6136328, 'pp': 16.2371002, 'p': 18.2608925, 'mp': 19.3655022, 'mf': 20.5369303, 'f': 21.5370118, 'ff': 22.585794, 'fff': 23.1291845, 'ffff': 23.4057628},
    'D4': {'pppp': 12.9571092, 'ppp': 13.3570534, 'pp': 14.1943578, 'p': 17.0345635, 'mp': 18.6611601, 'mf': 20.4430772, 'f': 21.2802936, 'ff': 22.151797, 'fff': 22.6008429, 'ffff': 22.8287679},
    'D#4': {'pppp': 10.7234054, 'ppp': 11.1229277, 'pp': 11.9671819, 'p': 14.9042534, 'mp': 16.6329543, 'mf': 18.5621621, 'f': 19.9964624, 'ff': 21.5415912, 'fff': 22.3583672, 'ffff': 22.7782963},
    'E4': {'pppp': 12.1295904, 'ppp': 12.3763162, 'pp': 12.8849257, 'p': 14.5396344, 'mp': 15.4450483, 'mf': 16.4068442, 'f': 18.3309816, 'ff': 20.4807752, 'fff': 21.6484459, 'ffff': 22.2570136},
    'F4': {'pppp': 13.8031474, 'ppp': 14.0440609, 'pp': 14.5385755, 'p': 16.1290696, 'mp': 16.9884222, 'mf': 17.8935609, 'f': 18.8420035, 'ff': 19.840718, 'fff': 20.3597545, 'ffff': 20.6243425},
    'F#4': {'pppp': 14.0499249, 'ppp': 14.2126142, 'pp': 14.5436662, 'p': 15.5838116, 'mp': 16.1314566, 'mf': 16.6983469, 'f': 18.0902258, 'ff': 19.5981238, 'fff': 20.3985713, 'ffff': 20.8109726},
    'G4': {'pppp': 13.8441732, 'ppp': 13.9625534, 'pp': 14.202359, 'p': 14.9467719, 'mp': 15.3334849, 'mf': 15.7302031, 'f': 16.9565212, 'ff': 18.2784425, 'fff': 18.9775612, 'ffff': 19.3370851},
    'G#4': {'pppp': 9.4832329, 'ppp': 9.8569566, 'pp': 10.6491685, 'p': 13.428709, 'mp': 15.0797293, 'mf': 16.9337377, 'f': 17.8926403, 'ff': 18.9058424, 'fff': 19.43376, 'ffff': 19.7032213},
    'A4': {'pppp': 10.9719481, 'ppp': 11.2151169, 'pp': 11.7177416, 'p': 13.3648552, 'mp': 14.2733011, 'mf': 15.2434966, 'f': 15.2434966, 'ff': 15.2434966, 'fff': 15.2434966, 'ffff': 15.2434966},
    'A#4': {'pppp': 8.4133228, 'ppp': 8.6309743, 'pp': 9.083315, 'p': 10.5876121, 'mp': 11.4307532, 'mf': 12.3410375, 'f': 12.6847129, 'ff': 13.037959, 'fff': 13.2182541, 'ffff': 13.3093344},
    'B4': {'pppp': 8.6432452, 'ppp': 8.8689922, 'pp': 9.3383285, 'p': 10.9006846, 'mp': 11.7773094, 'mf': 12.7244318, 'f': 13.0688621, 'ff': 13.4226155, 'fff': 13.603067, 'ffff': 13.6942005},
    'C5': {'pppp': 7.05033, 'ppp': 7.2490541, 'pp': 7.6634643, 'p': 9.0543343, 'mp': 9.8417475, 'mf': 10.6976384, 'f': 10.9504445, 'ff': 11.209225, 'fff': 11.3408996, 'ffff': 11.4073158},
    'C#5': {'pppp': 7.0996515, 'ppp': 7.2238962, 'pp': 7.4789465, 'p': 8.29941, 'mp': 8.7428015, 'mf': 9.2098809, 'f': 9.7285324, 'ff': 10.2763916, 'fff': 10.5617845, 'ffff': 10.7074396},
    'D5': {'pppp': 5.6017592, 'ppp': 5.7748537, 'pp': 6.1372538, 'p': 7.3667067, 'mp': 8.0709197, 'mf': 8.8424512, 'f': 8.8424512, 'ff': 8.8424512, 'fff': 8.8424512, 'ffff': 8.8424512},
    'D#5': {'pppp': 6.1300298, 'ppp': 6.2356546, 'pp': 6.4523956, 'p': 7.1488765, 'mp': 7.5248215, 'mf': 7.9205366, 'f': 7.9205366, 'ff': 7.9205366, 'fff': 7.9205366, 'ffff': 7.9205366},
    'E5': {'pppp': 6.4314365, 'ppp': 6.4872949, 'pp': 6.6004713, 'p': 6.9519855, 'mp': 7.1347017, 'mf': 7.32222, 'f': 8.0270332, 'ff': 8.7996895, 'fff': 9.2134756, 'ffff': 9.4276089},
    'F5': {'pppp': 5.3737656, 'ppp': 5.5054267, 'pp': 5.7785052, 'p': 6.6817324, 'mp': 7.1849849, 'mf': 7.7261413, 'f': 9.2077384, 'ff': 10.9734527, 'fff': 11.9794936, 'ffff': 12.5165904},
    'F#5': {'pppp': 5.044374, 'ppp': 5.2163585, 'pp': 5.5781185, 'p': 6.8210094, 'mp': 7.5427395, 'mf': 8.3408357, 'f': 9.6731002, 'ff': 11.2181646, 'fff': 12.0809161, 'ffff': 12.5368636},
    'G5': {'pppp': 5.6606684, 'ppp': 5.9332005, 'pp': 6.5182595, 'p': 8.6429002, 'mp': 9.9522992, 'mf': 11.4600721, 'f': 11.4600721, 'ff': 11.4600721, 'fff': 11.4600721, 'ffff': 11.4600721},
    'G#5': {'pppp': 4.7471533, 'ppp': 4.9462583, 'pp': 5.369871, 'p': 6.8710806, 'mp': 7.7724088, 'mf': 8.7919707, 'f': 8.9217045, 'ff': 9.0533527, 'fff': 9.1199035, 'ffff': 9.1533621},
    'A5': {'pppp': 3.68701, 'ppp': 3.8618625, 'pp': 4.2368373, 'p': 5.5946989, 'mp': 6.4290113, 'mf': 7.3877409, 'f': 7.3877409, 'ff': 7.3877409, 'fff': 7.3877409, 'ffff': 7.3877409},
    'A#5': {'pppp': 3.7341646, 'ppp': 3.8401713, 'pp': 4.0612982, 'p': 4.8040523, 'mp': 5.224914, 'mf': 5.6826455, 'f': 5.8194611, 'ff': 5.9595706, 'fff': 6.0308853, 'ffff': 6.0668621},
    'B5': {'pppp': 2.4086211, 'ppp': 2.5544562, 'pp': 2.8731509, 'p': 4.0882584, 'mp': 4.8767252, 'mf': 5.8172568, 'f': 5.9250231, 'ff': 6.0347858, 'fff': 6.0904274, 'ffff': 6.1184402},
    'C6': {'pppp': 5.5582074, 'ppp': 5.5584217, 'pp': 5.5588502, 'p': 5.560136, 'mp': 5.560779, 'mf': 5.5614221, 'f': 5.5614221, 'ff': 5.5614221, 'fff': 5.5614221, 'ffff': 5.5614221},
    'C#6': {'pppp': 4.3889115, 'ppp': 4.3980417, 'pp': 4.416359, 'p': 4.4717702, 'mp': 4.499736, 'mf': 4.5278766, 'f': 4.9273519, 'ff': 5.3620712, 'fff': 5.5936087, 'ffff': 5.7131},
    'D6': {'pppp': 3.5565059, 'ppp': 3.6378017, 'pp': 3.8060108, 'p': 4.3587602, 'mp': 4.6645468, 'mf': 4.9917858, 'f': 5.0690991, 'ff': 5.1476099, 'fff': 5.1873201, 'ffff': 5.2072899},
    'D#6': {'pppp': 3.8151629, 'ppp': 3.8830061, 'pp': 4.0223332, 'p': 4.4710339, 'mp': 4.7138193, 'mf': 4.9697883, 'f': 5.6022007, 'ff': 6.3150885, 'fff': 6.7048618, 'ffff': 6.9086791},
    'E6': {'pppp': 3.1323983, 'ppp': 3.2207979, 'pp': 3.4051516, 'p': 4.0239761, 'mp': 4.3743634, 'mf': 4.7552607, 'f': 4.7552607, 'ff': 4.7552607, 'fff': 4.7552607, 'ffff': 4.7552607},
    'F6': {'pppp': 3.317954, 'ppp': 3.317954, 'pp': 3.317954, 'p': 3.317954, 'mp': 3.317954, 'mf': 3.317954, 'f': 3.317954, 'ff': 3.317954, 'fff': 3.317954, 'ffff': 3.317954},
    'F#6': {'pppp': 2.3626637, 'ppp': 2.41925, 'pp': 2.5365206, 'p': 2.9235556, 'mp': 3.1386858, 'mf': 3.3696464, 'f': 3.4356685, 'ff': 3.5029842, 'fff': 3.5371351, 'ffff': 3.5543352},
    'G6': {'pppp': 2.0198289, 'ppp': 2.1614, 'pp': 2.4750061, 'p': 3.716205, 'mp': 4.5536679, 'mf': 5.5798567, 'f': 5.5798567, 'ff': 5.5798567, 'fff': 5.5798567, 'ffff': 5.5798567},
    'G#6': {'pppp': 3.1171868, 'ppp': 3.1171868, 'pp': 3.1171868, 'p': 3.1171868, 'mp': 3.1171868, 'mf': 3.1171868, 'f': 3.3030092, 'ff': 3.4999088, 'fff': 3.6027175, 'ffff': 3.6552488},
    'A6': {'pppp': 1.6212951, 'ppp': 1.7124719, 'pp': 1.9104962, 'p': 2.6528605, 'mp': 3.1260688, 'mf': 3.6836863, 'f': 3.6836863, 'ff': 3.6836863, 'fff': 3.6836863, 'ffff': 3.6836863},
    'A#6': {'pppp': 3.0970668, 'ppp': 3.1745882, 'pp': 3.3355007, 'p': 3.8688507, 'mp': 4.1667019, 'mf': 4.4874838, 'f': 4.4874838, 'ff': 4.4874838, 'fff': 4.4874838, 'ffff': 4.4874838},
    'B6': {'pppp': 2.1143495, 'ppp': 2.1889419, 'pp': 2.3461141, 'p': 2.8886426, 'mp': 3.2052813, 'mf': 3.5566284, 'f': 3.5566284, 'ff': 3.5566284, 'fff': 3.5566284, 'ffff': 3.5566284},
    'C7': {'pppp': 2.9601746, 'ppp': 2.9729093, 'pp': 2.9985434, 'p': 3.0767796, 'mp': 3.1166598, 'mf': 3.157057, 'f': 3.6789128, 'ff': 4.2870305, 'fff': 4.6278056, 'ffff': 4.8082206},
    'C#7': {'pppp': 3.81881, 'ppp': 3.81881, 'pp': 3.81881, 'p': 3.81881, 'mp': 3.81881, 'mf': 3.81881, 'f': 3.9452245, 'ff': 4.0758238, 'fff': 4.1427358, 'ffff': 4.1766026},
    'D7': {'pppp': 3.8496842, 'ppp': 3.8496842, 'pp': 3.8496842, 'p': 3.8496842, 'mp': 3.8496842, 'mf': 3.8496842, 'f': 3.8616561, 'ff': 3.8736653, 'fff': 3.8796838, 'ffff': 3.8826966},
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
