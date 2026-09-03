# instrumentos/double_bass.py
"""
Double bass (arco ordinario) instrument density module.

The ``spectral_data`` table stores a committed 10-dynamic Combined Density
Metric (CDM) ladder from the ``Results`` sheet of
``DOUBLEBASS_Zenodo_collections_Arco_normal_Dynamics10.xlsx``
(measured pp/mf/ff anchors; remaining levels committed from that workbook —
no runtime dynamic extrapolation).

Runtime analysis does not ingest audio; it maps notated pitch + dynamic to
these pre-loaded acoustic metadata tables.
"""

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="external_acoustic_metadata",
    citation=(
        "Double bass arco_sustain CDM ladder: measured pp/mf/ff anchors with "
        "committed Results sheet values for all 10 dynamic levels from "
        "DOUBLEBASS_Zenodo_collections_Arco_normal_Dynamics10.xlsx "
        "(dest Zenodo DBass_Media (IOWA+Orchidea average); Dynamics_predicter Results ladder)."
    ),
    source_url_or_identifier='docs/instrument_acoustic_sources.md#double-bass-double_bass',
    extraction_method=(
        "Committed full dynamic ladder from Dynamics extrapolator v1.5.2.1 Results sheet "
        "(PCHIP interiors, tapered outers r=0.80) on measured pp/mf/ff anchors; "
        "interior cells clamped into their measured segment where the workbook "
        "marginally overshoots; pitch lookup via MIDI-space spectral_lookup"
    ),
    dynamic_levels=('pppp', 'ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', 'ffff'),
    pitch_range=(28, 72),
    uncertainty="medium",
    version="2026-09-03",
    source_technique="arco_sustain",
    table_supported_techniques=("arco_sustain",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("double_bass")

# Full 10-dynamic CDM ladder (Results sheet). Anchors pp/mf/ff match measured
# workbook midpoints; other levels are workbook-committed.
spectral_data = {
    'E1': {'pppp': 44.038028, 'ppp': 44.765837, 'pp': 45.692536, 'p': 46.62229, 'mp': 47.647543, 'mf': 48.759456, 'f': 49.98191, 'ff': 51.32876, 'fff': 52.58869, 'ffff': 53.618865},
    'F1': {'pppp': 41.620318, 'ppp': 42.60089, 'pp': 43.859157, 'p': 45.621767, 'mp': 47.106191, 'mf': 48.201482, 'f': 48.983086, 'ff': 49.472531, 'fff': 50.129623, 'ffff': 50.661575},
    'F#1': {'pppp': 39.937825, 'ppp': 40.243848, 'pp': 40.629677, 'p': 40.772438, 'mp': 41.165752, 'mf': 41.759047, 'f': 43.354762, 'ff': 46.155967, 'fff': 48.318543, 'ffff': 50.121333},
    'G1': {'pppp': 31.327784, 'ppp': 32.213196, 'pp': 33.355233, 'p': 35.118717, 'mp': 36.533738, 'mf': 37.36637, 'f': 37.77621, 'ff': 37.954466, 'fff': 38.282257, 'ffff': 38.546526},
    'G#1': {'pppp': 29.790797, 'ppp': 30.062225, 'pp': 30.40499, 'p': 31.009551, 'mp': 31.335263, 'mf': 31.431595, 'f': 31.221308, 'ff': 30.68436, 'fff': 30.468787, 'ffff': 30.29742},
    'A1': {'pppp': 32.24511, 'ppp': 32.355596, 'pp': 32.494237, 'p': 32.506022, 'mp': 32.53865, 'mf': 32.588041, 'f': 32.728432, 'ff': 32.968252, 'fff': 33.242693, 'ffff': 33.46389},
    'A#1': {'pppp': 45.045775, 'ppp': 44.18211, 'pp': 43.125778, 'p': 41.05039, 'mp': 39.892991, 'mf': 39.526377, 'f': 39.998881, 'ff': 41.366478, 'fff': 42.277481, 'ffff': 43.020708},
    'B1': {'pppp': 37.732733, 'ppp': 39.295592, 'pp': 41.340508, 'p': 44.773411, 'mp': 47.494094, 'mf': 48.740543, 'f': 48.948286, 'ff': 49.027758, 'fff': 49.227642, 'ffff': 49.388136},
    'C2': {'pppp': 34.12412, 'ppp': 34.21615, 'pp': 34.331537, 'p': 34.352565, 'mp': 34.417178, 'mf': 34.52781, 'f': 35.662088, 'ff': 38.002027, 'fff': 39.683872, 'ffff': 41.082784},
    'C#2': {'pppp': 27.621369, 'ppp': 27.658096, 'pp': 27.704072, 'p': 27.581128, 'mp': 27.535971, 'mf': 27.529526, 'f': 27.67951, 'ff': 28.011784, 'fff': 28.298258, 'ffff': 28.529546},
    'D2': {'pppp': 29.506038, 'ppp': 29.716542, 'pp': 29.981785, 'p': 30.080934, 'mp': 30.347853, 'mf': 30.737617, 'f': 31.633193, 'ff': 33.128265, 'fff': 34.282055, 'ffff': 35.233953},
    'D#2': {'pppp': 30.794255, 'ppp': 30.769371, 'pp': 30.738294, 'p': 30.435152, 'mp': 30.296635, 'mf': 30.263302, 'f': 30.408895, 'ff': 30.762622, 'fff': 31.061457, 'ffff': 31.302615},
    'E2': {'pppp': 33.931783, 'ppp': 33.207608, 'pp': 32.324084, 'p': 30.548729, 'mp': 29.670792, 'mf': 29.425969, 'f': 30.048248, 'ff': 31.686857, 'fff': 32.808179, 'ffff': 33.73374},
    'F2': {'pppp': 26.790251, 'ppp': 27.083807, 'pp': 27.455279, 'p': 27.978315, 'mp': 28.386919, 'mf': 28.625265, 'f': 28.744454, 'ff': 28.796328, 'fff': 28.94991, 'ffff': 29.073365},
    'F#2': {'pppp': 28.303087, 'ppp': 28.530328, 'pp': 28.816945, 'p': 29.377008, 'mp': 29.605102, 'mf': 29.647234, 'f': 29.305035, 'ff': 28.523662, 'fff': 28.143072, 'ffff': 27.84226},
    'G2': {'pppp': 27.109068, 'ppp': 27.067758, 'pp': 27.01621, 'p': 26.692976, 'mp': 26.570378, 'mf': 26.550696, 'f': 26.756821, 'ff': 27.23857, 'fff': 27.598995, 'ffff': 27.890766},
    'G#2': {'pppp': 22.158236, 'ppp': 22.231216, 'pp': 22.32278, 'p': 22.424802, 'mp': 22.462506, 'mf': 22.467897, 'f': 22.10825, 'ff': 21.365374, 'fff': 20.990909, 'ffff': 20.696068},
    'A2': {'pppp': 35.357816, 'ppp': 35.553544, 'pp': 35.799729, 'p': 36.302261, 'mp': 36.489178, 'mf': 36.515959, 'f': 32.35329, 'ff': 25.111009, 'fff': 21.036582, 'ffff': 18.258453},
    'A#2': {'pppp': 28.168548, 'ppp': 28.40695, 'pp': 28.707792, 'p': 29.341989, 'mp': 29.579156, 'mf': 29.613193, 'f': 28.020235, 'ff': 24.90087, 'fff': 23.03295, 'ffff': 21.640016},
    'B2': {'pppp': 26.247199, 'ppp': 27.068071, 'pp': 28.130357, 'p': 29.732445, 'mp': 31.042552, 'mf': 31.876408, 'f': 32.3642, 'ff': 32.585356, 'fff': 32.958166, 'ffff': 33.259483},
    'C3': {'pppp': 29.759679, 'ppp': 30.494509, 'pp': 31.438615, 'p': 33.163869, 'mp': 34.295725, 'mf': 34.697354, 'f': 34.433862, 'ff': 33.551868, 'fff': 33.114291, 'ffff': 32.768341},
    'C#3': {'pppp': 29.188158, 'ppp': 28.666094, 'pp': 28.026625, 'p': 26.590757, 'mp': 26.080501, 'mf': 26.008411, 'f': 27.945162, 'ff': 32.690429, 'fff': 36.420643, 'ffff': 39.709023},
    'D3': {'pppp': 26.810433, 'ppp': 27.528573, 'pp': 28.453359, 'p': 29.483869, 'mp': 30.540944, 'mf': 31.625899, 'f': 32.737527, 'ff': 33.875396, 'fff': 34.992204, 'ffff': 35.912102},
    'D#3': {'pppp': 29.893699, 'ppp': 30.219727, 'pp': 30.632268, 'p': 31.16192, 'mp': 31.602153, 'mf': 31.928445, 'f': 32.163818, 'ff': 32.315729, 'fff': 32.564349, 'ffff': 32.764621},
    'E3': {'pppp': 33.500312, 'ppp': 32.827483, 'pp': 32.005419, 'p': 30.928281, 'mp': 30.001698, 'mf': 29.218822, 'f': 28.56388, 'ff': 28.027067, 'fff': 27.562843, 'ffff': 27.197006},
    'F3': {'pppp': 28.739468, 'ppp': 29.392724, 'pp': 30.230214, 'p': 32.062901, 'mp': 32.868468, 'mf': 33.036176, 'f': 31.959604, 'ff': 29.564063, 'fff': 28.138794, 'ffff': 27.048213},
    'F#3': {'pppp': 23.057178, 'ppp': 23.28885, 'pp': 23.581715, 'p': 23.826967, 'mp': 24.131771, 'mf': 24.482596, 'f': 24.902, 'ff': 25.400805, 'fff': 25.855894, 'ffff': 26.22583},
    'G3': {'pppp': 21.834873, 'ppp': 22.300459, 'pp': 22.896427, 'p': 23.711015, 'mp': 24.404743, 'mf': 24.936973, 'f': 25.33376, 'ff': 25.601737, 'fff': 25.945176, 'ffff': 26.223241},
    'G#3': {'pppp': 23.662432, 'ppp': 22.908676, 'pp': 22.000157, 'p': 20.390738, 'mp': 19.482149, 'mf': 19.188369, 'f': 19.482103, 'ff': 20.390599, 'fff': 20.99022, 'ffff': 21.482588},
    'A3': {'pppp': 20.542716, 'ppp': 21.100227, 'pp': 21.818441, 'p': 23.419092, 'mp': 24.110181, 'mf': 24.246429, 'f': 23.262987, 'ff': 21.116295, 'fff': 19.830027, 'ffff': 18.857659},
    'A#3': {'pppp': 19.88514, 'ppp': 20.081621, 'pp': 20.329953, 'p': 20.514547, 'mp': 20.775921, 'mf': 21.091049, 'f': 21.496334, 'ff': 22.009155, 'fff': 22.458581, 'ffff': 22.82472},
    'B3': {'pppp': 22.354612, 'ppp': 22.617984, 'pp': 22.951565, 'p': 23.25455, 'mp': 23.61049, 'mf': 24.01, 'f': 24.470476, 'ff': 25.000726, 'fff': 25.488875, 'ffff': 25.886248},
    'C4': {'pppp': 21.173943, 'ppp': 21.625979, 'pp': 22.204619, 'p': 22.570954, 'mp': 23.249127, 'mf': 24.129324, 'f': 25.418724, 'ff': 27.249829, 'fff': 28.843475, 'ffff': 30.18524},
    'C#4': {'pppp': 20.810893, 'ppp': 21.569929, 'pp': 22.557771, 'p': 24.302346, 'mp': 25.58702, 'mf': 26.083986, 'f': 26.025114, 'ff': 25.616712, 'fff': 25.446674, 'ffff': 25.311457},
    'D4': {'pppp': 25.299955, 'ppp': 25.593155, 'pp': 25.964438, 'p': 26.308558, 'mp': 26.702954, 'mf': 27.139644, 'f': 27.633778, 'ff': 28.19303, 'fff': 28.714426, 'ffff': 29.138477},
    'D#4': {'pppp': 23.703148, 'ppp': 22.960579, 'pp': 22.064995, 'p': 20.199273, 'mp': 19.502836, 'mf': 19.381032, 'f': 20.45887, 'ff': 23.199377, 'fff': 25.263864, 'ffff': 27.046965},
    'E4': {'pppp': 21.031203, 'ppp': 21.472783, 'pp': 22.037818, 'p': 22.858207, 'mp': 23.528388, 'mf': 23.978061, 'f': 24.266403, 'ff': 24.41331, 'fff': 24.652458, 'ffff': 24.845462},
    'F4': {'pppp': 19.810626, 'ppp': 20.12875, 'pp': 20.533597, 'p': 20.878305, 'mp': 21.329661, 'mf': 21.863508, 'f': 22.526439, 'ff': 23.344372, 'fff': 24.069348, 'ffff': 24.665506},
    'F#4': {'pppp': 26.348622, 'ppp': 25.44144, 'pp': 24.351259, 'p': 22.106577, 'mp': 21.277949, 'mf': 21.135267, 'f': 22.434562, 'ff': 25.765555, 'fff': 28.310844, 'ffff': 30.526954},
    'G4': {'pppp': 15.984558, 'ppp': 16.564609, 'pp': 17.319363, 'p': 18.442769, 'mp': 19.37733, 'mf': 20.002173, 'f': 20.397453, 'ff': 20.589314, 'fff': 20.889317, 'ffff': 21.132463},
    'G#4': {'pppp': 19.877136, 'ppp': 20.168105, 'pp': 20.537812, 'p': 20.697409, 'mp': 21.120157, 'mf': 21.724077, 'f': 22.947167, 'ff': 24.968026, 'fff': 26.636641, 'ffff': 28.051472},
    'A4': {'pppp': 18.467322, 'ppp': 18.730011, 'pp': 19.063634, 'p': 19.204299, 'mp': 19.581401, 'mf': 20.129923, 'f': 21.328931, 'ff': 23.365298, 'fff': 25.043168, 'ffff': 26.471809},
    'A#4': {'pppp': 19.485461, 'ppp': 19.736841, 'pp': 20.055631, 'p': 20.31534, 'mp': 20.663908, 'mf': 21.07851, 'f': 21.598906, 'ff': 22.245663, 'fff': 22.814297, 'ffff': 23.279651},
    'B4': {'pppp': 18.213748, 'ppp': 18.161945, 'pp': 18.097398, 'p': 17.912204, 'mp': 17.844453, 'mf': 17.834796, 'f': 19.189299, 'ff': 22.373689, 'fff': 24.872985, 'ffff': 27.071988},
    'C5': {'pppp': 16.920699, 'ppp': 16.935437, 'pp': 16.953876, 'p': 16.954408, 'mp': 16.956115, 'mf': 16.959161, 'f': 18.252652, 'ff': 21.258691, 'fff': 23.615894, 'ffff': 25.688497},
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
