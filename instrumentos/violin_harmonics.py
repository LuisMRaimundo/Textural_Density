# instrumentos/violin_harmonics.py
"""
Violin (arco harmonics) instrument density module.

The ``spectral_data`` table stores a committed 10-dynamic Combined Density
Metric (CDM) ladder from the ``Results`` sheet of
``OK_VIOLIN_harmonics_dynamics extrapolation.xlsx``
(measured pp/mf/ff anchors; remaining levels committed from that workbook —
no runtime dynamic extrapolation).

Runtime analysis does not ingest audio; it maps notated pitch + dynamic to
these pre-loaded acoustic metadata tables.
"""

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="external_acoustic_metadata",
    citation=(
        "Violin arco_harmonic CDM ladder: measured pp/mf/ff anchors with "
        "committed Results sheet values for all 10 dynamic levels from "
        "OK_VIOLIN_harmonics_dynamics extrapolation.xlsx "
        "(CDM Technique Extrapolator METApool, IOWA+ORCHIDEA collections)."
    ),
    source_url_or_identifier='docs/instrument_acoustic_sources.md#violin-harmonics',
    extraction_method=(
        "Committed full dynamic ladder from Dynamics extrapolator v1.5.2.1 Results sheet "
        "(PCHIP interiors, tapered outers r=0.80) on measured pp/mf/ff anchors; "
        "interior cells clamped into their measured segment where the workbook "
        "marginally overshoots; pitch lookup via MIDI-space spectral_lookup"
    ),
    dynamic_levels=('pppp', 'ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', 'ffff'),
    pitch_range=(67, 103),
    uncertainty="high",
    version="2026-08-11",
    source_technique="arco_harmonic",
    table_supported_techniques=("arco_harmonic",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("violin_harmonics")

# Full 10-dynamic CDM ladder (Results sheet). Anchors pp/mf/ff match measured
# workbook midpoints; other levels are workbook-committed.
spectral_data = {
    'G4': {'pppp': 16.857521, 'ppp': 17.106456, 'pp': 17.4228, 'p': 17.515719, 'mp': 17.762405, 'mf': 18.1157, 'f': 18.850909, 'ff': 20.0574, 'fff': 20.984814, 'ffff': 21.757527},
    'G#4': {'pppp': 11.815904, 'ppp': 12.002372, 'pp': 12.2396, 'p': 12.315052, 'mp': 12.511878, 'mf': 12.7863, 'f': 13.298639, 'ff': 14.1093, 'fff': 14.741933, 'ffff': 15.268403},
    'A4': {'pppp': 14.033189, 'ppp': 14.268938, 'pp': 14.5692, 'p': 14.671723, 'mp': 14.93474, 'mf': 15.2917, 'f': 15.895853, 'ff': 16.8173, 'fff': 17.547771, 'ffff': 18.154928},
    'A#4': {'pppp': 12.039585, 'ppp': 12.254132, 'pp': 12.5277, 'p': 12.631762, 'mp': 12.881017, 'mf': 13.2109, 'f': 13.724849, 'ff': 14.4802, 'fff': 15.08886, 'ffff': 15.594158},
    'B4': {'pppp': 14.882565, 'ppp': 15.163006, 'pp': 15.521, 'p': 15.689168, 'mp': 16.018075, 'mf': 16.4445, 'f': 17.073563, 'ff': 17.9641, 'fff': 18.694018, 'ffff': 19.299249},
    'C5': {'pppp': 9.8178, 'ppp': 10.012884, 'pp': 10.2622, 'p': 10.399819, 'mp': 10.631073, 'mf': 10.924, 'f': 11.33427, 'ff': 11.8934, 'fff': 12.35993, 'ffff': 12.746295},
    'C#5': {'pppp': 9.054522, 'ppp': 9.243769, 'pp': 9.4859, 'p': 9.637978, 'mp': 9.864955, 'mf': 10.1452, 'f': 10.518698, 'ff': 11.0084, 'fff': 11.424722, 'ffff': 11.769087},
    'D5': {'pppp': 10.757063, 'ppp': 10.993038, 'pp': 11.2953, 'p': 11.506573, 'mp': 11.793188, 'mf': 12.1374, 'f': 12.574725, 'ff': 13.1259, 'fff': 13.603826, 'ffff': 13.998666},
    'D#5': {'pppp': 9.747812, 'ppp': 9.971741, 'pp': 10.2589, 'p': 10.478588, 'mp': 10.754208, 'mf': 11.0756, 'f': 11.465507, 'ff': 11.9375, 'fff': 12.355372, 'ffff': 12.700178},
    'E5': {'pppp': 13.6977, 'ppp': 14.02662, 'pp': 14.4489, 'p': 14.798203, 'mp': 15.208725, 'mf': 15.6727, 'f': 16.210795, 'ff': 16.8357, 'fff': 17.401327, 'ffff': 17.867481},
    'F5': {'pppp': 10.621618, 'ppp': 10.887745, 'pp': 11.2298, 'p': 11.532767, 'mp': 11.869736, 'mf': 12.2383, 'f': 12.6473, 'ff': 13.1024, 'fff': 13.524153, 'ffff': 13.871309},
    'F#5': {'pppp': 10.161386, 'ppp': 10.426612, 'pp': 10.7679, 'p': 11.089134, 'mp': 11.429981, 'mf': 11.7902, 'f': 12.17289, 'ff': 12.5802, 'fff': 12.967351, 'ffff': 13.285632},
    'G5': {'pppp': 10.728924, 'ppp': 11.020226, 'pp': 11.3955, 'p': 11.768488, 'mp': 12.148583, 'mf': 12.5362, 'f': 12.9306, 'ff': 13.3314, 'fff': 13.722893, 'ffff': 14.04435},
    'G#5': {'pppp': 9.122767, 'ppp': 9.380058, 'pp': 9.7119, 'p': 10.058388, 'mp': 10.399347, 'mf': 10.7344, 'f': 11.060919, 'ff': 11.377, 'fff': 11.695031, 'ffff': 11.955846},
    'A5': {'pppp': 8.661281, 'ppp': 8.914689, 'pp': 9.2419, 'p': 9.599254, 'mp': 9.940391, 'mf': 10.263, 'f': 10.564054, 'ff': 10.8409, 'fff': 11.128636, 'ffff': 11.364314},
    'A#5': {'pppp': 7.126555, 'ppp': 7.342604, 'pp': 7.6219, 'p': 7.939786, 'mp': 8.235309, 'mf': 8.5039, 'f': 8.743775, 'ff': 8.9526, 'fff': 9.17756, 'ffff': 9.361592},
    'B5': {'pppp': 8.567888, 'ppp': 8.83674, 'pp': 9.1847, 'p': 9.596145, 'mp': 9.969877, 'mf': 10.2959, 'f': 10.574318, 'ff': 10.8028, 'fff': 11.058983, 'ffff': 11.268297},
    'C6': {'pppp': 7.40339, 'ppp': 7.643578, 'pp': 7.9548, 'p': 8.336084, 'mp': 8.675442, 'mf': 8.9592, 'f': 9.190629, 'ff': 9.3687, 'fff': 9.577601, 'ffff': 9.74807},
    'C#6': {'pppp': 6.086119, 'ppp': 6.29005, 'pp': 6.5546, 'p': 6.889562, 'mp': 7.182434, 'mf': 7.4169, 'f': 7.599276, 'ff': 7.73, 'fff': 7.891472, 'ffff': 8.023075},
    'D6': {'pppp': 6.319456, 'ppp': 6.537984, 'pp': 6.8218, 'p': 7.1925, 'mp': 7.511553, 'mf': 7.7557, 'f': 7.936384, 'ff': 8.0559, 'fff': 8.212742, 'ffff': 8.340411},
    'D#6': {'pppp': 6.976162, 'ppp': 7.224887, 'pp': 7.5483, 'p': 7.983219, 'mp': 8.352411, 'mf': 8.6221, 'f': 8.811524, 'ff': 8.9258, 'fff': 9.086945, 'ffff': 9.217953},
    'E6': {'pppp': 7.038636, 'ppp': 7.297156, 'pp': 7.6337, 'p': 8.0989, 'mp': 8.489039, 'mf': 8.7607, 'f': 8.94121, 'ff': 9.0389, 'fff': 9.189304, 'ffff': 9.311427},
    'F6': {'pppp': 5.749077, 'ppp': 5.966424, 'pp': 6.2497, 'p': 6.651611, 'mp': 6.9851, 'mf': 7.2061, 'f': 7.344447, 'ff': 7.41, 'fff': 7.522807, 'ffff': 7.614288},
    'F#6': {'pppp': 5.359843, 'ppp': 5.568296, 'pp': 5.8403, 'p': 6.235951, 'mp': 6.56118, 'mf': 6.7659, 'f': 6.881766, 'ff': 6.9339, 'fff': 7.029591, 'ffff': 7.107093},
    'G6': {'pppp': 4.989466, 'ppp': 5.188926, 'pp': 5.4495, 'p': 5.837586, 'mp': 6.154005, 'mf': 6.3429, 'f': 6.437331, 'ff': 6.4786, 'fff': 6.55883, 'ffff': 6.62373},
    'G#6': {'pppp': 5.491232, 'ppp': 5.716701, 'pp': 6.0116, 'p': 6.460801, 'mp': 6.824463, 'mf': 7.03, 'f': 7.118738, 'ff': 7.1564, 'fff': 7.234918, 'ffff': 7.298352},
    'A6': {'pppp': 5.472187, 'ppp': 5.702851, 'pp': 6.0049, 'p': 6.475045, 'mp': 6.85333, 'mf': 7.0553, 'f': 7.128102, 'ff': 7.1581, 'fff': 7.226504, 'ffff': 7.281698},
    'A#6': {'pppp': 3.999675, 'ppp': 4.172639, 'pp': 4.3994, 'p': 4.759785, 'mp': 5.048211, 'mf': 5.1933, 'f': 5.234661, 'ff': 5.2512, 'fff': 5.293898, 'ffff': 5.328306},
    'B6': {'pppp': 3.676358, 'ppp': 3.839355, 'pp': 4.0533, 'p': 4.400131, 'mp': 4.676466, 'mf': 4.8072, 'f': 4.834143, 'ff': 4.8446, 'fff': 4.877168, 'ffff': 4.90338},
    'C7': {'pppp': 4.238523, 'ppp': 4.431117, 'pp': 4.684213, 'p': 5.102503, 'mp': 5.434497, 'mf': 5.581725, 'f': 5.599526, 'ff': 5.606227, 'fff': 5.635942, 'ffff': 5.659827},
    'C#7': {'pppp': 4.294785, 'ppp': 4.494667, 'pp': 4.757651, 'p': 5.200426, 'mp': 5.550738, 'mf': 5.695943, 'f': 5.700201, 'ff': 5.701756, 'fff': 5.723891, 'ffff': 5.741661},
    'D7': {'pppp': 2.767529, 'ppp': 2.899492, 'pp': 3.073329, 'p': 3.369416, 'mp': 3.602481, 'mf': 3.696777, 'f': 3.695696, 'ff': 3.688137, 'fff': 3.697046, 'ffff': 3.704189},
    'D#7': {'pppp': 2.613794, 'ppp': 2.741474, 'pp': 2.909881, 'p': 3.199103, 'mp': 3.42546, 'mf': 3.516661, 'f': 3.514156, 'ff': 3.496673, 'fff': 3.499898, 'ffff': 3.50248},
    'E7': {'pppp': 4.280485, 'ppp': 4.494604, 'pp': 4.777378, 'p': 5.266842, 'mp': 5.647867, 'mf': 5.800777, 'f': 5.794211, 'ff': 5.748459, 'fff': 5.745142, 'ffff': 5.742489},
    'F7': {'pppp': 4.494038, 'ppp': 4.724148, 'pp': 5.028424, 'p': 5.559045, 'mp': 5.97005, 'mf': 6.134365, 'f': 6.124849, 'ff': 6.058647, 'fff': 6.046033, 'ffff': 6.035961},
    'F#7': {'pppp': 4.321545, 'ppp': 4.547957, 'pp': 4.847725, 'p': 5.3742, 'mp': 5.780098, 'mf': 5.941784, 'f': 5.930075, 'ff': 5.848759, 'fff': 5.827751, 'ffff': 5.810999},
    'G7': {'pppp': 3.838691, 'ppp': 4.044392, 'pp': 4.317087, 'p': 4.799261, 'mp': 5.16939, 'mf': 5.316318, 'f': 5.303614, 'ff': 5.215531, 'fff': 5.1889, 'ffff': 5.167693},
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
