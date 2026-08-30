# instrumentos/double_bass.py
"""
Double bass (arco ordinario) instrument density module.

The ``spectral_data`` table stores a committed 10-dynamic Combined Density
Metric (CDM) ladder from the ``Results`` sheet of
``DoubleBass_Dynamics10_Arco_normal.xlsx``
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
        "DoubleBass_Dynamics10_Arco_normal.xlsx "
        "(Dynamics10 dest-Zenodo DBass_Media (IOWA+Orchidea average); Dynamics_predicter Results ladder)."
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
    version="2026-08-30",
    source_technique="arco_sustain",
    table_supported_techniques=("arco_sustain",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("double_bass")

# Full 10-dynamic CDM ladder (Results sheet). Anchors pp/mf/ff match measured
# workbook midpoints; other levels are workbook-committed.
spectral_data = {
    'E1': {'pppp': 44.021731, 'ppp': 44.756633, 'pp': 45.692536, 'p': 46.62229, 'mp': 47.647543, 'mf': 48.759456, 'f': 49.98191, 'ff': 51.32876, 'fff': 52.568071, 'ffff': 53.581029},
    'F1': {'pppp': 41.602806, 'ppp': 42.590931, 'pp': 43.859157, 'p': 45.621767, 'mp': 47.106191, 'mf': 48.201482, 'f': 48.983086, 'ff': 49.472531, 'fff': 50.108336, 'ffff': 50.622858},
    'F#1': {'pppp': 39.926759, 'ppp': 40.237653, 'pp': 40.629677, 'p': 40.772438, 'mp': 41.165752, 'mf': 41.759047, 'f': 43.354762, 'ff': 46.155967, 'fff': 48.304582, 'ffff': 50.095267},
    'G1': {'pppp': 31.313955, 'ppp': 32.205295, 'pp': 33.355233, 'p': 35.118717, 'mp': 36.533738, 'mf': 37.36637, 'f': 37.77621, 'ff': 37.954466, 'fff': 38.266089, 'ffff': 38.517229},
    'G#1': {'pppp': 29.777104, 'ppp': 30.054548, 'pp': 30.40499, 'p': 31.009551, 'mp': 31.335263, 'mf': 31.431595, 'f': 31.221308, 'ff': 30.68436, 'fff': 30.446408, 'ffff': 30.257376},
    'A1': {'pppp': 32.223165, 'ppp': 32.343361, 'pp': 32.494237, 'p': 32.506022, 'mp': 32.53865, 'mf': 32.588041, 'f': 32.728432, 'ff': 32.968252, 'fff': 33.209217, 'ffff': 33.403256},
    'A#1': {'pppp': 45.043537, 'ppp': 44.18089, 'pp': 43.125778, 'p': 41.05039, 'mp': 39.892991, 'mf': 39.526377, 'f': 39.998881, 'ff': 41.366478, 'fff': 42.261956, 'ffff': 42.992275},
    'B1': {'pppp': 37.715256, 'ppp': 39.28548, 'pp': 41.340508, 'p': 44.773411, 'mp': 47.494094, 'mf': 48.740543, 'f': 48.948286, 'ff': 49.027758, 'fff': 49.209751, 'ffff': 49.355831},
    'C2': {'pppp': 34.114651, 'ppp': 34.210875, 'pp': 34.331537, 'p': 34.352565, 'mp': 34.417178, 'mf': 34.52781, 'f': 35.662088, 'ff': 38.002027, 'fff': 39.66989, 'ffff': 41.056732},
    'C#2': {'pppp': 27.605501, 'ppp': 27.649267, 'pp': 27.704072, 'p': 27.581128, 'mp': 27.535971, 'mf': 27.529526, 'f': 27.67951, 'ff': 28.011784, 'fff': 28.27277, 'ffff': 28.483309},
    'D2': {'pppp': 29.496571, 'ppp': 29.711245, 'pp': 29.981785, 'p': 30.080934, 'mp': 30.347853, 'mf': 30.737617, 'f': 31.633193, 'ff': 33.128265, 'fff': 34.268572, 'ffff': 35.209015},
    'D#2': {'pppp': 30.77913, 'ppp': 30.760974, 'pp': 30.738294, 'p': 30.435152, 'mp': 30.296635, 'mf': 30.263302, 'f': 30.408895, 'ff': 30.762622, 'fff': 31.035734, 'ffff': 31.255968},
    'E2': {'pppp': 33.931275, 'ppp': 33.207332, 'pp': 32.324084, 'p': 30.548729, 'mp': 29.670792, 'mf': 29.425969, 'f': 30.048248, 'ff': 31.686857, 'fff': 32.799386, 'ffff': 33.717469},
    'F2': {'pppp': 26.776369, 'ppp': 27.076009, 'pp': 27.455279, 'p': 27.978315, 'mp': 28.386919, 'mf': 28.625265, 'f': 28.744454, 'ff': 28.796328, 'fff': 28.928647, 'ffff': 29.034941},
    'F#2': {'pppp': 28.291366, 'ppp': 28.523763, 'pp': 28.816945, 'p': 29.377008, 'mp': 29.605102, 'mf': 29.647234, 'f': 29.305035, 'ff': 28.523662, 'fff': 28.122992, 'ffff': 27.806512},
    'G2': {'pppp': 27.097748, 'ppp': 27.061479, 'pp': 27.01621, 'p': 26.692976, 'mp': 26.570378, 'mf': 26.550696, 'f': 26.756821, 'ff': 27.23857, 'fff': 27.578836, 'ffff': 27.854106},
    'G#2': {'pppp': 22.149291, 'ppp': 22.22623, 'pp': 22.32278, 'p': 22.424802, 'mp': 22.462506, 'mf': 22.467897, 'f': 22.10825, 'ff': 21.365374, 'fff': 20.974447, 'ffff': 20.666862},
    'A2': {'pppp': 35.354096, 'ppp': 35.551466, 'pp': 35.799729, 'p': 36.302261, 'mp': 36.489178, 'mf': 36.515959, 'f': 32.35329, 'ff': 25.111009, 'fff': 21.025557, 'ffff': 18.241232},
    'A#2': {'pppp': 28.162875, 'ppp': 28.403772, 'pp': 28.707792, 'p': 29.341989, 'mp': 29.579156, 'mf': 29.613193, 'f': 28.020235, 'ff': 24.90087, 'fff': 23.020126, 'ffff': 21.618335},
    'B2': {'pppp': 26.235885, 'ppp': 27.061589, 'pp': 28.130357, 'p': 29.732445, 'mp': 31.042552, 'mf': 31.876408, 'f': 32.3642, 'ff': 32.585356, 'fff': 32.945722, 'ffff': 33.236881},
    'C3': {'pppp': 29.747565, 'ppp': 30.487613, 'pp': 31.438615, 'p': 33.163869, 'mp': 34.295725, 'mf': 34.697354, 'f': 34.433862, 'ff': 33.551868, 'fff': 33.097909, 'ffff': 32.739168},
    'C#3': {'pppp': 29.187787, 'ppp': 28.665891, 'pp': 28.026625, 'p': 26.590757, 'mp': 26.080501, 'mf': 26.008411, 'f': 27.945162, 'ff': 32.690429, 'fff': 36.420635, 'ffff': 39.709007},
    'D3': {'pppp': 26.800899, 'ppp': 27.523134, 'pp': 28.453359, 'p': 29.483869, 'mp': 30.540944, 'mf': 31.625899, 'f': 32.737527, 'ff': 33.875396, 'fff': 34.982837, 'ffff': 35.894802},
    'D#3': {'pppp': 29.878977, 'ppp': 30.211458, 'pp': 30.632268, 'p': 31.16192, 'mp': 31.602153, 'mf': 31.928445, 'f': 32.163818, 'ff': 32.315729, 'fff': 32.541888, 'ffff': 32.723954},
    'E3': {'pppp': 33.498902, 'ppp': 32.826716, 'pp': 32.005419, 'p': 30.928281, 'mp': 30.001698, 'mf': 29.218822, 'f': 28.56388, 'ff': 28.027067, 'fff': 27.548885, 'ffff': 27.172221},
    'F3': {'pppp': 28.730906, 'ppp': 29.387859, 'pp': 30.230214, 'p': 32.062901, 'mp': 32.868468, 'mf': 33.036176, 'f': 31.959604, 'ff': 29.564063, 'fff': 28.125252, 'ffff': 27.024786},
    'F#3': {'pppp': 23.047701, 'ppp': 23.283531, 'pp': 23.581715, 'p': 23.826967, 'mp': 24.131771, 'mf': 24.482596, 'f': 24.902, 'ff': 25.400805, 'fff': 25.84178, 'ffff': 26.200066},
    'G3': {'pppp': 21.825696, 'ppp': 22.295252, 'pp': 22.896427, 'p': 23.711015, 'mp': 24.404743, 'mf': 24.936973, 'f': 25.33376, 'ff': 25.601737, 'fff': 25.933625, 'ffff': 26.20223},
    'G#3': {'pppp': 23.663973, 'ppp': 22.909505, 'pp': 22.000157, 'p': 20.390738, 'mp': 19.482149, 'mf': 19.188369, 'f': 19.482103, 'ff': 20.390599, 'fff': 20.98491, 'ffff': 21.472806},
    'A3': {'pppp': 20.536904, 'ppp': 21.096911, 'pp': 21.818441, 'p': 23.419092, 'mp': 24.110181, 'mf': 24.246429, 'f': 23.262987, 'ff': 21.116295, 'fff': 19.821047, 'ffff': 18.842291},
    'A#3': {'pppp': 19.877287, 'ppp': 20.077214, 'pp': 20.329953, 'p': 20.514547, 'mp': 20.775921, 'mf': 21.091049, 'f': 21.496334, 'ff': 22.009155, 'fff': 22.446997, 'ffff': 22.803533},
    'B3': {'pppp': 22.345752, 'ppp': 22.613003, 'pp': 22.951565, 'p': 23.25455, 'mp': 23.61049, 'mf': 24.01, 'f': 24.470476, 'ff': 25.000726, 'fff': 25.476192, 'ffff': 25.863067},
    'C4': {'pppp': 21.167931, 'ppp': 21.622567, 'pp': 22.204619, 'p': 22.570954, 'mp': 23.249127, 'mf': 24.129324, 'f': 25.418724, 'ff': 27.249829, 'fff': 28.838712, 'ffff': 30.176267},
    'C#4': {'pppp': 20.801722, 'ppp': 21.564647, 'pp': 22.557771, 'p': 24.302346, 'mp': 25.58702, 'mf': 26.083986, 'f': 26.025114, 'ff': 25.616712, 'fff': 25.436243, 'ffff': 25.292783},
    'D4': {'pppp': 25.289761, 'ppp': 25.587426, 'pp': 25.964438, 'p': 26.308558, 'mp': 26.702954, 'mf': 27.139644, 'f': 27.633778, 'ff': 28.19303, 'fff': 28.699697, 'ffff': 29.111578},
    'D#4': {'pppp': 23.202844, 'ppp': 22.690064, 'pp': 22.064995, 'p': 20.6606, 'mp': 20.161374, 'mf': 20.088756, 'f': 20.985279, 'ff': 23.199377, 'fff': 24.818684, 'ffff': 26.195139},
    'E4': {'pppp': 20.636078, 'ppp': 21.247715, 'pp': 22.037818, 'p': 23.418, 'mp': 24.418439, 'mf': 24.801778, 'f': 24.752884, 'ff': 24.41331, 'fff': 24.273052, 'ffff': 24.161426},
    'F4': {'pppp': 19.35399, 'ppp': 19.869654, 'pp': 20.533597, 'p': 21.50141, 'mp': 22.297463, 'mf': 22.831556, 'f': 23.172874, 'ff': 23.344372, 'fff': 23.604788, 'ffff': 23.815211},
    'F#4': {'pppp': 25.539128, 'ppp': 25.004196, 'pp': 24.351259, 'p': 22.870339, 'mp': 22.347738, 'mf': 22.274062, 'f': 23.284221, 'ff': 25.765555, 'fff': 27.583777, 'ffff': 29.130312},
    'G4': {'pppp': 15.393134, 'ppp': 16.221267, 'pp': 17.319363, 'p': 19.299913, 'mp': 20.768453, 'mf': 21.336434, 'f': 21.237849, 'ff': 20.589314, 'fff': 20.267885, 'ffff': 20.014359},
    'G#4': {'pppp': 19.139242, 'ppp': 19.748668, 'pp': 20.537812, 'p': 21.540489, 'mp': 22.461115, 'mf': 23.276959, 'f': 23.985061, 'ff': 24.577983, 'fff': 25.218048, 'ffff': 25.742081},
    'A4': {'pppp': 17.643065, 'ppp': 18.260869, 'pp': 19.063634, 'p': 20.425729, 'mp': 21.485513, 'mf': 21.923079, 'f': 21.93954, 'ff': 21.945566, 'fff': 21.981943, 'ffff': 22.011088},
    'A#4': {'pppp': 18.489854, 'ppp': 19.170068, 'pp': 20.055631, 'p': 21.83117, 'mp': 22.831404, 'mf': 23.132105, 'f': 22.462554, 'ff': 20.826153, 'fff': 19.850942, 'ffff': 19.103757},
    'B4': {'pppp': 17.035213, 'ppp': 17.499373, 'pp': 18.097398, 'p': 18.951881, 'mp': 19.664626, 'mf': 20.167478, 'f': 20.508089, 'ff': 20.701148, 'fff': 20.968392, 'ffff': 21.184668},
    'C5': {'pppp': 15.695856, 'ppp': 16.24302, 'pp': 16.953876, 'p': 18.177391, 'mp': 19.1103, 'mf': 19.480369, 'f': 19.466838, 'ff': 19.372384, 'fff': 19.347152, 'ffff': 19.32699},
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
