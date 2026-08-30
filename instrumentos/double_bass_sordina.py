# instrumentos/double_bass_sordina.py
"""
Double bass (arco con sordino) instrument density module.

The ``spectral_data`` table stores a committed 10-dynamic Combined Density
Metric (CDM) ladder from the ``Results`` sheet of
``DoubleBass_Dynamics10_con_sordino.xlsx``
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
        "DoubleBass_Dynamics10_con_sordino.xlsx "
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
    pitch_range=(28, 72),
    uncertainty="high",
    version="2026-08-27",
    source_technique="arco_sordina",
    table_supported_techniques=("arco_sordina",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("double_bass_sordina")

# Full 10-dynamic CDM ladder (Results sheet). Anchors pp/mf/ff match measured
# workbook midpoints; other levels are workbook-committed.
spectral_data = {
    'E1': {'pppp': 45.061486, 'ppp': 45.210979, 'pp': 45.398542, 'p': 45.529871, 'mp': 45.578351, 'mf': 45.585281, 'f': 45.386151, 'ff': 44.956417, 'fff': 44.470446, 'ffff': 44.085454},
    'F1': {'pppp': 42.708603, 'ppp': 43.092382, 'pp': 43.576959, 'p': 44.54084, 'mp': 44.968779, 'mf': 45.06363, 'f': 44.542716, 'ff': 43.330634, 'fff': 42.480008, 'ffff': 41.811546},
    'F#1': {'pppp': 31.740508, 'ppp': 32.217193, 'pp': 32.823129, 'p': 33.107726, 'mp': 33.832811, 'mf': 34.805431, 'f': 36.377738, 'ff': 38.743664, 'fff': 40.545911, 'ffff': 42.047886},
    'G1': {'pppp': 32.90741, 'ppp': 32.396302, 'pp': 31.768566, 'p': 30.264735, 'mp': 29.728818, 'mf': 29.653038, 'f': 30.761747, 'ff': 33.434166, 'fff': 35.216961, 'ffff': 36.711403},
    'G#1': {'pppp': 33.546659, 'ppp': 32.934216, 'pp': 32.184363, 'p': 30.685284, 'mp': 29.846761, 'mf': 29.580547, 'f': 29.919509, 'ff': 30.902204, 'fff': 31.410878, 'ffff': 31.823839},
    'A1': {'pppp': 39.993724, 'ppp': 40.878459, 'pp': 42.011951, 'p': 44.607222, 'mp': 45.603276, 'mf': 45.747373, 'f': 41.965682, 'ff': 34.775541, 'fff': 30.534202, 'ffff': 27.516724},
    'A#1': {'pppp': 46.528474, 'ppp': 46.539105, 'pp': 46.552398, 'p': 46.523652, 'mp': 46.436374, 'mf': 46.289177, 'f': 45.089092, 'ff': 42.846172, 'fff': 41.344299, 'ffff': 40.180794},
    'B1': {'pppp': 40.644762, 'ppp': 40.941229, 'pp': 41.314856, 'p': 42.079791, 'mp': 42.365165, 'mf': 42.406091, 'f': 41.555738, 'ff': 39.737322, 'fff': 38.5377, 'ffff': 37.604131},
    'C2': {'pppp': 38.356227, 'ppp': 38.489871, 'pp': 38.657582, 'p': 38.821267, 'mp': 38.881746, 'mf': 38.890394, 'f': 38.623705, 'ff': 38.052201, 'fff': 37.544389, 'ffff': 37.143024},
    'C#2': {'pppp': 27.224947, 'ppp': 27.675075, 'pp': 28.248215, 'p': 29.362602, 'mp': 29.987545, 'mf': 30.179091, 'f': 29.8155, 'ff': 28.877788, 'fff': 28.253154, 'ffff': 27.76319},
    'D2': {'pppp': 35.542868, 'ppp': 34.336033, 'pp': 32.884949, 'p': 30.168405, 'mp': 28.850436, 'mf': 28.484926, 'f': 29.39967, 'ff': 31.860405, 'fff': 33.489932, 'ffff': 34.85336},
    'D#2': {'pppp': 29.519182, 'ppp': 30.114059, 'pp': 30.874541, 'p': 32.541919, 'mp': 33.277557, 'mf': 33.433068, 'f': 32.469592, 'ff': 30.307837, 'fff': 28.941455, 'ffff': 27.892838},
    'E2': {'pppp': 25.289134, 'ppp': 27.098986, 'pp': 29.544517, 'p': 34.857887, 'mp': 37.846555, 'mf': 38.699174, 'f': 36.169895, 'ff': 30.574352, 'fff': 27.295712, 'ffff': 24.927812},
    'F2': {'pppp': 27.959597, 'ppp': 27.8202, 'pp': 27.646931, 'p': 27.472732, 'mp': 27.182093, 'mf': 26.825893, 'f': 26.346853, 'ff': 25.730982, 'fff': 25.2004, 'ffff': 24.783823},
    'F#2': {'pppp': 28.797369, 'ppp': 28.645068, 'pp': 28.455823, 'p': 27.911723, 'mp': 27.608439, 'mf': 27.513567, 'f': 27.657019, 'ff': 28.054076, 'fff': 28.151261, 'ffff': 28.229251},
    'G2': {'pppp': 23.780081, 'ppp': 24.040551, 'pp': 24.370153, 'p': 24.908972, 'mp': 25.291773, 'mf': 25.437088, 'f': 25.422711, 'ff': 25.322303, 'fff': 25.164525, 'ffff': 25.039011},
    'G#2': {'pppp': 26.835744, 'ppp': 26.485634, 'pp': 26.054413, 'p': 25.207735, 'mp': 24.601522, 'mf': 24.349348, 'f': 24.320099, 'ff': 24.309129, 'fff': 24.200693, 'ffff': 24.114292},
    'A2': {'pppp': 25.556435, 'ppp': 25.373878, 'pp': 25.147513, 'p': 24.519767, 'mp': 24.292463, 'mf': 24.260163, 'f': 24.959898, 'ff': 26.576088, 'fff': 27.576297, 'ffff': 28.4035},
    'A#2': {'pppp': 28.346452, 'ppp': 28.430112, 'pp': 28.535034, 'p': 28.655835, 'mp': 28.70047, 'mf': 28.706852, 'f': 28.135932, 'ff': 26.969585, 'fff': 26.190547, 'ffff': 25.58355},
    'B2': {'pppp': 33.796014, 'ppp': 33.052335, 'pp': 32.145707, 'p': 30.158134, 'mp': 29.38213, 'mf': 29.236044, 'f': 30.3573, 'ff': 33.146339, 'fff': 35.031662, 'ffff': 36.616841},
    'C3': {'pppp': 29.203864, 'ppp': 29.347571, 'pp': 29.528199, 'p': 29.58646, 'mp': 29.740423, 'mf': 29.959071, 'f': 30.409584, 'ff': 31.12757, 'fff': 31.468985, 'ffff': 31.744812},
    'C#3': {'pppp': 23.061539, 'ppp': 23.994275, 'pp': 25.213424, 'p': 27.552786, 'mp': 29.055702, 'mf': 29.573554, 'f': 29.045992, 'ff': 27.526149, 'fff': 26.590554, 'ffff': 25.865026},
    'D3': {'pppp': 23.244775, 'ppp': 23.083199, 'pp': 22.882808, 'p': 22.329998, 'mp': 22.079346, 'mf': 22.018994, 'f': 22.279812, 'ff': 22.921712, 'fff': 23.223678, 'ffff': 23.468112},
    'D#3': {'pppp': 28.181888, 'ppp': 28.703244, 'pp': 29.368522, 'p': 30.755335, 'mp': 31.434518, 'mf': 31.608235, 'f': 30.948012, 'ff': 29.398078, 'fff': 28.403686, 'ffff': 27.632446},
    'E3': {'pppp': 30.459734, 'ppp': 31.320012, 'pp': 32.429606, 'p': 34.970484, 'mp': 35.955978, 'mf': 36.099012, 'f': 30.569264, 'ff': 21.405973, 'fff': 16.632383, 'ffff': 13.592211},
    'F3': {'pppp': 23.581008, 'ppp': 23.147044, 'pp': 22.615801, 'p': 21.436555, 'mp': 20.947969, 'mf': 20.844837, 'f': 21.461819, 'ff': 22.993716, 'fff': 23.976134, 'ffff': 24.792205},
    'F#3': {'pppp': 22.83419, 'ppp': 23.130011, 'pp': 23.505182, 'p': 24.347667, 'mp': 24.665612, 'mf': 24.71137, 'f': 23.807963, 'ff': 21.922992, 'fff': 20.735893, 'ffff': 19.832664},
    'G3': {'pppp': 25.335211, 'ppp': 25.210161, 'pp': 25.054717, 'p': 24.983084, 'mp': 24.776694, 'mf': 24.449667, 'f': 23.104964, 'ff': 20.844549, 'fff': 19.362065, 'ffff': 18.252359},
    'G#3': {'pppp': 22.510524, 'ppp': 21.695296, 'pp': 20.717652, 'p': 20.049274, 'mp': 19.024282, 'mf': 17.836667, 'f': 16.360447, 'ff': 14.629176, 'fff': 13.313369, 'ffff': 12.346459},
    'A3': {'pppp': 19.780308, 'ppp': 18.629268, 'pp': 17.284197, 'p': 14.95216, 'mp': 13.892858, 'mf': 13.612201, 'f': 14.40213, 'ff': 16.593803, 'fff': 18.208683, 'ffff': 19.613026},
    'A#3': {'pppp': 19.863094, 'ppp': 19.916263, 'pp': 19.982926, 'p': 19.994239, 'mp': 20.028751, 'mf': 20.087386, 'f': 20.602262, 'ff': 21.643618, 'fff': 22.245668, 'ffff': 22.739343},
    'B3': {'pppp': 18.974832, 'ppp': 19.643762, 'pp': 20.513184, 'p': 22.236904, 'mp': 23.253172, 'mf': 23.575534, 'f': 23.023133, 'ff': 21.606296, 'fff': 20.725413, 'ffff': 20.046635},
    'C4': {'pppp': 19.382917, 'ppp': 19.470601, 'pp': 19.580765, 'p': 19.613095, 'mp': 19.70595, 'mf': 19.853451, 'f': 20.421098, 'ff': 21.477357, 'fff': 22.128492, 'ffff': 22.663586},
    'C#4': {'pppp': 17.725639, 'ppp': 18.05519, 'pp': 18.475759, 'p': 18.774, 'mp': 19.263036, 'mf': 19.881659, 'f': 20.743219, 'ff': 21.915587, 'fff': 22.838676, 'ffff': 23.605064},
    'D4': {'pppp': 18.058171, 'ppp': 18.432243, 'pp': 18.910748, 'p': 20.016201, 'mp': 20.439566, 'mf': 20.500773, 'f': 19.469392, 'ff': 17.345874, 'fff': 16.037211, 'ffff': 15.061734},
    'D#4': {'pppp': 24.075453, 'ppp': 22.957169, 'pp': 21.632074, 'p': 19.327821, 'mp': 18.166264, 'mf': 17.825025, 'f': 18.439956, 'ff': 20.182493, 'fff': 21.3567, 'ffff': 22.345065},
    'E4': {'pppp': 18.92758, 'ppp': 19.312955, 'pp': 19.805726, 'p': 20.947004, 'mp': 21.383856, 'mf': 21.447003, 'f': 20.506201, 'ff': 18.530091, 'fff': 17.302861, 'ffff': 16.379861},
    'F4': {'pppp': 19.563057, 'ppp': 19.91287, 'pp': 20.358946, 'p': 20.553509, 'mp': 21.072412, 'mf': 21.821993, 'f': 23.389036, 'ff': 26.044998, 'fff': 28.200248, 'ffff': 30.052167},
    'F#4': {'pppp': 23.184342, 'ppp': 23.685559, 'pp': 24.327347, 'p': 24.957376, 'mp': 25.690141, 'mf': 26.514173, 'f': 27.462888, 'ff': 28.557305, 'fff': 29.445813, 'ffff': 30.176483},
    'G4': {'pppp': 17.330944, 'ppp': 18.028156, 'pp': 18.939246, 'p': 21.051275, 'mp': 21.952231, 'mf': 22.116293, 'f': 20.725839, 'ff': 17.825216, 'fff': 16.085209, 'ffff': 14.816316},
    'G#4': {'pppp': 21.560841, 'ppp': 21.955378, 'pp': 22.458717, 'p': 23.620686, 'mp': 24.063772, 'mf': 24.127745, 'f': 23.217569, 'ff': 21.278409, 'fff': 20.063748, 'ffff': 19.142136},
    'A4': {'pppp': 19.843799, 'ppp': 20.283416, 'pp': 20.846659, 'p': 22.151038, 'mp': 22.651908, 'mf': 22.72438, 'f': 21.501613, 'ff': 18.999392, 'fff': 17.465046, 'ffff': 16.327277},
    'A#4': {'pppp': 20.829236, 'ppp': 21.312094, 'pp': 21.931438, 'p': 23.352187, 'mp': 23.898514, 'mf': 23.977597, 'f': 21.921019, 'ff': 18.030259, 'fff': 15.746924, 'ffff': 14.130279},
    'B4': {'pppp': 19.172689, 'ppp': 19.444658, 'pp': 19.790051, 'p': 20.567981, 'mp': 20.862233, 'mf': 20.904611, 'f': 19.920832, 'ff': 17.922036, 'fff': 16.68093, 'ffff': 15.750218},
    'C5': {'pppp': 17.655271, 'ppp': 18.042965, 'pp': 18.539575, 'p': 19.687867, 'mp': 20.128623, 'mf': 20.192388, 'f': 19.064488, 'ff': 16.771657, 'fff': 15.369042, 'ffff': 14.33189},
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
