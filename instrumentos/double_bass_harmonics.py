# instrumentos/double_bass_harmonics.py
"""
Double bass (arco harmonics) instrument density module.

The ``spectral_data`` table stores a committed 10-dynamic Combined Density
Metric (CDM) ladder from the ``Results`` sheet of
``Double_bass_Zenodo_collections_harmonics_Dynamics10.xlsx``
(measured pp/mf/ff anchors; remaining levels committed from that workbook —
no runtime dynamic extrapolation).

Runtime analysis does not ingest audio; it maps notated pitch + dynamic to
these pre-loaded acoustic metadata tables.
"""

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="external_acoustic_metadata",
    citation=(
        "Double bass arco_harmonic CDM ladder: measured pp/mf/ff anchors with "
        "committed Results sheet values for all 10 dynamic levels from "
        "Double_bass_Zenodo_collections_harmonics_Dynamics10.xlsx "
        "(dest Zenodo DoubleBass_harmonics Media (IOWA+Orchidea average); Dynamics_predicter Results ladder)."
    ),
    source_url_or_identifier='docs/instrument_acoustic_sources.md#double-bass-harmonics',
    extraction_method=(
        "Committed full dynamic ladder from Dynamics extrapolator v1.5.2.1 Results sheet "
        "(PCHIP interiors, tapered outers r=0.80) on measured pp/mf/ff anchors; "
        "interior cells clamped into their measured segment where the workbook "
        "marginally overshoots; pitch lookup via MIDI-space spectral_lookup"
    ),
    dynamic_levels=('pppp', 'ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', 'ffff'),
    pitch_range=(52, 91),
    uncertainty="high",
    version="2026-09-03",
    source_technique="arco_harmonic",
    table_supported_techniques=("arco_harmonic",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("double_bass_harmonics")

# Full 10-dynamic CDM ladder (Results sheet). Anchors pp/mf/ff match measured
# workbook midpoints; other levels are workbook-committed.
spectral_data = {
    'E3': {'pppp': 29.703849, 'ppp': 29.043306, 'pp': 28.238245, 'p': 27.287892, 'mp': 26.47037, 'mf': 25.779643, 'f': 25.20179, 'ff': 24.728162, 'fff': 24.699601, 'ffff': 24.676775},
    'F3': {'pppp': 23.538934, 'ppp': 23.178492, 'pp': 22.735691, 'p': 21.993166, 'mp': 21.589836, 'mf': 21.466235, 'f': 21.67148, 'ff': 22.234689, 'fff': 22.92748, 'ffff': 23.497224},
    'F#3': {'pppp': 14.553701, 'ppp': 15.20499, 'pp': 16.060239, 'p': 18.02483, 'mp': 19.214676, 'mf': 19.596889, 'f': 18.943722, 'ff': 17.299123, 'fff': 16.550955, 'ffff': 15.975786},
    'G3': {'pppp': 13.027257, 'ppp': 13.78191, 'pp': 14.786997, 'p': 17.034401, 'mp': 18.472247, 'mf': 18.95584, 'f': 18.28294, 'ff': 16.534143, 'fff': 15.706326, 'ffff': 15.074016},
    'G#3': {'pppp': 12.645907, 'ppp': 13.192098, 'pp': 13.90813, 'p': 15.788694, 'mp': 16.595678, 'mf': 16.740075, 'f': 15.472408, 'ff': 12.890595, 'fff': 11.565596, 'ffff': 10.60435},
    'A3': {'pppp': 13.100775, 'ppp': 13.380775, 'pp': 13.739204, 'p': 14.747143, 'mp': 15.182327, 'mf': 15.268123, 'f': 14.648844, 'ff': 13.297058, 'fff': 12.691072, 'ffff': 12.226228},
    'A#3': {'pppp': 12.346647, 'ppp': 12.957568, 'pp': 13.763901, 'p': 15.606256, 'mp': 16.72758, 'mf': 17.087954, 'f': 16.462288, 'ff': 14.900763, 'fff': 14.166737, 'ffff': 13.605637},
    'B3': {'pppp': 17.824807, 'ppp': 17.917266, 'pp': 18.033515, 'p': 18.271576, 'mp': 18.551245, 'mf': 18.865148, 'f': 19.226954, 'ff': 19.643582, 'fff': 20.302387, 'ffff': 20.845305},
    'C4': {'pppp': 20.991612, 'ppp': 21.320601, 'pp': 21.739098, 'p': 22.097753, 'mp': 22.761708, 'mf': 23.623452, 'f': 24.88582, 'ff': 26.678536, 'fff': 28.406836, 'ffff': 29.869749},
    'C#4': {'pppp': 18.904374, 'ppp': 19.44414, 'pp': 20.14057, 'p': 21.698203, 'mp': 22.845217, 'mf': 23.28893, 'f': 23.236366, 'ff': 22.871727, 'fff': 23.025478, 'ffff': 23.149222},
    'D4': {'pppp': 17.577398, 'ppp': 17.664342, 'pp': 17.773626, 'p': 18.009188, 'mp': 18.279167, 'mf': 18.578098, 'f': 18.916351, 'ff': 19.29918, 'fff': 19.93163, 'ffff': 20.452481},
    'D#4': {'pppp': 24.100074, 'ppp': 23.341627, 'pp': 22.427046, 'p': 20.530711, 'mp': 19.822847, 'mf': 19.699044, 'f': 20.794568, 'ff': 23.580041, 'fff': 25.73464, 'ffff': 27.599228},
    'E4': {'pppp': 15.793117, 'ppp': 16.009222, 'pp': 16.283517, 'p': 16.889694, 'mp': 17.384884, 'mf': 17.717143, 'f': 17.930196, 'ff': 18.038744, 'fff': 18.470879, 'ffff': 18.824028},
    'F4': {'pppp': 15.92041, 'ppp': 16.076531, 'pp': 16.273838, 'p': 16.547036, 'mp': 16.904756, 'mf': 17.327855, 'f': 17.853259, 'ff': 18.501509, 'fff': 19.27966, 'ffff': 19.92568},
    'F#4': {'pppp': 25.272174, 'ppp': 24.405651, 'pp': 23.364159, 'p': 21.210467, 'mp': 20.415428, 'mf': 20.27853, 'f': 21.525157, 'ff': 24.721125, 'fff': 27.198701, 'ffff': 29.358381},
    'G4': {'pppp': 10.767833, 'ppp': 11.075343, 'pp': 11.472109, 'p': 12.216238, 'mp': 12.835278, 'mf': 13.249165, 'f': 13.510994, 'ff': 13.63808, 'fff': 13.988311, 'ffff': 14.274961},
    'G#4': {'pppp': 13.082276, 'ppp': 13.206957, 'pp': 13.36448, 'p': 13.468333, 'mp': 13.743426, 'mf': 14.136413, 'f': 14.932308, 'ff': 16.247333, 'fff': 17.425882, 'ffff': 18.429983},
    'A4': {'pppp': 17.623099, 'ppp': 17.786245, 'pp': 17.992302, 'p': 18.125062, 'mp': 18.480972, 'mf': 18.998668, 'f': 20.130294, 'ff': 22.052222, 'fff': 23.748136, 'ffff': 25.198301},
    'A#4': {'pppp': 15.963507, 'ppp': 16.068131, 'pp': 16.199875, 'p': 16.409654, 'mp': 16.691209, 'mf': 17.026102, 'f': 17.44645, 'ff': 17.968866, 'fff': 18.653688, 'ffff': 19.220289},
    'B4': {'pppp': 20.644138, 'ppp': 20.524774, 'pp': 20.376538, 'p': 20.168021, 'mp': 20.091738, 'mf': 20.080864, 'f': 21.60595, 'ff': 25.191374, 'fff': 28.02952, 'ffff': 30.528587},
    'C5': {'pppp': 12.980805, 'ppp': 12.947825, 'pp': 12.906716, 'p': 12.907121, 'mp': 12.90842, 'mf': 12.910739, 'f': 13.895453, 'ff': 16.183903, 'fff': 17.997226, 'ffff': 19.593111},
    'C#5': {'pppp': 17.295697, 'ppp': 16.870434, 'pp': 16.353529, 'p': 15.26208, 'mp': 14.878594, 'mf': 14.824603, 'f': 16.166087, 'ff': 19.548558, 'fff': 22.265843, 'ffff': 24.709199},
    'D5': {'pppp': 16.721287, 'ppp': 16.50715, 'pp': 16.24333, 'p': 15.721313, 'mp': 15.533248, 'mf': 15.506566, 'f': 16.651513, 'ff': 19.39891, 'fff': 21.567702, 'ffff': 23.476054},
    'D#5': {'pppp': 17.576334, 'ppp': 16.900336, 'pp': 16.091783, 'p': 14.407243, 'mp': 13.832098, 'mf': 13.751831, 'f': 15.240033, 'ff': 19.172059, 'fff': 22.419505, 'ffff': 25.40925},
    'E5': {'pppp': 17.21025, 'ppp': 16.612194, 'pp': 15.893764, 'p': 14.386966, 'mp': 13.868587, 'mf': 13.796074, 'f': 15.200463, 'ff': 18.862652, 'fff': 21.855632, 'ffff': 24.58849},
    'F5': {'pppp': 17.641089, 'ppp': 16.72416, 'pp': 15.644725, 'p': 13.457752, 'mp': 12.731496, 'mf': 12.630996, 'f': 14.188961, 'ff': 18.466879, 'fff': 22.095445, 'ffff': 25.505283},
    'F#5': {'pppp': 16.910887, 'ppp': 16.194183, 'pp': 15.340866, 'p': 13.573933, 'mp': 12.975565, 'mf': 12.892265, 'f': 14.281799, 'ff': 17.982726, 'fff': 21.038411, 'ffff': 23.852772},
    'G5': {'pppp': 16.521559, 'ppp': 15.817425, 'pp': 14.979306, 'p': 13.243302, 'mp': 12.655736, 'mf': 12.573954, 'f': 13.895388, 'ff': 17.410193, 'fff': 20.299669, 'ffff': 22.952884},
    'G#5': {'pppp': 15.218045, 'ppp': 14.921202, 'pp': 14.558278, 'p': 13.79692, 'mp': 13.526569, 'mf': 13.488383, 'f': 14.435606, 'ff': 16.751459, 'fff': 18.571226, 'ffff': 20.168374},
    'A5': {'pppp': 15.77407, 'ppp': 14.996058, 'pp': 14.077281, 'p': 12.198407, 'mp': 11.571284, 'mf': 11.484367, 'f': 12.707525, 'ff': 16.010974, 'fff': 18.734403, 'ffff': 21.243082},
    'A#5': {'pppp': 15.266525, 'ppp': 14.472238, 'pp': 13.537239, 'p': 11.641239, 'mp': 11.00666, 'mf': 10.916384, 'f': 12.068275, 'ff': 15.195465, 'fff': 17.769826, 'ffff': 20.139955},
    'B5': {'pppp': 14.200579, 'ppp': 13.626112, 'pp': 12.940598, 'p': 11.506863, 'mp': 11.019666, 'mf': 10.951772, 'f': 11.881113, 'ff': 14.313849, 'fff': 16.251687, 'ffff': 17.989209},
    'C6': {'pppp': 12.965823, 'ppp': 12.661623, 'pp': 12.291389, 'p': 11.502442, 'mp': 11.22472, 'mf': 11.185596, 'f': 11.818088, 'ff': 13.377042, 'fff': 14.590899, 'ffff': 15.640823},
    'C#6': {'pppp': 12.64568, 'ppp': 12.167548, 'pp': 11.595225, 'p': 10.414459, 'mp': 9.987301, 'mf': 9.916399, 'f': 10.60743, 'ff': 12.397661, 'fff': 13.795379, 'ffff': 15.026185},
    'D6': {'pppp': 11.796703, 'ppp': 11.370446, 'pp': 10.85922, 'p': 9.819708, 'mp': 9.423542, 'mf': 9.34929, 'f': 9.919141, 'ff': 11.389644, 'fff': 12.527948, 'ffff': 13.519972},
    'D#6': {'pppp': 10.963839, 'ppp': 10.567348, 'pp': 10.091836, 'p': 9.147394, 'mp': 8.764601, 'mf': 8.683137, 'f': 9.152255, 'ff': 10.367778, 'fff': 11.303784, 'ffff': 12.113074},
    'E6': {'pppp': 9.715417, 'ppp': 9.529757, 'pp': 9.302663, 'p': 8.864517, 'mp': 8.670886, 'mf': 8.625202, 'f': 8.831222, 'ff': 9.347177, 'fff': 9.79211, 'ffff': 10.163257},
    'F6': {'pppp': 9.189547, 'ppp': 8.87741, 'pp': 8.502105, 'p': 7.793656, 'mp': 7.462707, 'mf': 7.375208, 'f': 7.640371, 'ff': 8.342733, 'fff': 8.887147, 'ffff': 9.348148},
    'F#6': {'pppp': 7.925911, 'ppp': 7.825167, 'pp': 7.701036, 'p': 7.538473, 'mp': 7.421208, 'mf': 7.37358, 'f': 7.36992, 'ff': 7.368565, 'fff': 7.521017, 'ffff': 7.645246},
    'G6': {'pppp': 7.488994, 'ppp': 7.369296, 'pp': 7.222361, 'p': 7.012532, 'mp': 6.861273, 'mf': 6.795791, 'f': 6.784981, 'ff': 6.780861, 'fff': 6.907065, 'ffff': 7.009718},
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
