# instrumentos/violin_harmonics.py
"""
Violin (arco harmonics) instrument density module.

The ``spectral_data`` table stores a committed 10-dynamic Combined Density
Metric (CDM) ladder from the ``Results`` sheet of
``Violin_Dynamics10_harmonics.xlsx``
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
        "Violin_Dynamics10_harmonics.xlsx "
        "(dest Zenodo Violin_harmonics Media (IOWA+Orchidea average); Dynamics_predicter Results ladder)."
    ),
    source_url_or_identifier='docs/instrument_acoustic_sources.md#violin-harmonics',
    extraction_method=(
        "Committed full dynamic ladder from Dynamics extrapolator v1.5.2.1 Results sheet "
        "(PCHIP interiors, tapered outers r=0.80) on measured pp/mf/ff anchors; "
        "interior cells clamped into their measured segment where the workbook "
        "marginally overshoots; pitch lookup via MIDI-space spectral_lookup"
    ),
    dynamic_levels=('pppp', 'ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', 'ffff'),
    pitch_range=(79, 107),
    uncertainty="high",
    version="2026-08-30",
    source_technique="arco_harmonic",
    table_supported_techniques=("arco_harmonic",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("violin_harmonics")

# Full 10-dynamic CDM ladder (Results sheet). Anchors pp/mf/ff match measured
# workbook midpoints; other levels are workbook-committed.
spectral_data = {
    'G5': {'pppp': 14.270263, 'ppp': 14.502689, 'pp': 14.798554, 'p': 15.043608, 'mp': 15.358828, 'mf': 15.728918, 'f': 16.183409, 'ff': 16.738575, 'fff': 17.152437, 'ffff': 17.490882},
    'G#5': {'pppp': 11.107889, 'ppp': 11.158442, 'pp': 11.221956, 'p': 11.244355, 'mp': 11.252618, 'mf': 11.253799, 'f': 11.147381, 'ff': 10.926388, 'fff': 10.766271, 'ffff': 10.639869},
    'A5': {'pppp': 9.735174, 'ppp': 9.892913, 'pp': 10.093685, 'p': 10.41372, 'mp': 10.640229, 'mf': 10.725884, 'f': 10.715188, 'ff': 10.640615, 'fff': 10.575841, 'ffff': 10.524306},
    'A#5': {'pppp': 11.768663, 'ppp': 11.876467, 'pp': 12.012611, 'p': 12.273763, 'mp': 12.371401, 'mf': 12.385413, 'f': 11.936904, 'ff': 11.022004, 'fff': 10.457068, 'ffff': 10.026039},
    'B5': {'pppp': 13.543747, 'ppp': 13.682047, 'pp': 13.85691, 'p': 14.087572, 'mp': 14.243791, 'mf': 14.301112, 'f': 14.286559, 'ff': 14.210318, 'fff': 14.125099, 'ffff': 14.057293},
    'C6': {'pppp': 10.594019, 'ppp': 10.862075, 'pp': 11.206702, 'p': 11.687471, 'mp': 12.090236, 'mf': 12.381132, 'f': 12.583698, 'ff': 12.704946, 'fff': 12.818787, 'ffff': 12.910594},
    'C#6': {'pppp': 9.601932, 'ppp': 9.719133, 'pp': 9.867648, 'p': 10.002959, 'mp': 10.145892, 'mf': 10.295834, 'f': 10.454195, 'ff': 10.62171, 'fff': 10.726346, 'ffff': 10.810797},
    'D6': {'pppp': 12.973107, 'ppp': 13.116636, 'pp': 13.298283, 'p': 13.382432, 'mp': 13.568941, 'mf': 13.812508, 'f': 14.18157, 'ff': 14.710056, 'fff': 15.066547, 'ffff': 15.35795},
    'D#6': {'pppp': 12.52271, 'ppp': 12.599311, 'pp': 12.695722, 'p': 12.721091, 'mp': 12.795066, 'mf': 12.914801, 'f': 13.451453, 'ff': 14.489821, 'fff': 15.193677, 'ffff': 15.781301},
    'E6': {'pppp': 11.812149, 'ppp': 12.033685, 'pp': 12.316457, 'p': 12.872763, 'mp': 13.153758, 'mf': 13.229071, 'f': 12.982322, 'ff': 12.393258, 'fff': 12.024749, 'ffff': 11.737847},
    'F6': {'pppp': 8.894031, 'ppp': 9.033446, 'pp': 9.210792, 'p': 9.549564, 'mp': 9.718966, 'mf': 9.763996, 'f': 9.613442, 'ff': 9.252615, 'fff': 9.02388, 'ffff': 8.84497},
    'F#6': {'pppp': 8.383236, 'ppp': 8.494874, 'pp': 8.636514, 'p': 8.880409, 'mp': 9.016331, 'mf': 9.057928, 'f': 8.979825, 'ff': 8.776764, 'fff': 8.641069, 'ffff': 8.534024},
    'G6': {'pppp': 8.957976, 'ppp': 9.023957, 'pp': 9.107117, 'p': 9.15875, 'mp': 9.207621, 'mf': 9.253809, 'f': 9.297107, 'ff': 9.337413, 'fff': 9.330395, 'ffff': 9.324785},
    'G#6': {'pppp': 9.517963, 'ppp': 9.623498, 'pp': 9.757063, 'p': 9.923373, 'mp': 10.050049, 'mf': 10.11377, 'f': 10.134345, 'ff': 10.14267, 'fff': 10.117295, 'ffff': 10.097041},
    'A6': {'pppp': 4.725248, 'ppp': 4.826195, 'pp': 4.955418, 'p': 5.176833, 'mp': 5.329563, 'mf': 5.386115, 'f': 5.370259, 'ff': 5.292045, 'fff': 5.240545, 'ffff': 5.199707},
    'A#6': {'pppp': 7.25271, 'ppp': 7.442494, 'pp': 7.686724, 'p': 8.122628, 'mp': 8.415528, 'mf': 8.521503, 'f': 8.468041, 'ff': 8.270159, 'fff': 8.147516, 'ffff': 8.050712},
    'B6': {'pppp': 8.960675, 'ppp': 9.066747, 'pp': 9.201104, 'p': 9.409705, 'mp': 9.537099, 'mf': 9.579938, 'f': 9.537022, 'ff': 9.409484, 'fff': 9.314053, 'ffff': 9.238406},
    'C7': {'pppp': 6.682511, 'ppp': 7.030101, 'pp': 7.490123, 'p': 8.36319, 'mp': 8.95623, 'mf': 9.169657, 'f': 9.01277, 'ff': 8.516876, 'fff': 8.223505, 'ffff': 7.996101},
    'C#7': {'pppp': 6.009081, 'ppp': 6.229841, 'pp': 6.517231, 'p': 7.121037, 'mp': 7.431757, 'mf': 7.514473, 'f': 7.227165, 'ff': 6.568444, 'fff': 6.168319, 'ffff': 5.865842},
    'D7': {'pppp': 5.742992, 'ppp': 5.814469, 'pp': 5.905068, 'p': 6.050568, 'mp': 6.137899, 'mf': 6.166775, 'f': 6.133402, 'ff': 6.037749, 'fff': 5.969201, 'ffff': 5.914924},
    'D#7': {'pppp': 4.466202, 'ppp': 4.563715, 'pp': 4.688607, 'p': 4.908155, 'mp': 5.053296, 'mf': 5.105231, 'f': 5.076088, 'ff': 4.972485, 'fff': 4.906209, 'ffff': 4.853824},
    'E7': {'pppp': 6.970076, 'ppp': 6.996448, 'pp': 7.029554, 'p': 7.062202, 'mp': 7.074268, 'mf': 7.075994, 'f': 6.81675, 'ff': 6.304013, 'fff': 5.987791, 'ffff': 5.746274},
    'F7': {'pppp': 5.119033, 'ppp': 5.445876, 'pp': 5.883932, 'p': 6.805179, 'mp': 7.341238, 'mf': 7.503067, 'f': 7.120135, 'ff': 6.228868, 'fff': 5.701857, 'ffff': 5.312539},
    'F#7': {'pppp': 5.842032, 'ppp': 6.004644, 'pp': 6.214289, 'p': 6.698803, 'mp': 6.886678, 'mf': 6.913945, 'f': 6.494178, 'ff': 5.63996, 'fff': 5.128271, 'ffff': 4.752552},
    'G7': {'pppp': 4.50034, 'ppp': 4.856442, 'pp': 5.341453, 'p': 6.449371, 'mp': 7.033482, 'mf': 7.182045, 'f': 6.554843, 'ff': 5.259559, 'fff': 4.529053, 'ffff': 4.018406},
    'G#7': {'pppp': 3.947414, 'ppp': 4.305079, 'pp': 4.798072, 'p': 5.862863, 'mp': 6.521023, 'mf': 6.728117, 'f': 6.284056, 'ff': 5.267359, 'fff': 4.68366, 'ffff': 4.263628},
    'A7': {'pppp': 5.080694, 'ppp': 5.010818, 'pp': 4.924824, 'p': 4.736926, 'mp': 4.611734, 'mf': 4.565975, 'f': 4.571766, 'ff': 4.612512, 'fff': 4.619706, 'ffff': 4.62547},
    'A#7': {'pppp': 3.995489, 'ppp': 4.104509, 'pp': 4.244977, 'p': 4.541424, 'mp': 4.683691, 'mf': 4.71827, 'f': 4.564455, 'ff': 4.214883, 'fff': 4.000387, 'ffff': 3.836678},
    'B7': {'pppp': 4.930528, 'ppp': 4.920731, 'pp': 4.908513, 'p': 4.897625, 'mp': 4.866593, 'mf': 4.818004, 'f': 4.63889, 'ff': 4.334977, 'fff': 4.134689, 'ffff': 3.981141},
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
