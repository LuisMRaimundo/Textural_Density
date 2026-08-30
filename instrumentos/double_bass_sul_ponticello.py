# instrumentos/double_bass_sul_ponticello.py
"""
Double bass (arco sul ponticello) instrument density module.

The ``spectral_data`` table stores a committed 10-dynamic Combined Density
Metric (CDM) ladder from the ``Results`` sheet of
``DoubleBass_Dynamics10_sul_ponticello.xlsx``
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
        "DoubleBass_Dynamics10_sul_ponticello.xlsx "
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
    pitch_range=(28, 72),
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
    'E1': {'pppp': 46.638681, 'ppp': 47.41727, 'pp': 48.40881, 'p': 49.393835, 'mp': 50.480035, 'mf': 51.658048, 'f': 52.953173, 'ff': 54.380089, 'fff': 55.693073, 'ffff': 56.766248},
    'F1': {'pppp': 39.187704, 'ppp': 40.118467, 'pp': 41.313071, 'p': 42.973359, 'mp': 44.37161, 'mf': 45.403317, 'f': 46.139548, 'ff': 46.60058, 'fff': 47.199476, 'ffff': 47.68413},
    'F#1': {'pppp': 45.504775, 'ppp': 45.859103, 'pp': 46.305895, 'p': 46.468602, 'mp': 46.916863, 'mf': 47.593045, 'f': 49.411692, 'ff': 52.604243, 'fff': 55.053032, 'ffff': 57.093888},
    'G1': {'pppp': 46.995104, 'ppp': 48.332802, 'pp': 50.058597, 'p': 52.705184, 'mp': 54.828808, 'mf': 56.078399, 'f': 56.693476, 'ff': 56.960996, 'fff': 57.428672, 'ffff': 57.805576},
    'G#1': {'pppp': 32.405447, 'ppp': 32.70738, 'pp': 33.088755, 'p': 33.746679, 'mp': 34.101141, 'mf': 34.205976, 'f': 33.977128, 'ff': 33.392784, 'fff': 33.133829, 'ffff': 32.928111},
    'A1': {'pppp': 60.783875, 'ppp': 61.010605, 'pp': 61.295208, 'p': 61.31744, 'mp': 61.378985, 'mf': 61.472155, 'f': 61.73698, 'ff': 62.189363, 'fff': 62.643904, 'ffff': 63.009929},
    'A#1': {'pppp': 71.28596, 'ppp': 69.920735, 'pp': 68.250912, 'p': 64.9664, 'mp': 63.134699, 'mf': 62.554495, 'f': 63.302281, 'ff': 65.466642, 'fff': 66.883826, 'ffff': 68.03963},
    'B1': {'pppp': 39.802965, 'ppp': 41.460108, 'pp': 43.628892, 'p': 47.251821, 'mp': 50.123106, 'mf': 51.438552, 'f': 51.657794, 'ff': 51.741665, 'fff': 51.933732, 'ffff': 52.087899},
    'C2': {'pppp': 45.84589, 'ppp': 45.975203, 'pp': 46.137358, 'p': 46.165617, 'mp': 46.252449, 'mf': 46.401124, 'f': 47.925454, 'ff': 51.070045, 'fff': 53.311447, 'ffff': 55.175192},
    'C#2': {'pppp': 47.597773, 'ppp': 47.673235, 'pp': 47.76773, 'p': 47.555749, 'mp': 47.477888, 'mf': 47.466775, 'f': 47.72538, 'ff': 48.298291, 'fff': 48.748287, 'ffff': 49.111301},
    'D2': {'pppp': 58.506301, 'ppp': 58.932105, 'pp': 59.468721, 'p': 59.665382, 'mp': 60.194814, 'mf': 60.96791, 'f': 62.74428, 'ff': 65.709747, 'fff': 67.971542, 'ffff': 69.836904},
    'D#2': {'pppp': 29.409895, 'ppp': 29.392547, 'pp': 29.370876, 'p': 29.08122, 'mp': 28.948865, 'mf': 28.917014, 'f': 29.056131, 'ff': 29.394121, 'fff': 29.655084, 'ffff': 29.865521},
    'E2': {'pppp': 45.648173, 'ppp': 44.674243, 'pp': 43.485999, 'p': 41.097591, 'mp': 39.916491, 'mf': 39.587128, 'f': 40.424287, 'ff': 42.628729, 'fff': 44.125429, 'ffff': 45.360537},
    'F2': {'pppp': 50.924798, 'ppp': 51.494671, 'pp': 52.215988, 'p': 53.210726, 'mp': 53.987833, 'mf': 54.441132, 'f': 54.667814, 'ff': 54.76647, 'fff': 55.018122, 'ffff': 55.220276},
    'F#2': {'pppp': 34.375784, 'ppp': 34.658161, 'pp': 35.014396, 'p': 35.694907, 'mp': 35.972055, 'mf': 36.023248, 'f': 35.607455, 'ff': 34.658038, 'fff': 34.171199, 'ffff': 33.786656},
    'G2': {'pppp': 41.903591, 'ppp': 41.847504, 'pp': 41.777501, 'p': 41.277657, 'mp': 41.088072, 'mf': 41.057636, 'f': 41.376386, 'ff': 42.121356, 'fff': 42.647538, 'ffff': 43.073212},
    'G#2': {'pppp': 57.058081, 'ppp': 57.256282, 'pp': 57.505001, 'p': 57.767815, 'mp': 57.864944, 'mf': 57.878833, 'f': 56.952355, 'ff': 55.038656, 'fff': 54.031603, 'ffff': 53.239243},
    'A2': {'pppp': 30.13745, 'ppp': 30.305697, 'pp': 30.517327, 'p': 30.945709, 'mp': 31.105046, 'mf': 31.127875, 'f': 27.579425, 'ff': 21.405774, 'fff': 17.923147, 'ffff': 15.549661},
    'A#2': {'pppp': 26.785554, 'ppp': 27.01467, 'pp': 27.303822, 'p': 27.907003, 'mp': 28.132571, 'mf': 28.164943, 'f': 26.64989, 'ff': 23.683079, 'fff': 21.894314, 'ffff': 20.561079},
    'B2': {'pppp': 25.63601, 'ppp': 26.442834, 'pp': 27.487165, 'p': 29.052622, 'mp': 30.332774, 'mf': 31.147564, 'f': 31.624203, 'ff': 31.840303, 'fff': 32.192428, 'ffff': 32.476931},
    'C3': {'pppp': 20.242232, 'ppp': 20.74581, 'pp': 21.392936, 'p': 22.566914, 'mp': 23.337105, 'mf': 23.6104, 'f': 23.431102, 'ff': 22.830934, 'fff': 22.52203, 'ffff': 22.277919},
    'C#3': {'pppp': 41.264464, 'ppp': 40.52663, 'pp': 39.622862, 'p': 37.592893, 'mp': 36.871514, 'mf': 36.769596, 'f': 39.507693, 'ff': 46.216352, 'fff': 51.489959, 'ffff': 56.138921},
    'D3': {'pppp': 26.17001, 'ppp': 26.875244, 'pp': 27.783572, 'p': 28.789823, 'mp': 29.822015, 'mf': 30.881431, 'f': 31.966891, 'ff': 33.077974, 'fff': 34.159347, 'ffff': 35.049844},
    'D#3': {'pppp': 32.351044, 'ppp': 32.711034, 'pp': 33.16666, 'p': 33.740133, 'mp': 34.216789, 'mf': 34.570077, 'f': 34.824925, 'ff': 34.989404, 'fff': 35.234274, 'ffff': 35.431404},
    'E3': {'pppp': 42.496366, 'ppp': 41.643638, 'pp': 40.601748, 'p': 39.235303, 'mp': 38.059848, 'mf': 37.0667, 'f': 36.235847, 'ff': 35.554851, 'fff': 34.948235, 'ffff': 34.470403},
    'F3': {'pppp': 21.763155, 'ppp': 22.260785, 'pp': 22.898854, 'p': 24.287082, 'mp': 24.897285, 'mf': 25.024321, 'f': 24.208836, 'ff': 22.394256, 'fff': 21.304382, 'ffff': 20.470799},
    'F#3': {'pppp': 30.779256, 'ppp': 31.094197, 'pp': 31.49241, 'p': 31.819933, 'mp': 32.226986, 'mf': 32.695498, 'f': 33.255596, 'ff': 33.921729, 'fff': 34.510633, 'ffff': 34.98911},
    'G3': {'pppp': 24.575366, 'ppp': 25.104078, 'pp': 25.780992, 'p': 26.698204, 'mp': 27.47933, 'mf': 28.078612, 'f': 28.525387, 'ff': 28.827125, 'fff': 29.200824, 'ffff': 29.503269},
    'G#3': {'pppp': 32.896247, 'ppp': 31.847431, 'pp': 30.583308, 'p': 28.34599, 'mp': 27.082924, 'mf': 26.674528, 'f': 27.082861, 'ff': 28.345797, 'fff': 29.171973, 'ffff': 29.850217},
    'A3': {'pppp': 18.537759, 'ppp': 19.043252, 'pp': 19.694546, 'p': 21.139382, 'mp': 21.763199, 'mf': 21.886184, 'f': 20.998474, 'ff': 19.060749, 'fff': 17.891586, 'ffff': 17.008106},
    'A#3': {'pppp': 30.28508, 'ppp': 30.589689, 'pp': 30.974763, 'p': 31.256011, 'mp': 31.654241, 'mf': 32.13437, 'f': 32.751863, 'ff': 33.533198, 'fff': 34.200295, 'ffff': 34.743515},
    'B3': {'pppp': 20.583363, 'ppp': 20.829535, 'pp': 21.141396, 'p': 21.420484, 'mp': 21.748352, 'mf': 22.116353, 'f': 22.540511, 'ff': 23.028942, 'fff': 23.466908, 'ffff': 23.82327},
    'C4': {'pppp': 22.008458, 'ppp': 22.481148, 'pp': 23.086311, 'p': 23.467192, 'mp': 24.172294, 'mf': 25.087441, 'f': 26.428041, 'ff': 28.331855, 'fff': 29.983828, 'ffff': 31.374495},
    'C#4': {'pppp': 23.532577, 'ppp': 24.39566, 'pp': 25.519162, 'p': 27.492765, 'mp': 28.946092, 'mf': 29.508299, 'f': 29.441698, 'ff': 28.979681, 'fff': 28.77552, 'ffff': 28.613227},
    'D4': {'pppp': 18.881483, 'ppp': 19.103722, 'pp': 19.385201, 'p': 19.642123, 'mp': 19.936582, 'mf': 20.262617, 'f': 20.63154, 'ff': 21.049081, 'fff': 21.427361, 'ffff': 21.734875},
    'D#4': {'pppp': 21.770582, 'ppp': 21.289454, 'pp': 20.70297, 'p': 19.385265, 'mp': 18.916855, 'mf': 18.84872, 'f': 19.689903, 'ff': 21.767328, 'fff': 23.28668, 'ffff': 24.578169},
    'E4': {'pppp': 14.185544, 'ppp': 14.605993, 'pp': 15.149121, 'p': 16.097879, 'mp': 16.785595, 'mf': 17.049108, 'f': 17.015497, 'ff': 16.782069, 'fff': 16.685654, 'ffff': 16.60892},
    'F4': {'pppp': 15.676686, 'ppp': 16.094373, 'pp': 16.632166, 'p': 17.416092, 'mp': 18.060893, 'mf': 18.493507, 'f': 18.769973, 'ff': 18.908886, 'fff': 19.119823, 'ffff': 19.290265},
    'F#4': {'pppp': 23.133083, 'ppp': 22.648547, 'pp': 22.057124, 'p': 20.715721, 'mp': 20.242354, 'mf': 20.175619, 'f': 21.090611, 'ff': 23.338178, 'fff': 24.985106, 'ffff': 26.385941},
    'G4': {'pppp': 13.729878, 'ppp': 14.468529, 'pp': 15.447974, 'p': 17.214522, 'mp': 18.524383, 'mf': 19.030993, 'f': 18.94306, 'ff': 18.364601, 'fff': 18.077903, 'ffff': 17.85177},
    'G#4': {'pppp': 17.071211, 'ppp': 17.614789, 'pp': 18.318664, 'p': 19.212999, 'mp': 20.03415, 'mf': 20.761841, 'f': 21.393431, 'ff': 21.922287, 'fff': 22.493192, 'ffff': 22.960602},
    'A4': {'pppp': 15.7367, 'ppp': 16.287749, 'pp': 17.003773, 'p': 18.218692, 'mp': 19.163964, 'mf': 19.55425, 'f': 19.568933, 'ff': 19.574307, 'fff': 19.606754, 'ffff': 19.63275},
    'A#4': {'pppp': 16.491991, 'ppp': 17.098707, 'pp': 17.888584, 'p': 19.472272, 'mp': 20.364429, 'mf': 20.632638, 'f': 20.035433, 'ff': 18.575849, 'fff': 17.706012, 'ffff': 17.039561},
    'B4': {'pppp': 15.194527, 'ppp': 15.608534, 'pp': 16.141941, 'p': 16.904096, 'mp': 17.539827, 'mf': 17.988345, 'f': 18.292152, 'ff': 18.464351, 'fff': 18.702718, 'ffff': 18.895626},
    'C5': {'pppp': 13.99989, 'ppp': 14.487932, 'pp': 15.121979, 'p': 16.21329, 'mp': 17.045397, 'mf': 17.37548, 'f': 17.363411, 'ff': 17.279162, 'fff': 17.256656, 'ffff': 17.238673},
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
