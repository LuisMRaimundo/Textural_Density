# instrumentos/double_bass_sordina.py
"""
Double bass (arco con sordino) instrument density module.

The ``spectral_data`` table stores a committed 10-dynamic Combined Density
Metric (CDM) ladder from the ``Results`` sheet of
``Double_bass_Zenodo_collections_con_sordino_Dynamics10.xlsx``
(measured pp/mf/ff anchors; remaining levels committed from that workbook —
no runtime dynamic extrapolation).

Runtime analysis does not ingest audio; it maps notated pitch + dynamic to
these pre-loaded acoustic metadata tables.
"""

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="external_acoustic_metadata",
    citation=(
        "Double bass arco_sordina CDM ladder: measured pp/mf/ff anchors with "
        "committed Results sheet values for all 10 dynamic levels from "
        "Double_bass_Zenodo_collections_con_sordino_Dynamics10.xlsx "
        "(dest Zenodo DoubleBass_con sordino Media (IOWA+Orchidea average); Dynamics_predicter Results ladder (CORDAS_4))."
    ),
    source_url_or_identifier='docs/instrument_acoustic_sources.md#double-bass-sordina',
    extraction_method=(
        "Committed full dynamic ladder from Dynamics extrapolator v1.5.2.1 Results sheet "
        "(PCHIP interiors, tapered outers r=0.80) on measured pp/mf/ff anchors; "
        "interior cells clamped into their measured segment where the workbook "
        "marginally overshoots; pitch lookup via MIDI-space spectral_lookup"
    ),
    dynamic_levels=('pppp', 'ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', 'ffff'),
    pitch_range=(28, 67),
    uncertainty="high",
    version="2026-09-18",
    source_technique="arco_sordina",
    table_supported_techniques=("arco_sordina",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("double_bass_sordina")

# Full 10-dynamic CDM ladder (Results sheet). Anchors pp/mf/ff match measured
# workbook midpoints; other levels are workbook-committed.
spectral_data = {
    'E1': {'pppp': 50.632638, 'ppp': 49.829093, 'pp': 48.842571, 'p': 47.569265, 'mp': 46.527512, 'mf': 45.73279, 'f': 45.135645, 'ff': 44.715474, 'fff': 44.23129, 'ffff': 43.847721},
    'F1': {'pppp': 43.483907, 'ppp': 43.525239, 'pp': 43.576959, 'p': 43.598497, 'mp': 43.606435, 'mf': 43.607569, 'f': 43.51839, 'ff': 43.330634, 'fff': 43.154642, 'ffff': 43.014364},
    'F#1': {'pppp': 29.941398, 'ppp': 31.189536, 'pp': 32.823129, 'p': 35.460159, 'mp': 37.547181, 'mf': 38.509204, 'f': 38.678633, 'ff': 38.743664, 'fff': 38.845017, 'ffff': 38.926291},
    'G1': {'pppp': 31.550587, 'ppp': 31.647281, 'pp': 31.768566, 'p': 31.815842, 'mp': 31.944733, 'mf': 32.136064, 'f': 32.619615, 'ff': 33.434166, 'fff': 34.002282, 'ffff': 34.463717},
    'G#1': {'pppp': 33.257315, 'ppp': 32.776101, 'pp': 32.184363, 'p': 31.150478, 'mp': 30.514542, 'mf': 30.295953, 'f': 30.430273, 'ff': 30.902204, 'fff': 31.168541, 'ffff': 31.383262},
    'A1': {'pppp': 41.543984, 'ppp': 41.751322, 'pp': 42.011951, 'p': 42.575254, 'mp': 42.784685, 'mf': 42.814688, 'f': 40.041758, 'ff': 34.775541, 'fff': 31.444283, 'ffff': 29.010549},
    'A#1': {'pppp': 47.861825, 'ppp': 47.275371, 'pp': 46.552398, 'p': 45.744668, 'mp': 44.971713, 'mf': 44.230561, 'f': 43.522195, 'ff': 42.846172, 'fff': 42.201785, 'ffff': 41.69326},
    'B1': {'pppp': 40.693032, 'ppp': 40.968234, 'pp': 41.314856, 'p': 42.088943, 'mp': 42.377775, 'mf': 42.419198, 'f': 41.564836, 'ff': 39.737322, 'fff': 38.53431, 'ffff': 37.598177},
    'C2': {'pppp': 39.849841, 'ppp': 39.315475, 'pp': 38.657582, 'p': 37.412032, 'mp': 36.764683, 'mf': 36.575727, 'f': 36.980884, 'ff': 38.052201, 'fff': 38.740372, 'ffff': 39.299859},
    'C#2': {'pppp': 27.93126, 'ppp': 28.071687, 'pp': 28.248215, 'p': 28.522773, 'mp': 28.73029, 'mf': 28.833158, 'f': 28.864983, 'ff': 28.877788, 'fff': 28.861929, 'ffff': 28.849249},
    'D2': {'pppp': 33.874622, 'ppp': 33.431143, 'pp': 32.884949, 'p': 31.902211, 'mp': 31.321405, 'mf': 31.128562, 'f': 31.307215, 'ff': 31.860405, 'fff': 32.184621, 'ffff': 32.446367},
    'D#2': {'pppp': 31.354059, 'ppp': 31.140028, 'pp': 30.874541, 'p': 30.353155, 'mp': 30.03875, 'mf': 29.93292, 'f': 30.023243, 'ff': 30.307837, 'fff': 30.448708, 'ffff': 30.561877},
    'E2': {'pppp': 26.969574, 'ppp': 28.085059, 'pp': 29.544517, 'p': 32.445938, 'mp': 34.058944, 'mf': 34.533684, 'f': 33.366752, 'ff': 30.574352, 'fff': 28.812219, 'ffff': 27.475922},
    'F2': {'pppp': 29.188054, 'ppp': 28.49278, 'pp': 27.646931, 'p': 26.264573, 'mp': 25.401001, 'mf': 25.099289, 'f': 25.221462, 'ff': 25.730982, 'fff': 26.024222, 'ffff': 26.261218},
    'F#2': {'pppp': 28.8177, 'ppp': 28.656302, 'pp': 28.455823, 'p': 28.044319, 'mp': 27.80153, 'mf': 27.721447, 'f': 27.804872, 'ff': 28.054076, 'fff': 28.174302, 'ffff': 28.270854},
    'G2': {'pppp': 25.044631, 'ppp': 24.742589, 'pp': 24.370153, 'p': 23.549578, 'mp': 23.254276, 'mf': 23.212393, 'f': 23.839375, 'ff': 25.322303, 'fff': 26.378294, 'ffff': 27.254706},
    'G#2': {'pppp': 26.379126, 'ppp': 26.234312, 'pp': 26.054413, 'p': 25.964111, 'mp': 25.73754, 'mf': 25.4412, 'f': 24.971667, 'ff': 24.309129, 'fff': 23.79721, 'ffff': 23.395447},
    'A2': {'pppp': 22.98384, 'ppp': 23.921484, 'pp': 25.147513, 'p': 27.50995, 'mp': 28.90318, 'mf': 29.34333, 'f': 28.560266, 'ff': 26.576088, 'fff': 25.325156, 'ffff': 24.366939},
    'A#2': {'pppp': 28.880293, 'ppp': 28.726332, 'pp': 28.535034, 'p': 28.393142, 'mp': 28.156655, 'mf': 27.866233, 'f': 27.474759, 'ff': 26.969585, 'fff': 26.559728, 'ffff': 26.236331},
    'B2': {'pppp': 33.586058, 'ppp': 32.938102, 'pp': 32.145707, 'p': 30.506664, 'mp': 29.88284, 'mf': 29.774488, 'f': 30.752269, 'ff': 33.146339, 'fff': 34.887527, 'ffff': 36.346104},
    'C3': {'pppp': 29.820663, 'ppp': 29.690323, 'pp': 29.528199, 'p': 29.143365, 'mp': 29.002852, 'mf': 28.982834, 'f': 29.644724, 'ff': 31.12757, 'fff': 32.158183, 'ffff': 33.007188},
    'C#3': {'pppp': 22.89368, 'ppp': 23.897091, 'pp': 25.213424, 'p': 27.661138, 'mp': 29.223891, 'mf': 29.758478, 'f': 29.174525, 'ff': 27.526149, 'fff': 26.500805, 'ffff': 25.708098},
    'D3': {'pppp': 22.581606, 'ppp': 22.714981, 'pp': 22.882808, 'p': 23.21981, 'mp': 23.385253, 'mf': 23.428787, 'f': 23.281061, 'ff': 22.921712, 'fff': 22.684673, 'ffff': 22.496807},
    'D#3': {'pppp': 28.736824, 'ppp': 29.015883, 'pp': 29.368522, 'p': 30.085892, 'mp': 30.433476, 'mf': 30.522533, 'f': 30.191208, 'ff': 29.398078, 'fff': 28.881483, 'ffff': 28.474751},
    'E3': {'pppp': 31.105814, 'ppp': 31.687361, 'pp': 32.429606, 'p': 34.074802, 'mp': 34.701745, 'mf': 34.792245, 'f': 29.781224, 'ff': 21.405973, 'fff': 16.848382, 'ffff': 13.91159},
    'F3': {'pppp': 22.224294, 'ppp': 22.397453, 'pp': 22.615801, 'p': 23.018354, 'mp': 23.260093, 'mf': 23.340256, 'f': 23.251486, 'ff': 22.993716, 'fff': 22.825189, 'ffff': 22.691256},
    'F#3': {'pppp': 23.445803, 'ppp': 23.472175, 'pp': 23.505182, 'p': 23.564325, 'mp': 23.586152, 'mf': 23.589272, 'f': 23.037028, 'ff': 21.922992, 'fff': 21.188011, 'ffff': 20.617808},
    'G3': {'pppp': 25.020734, 'ppp': 25.035832, 'pp': 25.054717, 'p': 25.088021, 'mp': 25.100303, 'mf': 25.102058, 'f': 23.632174, 'ff': 20.844549, 'fff': 19.060459, 'ffff': 17.743775},
    'G#3': {'pppp': 21.838873, 'ppp': 21.33325, 'pp': 20.717652, 'p': 20.46904, 'mp': 19.822309, 'mf': 18.931708, 'f': 17.138548, 'ff': 14.629176, 'fff': 12.895669, 'ffff': 11.657974},
    'A3': {'pppp': 17.54067, 'ppp': 17.426216, 'pp': 17.284197, 'p': 17.08027, 'mp': 16.909476, 'mf': 16.774806, 'f': 16.670362, 'ff': 16.593803, 'fff': 16.501826, 'ffff': 16.428612},
    'A#3': {'pppp': 19.636414, 'ppp': 19.789671, 'pp': 19.982926, 'p': 20.091244, 'mp': 20.316036, 'mf': 20.606697, 'f': 21.037628, 'ff': 21.643618, 'fff': 22.125624, 'ffff': 22.518947},
    'B3': {'pppp': 19.06729, 'ppp': 19.696881, 'pp': 20.513184, 'p': 22.055757, 'mp': 22.975139, 'mf': 23.271242, 'f': 22.812245, 'ff': 21.606296, 'fff': 20.843104, 'ffff': 20.252007},
    'C4': {'pppp': 18.885308, 'ppp': 19.191297, 'pp': 19.580765, 'p': 20.062384, 'mp': 20.496773, 'mf': 20.877102, 'f': 21.204347, 'ff': 21.477357, 'fff': 21.751358, 'ffff': 21.973074},
    'C#4': {'pppp': 17.552971, 'ppp': 17.957268, 'pp': 18.475759, 'p': 18.95103, 'mp': 19.527409, 'mf': 20.19059, 'f': 20.978633, 'ff': 21.915587, 'fff': 22.785622, 'ffff': 23.506453},
    'D4': {'pppp': 18.061684, 'ppp': 18.434235, 'pp': 18.910748, 'p': 19.98748, 'mp': 20.399444, 'mf': 20.458985, 'f': 19.441273, 'ff': 17.345874, 'fff': 16.010155, 'ffff': 15.016025},
    'D#4': {'pppp': 23.815153, 'ppp': 22.818942, 'pp': 21.632074, 'p': 19.672822, 'mp': 18.645125, 'mf': 18.33301, 'f': 18.810665, 'ff': 20.182493, 'fff': 21.141924, 'ffff': 21.942205},
    'E4': {'pppp': 19.674853, 'ppp': 19.732912, 'pp': 19.805726, 'p': 19.960081, 'mp': 20.017252, 'mf': 20.025432, 'f': 19.533843, 'ff': 18.530091, 'fff': 17.868126, 'ffff': 17.355622},
    'F4': {'pppp': 20.0485, 'ppp': 20.185887, 'pp': 20.358946, 'p': 20.41937, 'mp': 20.59898, 'mf': 20.89675, 'f': 22.562944, 'ff': 26.044998, 'fff': 28.971016, 'ffff': 31.546795},
    'F#4': {'pppp': 23.856492, 'ppp': 24.064625, 'pp': 24.327347, 'p': 24.431543, 'mp': 24.720067, 'mf': 25.158596, 'f': 26.377008, 'ff': 28.557305, 'fff': 30.327902, 'ffff': 31.823101},
    'G4': {'pppp': 17.965397, 'ppp': 18.391879, 'pp': 18.939246, 'p': 20.184674, 'mp': 20.663883, 'mf': 20.733264, 'f': 19.799178, 'ff': 17.825216, 'fff': 16.564321, 'ffff': 15.620132},
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
