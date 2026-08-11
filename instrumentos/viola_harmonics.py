# instrumentos/viola_harmonics.py
"""
Viola (arco harmonics) instrument density module.

The ``spectral_data`` table stores a committed 10-dynamic Combined Density
Metric (CDM) ladder from the ``Results`` sheet of
``OK_VIOLA_harmonics_dynamics extrapolation.xlsx``
(measured pp/mf/ff anchors; remaining levels committed from that workbook —
no runtime dynamic extrapolation).

Runtime analysis does not ingest audio; it maps notated pitch + dynamic to
these pre-loaded acoustic metadata tables.
"""

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="external_acoustic_metadata",
    citation=(
        "Viola arco_harmonic CDM ladder: measured pp/mf/ff anchors with "
        "committed Results sheet values for all 10 dynamic levels from "
        "OK_VIOLA_harmonics_dynamics extrapolation.xlsx "
        "(CDM Technique Extrapolator METApool, IOWA+ORCHIDEA collections)."
    ),
    source_url_or_identifier='docs/instrument_acoustic_sources.md#viola-harmonics',
    extraction_method=(
        "Committed full dynamic ladder from Dynamics extrapolator v1.5.2.1 Results sheet "
        "(PCHIP interiors, tapered outers r=0.80) on measured pp/mf/ff anchors; "
        "interior cells clamped into their measured segment where the workbook "
        "marginally overshoots; pitch lookup via MIDI-space spectral_lookup"
    ),
    dynamic_levels=('pppp', 'ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', 'ffff'),
    pitch_range=(60, 107),
    uncertainty="high",
    version="2026-08-11",
    source_technique="arco_harmonic",
    table_supported_techniques=("arco_harmonic",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("viola_harmonics")

# Full 10-dynamic CDM ladder (Results sheet). Anchors pp/mf/ff match measured
# workbook midpoints; other levels are workbook-committed.
spectral_data = {
    'C4': {'pppp': 16.227915, 'ppp': 16.475936, 'pp': 16.7913, 'p': 16.880853, 'mp': 17.118605, 'mf': 17.4591, 'f': 18.167656, 'ff': 19.3304, 'fff': 20.210404, 'ffff': 20.943164},
    'C#4': {'pppp': 12.738994, 'ppp': 12.946569, 'pp': 13.2108, 'p': 13.292242, 'mp': 13.504694, 'mf': 13.8009, 'f': 14.353902, 'ff': 15.2289, 'fff': 15.900977, 'ffff': 16.459933},
    'D4': {'pppp': 15.315922, 'ppp': 15.58104, 'pp': 15.9189, 'p': 16.030933, 'mp': 16.318343, 'mf': 16.7084, 'f': 17.368521, 'ff': 18.3753, 'fff': 19.160554, 'ffff': 19.81285},
    'D#4': {'pppp': 12.283199, 'ppp': 12.508306, 'pp': 12.7955, 'p': 12.901776, 'mp': 13.15636, 'mf': 13.4933, 'f': 14.018257, 'ff': 14.7898, 'fff': 15.401233, 'ffff': 15.908529},
    'E4': {'pppp': 11.120919, 'ppp': 11.336082, 'pp': 11.6109, 'p': 11.736735, 'mp': 11.982794, 'mf': 12.3018, 'f': 12.772368, 'ff': 13.4385, 'fff': 13.975249, 'ffff': 14.420043},
    'F4': {'pppp': 9.444482, 'ppp': 9.63688, 'pp': 9.8829, 'p': 10.015468, 'mp': 10.23819, 'mf': 10.5203, 'f': 10.91539, 'ff': 11.4538, 'fff': 11.895241, 'ffff': 12.260612},
    'F#4': {'pppp': 10.186189, 'ppp': 10.404162, 'pp': 10.6832, 'p': 10.854516, 'mp': 11.110166, 'mf': 11.4258, 'f': 11.846432, 'ff': 12.3979, 'fff': 12.858365, 'ffff': 13.23902},
    'G4': {'pppp': 10.899537, 'ppp': 11.143999, 'pp': 11.4573, 'p': 11.671567, 'mp': 11.962268, 'mf': 12.3114, 'f': 12.754997, 'ff': 13.3141, 'fff': 13.789971, 'ffff': 14.182884},
    'G#4': {'pppp': 9.852136, 'ppp': 10.083301, 'pp': 10.3799, 'p': 10.602219, 'mp': 10.881109, 'mf': 11.2063, 'f': 11.600789, 'ff': 12.0783, 'fff': 12.493052, 'ffff': 12.835085},
    'A4': {'pppp': 11.668977, 'ppp': 11.954867, 'pp': 12.3221, 'p': 12.620006, 'mp': 12.970112, 'mf': 13.3658, 'f': 13.824689, 'ff': 14.3576, 'fff': 14.830519, 'ffff': 15.220045},
    'A#4': {'pppp': 8.90008, 'ppp': 9.127386, 'pp': 9.4197, 'p': 9.67386, 'mp': 9.956533, 'mf': 10.2657, 'f': 10.608773, 'ff': 10.9905, 'fff': 11.337099, 'ffff': 11.622232},
    'B4': {'pppp': 9.482978, 'ppp': 9.735057, 'pp': 10.0596, 'p': 10.359713, 'mp': 10.678155, 'mf': 11.0147, 'f': 11.372245, 'ff': 11.7528, 'fff': 12.106923, 'ffff': 12.397888},
    'C5': {'pppp': 10.874309, 'ppp': 11.17475, 'pp': 11.562, 'p': 11.940456, 'mp': 12.326115, 'mf': 12.7194, 'f': 13.119558, 'ff': 13.5262, 'fff': 13.914748, 'ffff': 14.233607},
    'C#5': {'pppp': 9.898741, 'ppp': 10.182601, 'pp': 10.5489, 'p': 10.925236, 'mp': 11.295572, 'mf': 11.6595, 'f': 12.014165, 'ff': 12.3575, 'fff': 12.695112, 'ffff': 12.97183},
    'D5': {'pppp': 10.212198, 'ppp': 10.515789, 'pp': 10.908, 'p': 11.329782, 'mp': 11.732424, 'mf': 12.1132, 'f': 12.468535, 'ff': 12.7953, 'fff': 13.126877, 'ffff': 13.398314},
    'D#5': {'pppp': 9.183377, 'ppp': 9.466068, 'pp': 9.8317, 'p': 10.241741, 'mp': 10.622938, 'mf': 10.9694, 'f': 11.278825, 'ff': 11.5482, 'fff': 11.831198, 'ffff': 12.062581},
    'E5': {'pppp': 7.12805, 'ppp': 7.35501, 'pp': 7.6489, 'p': 7.991492, 'mp': 8.302697, 'mf': 8.5742, 'f': 8.806082, 'ff': 8.9964, 'fff': 9.204224, 'ffff': 9.373935},
    'F5': {'pppp': 6.603924, 'ppp': 6.821211, 'pp': 7.1029, 'p': 7.443324, 'mp': 7.746325, 'mf': 7.9997, 'f': 8.206365, 'ff': 8.3654, 'fff': 8.546842, 'ffff': 8.694824},
    'F#5': {'pppp': 7.167361, 'ppp': 7.410818, 'pp': 7.7268, 'p': 8.121726, 'mp': 8.46701, 'mf': 8.7434, 'f': 8.958356, 'ff': 9.1124, 'fff': 9.297193, 'ffff': 9.447721},
    'G5': {'pppp': 6.256393, 'ppp': 6.475582, 'pp': 6.7604, 'p': 7.127765, 'mp': 7.443949, 'mf': 7.6859, 'f': 7.864959, 'ff': 7.9834, 'fff': 8.134044, 'ffff': 8.256604},
    'G#5': {'pppp': 7.621936, 'ppp': 7.897114, 'pp': 8.2551, 'p': 8.730707, 'mp': 9.134449, 'mf': 9.4294, 'f': 9.636587, 'ff': 9.7616, 'fff': 9.932063, 'ffff': 10.070575},
    'A5': {'pppp': 7.593978, 'ppp': 7.876297, 'pp': 8.244, 'p': 8.746401, 'mp': 9.167733, 'mf': 9.4611, 'f': 9.656022, 'ff': 9.7615, 'fff': 9.918168, 'ffff': 10.04531},
    'A#5': {'pppp': 6.395272, 'ppp': 6.639906, 'pp': 6.9589, 'p': 7.40646, 'mp': 7.777822, 'mf': 8.0239, 'f': 8.177932, 'ff': 8.2509, 'fff': 8.371684, 'ffff': 8.469582},
    'B5': {'pppp': 5.39838, 'ppp': 5.610708, 'pp': 5.8879, 'p': 6.286748, 'mp': 6.614609, 'mf': 6.821, 'f': 6.93783, 'ff': 6.9904, 'fff': 7.082849, 'ffff': 7.157688},
    'C6': {'pppp': 4.595034, 'ppp': 4.780714, 'pp': 5.0234, 'p': 5.381047, 'mp': 5.67266, 'mf': 5.8468, 'f': 5.93392, 'ff': 5.972, 'fff': 6.04259, 'ffff': 6.099663},
    'C#6': {'pppp': 4.632711, 'ppp': 4.824948, 'pp': 5.0765, 'p': 5.455817, 'mp': 5.76291, 'mf': 5.9365, 'f': 6.011476, 'ff': 6.0433, 'fff': 6.106209, 'ffff': 6.157007},
    'D6': {'pppp': 4.635501, 'ppp': 4.832895, 'pp': 5.0915, 'p': 5.49011, 'mp': 5.810841, 'mf': 5.9821, 'f': 6.043853, 'ff': 6.0693, 'fff': 6.123912, 'ffff': 6.167955},
    'D#6': {'pppp': 5.52091, 'ppp': 5.762033, 'pp': 6.0783, 'p': 6.576214, 'mp': 6.974716, 'mf': 7.1752, 'f': 7.232382, 'ff': 7.25525, 'fff': 7.310235, 'ffff': 7.354523},
    'E6': {'pppp': 5.456919, 'ppp': 5.701206, 'pp': 6.022, 'p': 6.537364, 'mp': 6.947974, 'mf': 7.1422, 'f': 7.182186, 'ff': 7.197703, 'fff': 7.242105, 'ffff': 7.277823},
    'F6': {'pppp': 3.249054, 'ppp': 3.398075, 'pp': 3.594, 'p': 3.914978, 'mp': 4.169736, 'mf': 4.2827, 'f': 4.29634, 'ff': 4.301475, 'fff': 4.321921, 'ffff': 4.338348},
    'F#6': {'pppp': 3.422715, 'ppp': 3.58344, 'pp': 3.795, 'p': 4.148168, 'mp': 4.427585, 'mf': 4.5434, 'f': 4.546793, 'ff': 4.548031, 'fff': 4.563233, 'ffff': 4.575431},
    'G6': {'pppp': 3.325939, 'ppp': 3.485895, 'pp': 3.6967, 'p': 4.052843, 'mp': 4.333178, 'mf': 4.4466, 'f': 4.445298, 'ff': 4.436192, 'fff': 4.444566, 'ffff': 4.451277},
    'G#6': {'pppp': 3.086942, 'ppp': 3.23898, 'pp': 3.4396, 'p': 3.781504, 'mp': 4.049089, 'mf': 4.1569, 'f': 4.153935, 'ff': 4.133241, 'fff': 4.134926, 'ffff': 4.136275},
    'A6': {'pppp': 3.336216, 'ppp': 3.504399, 'pp': 3.7266, 'p': 4.108401, 'mp': 4.405621, 'mf': 4.5249, 'f': 4.519783, 'ff': 4.484125, 'fff': 4.479328, 'ffff': 4.475493},
    'A#6': {'pppp': 3.410843, 'ppp': 3.586773, 'pp': 3.8195, 'p': 4.222523, 'mp': 4.534696, 'mf': 4.6595, 'f': 4.652275, 'ff': 4.602014, 'fff': 4.590226, 'ffff': 4.580818},
    'B6': {'pppp': 2.924612, 'ppp': 3.078918, 'pp': 3.2833, 'p': 3.639884, 'mp': 3.914794, 'mf': 4.0243, 'f': 4.016364, 'ff': 3.961249, 'fff': 3.945145, 'ffff': 3.932309},
    'C7': {'pppp': 2.124026, 'ppp': 2.238622, 'pp': 2.3906, 'p': 2.657639, 'mp': 2.862627, 'mf': 2.944, 'f': 2.936963, 'ff': 2.888175, 'fff': 2.872106, 'ffff': 2.859316},
    'G#7': {'pppp': 1.939723, 'ppp': 2.046677, 'pp': 2.1887, 'p': 2.439928, 'mp': 2.632003, 'mf': 2.708, 'f': 2.7004, 'ff': 2.647793, 'fff': 2.6291, 'ffff': 2.61424},
    'A7': {'pppp': 1.771426, 'ppp': 1.871218, 'pp': 2.0039, 'p': 2.24013, 'mp': 2.420044, 'mf': 2.491, 'f': 2.482957, 'ff': 2.427375, 'fff': 2.406542, 'ffff': 2.390003},
    'A#7': {'pppp': 1.60889, 'ppp': 1.701467, 'pp': 1.824716, 'p': 2.04551, 'mp': 2.213082, 'mf': 2.278972, 'f': 2.270664, 'ff': 2.213344, 'fff': 2.19101, 'ffff': 2.173306},
    'B7': {'pppp': 1.582744, 'ppp': 1.675734, 'pp': 1.799691, 'p': 2.023074, 'mp': 2.192054, 'mf': 2.258306, 'f': 2.249128, 'ff': 2.185916, 'fff': 2.160543, 'ffff': 2.140457},
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
