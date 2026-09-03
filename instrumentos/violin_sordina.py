# instrumentos/violin_sordina.py
"""
Violin (arco con sordino) instrument density module.

The ``spectral_data`` table stores a committed 10-dynamic Combined Density
Metric (CDM) ladder from the ``Results`` sheet of
``Violin_Zenodo_collections_con_sordino_Dynamics10.xlsx``
(measured pp/mf/ff anchors; remaining levels committed from that workbook —
no runtime dynamic extrapolation).

Runtime analysis does not ingest audio; it maps notated pitch + dynamic to
these pre-loaded acoustic metadata tables.
"""

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="external_acoustic_metadata",
    citation=(
        "Violin arco_sordina CDM ladder: measured pp/mf/ff anchors with "
        "committed Results sheet values for all 10 dynamic levels from "
        "Violin_Zenodo_collections_con_sordino_Dynamics10.xlsx "
        "(dest Zenodo Violin_con sordino Media (IOWA+Orchidea average); Dynamics_predicter Results ladder)."
    ),
    source_url_or_identifier='docs/instrument_acoustic_sources.md#violin-sordina',
    extraction_method=(
        "Committed full dynamic ladder from Dynamics extrapolator v1.5.2.1 Results sheet "
        "(PCHIP interiors, tapered outers r=0.80) on measured pp/mf/ff anchors; "
        "interior cells clamped into their measured segment where the workbook "
        "marginally overshoots; pitch lookup via MIDI-space spectral_lookup"
    ),
    dynamic_levels=('pppp', 'ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', 'ffff'),
    pitch_range=(55, 96),
    uncertainty="high",
    version="2026-09-03",
    source_technique="arco_sordina",
    table_supported_techniques=("arco_sordina",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("violin_sordina")

# Full 10-dynamic CDM ladder (Results sheet). Anchors pp/mf/ff match measured
# workbook midpoints; other levels are workbook-committed.
spectral_data = {
    'G3': {'pppp': 31.325172, 'ppp': 32.313734, 'pp': 33.593421, 'p': 36.011482, 'mp': 37.349774, 'mf': 37.747128, 'f': 36.833177, 'ff': 34.589008, 'fff': 33.368839, 'ffff': 32.423768},
    'G#3': {'pppp': 16.521266, 'ppp': 17.260161, 'pp': 18.230423, 'p': 20.213623, 'mp': 21.296109, 'mf': 21.60547, 'f': 20.746488, 'ff': 18.740673, 'fff': 17.609372, 'ffff': 16.753704},
    'A3': {'pppp': 27.95906, 'ppp': 28.947625, 'pp': 30.232629, 'p': 31.431971, 'mp': 32.863439, 'mf': 34.510125, 'f': 36.457526, 'ff': 38.769367, 'fff': 40.851247, 'ffff': 42.59696},
    'A#3': {'pppp': 26.63152, 'ppp': 27.466032, 'pp': 28.54604, 'p': 29.038915, 'mp': 30.309367, 'mf': 32.046058, 'f': 34.903889, 'ff': 39.394191, 'fff': 43.256825, 'ffff': 46.617889},
    'B3': {'pppp': 29.306773, 'ppp': 29.372255, 'pp': 29.454313, 'p': 28.951183, 'mp': 28.697135, 'mf': 28.626164, 'f': 28.814147, 'ff': 29.294089, 'fff': 29.631482, 'ffff': 29.904192},
    'C4': {'pppp': 22.403493, 'ppp': 23.265261, 'pp': 24.389235, 'p': 25.769129, 'mp': 27.053865, 'mf': 28.212951, 'f': 29.237222, 'ff': 30.113106, 'fff': 31.01849, 'ffff': 31.762358},
    'C#4': {'pppp': 19.267052, 'ppp': 19.468965, 'pp': 19.724334, 'p': 19.764481, 'mp': 19.874022, 'mf': 20.036878, 'f': 20.449404, 'ff': 21.149092, 'fff': 21.648388, 'ffff': 22.056298},
    'D4': {'pppp': 21.016914, 'ppp': 20.690131, 'pp': 20.288789, 'p': 19.158658, 'mp': 18.758353, 'mf': 18.701854, 'f': 19.919297, 'ff': 22.897467, 'fff': 25.075657, 'ffff': 26.966478},
    'D#4': {'pppp': 21.005457, 'ppp': 21.34047, 'pp': 21.76676, 'p': 21.917267, 'mp': 22.301496, 'mf': 22.818714, 'f': 23.671635, 'ff': 24.956866, 'fff': 25.946078, 'ffff': 26.765605},
    'E4': {'pppp': 18.568446, 'ppp': 18.932175, 'pp': 19.396872, 'p': 19.881645, 'mp': 20.290743, 'mf': 20.602488, 'f': 20.833786, 'ff': 20.989567, 'fff': 21.194846, 'ffff': 21.360514},
    'F4': {'pppp': 15.27095, 'ppp': 16.141374, 'pp': 17.299499, 'p': 19.243329, 'mp': 20.826761, 'mf': 21.592629, 'f': 21.76002, 'ff': 21.825341, 'fff': 21.95944, 'ffff': 22.067313},
    'F#4': {'pppp': 17.291769, 'ppp': 17.528974, 'pp': 17.830063, 'p': 17.920301, 'mp': 18.16155, 'mf': 18.510629, 'f': 19.270332, 'ff': 20.534771, 'fff': 21.476465, 'ffff': 22.260819},
    'G4': {'pppp': 15.694943, 'ppp': 16.674038, 'pp': 17.984239, 'p': 19.993262, 'mp': 21.722215, 'mf': 22.889298, 'f': 23.624266, 'ff': 23.966451, 'fff': 24.491013, 'ffff': 24.918918},
    'G#4': {'pppp': 16.035915, 'ppp': 16.283356, 'pp': 16.598034, 'p': 16.825162, 'mp': 17.042231, 'mf': 17.249361, 'f': 17.445358, 'ff': 17.629513, 'fff': 17.824094, 'ffff': 17.981304},
    'A4': {'pppp': 16.473133, 'ppp': 16.783312, 'pp': 17.179263, 'p': 17.335726, 'mp': 17.734042, 'mf': 18.267595, 'f': 19.12455, 'ff': 20.412463, 'fff': 21.429054, 'ffff': 22.278661},
    'A#4': {'pppp': 15.551897, 'ppp': 16.291651, 'pp': 17.266021, 'p': 18.949366, 'mp': 20.242035, 'mf': 20.756118, 'f': 20.723811, 'ff': 20.499066, 'fff': 20.423232, 'ffff': 20.362767},
    'B4': {'pppp': 20.872332, 'ppp': 21.756773, 'pp': 22.915212, 'p': 24.264973, 'mp': 25.603723, 'mf': 26.924713, 'f': 28.213027, 'ff': 29.455927, 'fff': 30.680437, 'ffff': 31.696596},
    'C5': {'pppp': 16.395688, 'ppp': 16.620295, 'pp': 16.905386, 'p': 17.0283, 'mp': 17.215107, 'mf': 17.444265, 'f': 17.748404, 'ff': 18.142574, 'fff': 18.466109, 'ffff': 18.729086},
    'C#5': {'pppp': 11.319599, 'ppp': 12.300563, 'pp': 13.647164, 'p': 15.945047, 'mp': 17.927433, 'mf': 19.032689, 'f': 19.436665, 'ff': 19.60423, 'fff': 19.889513, 'ffff': 20.120725},
    'D5': {'pppp': 11.506337, 'ppp': 12.023237, 'pp': 12.702138, 'p': 13.090956, 'mp': 13.916577, 'mf': 15.044826, 'f': 16.846467, 'ff': 19.666478, 'fff': 22.253934, 'ffff': 24.566935},
    'D#5': {'pppp': 10.996688, 'ppp': 11.889317, 'pp': 13.107675, 'p': 15.322242, 'mp': 17.166627, 'mf': 17.937872, 'f': 17.930957, 'ff': 17.882626, 'fff': 17.879343, 'ffff': 17.876717},
    'E5': {'pppp': 16.166384, 'ppp': 17.153924, 'pp': 18.473609, 'p': 19.925355, 'mp': 21.535855, 'mf': 23.318222, 'f': 25.302695, 'ff': 27.519035, 'fff': 29.702589, 'ffff': 31.573534},
    'F5': {'pppp': 14.360094, 'ppp': 15.137947, 'pp': 16.169781, 'p': 17.886422, 'mp': 19.279744, 'mf': 19.958999, 'f': 20.116621, 'ff': 20.178432, 'fff': 20.304768, 'ffff': 20.406406},
    'F#5': {'pppp': 18.671809, 'ppp': 18.75762, 'pp': 18.865439, 'p': 18.866543, 'mp': 18.87008, 'mf': 18.876386, 'f': 20.134038, 'ff': 23.011546, 'fff': 25.088476, 'ffff': 26.884197},
    'G5': {'pppp': 15.137418, 'ppp': 15.765254, 'pp': 16.586794, 'p': 18.048374, 'mp': 19.060938, 'mf': 19.433979, 'f': 19.261326, 'ff': 18.602898, 'fff': 18.286658, 'ffff': 18.03754},
    'G#5': {'pppp': 11.848067, 'ppp': 12.256973, 'pp': 12.788007, 'p': 13.32135, 'mp': 13.908087, 'mf': 14.547974, 'f': 15.253077, 'ff': 16.032624, 'fff': 16.747402, 'ffff': 17.342101},
    'A5': {'pppp': 15.633146, 'ppp': 16.03904, 'pp': 16.561259, 'p': 17.670356, 'mp': 18.10851, 'mf': 18.177469, 'f': 17.425381, 'ff': 15.809592, 'fff': 14.900792, 'ffff': 14.211512},
    'A#5': {'pppp': 13.490786, 'ppp': 13.818415, 'pp': 14.239162, 'p': 14.411184, 'mp': 14.869039, 'mf': 15.52889, 'f': 16.872097, 'ff': 19.159958, 'fff': 21.061155, 'ffff': 22.71707},
    'B5': {'pppp': 17.587587, 'ppp': 17.699263, 'pp': 17.839854, 'p': 17.913146, 'mp': 17.940224, 'mf': 17.944096, 'f': 17.070037, 'ff': 15.379156, 'fff': 14.443352, 'ffff': 13.735877},
    'C6': {'pppp': 13.470029, 'ppp': 13.808079, 'pp': 14.242596, 'p': 14.828674, 'mp': 15.288025, 'mf': 15.535706, 'f': 15.633113, 'ff': 15.673708, 'fff': 15.765321, 'ffff': 15.838996},
    'C#6': {'pppp': 16.63445, 'ppp': 16.529789, 'pp': 16.399889, 'p': 15.846532, 'mp': 15.530288, 'mf': 15.428319, 'f': 15.548371, 'ff': 15.899983, 'fff': 16.128114, 'ffff': 16.312974},
    'D6': {'pppp': 13.300827, 'ppp': 13.869033, 'pp': 14.613544, 'p': 16.361181, 'mp': 17.056466, 'mf': 17.158176, 'f': 15.698255, 'ff': 12.837808, 'fff': 11.248284, 'ffff': 10.119582},
    'D#6': {'pppp': 14.816167, 'ppp': 14.983365, 'pp': 15.195017, 'p': 15.401049, 'mp': 15.477657, 'mf': 15.488632, 'f': 15.262122, 'ff': 14.773179, 'fff': 14.547427, 'ffff': 14.369312},
    'E6': {'pppp': 15.456323, 'ppp': 15.760133, 'pp': 16.148306, 'p': 16.699312, 'mp': 17.045996, 'mf': 17.165315, 'f': 17.064961, 'ff': 16.753131, 'fff': 16.634733, 'ffff': 16.540617},
    'F6': {'pppp': 12.341977, 'ppp': 12.085112, 'pp': 11.771534, 'p': 10.989697, 'mp': 10.636565, 'mf': 10.548769, 'f': 10.882944, 'ff': 11.74256, 'fff': 12.317757, 'ffff': 12.798137},
    'F#6': {'pppp': 10.063013, 'ppp': 10.565057, 'pp': 11.227979, 'p': 12.717626, 'mp': 13.411724, 'mf': 13.562314, 'f': 12.65974, 'ff': 10.761989, 'fff': 9.692894, 'ffff': 8.914608},
    'G6': {'pppp': 12.072426, 'ppp': 12.331522, 'pp': 12.663226, 'p': 13.340279, 'mp': 13.598745, 'mf': 13.636075, 'f': 13.014616, 'ff': 11.723575, 'fff': 10.9969, 'ffff': 10.448128},
    'G#6': {'pppp': 9.143643, 'ppp': 9.659928, 'pp': 10.346469, 'p': 11.801459, 'mp': 12.600303, 'mf': 12.826046, 'f': 12.155792, 'ff': 10.636575, 'fff': 9.777763, 'ffff': 9.140914},
    'A6': {'pppp': 9.412582, 'ppp': 9.737876, 'pp': 10.160347, 'p': 11.088519, 'mp': 11.483478, 'mf': 11.556954, 'f': 10.960588, 'ff': 9.689645, 'fff': 8.969249, 'ffff': 8.431691},
    'A#6': {'pppp': 8.812722, 'ppp': 8.83969, 'pp': 8.873515, 'p': 8.739671, 'mp': 8.64537, 'mf': 8.609648, 'f': 8.611396, 'ff': 8.623636, 'fff': 8.656236, 'ffff': 8.682405},
    'B6': {'pppp': 7.265242, 'ppp': 7.509703, 'pp': 7.826878, 'p': 8.183091, 'mp': 8.532269, 'mf': 8.873093, 'f': 9.20218, 'ff': 9.516802, 'fff': 9.821967, 'ffff': 10.073129},
    'C7': {'pppp': 7.85046, 'ppp': 8.152533, 'pp': 8.546523, 'p': 9.43134, 'mp': 9.806438, 'mf': 9.874407, 'f': 9.29376, 'ff': 8.074113, 'fff': 7.383315, 'ffff': 6.873479},
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
