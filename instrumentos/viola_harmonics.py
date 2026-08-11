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
    pitch_range=(60, 96),
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
    'C4': {'pppp': 16.246484, 'ppp': 16.486407, 'pp': 16.7913, 'p': 16.880853, 'mp': 17.118605, 'mf': 17.4591, 'f': 18.167656, 'ff': 19.3304, 'fff': 20.224169, 'ffff': 20.968847},
    'C#4': {'pppp': 12.753462, 'ppp': 12.954735, 'pp': 13.2108, 'p': 13.292242, 'mp': 13.504694, 'mf': 13.8009, 'f': 14.353902, 'ff': 15.2289, 'fff': 15.911727, 'ffff': 16.479967},
    'D4': {'pppp': 15.333186, 'ppp': 15.590795, 'pp': 15.9189, 'p': 16.030933, 'mp': 16.318343, 'mf': 16.7084, 'f': 17.368521, 'ff': 18.3753, 'fff': 19.173409, 'ffff': 19.836784},
    'D#4': {'pppp': 12.29694, 'ppp': 12.516078, 'pp': 12.7955, 'p': 12.901776, 'mp': 13.15636, 'mf': 13.4933, 'f': 14.018257, 'ff': 14.7898, 'fff': 15.411488, 'ffff': 15.927602},
    'E4': {'pppp': 11.133266, 'ppp': 11.343073, 'pp': 11.6109, 'p': 11.736735, 'mp': 11.982794, 'mf': 12.3018, 'f': 12.772368, 'ff': 13.4385, 'fff': 13.984485, 'ffff': 14.437201},
    'F4': {'pppp': 9.454888, 'ppp': 9.642778, 'pp': 9.8829, 'p': 10.015468, 'mp': 10.23819, 'mf': 10.5203, 'f': 10.91539, 'ff': 11.4538, 'fff': 11.903042, 'ffff': 12.27509},
    'F#4': {'pppp': 10.197327, 'ppp': 10.410481, 'pp': 10.6832, 'p': 10.854516, 'mp': 11.110166, 'mf': 11.4258, 'f': 11.846432, 'ff': 12.3979, 'fff': 12.866733, 'ffff': 13.254533},
    'G4': {'pppp': 10.911364, 'ppp': 11.150715, 'pp': 11.4573, 'p': 11.671567, 'mp': 11.962268, 'mf': 12.3114, 'f': 12.754997, 'ff': 13.3141, 'fff': 13.798877, 'ffff': 14.199377},
    'G#4': {'pppp': 9.862744, 'ppp': 10.089331, 'pp': 10.3799, 'p': 10.602219, 'mp': 10.881109, 'mf': 11.2063, 'f': 11.600789, 'ff': 12.0783, 'fff': 12.501059, 'ffff': 12.849896},
    'A4': {'pppp': 11.681444, 'ppp': 11.961961, 'pp': 12.3221, 'p': 12.620006, 'mp': 12.970112, 'mf': 13.3658, 'f': 13.824689, 'ff': 14.3576, 'fff': 14.83995, 'ffff': 15.237471},
    'A#4': {'pppp': 8.909515, 'ppp': 9.13276, 'pp': 9.4197, 'p': 9.67386, 'mp': 9.956533, 'mf': 10.2657, 'f': 10.608773, 'ff': 10.9905, 'fff': 11.344253, 'ffff': 11.635436},
    'B4': {'pppp': 9.492953, 'ppp': 9.740745, 'pp': 10.0596, 'p': 10.359713, 'mp': 10.678155, 'mf': 11.0147, 'f': 11.372245, 'ff': 11.7528, 'fff': 12.114503, 'ffff': 12.411864},
    'C5': {'pppp': 10.885659, 'ppp': 11.181228, 'pp': 11.562, 'p': 11.940456, 'mp': 12.326115, 'mf': 12.7194, 'f': 13.119558, 'ff': 13.5262, 'fff': 13.923392, 'ffff': 14.249527},
    'C#5': {'pppp': 9.908992, 'ppp': 10.188458, 'pp': 10.5489, 'p': 10.925236, 'mp': 11.295572, 'mf': 11.6595, 'f': 12.014165, 'ff': 12.3575, 'fff': 12.702937, 'ffff': 12.986225},
    'D5': {'pppp': 10.22269, 'ppp': 10.521789, 'pp': 10.908, 'p': 11.329782, 'mp': 11.732424, 'mf': 12.1132, 'f': 12.468535, 'ff': 12.7953, 'fff': 13.134904, 'ffff': 13.413065},
    'D#5': {'pppp': 9.192737, 'ppp': 9.471427, 'pp': 9.8317, 'p': 10.241741, 'mp': 10.622938, 'mf': 10.9694, 'f': 11.278825, 'ff': 11.5482, 'fff': 11.838376, 'ffff': 12.075757},
    'E5': {'pppp': 7.135258, 'ppp': 7.359141, 'pp': 7.6489, 'p': 7.991492, 'mp': 8.302697, 'mf': 8.5742, 'f': 8.806082, 'ff': 8.9964, 'fff': 9.209764, 'ffff': 9.384093},
    'F5': {'pppp': 6.610549, 'ppp': 6.825012, 'pp': 7.1029, 'p': 7.443324, 'mp': 7.746325, 'mf': 7.9997, 'f': 8.206365, 'ff': 8.3654, 'fff': 8.551945, 'ffff': 8.704172},
    'F#5': {'pppp': 7.174494, 'ppp': 7.414914, 'pp': 7.7268, 'p': 8.121726, 'mp': 8.46701, 'mf': 8.7434, 'f': 8.958356, 'ff': 9.1124, 'fff': 9.302699, 'ffff': 9.457796},
    'G5': {'pppp': 6.262569, 'ppp': 6.479133, 'pp': 6.7604, 'p': 7.127765, 'mp': 7.443949, 'mf': 7.6859, 'f': 7.864959, 'ff': 7.9834, 'fff': 8.138824, 'ffff': 8.265338},
    'G#5': {'pppp': 7.6294, 'ppp': 7.90141, 'pp': 8.2551, 'p': 8.730707, 'mp': 9.134449, 'mf': 9.4294, 'f': 9.636587, 'ff': 9.7616, 'fff': 9.937852, 'ffff': 10.081142},
    'A5': {'pppp': 7.601354, 'ppp': 7.880546, 'pp': 8.244, 'p': 8.746401, 'mp': 9.167733, 'mf': 9.4611, 'f': 9.656022, 'ff': 9.7615, 'fff': 9.923901, 'ffff': 10.055766},
    'A#5': {'pppp': 6.401433, 'ppp': 6.643459, 'pp': 6.9589, 'p': 7.40646, 'mp': 7.777822, 'mf': 8.0239, 'f': 8.177932, 'ff': 8.2509, 'fff': 8.376484, 'ffff': 8.478326},
    'B5': {'pppp': 5.403539, 'ppp': 5.613686, 'pp': 5.8879, 'p': 6.286748, 'mp': 6.614609, 'mf': 6.821, 'f': 6.93783, 'ff': 6.9904, 'fff': 7.086877, 'ffff': 7.165017},
    'C6': {'pppp': 4.599389, 'ppp': 4.78323, 'pp': 5.0234, 'p': 5.381047, 'mp': 5.67266, 'mf': 5.8468, 'f': 5.93392, 'ff': 5.972, 'fff': 6.045999, 'ffff': 6.105858},
    'C#6': {'pppp': 4.637065, 'ppp': 4.827467, 'pp': 5.0765, 'p': 5.455817, 'mp': 5.76291, 'mf': 5.9365, 'f': 6.011476, 'ff': 6.0433, 'fff': 6.109625, 'ffff': 6.163208},
    'D6': {'pppp': 4.639822, 'ppp': 4.835398, 'pp': 5.0915, 'p': 5.49011, 'mp': 5.810841, 'mf': 5.9821, 'f': 6.043853, 'ff': 6.0693, 'fff': 6.12731, 'ffff': 6.174116},
    'D#6': {'pppp': 5.526014, 'ppp': 5.764992, 'pp': 6.0783, 'p': 6.576214, 'mp': 6.974716, 'mf': 7.1752, 'f': 7.232382, 'ff': 7.25525, 'fff': 7.314258, 'ffff': 7.361809},
    'E6': {'pppp': 5.461921, 'ppp': 5.704109, 'pp': 6.022, 'p': 6.537364, 'mp': 6.947974, 'mf': 7.1422, 'f': 7.182186, 'ff': 7.197703, 'fff': 7.246057, 'ffff': 7.284973},
    'F6': {'pppp': 3.252008, 'ppp': 3.399791, 'pp': 3.594, 'p': 3.914978, 'mp': 4.169736, 'mf': 4.2827, 'f': 4.29634, 'ff': 4.301475, 'fff': 4.324259, 'ffff': 4.342574},
    'F#6': {'pppp': 3.425801, 'ppp': 3.585234, 'pp': 3.795, 'p': 4.148168, 'mp': 4.427585, 'mf': 4.5434, 'f': 4.546793, 'ff': 4.548031, 'fff': 4.565682, 'ffff': 4.579851},
    'G6': {'pppp': 3.328871, 'ppp': 3.487601, 'pp': 3.6967, 'p': 4.052843, 'mp': 4.333178, 'mf': 4.4466, 'f': 4.445298, 'ff': 4.436192, 'fff': 4.446898, 'ffff': 4.455481},
    'G#6': {'pppp': 3.089587, 'ppp': 3.240521, 'pp': 3.4396, 'p': 3.781504, 'mp': 4.049089, 'mf': 4.1569, 'f': 4.153935, 'ff': 4.133241, 'fff': 4.137035, 'ffff': 4.140073},
    'A6': {'pppp': 3.338997, 'ppp': 3.506021, 'pp': 3.7266, 'p': 4.108401, 'mp': 4.405621, 'mf': 4.5249, 'f': 4.519783, 'ff': 4.484125, 'fff': 4.481549, 'ffff': 4.47949},
    'A#6': {'pppp': 3.413608, 'ppp': 3.588388, 'pp': 3.8195, 'p': 4.222523, 'mp': 4.534696, 'mf': 4.6595, 'f': 4.652275, 'ff': 4.602014, 'fff': 4.592441, 'ffff': 4.584797},
    'B6': {'pppp': 2.926919, 'ppp': 3.080267, 'pp': 3.2833, 'p': 3.639884, 'mp': 3.914794, 'mf': 4.0243, 'f': 4.016364, 'ff': 3.961249, 'fff': 3.946997, 'ffff': 3.935633},
    'C7': {'pppp': 2.125657, 'ppp': 2.239577, 'pp': 2.3906, 'p': 2.657639, 'mp': 2.862627, 'mf': 2.944, 'f': 2.936963, 'ff': 2.888175, 'fff': 2.873419, 'ffff': 2.861668},
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
