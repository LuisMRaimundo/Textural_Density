# instrumentos/cello_harmonics.py
"""
Cello (arco harmonics) instrument density module.

The ``spectral_data`` table stores a committed 10-dynamic Combined Density
Metric (CDM) ladder from the ``Results`` sheet of
``Cello_Dynamics10_harmonics.xlsx``
(measured pp/mf/ff anchors; remaining levels committed from that workbook —
no runtime dynamic extrapolation).

Runtime analysis does not ingest audio; it maps notated pitch + dynamic to
these pre-loaded acoustic metadata tables.
"""

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="external_acoustic_metadata",
    citation=(
        "Cello arco_harmonic CDM ladder: measured pp/mf/ff anchors with "
        "committed Results sheet values for all 10 dynamic levels from "
        "Cello_Dynamics10_harmonics.xlsx "
        "(dest Zenodo Cello_harmonics Media (IOWA+Orchidea average); Dynamics_predicter Results ladder)."
    ),
    source_url_or_identifier='docs/instrument_acoustic_sources.md#cello-harmonics',
    extraction_method=(
        "Committed full dynamic ladder from Dynamics extrapolator v1.5.2.1 Results sheet "
        "(PCHIP interiors, tapered outers r=0.80) on measured pp/mf/ff anchors; "
        "interior cells clamped into their measured segment where the workbook "
        "marginally overshoots; pitch lookup via MIDI-space spectral_lookup"
    ),
    dynamic_levels=('pppp', 'ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', 'ffff'),
    pitch_range=(60, 84),
    uncertainty="high",
    version="2026-08-27",
    source_technique="arco_harmonic",
    table_supported_techniques=("arco_harmonic",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("cello_harmonics")

# Full 10-dynamic CDM ladder (Results sheet). Anchors pp/mf/ff match measured
# workbook midpoints; other levels are workbook-committed.
spectral_data = {
    'C4': {'pppp': 22.88461, 'ppp': 22.441255, 'pp': 21.899122, 'p': 20.725169, 'mp': 20.308708, 'mf': 20.2499, 'f': 21.016675, 'ff': 22.886292, 'fff': 24.222592, 'ffff': 25.347595},
    'C#4': {'pppp': 18.452082, 'ppp': 18.374946, 'pp': 18.27898, 'p': 18.05123, 'mp': 17.935679, 'mf': 17.903298, 'f': 17.988486, 'ff': 18.205448, 'fff': 18.278119, 'ffff': 18.336464},
    'D4': {'pppp': 17.792076, 'ppp': 18.593493, 'pp': 19.646216, 'p': 21.599395, 'mp': 22.903454, 'mf': 23.367825, 'f': 23.010992, 'ff': 21.894156, 'fff': 21.20996, 'ffff': 20.678029},
    'D#4': {'pppp': 27.451503, 'ppp': 27.104379, 'pp': 26.676639, 'p': 26.373845, 'mp': 25.889106, 'mf': 25.304073, 'f': 24.536171, 'ff': 23.57236, 'fff': 22.788876, 'ffff': 22.18088},
    'E4': {'pppp': 21.675471, 'ppp': 21.870151, 'pp': 22.115962, 'p': 22.580799, 'mp': 22.874665, 'mf': 22.976599, 'f': 22.902158, 'ff': 22.659422, 'fff': 22.471585, 'ffff': 22.322437},
    'F4': {'pppp': 17.335689, 'ppp': 17.959397, 'pp': 18.770682, 'p': 20.342462, 'mp': 21.279639, 'mf': 21.580538, 'f': 21.098103, 'ff': 19.844348, 'fff': 19.055283, 'ffff': 18.446683},
    'F#4': {'pppp': 16.501952, 'ppp': 16.823211, 'pp': 17.233593, 'p': 18.073224, 'mp': 18.504815, 'mf': 18.62304, 'f': 18.26215, 'ff': 17.395902, 'fff': 16.835645, 'ffff': 16.400459},
    'G4': {'pppp': 22.732037, 'ppp': 22.984748, 'pp': 23.304592, 'p': 24.033588, 'mp': 24.307877, 'mf': 24.347316, 'f': 23.342561, 'ff': 21.290493, 'fff': 19.973872, 'ffff': 18.979445},
    'G#4': {'pppp': 15.52182, 'ppp': 15.948662, 'pp': 16.49876, 'p': 17.495133, 'mp': 18.165726, 'mf': 18.408479, 'f': 18.284058, 'ff': 17.826939, 'fff': 17.543095, 'ffff': 17.319277},
    'A4': {'pppp': 21.870697, 'ppp': 21.858693, 'pp': 21.843698, 'p': 21.835045, 'mp': 21.808688, 'mf': 21.764063, 'f': 21.378202, 'ff': 20.645554, 'fff': 20.138008, 'ffff': 19.74097},
    'A#4': {'pppp': 24.384437, 'ppp': 24.172142, 'pp': 23.90937, 'p': 23.32527, 'mp': 23.074246, 'mf': 23.019195, 'f': 23.323265, 'ff': 24.061142, 'fff': 24.493197, 'ffff': 24.844421},
    'B4': {'pppp': 22.56007, 'ppp': 22.470026, 'pp': 22.357976, 'p': 22.069543, 'mp': 21.951399, 'mf': 21.928254, 'f': 22.093904, 'ff': 22.486669, 'fff': 22.664229, 'ffff': 22.807285},
    'C5': {'pppp': 18.461594, 'ppp': 18.263871, 'pp': 18.019692, 'p': 17.667102, 'mp': 17.383082, 'mf': 17.176769, 'f': 17.029792, 'ff': 16.935128, 'fff': 16.795076, 'ffff': 16.683868},
    'C#5': {'pppp': 11.819629, 'ppp': 11.997855, 'pp': 12.22442, 'p': 12.749286, 'mp': 12.948288, 'mf': 12.97697, 'f': 12.583771, 'ff': 11.732671, 'fff': 11.182522, 'ffff': 10.761035},
    'D5': {'pppp': 16.345046, 'ppp': 16.263508, 'pp': 16.162156, 'p': 16.067673, 'mp': 15.938309, 'mf': 15.786548, 'f': 15.598192, 'ff': 15.369397, 'fff': 15.158762, 'ffff': 14.992335},
    'D#5': {'pppp': 13.25524, 'ppp': 13.436955, 'pp': 13.667605, 'p': 14.117522, 'mp': 14.376906, 'mf': 14.459047, 'f': 14.329892, 'ff': 13.98435, 'fff': 13.753821, 'ffff': 13.572137},
    'E5': {'pppp': 16.14288, 'ppp': 16.424661, 'pp': 16.783814, 'p': 17.599957, 'mp': 17.910545, 'mf': 17.95536, 'f': 16.781971, 'ff': 14.48363, 'fff': 13.059424, 'ffff': 12.021573},
    'F5': {'pppp': 16.543196, 'ppp': 16.609254, 'pp': 16.692199, 'p': 16.844743, 'mp': 16.944992, 'mf': 16.980987, 'f': 16.966518, 'ff': 16.906737, 'fff': 16.816857, 'ffff': 16.745298},
    'F#5': {'pppp': 15.403503, 'ppp': 15.630558, 'pp': 15.919089, 'p': 16.580244, 'mp': 16.839781, 'mf': 16.881686, 'f': 16.44499, 'ff': 15.480267, 'fff': 14.854083, 'ffff': 14.371422},
    'G5': {'pppp': 15.107848, 'ppp': 15.436206, 'pp': 15.856708, 'p': 16.499067, 'mp': 17.012908, 'mf': 17.324665, 'f': 17.491664, 'ff': 17.565619, 'fff': 17.647819, 'ffff': 17.713855},
    'G#5': {'pppp': 15.138414, 'ppp': 15.016844, 'pp': 14.866253, 'p': 14.714219, 'mp': 14.537759, 'mf': 14.344025, 'f': 14.125835, 'ff': 13.881625, 'fff': 13.656628, 'ffff': 13.479259},
    'A5': {'pppp': 17.680865, 'ppp': 17.531229, 'pp': 17.345963, 'p': 16.968812, 'mp': 16.76118, 'mf': 16.696978, 'f': 16.80053, 'ff': 17.084341, 'fff': 17.216126, 'ffff': 17.322285},
    'A#5': {'pppp': 13.739473, 'ppp': 13.71905, 'pp': 13.693563, 'p': 13.680577, 'mp': 13.643594, 'mf': 13.585647, 'f': 13.375561, 'ff': 13.009617, 'fff': 12.741717, 'ffff': 12.531376},
    'B5': {'pppp': 14.122689, 'ppp': 14.150596, 'pp': 14.185557, 'p': 14.198258, 'mp': 14.234368, 'mf': 14.290958, 'f': 14.490259, 'ff': 14.849057, 'fff': 15.050015, 'ffff': 15.212739},
    'C6': {'pppp': 14.107133, 'ppp': 14.030687, 'pp': 13.935711, 'p': 13.706439, 'mp': 13.622925, 'mf': 13.611036, 'f': 13.917253, 'ff': 14.610716, 'fff': 15.057527, 'ffff': 15.424794},
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
