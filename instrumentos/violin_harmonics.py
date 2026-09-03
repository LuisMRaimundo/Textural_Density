# instrumentos/violin_harmonics.py
"""
Violin (arco harmonics) instrument density module.

The ``spectral_data`` table stores a committed 10-dynamic Combined Density
Metric (CDM) ladder from the ``Results`` sheet of
``Violin_Zenodo_collections_harmonics_Dynamics10.xlsx``
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
        "Violin_Zenodo_collections_harmonics_Dynamics10.xlsx "
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
    version="2026-09-03",
    source_technique="arco_harmonic",
    table_supported_techniques=("arco_harmonic",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("violin_harmonics")

# Full 10-dynamic CDM ladder (Results sheet). Anchors pp/mf/ff match measured
# workbook midpoints; other levels are workbook-committed.
spectral_data = {
    'G5': {'pppp': 14.28128, 'ppp': 14.508909, 'pp': 14.798554, 'p': 15.043608, 'mp': 15.358828, 'mf': 15.728918, 'f': 16.183409, 'ff': 16.738575, 'fff': 17.177431, 'ffff': 17.536786},
    'G#5': {'pppp': 10.990911, 'ppp': 11.093005, 'pp': 11.221956, 'p': 11.48059, 'mp': 11.577371, 'mf': 11.591264, 'f': 11.383136, 'ff': 10.926388, 'fff': 10.638659, 'ffff': 10.413941},
    'A5': {'pppp': 9.745805, 'ppp': 9.898913, 'pp': 10.093685, 'p': 10.41372, 'mp': 10.640229, 'mf': 10.725884, 'f': 10.715188, 'ff': 10.640615, 'fff': 10.58603, 'ffff': 10.542564},
    'A#5': {'pppp': 11.780872, 'ppp': 11.88331, 'pp': 12.012611, 'p': 12.273763, 'mp': 12.371401, 'mf': 12.385413, 'f': 11.936904, 'ff': 11.022004, 'fff': 10.453142, 'ffff': 10.019264},
    'B5': {'pppp': 13.567459, 'ppp': 13.69535, 'pp': 13.85691, 'p': 14.087572, 'mp': 14.243791, 'mf': 14.301112, 'f': 14.286559, 'ff': 14.210318, 'fff': 14.141545, 'ffff': 14.086767},
    'C6': {'pppp': 10.597128, 'ppp': 10.863845, 'pp': 11.206702, 'p': 11.687471, 'mp': 12.090236, 'mf': 12.381132, 'f': 12.583698, 'ff': 12.704946, 'fff': 12.832617, 'ffff': 12.935678},
    'C#6': {'pppp': 9.614295, 'ppp': 9.726083, 'pp': 9.867648, 'p': 10.002959, 'mp': 10.145892, 'mf': 10.295834, 'f': 10.454195, 'ff': 10.62171, 'fff': 10.740906, 'ffff': 10.837226},
    'D6': {'pppp': 12.988251, 'ppp': 13.12514, 'pp': 13.298283, 'p': 13.382432, 'mp': 13.568941, 'mf': 13.812508, 'f': 14.18157, 'ff': 14.710056, 'fff': 15.090167, 'ffff': 15.401317},
    'D#6': {'pppp': 12.538514, 'ppp': 12.608143, 'pp': 12.695722, 'p': 12.721091, 'mp': 12.795066, 'mf': 12.914801, 'f': 13.451453, 'ff': 14.489821, 'fff': 15.223243, 'ffff': 15.83662},
    'E6': {'pppp': 12.093081, 'ppp': 12.191854, 'pp': 12.316457, 'p': 12.508894, 'mp': 12.610631, 'mf': 12.640122, 'f': 12.570221, 'ff': 12.393258, 'fff': 12.269806, 'ffff': 12.171929},
    'F6': {'pppp': 8.687295, 'ppp': 8.916183, 'pp': 9.210792, 'p': 9.818433, 'mp': 10.124028, 'mf': 10.204213, 'f': 9.918475, 'ff': 9.252615, 'fff': 8.840931, 'ffff': 8.524811},
    'F#6': {'pppp': 8.393136, 'ppp': 8.500445, 'pp': 8.636514, 'p': 8.880409, 'mp': 9.016331, 'mf': 9.057928, 'f': 8.979825, 'ff': 8.776764, 'fff': 8.646776, 'ffff': 8.544174},
    'G6': {'pppp': 8.820303, 'ppp': 8.946643, 'pp': 9.107117, 'p': 9.393124, 'mp': 9.561658, 'mf': 9.616262, 'f': 9.542022, 'ff': 9.337413, 'fff': 9.207047, 'ffff': 9.104067},
    'G#6': {'pppp': 9.534067, 'ppp': 9.63254, 'pp': 9.757063, 'p': 9.923373, 'mp': 10.050049, 'mf': 10.11377, 'f': 10.134345, 'ff': 10.14267, 'fff': 10.129904, 'ffff': 10.119703},
    'A6': {'pppp': 4.728054, 'ppp': 4.827788, 'pp': 4.955418, 'p': 5.176833, 'mp': 5.329563, 'mf': 5.386115, 'f': 5.370259, 'ff': 5.292045, 'fff': 5.244317, 'ffff': 5.206444},
    'A#6': {'pppp': 7.254377, 'ppp': 7.443445, 'pp': 7.686724, 'p': 8.122628, 'mp': 8.415528, 'mf': 8.521503, 'f': 8.468041, 'ff': 8.270159, 'fff': 8.151556, 'ffff': 8.057899},
    'B6': {'pppp': 8.973591, 'ppp': 9.074005, 'pp': 9.201104, 'p': 9.409705, 'mp': 9.537099, 'mf': 9.579938, 'f': 9.537022, 'ff': 9.409484, 'fff': 9.322579, 'ffff': 9.253633},
    'C7': {'pppp': 6.677031, 'ppp': 7.026898, 'pp': 7.490123, 'p': 8.36319, 'mp': 8.95623, 'mf': 9.169657, 'f': 9.01277, 'ff': 8.516876, 'fff': 8.223236, 'ffff': 7.995629},
    'C#7': {'pppp': 6.007323, 'ppp': 6.228828, 'pp': 6.517231, 'p': 7.121037, 'mp': 7.431757, 'mf': 7.514473, 'f': 7.227165, 'ff': 6.568444, 'fff': 6.165374, 'ffff': 5.8608},
    'D7': {'pppp': 5.750739, 'ppp': 5.818825, 'pp': 5.905068, 'p': 6.050568, 'mp': 6.137899, 'mf': 6.166775, 'f': 6.133402, 'ff': 6.037749, 'fff': 5.974251, 'ffff': 5.923934},
    'D#7': {'pppp': 4.468539, 'ppp': 4.565042, 'pp': 4.688607, 'p': 4.908155, 'mp': 5.053296, 'mf': 5.105231, 'f': 5.076088, 'ff': 4.972485, 'fff': 4.909116, 'ffff': 4.859004},
    'E7': {'pppp': 6.980117, 'ppp': 7.002046, 'pp': 7.029554, 'p': 7.062202, 'mp': 7.074268, 'mf': 7.075994, 'f': 6.81675, 'ff': 6.304013, 'fff': 5.985722, 'ffff': 5.7427},
    'F7': {'pppp': 6.573465, 'ppp': 6.723478, 'pp': 6.915819, 'p': 7.279688, 'mp': 7.493878, 'mf': 7.562615, 'f': 7.458591, 'ff': 7.180941, 'fff': 7.009692, 'ffff': 6.875638},
    'F#7': {'pppp': 6.946903, 'ppp': 6.967549, 'pp': 6.993442, 'p': 7.003691, 'mp': 7.007471, 'mf': 7.008011, 'f': 6.894699, 'ff': 6.663757, 'fff': 6.516907, 'ffff': 6.401761},
    'G7': {'pppp': 5.855624, 'ppp': 6.089047, 'pp': 6.393955, 'p': 7.026407, 'mp': 7.362916, 'mf': 7.456424, 'f': 7.172475, 'ff': 6.513308, 'fff': 6.110888, 'ffff': 5.806928},
    'G#7': {'pppp': 6.093235, 'ppp': 6.296904, 'pp': 6.56109, 'p': 6.990646, 'mp': 7.329155, 'mf': 7.495111, 'f': 7.538689, 'ff': 7.555953, 'fff': 7.573857, 'ffff': 7.58821},
    'A7': {'pppp': 4.068976, 'ppp': 4.101344, 'pp': 4.142165, 'p': 4.157399, 'mp': 4.197367, 'mf': 4.253555, 'f': 4.363473, 'ff': 4.537732, 'fff': 4.656698, 'ffff': 4.754113},
    'A#7': {'pppp': 3.435356, 'ppp': 3.561514, 'pp': 3.725747, 'p': 4.03711, 'mp': 4.233718, 'mf': 4.300569, 'f': 4.226875, 'ff': 4.01826, 'fff': 3.891943, 'ffff': 3.793754},
    'B7': {'pppp': 5.059493, 'ppp': 5.032683, 'pp': 4.999369, 'p': 4.914478, 'mp': 4.849872, 'mf': 4.811925, 'f': 4.791885, 'ff': 4.783086, 'fff': 4.76105, 'ffff': 4.743495},
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
