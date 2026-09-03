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
        "(dest Zenodo DoubleBass_con sordino Media (IOWA+Orchidea average); Dynamics_predicter Results ladder)."
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
    version="2026-09-03",
    source_technique="arco_sordina",
    table_supported_techniques=("arco_sordina",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("double_bass_sordina")

# Full 10-dynamic CDM ladder (Results sheet). Anchors pp/mf/ff match measured
# workbook midpoints; other levels are workbook-committed.
spectral_data = {
    'E1': {'pppp': 50.561105, 'ppp': 49.789971, 'pp': 48.842571, 'p': 47.569265, 'mp': 46.527512, 'mf': 45.73279, 'f': 45.135645, 'ff': 44.715474, 'fff': 44.216132, 'ffff': 43.820676},
    'F1': {'pppp': 42.766521, 'ppp': 43.124838, 'pp': 43.576959, 'p': 44.54084, 'mp': 44.968779, 'mf': 45.06363, 'f': 44.542716, 'ff': 43.330634, 'fff': 42.531566, 'ffff': 41.902934},
    'F#1': {'pppp': 31.741562, 'ppp': 32.217787, 'pp': 32.823129, 'p': 33.107726, 'mp': 33.832811, 'mf': 34.805431, 'f': 36.377738, 'ff': 38.743664, 'fff': 40.711044, 'ffff': 42.356639},
    'G1': {'pppp': 33.016694, 'ppp': 32.456028, 'pp': 31.768566, 'p': 30.264735, 'mp': 29.728818, 'mf': 29.653038, 'f': 30.761747, 'ff': 33.434166, 'fff': 35.359802, 'ffff': 36.979862},
    'G#1': {'pppp': 33.70108, 'ppp': 33.018354, 'pp': 32.184363, 'p': 30.685284, 'mp': 29.846761, 'mf': 29.580547, 'f': 29.919509, 'ff': 30.902204, 'fff': 31.504733, 'ffff': 31.995204},
    'A1': {'pppp': 39.973398, 'ppp': 40.866915, 'pp': 42.011951, 'p': 44.607222, 'mp': 45.603276, 'mf': 45.747373, 'f': 41.965682, 'ff': 34.775541, 'fff': 30.442849, 'ffff': 27.368715},
    'A#1': {'pppp': 46.651883, 'ppp': 46.607641, 'pp': 46.552398, 'p': 46.523652, 'mp': 46.436374, 'mf': 46.289177, 'f': 45.089092, 'ff': 42.846172, 'fff': 41.343199, 'ffff': 40.17887},
    'B1': {'pppp': 40.702647, 'ppp': 40.973612, 'pp': 41.314856, 'p': 42.079791, 'mp': 42.365165, 'mf': 42.406091, 'f': 41.555738, 'ff': 39.737322, 'fff': 38.548911, 'ffff': 37.623823},
    'C2': {'pppp': 38.481226, 'ppp': 38.559507, 'pp': 38.657582, 'p': 38.821267, 'mp': 38.881746, 'mf': 38.890394, 'f': 38.623705, 'ff': 38.052201, 'fff': 37.638584, 'ffff': 37.310929},
    'C#2': {'pppp': 27.223013, 'ppp': 27.673983, 'pp': 28.248215, 'p': 29.362602, 'mp': 29.987545, 'mf': 30.179091, 'f': 29.8155, 'ff': 28.877788, 'fff': 28.275212, 'ffff': 27.802218},
    'D2': {'pppp': 35.697424, 'ppp': 34.418902, 'pp': 32.884949, 'p': 30.168405, 'mp': 28.850436, 'mf': 28.484926, 'f': 29.39967, 'ff': 31.860405, 'fff': 33.597099, 'ffff': 35.05437},
    'D#2': {'pppp': 29.503086, 'ppp': 30.104936, 'pp': 30.874541, 'p': 32.541919, 'mp': 33.277557, 'mf': 33.433068, 'f': 32.469592, 'ff': 30.307837, 'fff': 28.921699, 'ffff': 27.858575},
    'E2': {'pppp': 25.217651, 'ppp': 27.056404, 'pp': 29.544517, 'p': 34.857887, 'mp': 37.846555, 'mf': 38.699174, 'f': 36.169895, 'ff': 30.574352, 'fff': 27.244078, 'ffff': 24.842998},
    'F2': {'pppp': 28.063764, 'ppp': 27.877735, 'pp': 27.646931, 'p': 27.472732, 'mp': 27.182093, 'mf': 26.825893, 'f': 26.346853, 'ff': 25.730982, 'fff': 25.229333, 'ffff': 24.835066},
    'F#2': {'pppp': 28.918447, 'ppp': 28.711915, 'pp': 28.455823, 'p': 27.911723, 'mp': 27.608439, 'mf': 27.513567, 'f': 27.657019, 'ff': 28.054076, 'fff': 28.244717, 'ffff': 28.398163},
    'G2': {'pppp': 23.813761, 'ppp': 24.059461, 'pp': 24.370153, 'p': 24.908972, 'mp': 25.291773, 'mf': 25.437088, 'f': 25.422711, 'ff': 25.322303, 'fff': 25.23133, 'ffff': 25.158787},
    'G#2': {'pppp': 26.974459, 'ppp': 26.561605, 'pp': 26.054413, 'p': 25.207735, 'mp': 24.601522, 'mf': 24.349348, 'f': 24.320099, 'ff': 24.309129, 'fff': 24.259136, 'ffff': 24.219215},
    'A2': {'pppp': 25.635461, 'ppp': 25.417437, 'pp': 25.147513, 'p': 24.519767, 'mp': 24.292463, 'mf': 24.260163, 'f': 24.959898, 'ff': 26.576088, 'fff': 27.69341, 'ffff': 28.620995},
    'A#2': {'pppp': 28.415565, 'ppp': 28.468601, 'pp': 28.535034, 'p': 28.655835, 'mp': 28.70047, 'mf': 28.706852, 'f': 28.135932, 'ff': 26.969585, 'fff': 26.204737, 'ffff': 25.608506},
    'B2': {'pppp': 33.918717, 'ppp': 33.118949, 'pp': 32.145707, 'p': 30.158134, 'mp': 29.38213, 'mf': 29.236044, 'f': 30.3573, 'ff': 33.146339, 'fff': 35.164706, 'ffff': 36.867537},
    'C3': {'pppp': 29.273477, 'ppp': 29.386414, 'pp': 29.528199, 'p': 29.58646, 'mp': 29.740423, 'mf': 29.959071, 'f': 30.409584, 'ff': 31.12757, 'fff': 31.592372, 'ffff': 31.969206},
    'C#3': {'pppp': 23.007389, 'ppp': 23.962959, 'pp': 25.213424, 'p': 27.552786, 'mp': 29.055702, 'mf': 29.573554, 'f': 29.045992, 'ff': 27.526149, 'fff': 26.587524, 'ffff': 25.859722},
    'D3': {'pppp': 23.335683, 'ppp': 23.133309, 'pp': 22.882808, 'p': 22.329998, 'mp': 22.079346, 'mf': 22.018994, 'f': 22.279812, 'ff': 22.921712, 'fff': 23.306455, 'ffff': 23.618894},
    'D#3': {'pppp': 28.171429, 'ppp': 28.697325, 'pp': 29.368522, 'p': 30.755335, 'mp': 31.434518, 'mf': 31.608235, 'f': 30.948012, 'ff': 29.398078, 'fff': 28.401435, 'ffff': 27.628503},
    'E3': {'pppp': 30.441911, 'ppp': 31.309829, 'pp': 32.429606, 'p': 34.970484, 'mp': 35.955978, 'mf': 36.099012, 'f': 30.569264, 'ff': 21.405973, 'fff': 16.562566, 'ffff': 13.489683},
    'F3': {'pppp': 23.66971, 'ppp': 23.195375, 'pp': 22.615801, 'p': 21.436555, 'mp': 20.947969, 'mf': 20.844837, 'f': 21.461819, 'ff': 22.993716, 'fff': 24.064575, 'ffff': 24.95706},
    'F#3': {'pppp': 22.840216, 'ppp': 23.133402, 'pp': 23.505182, 'p': 24.347667, 'mp': 24.665612, 'mf': 24.71137, 'f': 23.807963, 'ff': 21.922992, 'fff': 20.711322, 'ffff': 19.790383},
    'G3': {'pppp': 25.390966, 'ppp': 25.240969, 'pp': 25.054717, 'p': 24.983084, 'mp': 24.776694, 'mf': 24.449667, 'f': 23.104964, 'ff': 20.844549, 'fff': 19.322931, 'ffff': 18.186009},
    'G#3': {'pppp': 22.591478, 'ppp': 21.738607, 'pp': 20.717652, 'p': 20.049274, 'mp': 19.024282, 'mf': 17.836667, 'f': 16.360447, 'ff': 14.629176, 'fff': 13.287315, 'ffff': 12.303003},
    'A3': {'pppp': 19.866058, 'ppp': 18.674092, 'pp': 17.284197, 'p': 14.95216, 'mp': 13.892858, 'mf': 13.612201, 'f': 14.40213, 'ff': 16.593803, 'fff': 18.267152, 'ffff': 19.726533},
    'A#3': {'pppp': 19.908818, 'ppp': 19.941721, 'pp': 19.982926, 'p': 19.994239, 'mp': 20.028751, 'mf': 20.087386, 'f': 20.602262, 'ff': 21.643618, 'fff': 22.347781, 'ffff': 22.92757},
    'B3': {'pppp': 18.938749, 'ppp': 19.623, 'pp': 20.513184, 'p': 22.236904, 'mp': 23.253172, 'mf': 23.575534, 'f': 23.023133, 'ff': 21.606296, 'fff': 20.716829, 'ffff': 20.031693},
    'C4': {'pppp': 19.418577, 'ppp': 19.490494, 'pp': 19.580765, 'p': 19.613095, 'mp': 19.70595, 'mf': 19.853451, 'f': 20.421098, 'ff': 21.477357, 'fff': 22.227677, 'ffff': 22.846763},
    'C#4': {'pppp': 17.718966, 'ppp': 18.051414, 'pp': 18.475759, 'p': 18.774, 'mp': 19.263036, 'mf': 19.881659, 'f': 20.743219, 'ff': 21.915587, 'fff': 22.925056, 'ffff': 23.766007},
    'D4': {'pppp': 18.048765, 'ppp': 18.426908, 'pp': 18.910748, 'p': 20.016201, 'mp': 20.439566, 'mf': 20.500773, 'f': 19.469392, 'ff': 17.345874, 'fff': 16.00725, 'ffff': 15.011122},
    'D#4': {'pppp': 24.716714, 'ppp': 23.294892, 'pp': 21.632074, 'p': 18.896253, 'mp': 17.572893, 'mf': 17.197052, 'f': 17.977396, 'ff': 20.182493, 'fff': 21.804925, 'ffff': 23.196285},
    'E4': {'pppp': 19.292371, 'ppp': 19.518865, 'pp': 19.805726, 'p': 20.454999, 'mp': 20.699533, 'mf': 20.734705, 'f': 20.021418, 'ff': 18.530091, 'fff': 17.569019, 'ffff': 16.836177},
    'F4': {'pppp': 20.049372, 'ppp': 20.186375, 'pp': 20.358946, 'p': 20.41937, 'mp': 20.59898, 'mf': 20.89675, 'f': 22.562944, 'ff': 26.044998, 'fff': 28.918848, 'ffff': 31.444617},
    'F#4': {'pppp': 23.859816, 'ppp': 24.066488, 'pp': 24.327347, 'p': 24.431543, 'mp': 24.720067, 'mf': 25.158596, 'f': 26.377008, 'ff': 28.557305, 'fff': 30.279162, 'ffff': 31.731103},
    'G4': {'pppp': 17.975836, 'ppp': 18.397815, 'pp': 18.939246, 'p': 20.184674, 'mp': 20.663883, 'mf': 20.733264, 'f': 19.799178, 'ff': 17.825216, 'fff': 16.576724, 'ffff': 15.641192},
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
