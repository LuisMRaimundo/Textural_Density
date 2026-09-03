# instrumentos/double_bass_sul_ponticello.py
"""
Double bass (arco sul ponticello) instrument density module.

The ``spectral_data`` table stores a committed 10-dynamic Combined Density
Metric (CDM) ladder from the ``Results`` sheet of
``Double_bass_Zenodo_collections_sul_ponticello_Dynamics10.xlsx``
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
        "Double_bass_Zenodo_collections_sul_ponticello_Dynamics10.xlsx "
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
    pitch_range=(28, 67),
    uncertainty="high",
    version="2026-09-03",
    source_technique="arco_sul_ponticello",
    table_supported_techniques=("arco_sul_ponticello",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("double_bass_sul_ponticello")

# Full 10-dynamic CDM ladder (Results sheet). Anchors pp/mf/ff match measured
# workbook midpoints; other levels are workbook-committed.
spectral_data = {
    'E1': {'pppp': 46.647901, 'ppp': 47.422478, 'pp': 48.40881, 'p': 49.393835, 'mp': 50.480035, 'mf': 51.658048, 'f': 52.953173, 'ff': 54.380089, 'fff': 55.704838, 'ffff': 56.787836},
    'F1': {'pppp': 39.196608, 'ppp': 40.123531, 'pp': 41.313071, 'p': 42.973359, 'mp': 44.37161, 'mf': 45.403317, 'f': 46.139548, 'ff': 46.60058, 'fff': 47.210346, 'ffff': 47.703899},
    'F#1': {'pppp': 45.511371, 'ppp': 45.862796, 'pp': 46.305895, 'p': 46.468602, 'mp': 46.916863, 'mf': 47.593045, 'f': 49.411692, 'ff': 52.604243, 'fff': 55.061433, 'ffff': 57.109572},
    'G1': {'pppp': 47.00637, 'ppp': 48.339239, 'pp': 50.058597, 'p': 52.705184, 'mp': 54.828808, 'mf': 56.078399, 'f': 56.693476, 'ff': 56.960996, 'fff': 57.441854, 'ffff': 57.829462},
    'G#1': {'pppp': 32.41331, 'ppp': 32.711789, 'pp': 33.088755, 'p': 33.746679, 'mp': 34.101141, 'mf': 34.205976, 'f': 33.977128, 'ff': 33.392784, 'fff': 33.147177, 'ffff': 32.951993},
    'A1': {'pppp': 60.805756, 'ppp': 61.022806, 'pp': 61.295208, 'p': 61.31744, 'mp': 61.378985, 'mf': 61.472155, 'f': 61.73698, 'ff': 62.189363, 'fff': 62.67847, 'ffff': 63.072524},
    'A#1': {'pppp': 71.286984, 'ppp': 69.921293, 'pp': 68.250912, 'p': 64.9664, 'mp': 63.134699, 'mf': 62.554495, 'f': 63.302281, 'ff': 65.466642, 'fff': 66.897071, 'ffff': 68.063884},
    'B1': {'pppp': 39.813096, 'ppp': 41.46597, 'pp': 43.628892, 'p': 47.251821, 'mp': 50.123106, 'mf': 51.438552, 'f': 51.657794, 'ff': 51.741665, 'fff': 51.944005, 'ffff': 52.106446},
    'C2': {'pppp': 45.852448, 'ppp': 45.978857, 'pp': 46.137358, 'p': 46.165617, 'mp': 46.252449, 'mf': 46.401124, 'f': 47.925454, 'ff': 51.070045, 'fff': 53.321425, 'ffff': 55.193782},
    'C#2': {'pppp': 45.913321, 'ppp': 46.728445, 'pp': 47.76773, 'p': 49.832426, 'mp': 50.907414, 'mf': 51.208039, 'f': 50.360248, 'ff': 48.298291, 'fff': 47.140247, 'ffff': 46.233835},
    'D2': {'pppp': 58.516123, 'ppp': 58.937601, 'pp': 59.468721, 'p': 59.665382, 'mp': 60.194814, 'mf': 60.96791, 'f': 62.74428, 'ff': 65.709747, 'fff': 67.985858, 'ffff': 69.863382},
    'D#2': {'pppp': 29.417411, 'ppp': 29.39672, 'pp': 29.370876, 'p': 29.08122, 'mp': 28.948865, 'mf': 28.917014, 'f': 29.056131, 'ff': 29.394121, 'fff': 29.668504, 'ffff': 29.889853},
    'E2': {'pppp': 45.648014, 'ppp': 44.674156, 'pp': 43.485999, 'p': 41.097591, 'mp': 39.916491, 'mf': 39.587128, 'f': 40.424287, 'ff': 42.628729, 'fff': 44.131729, 'ffff': 45.372195},
    'F2': {'pppp': 50.93879, 'ppp': 51.502531, 'pp': 52.215988, 'p': 53.210726, 'mp': 53.987833, 'mf': 54.441132, 'f': 54.667814, 'ff': 54.76647, 'fff': 55.040203, 'ffff': 55.260175},
    'F#2': {'pppp': 34.383273, 'ppp': 34.662356, 'pp': 35.014396, 'p': 35.694907, 'mp': 35.972055, 'mf': 36.023248, 'f': 35.607455, 'ff': 34.658038, 'fff': 34.184596, 'ffff': 33.810503},
    'G2': {'pppp': 41.912623, 'ppp': 41.852515, 'pp': 41.777501, 'p': 41.277657, 'mp': 41.088072, 'mf': 41.057636, 'f': 41.376386, 'ff': 42.121356, 'fff': 42.664519, 'ffff': 43.104088},
    'G#2': {'pppp': 57.070075, 'ppp': 57.262968, 'pp': 57.505001, 'p': 57.767815, 'mp': 57.864944, 'mf': 57.878833, 'f': 56.952355, 'ff': 55.038656, 'fff': 54.054922, 'ffff': 53.280609},
    'A2': {'pppp': 30.139085, 'ppp': 30.30661, 'pp': 30.517327, 'p': 30.945709, 'mp': 31.105046, 'mf': 31.127875, 'f': 27.579425, 'ff': 21.405774, 'fff': 17.928435, 'ffff': 15.557921},
    'A#2': {'pppp': 26.788376, 'ppp': 27.01625, 'pp': 27.303822, 'p': 27.907003, 'mp': 28.132571, 'mf': 28.164943, 'f': 26.64989, 'ff': 23.683079, 'fff': 21.901108, 'ffff': 20.572564},
    'B2': {'pppp': 25.642031, 'ppp': 26.446284, 'pp': 27.487165, 'p': 29.052622, 'mp': 30.332774, 'mf': 31.147564, 'f': 31.624203, 'ff': 31.840303, 'fff': 32.199022, 'ffff': 32.488905},
    'C3': {'pppp': 20.246688, 'ppp': 20.748347, 'pp': 21.392936, 'p': 22.566914, 'mp': 23.337105, 'mf': 23.6104, 'f': 23.431102, 'ff': 22.830934, 'fff': 22.528143, 'ffff': 22.288804},
    'C#3': {'pppp': 41.264449, 'ppp': 40.526622, 'pp': 39.622862, 'p': 37.592893, 'mp': 36.871514, 'mf': 36.769596, 'f': 39.507693, 'ff': 46.216352, 'fff': 51.489595, 'ffff': 56.138205},
    'D3': {'pppp': 26.175055, 'ppp': 26.878122, 'pp': 27.783572, 'p': 28.789823, 'mp': 29.822015, 'mf': 30.881431, 'f': 31.966891, 'ff': 33.077974, 'fff': 34.164227, 'ffff': 35.058857},
    'D#3': {'pppp': 32.359487, 'ppp': 32.715776, 'pp': 33.16666, 'p': 33.740133, 'mp': 34.216789, 'mf': 34.570077, 'f': 34.824925, 'ff': 34.989404, 'fff': 35.247537, 'ffff': 35.455414},
    'E3': {'pppp': 42.496791, 'ppp': 41.643869, 'pp': 40.601748, 'p': 39.235303, 'mp': 38.059848, 'mf': 37.0667, 'f': 36.235847, 'ff': 35.554851, 'fff': 34.957958, 'ffff': 34.487666},
    'F3': {'pppp': 21.766651, 'ppp': 22.262772, 'pp': 22.898854, 'p': 24.287082, 'mp': 24.897285, 'mf': 25.024321, 'f': 24.208836, 'ff': 22.394256, 'fff': 21.310065, 'ffff': 20.480628},
    'F#3': {'pppp': 30.785937, 'ppp': 31.097947, 'pp': 31.49241, 'p': 31.819933, 'mp': 32.226986, 'mf': 32.695498, 'f': 33.255596, 'ff': 33.921729, 'fff': 34.520851, 'ffff': 35.007759},
    'G3': {'pppp': 24.580926, 'ppp': 25.107233, 'pp': 25.780992, 'p': 26.698204, 'mp': 27.47933, 'mf': 28.078612, 'f': 28.525387, 'ff': 28.827125, 'fff': 29.207877, 'ffff': 29.516097},
    'G#3': {'pppp': 32.894663, 'ppp': 31.846579, 'pp': 30.583308, 'p': 28.34599, 'mp': 27.082924, 'mf': 26.674528, 'f': 27.082861, 'ff': 28.345797, 'fff': 29.175921, 'ffff': 29.85749},
    'A3': {'pppp': 18.540603, 'ppp': 19.044875, 'pp': 19.694546, 'p': 21.139382, 'mp': 21.763199, 'mf': 21.886184, 'f': 20.998474, 'ff': 19.060749, 'fff': 17.896089, 'ffff': 17.015811},
    'A#3': {'pppp': 30.291392, 'ppp': 30.593231, 'pp': 30.974763, 'p': 31.256011, 'mp': 31.654241, 'mf': 32.13437, 'f': 32.751863, 'ff': 33.533198, 'fff': 34.209847, 'ffff': 34.760983},
    'B3': {'pppp': 20.587684, 'ppp': 20.831965, 'pp': 21.141396, 'p': 21.420484, 'mp': 21.748352, 'mf': 22.116353, 'f': 22.540511, 'ff': 23.028942, 'fff': 23.473231, 'ffff': 23.834826},
    'C4': {'pppp': 22.011821, 'ppp': 22.483056, 'pp': 23.086311, 'p': 23.467192, 'mp': 24.172294, 'mf': 25.087441, 'f': 26.428041, 'ff': 28.331855, 'fff': 29.986379, 'ffff': 31.3793},
    'C#4': {'pppp': 23.538255, 'ppp': 24.39893, 'pp': 25.519162, 'p': 27.492765, 'mp': 28.946092, 'mf': 29.508299, 'f': 29.441698, 'ff': 28.979681, 'fff': 28.781973, 'ffff': 28.624777},
    'D4': {'pppp': 18.885513, 'ppp': 19.105986, 'pp': 19.385201, 'p': 19.642123, 'mp': 19.936582, 'mf': 20.262617, 'f': 20.63154, 'ff': 21.049081, 'fff': 21.433317, 'ffff': 21.745751},
    'D#4': {'pppp': 22.240372, 'ppp': 21.54347, 'pp': 20.70297, 'p': 18.952415, 'mp': 18.298968, 'mf': 18.184682, 'f': 19.195988, 'ff': 21.767328, 'fff': 23.703703, 'ffff': 25.376111},
    'E4': {'pppp': 14.45423, 'ppp': 14.759046, 'pp': 15.149121, 'p': 15.713068, 'mp': 16.173761, 'mf': 16.482872, 'f': 16.681083, 'ff': 16.782069, 'fff': 16.942716, 'ffff': 17.07234},
    'F4': {'pppp': 16.043981, 'ppp': 16.302784, 'pp': 16.632166, 'p': 16.911378, 'mp': 17.276975, 'mf': 17.70939, 'f': 18.246363, 'ff': 18.908886, 'fff': 19.493006, 'ffff': 19.973268},
    'F#4': {'pppp': 23.866854, 'ppp': 23.044888, 'pp': 22.057124, 'p': 20.023913, 'mp': 19.27335, 'mf': 19.14411, 'f': 20.320999, 'ff': 23.338178, 'fff': 25.643219, 'ffff': 27.65012},
    'G4': {'pppp': 14.254661, 'ppp': 14.773198, 'pp': 15.447974, 'p': 16.449994, 'mp': 17.283573, 'mf': 17.840901, 'f': 18.193471, 'ff': 18.364601, 'fff': 18.629393, 'ffff': 18.843973},
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
