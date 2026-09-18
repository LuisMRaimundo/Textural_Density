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
        "(dest Zenodo Violin_harmonics Media (IOWA+Orchidea average); Dynamics_predicter Results ladder (CORDAS_4))."
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
    version="2026-09-18",
    source_technique="arco_harmonic",
    table_supported_techniques=("arco_harmonic",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("violin_harmonics")

# Full 10-dynamic CDM ladder (Results sheet). Anchors pp/mf/ff match measured
# workbook midpoints; other levels are workbook-committed.
spectral_data = {
    'G5': {'pppp': 14.859545, 'ppp': 15.03364, 'pp': 15.254131, 'p': 15.352637, 'mp': 15.602494, 'mf': 15.935195, 'f': 16.466438, 'ff': 17.253876, 'fff': 17.862741, 'ffff': 18.365268},
    'G#5': {'pppp': 16.325892, 'ppp': 15.281025, 'pp': 14.068472, 'p': 11.99461, 'mp': 11.089007, 'mf': 10.858997, 'f': 11.609736, 'ff': 13.697931, 'fff': 15.316819, 'ffff': 16.748637},
    'A5': {'pppp': 13.818559, 'ppp': 13.565613, 'pp': 13.255932, 'p': 12.544901, 'mp': 12.292666, 'mf': 12.257049, 'f': 12.75727, 'ff': 13.974211, 'fff': 14.841477, 'ffff': 15.573885},
    'A#5': {'pppp': 13.968559, 'ppp': 13.88058, 'pp': 13.771385, 'p': 13.680236, 'mp': 13.512438, 'mf': 13.303901, 'f': 13.014671, 'ff': 12.635743, 'fff': 12.34749, 'ffff': 12.12163},
    'B5': {'pppp': 15.07149, 'ppp': 15.070423, 'pp': 15.069091, 'p': 14.956136, 'mp': 14.914735, 'mf': 14.90883, 'f': 15.078306, 'ff': 15.453414, 'fff': 15.659926, 'ffff': 15.82712},
    'C6': {'pppp': 11.896337, 'ppp': 12.057906, 'pp': 12.262956, 'p': 12.390066, 'mp': 12.61845, 'mf': 12.910123, 'f': 13.327083, 'ff': 13.902412, 'fff': 14.358969, 'ffff': 14.734986},
    'C#6': {'pppp': 11.283532, 'ppp': 11.236045, 'pp': 11.176967, 'p': 10.99517, 'mp': 10.92894, 'mf': 10.919511, 'f': 11.260271, 'ff': 12.031084, 'fff': 12.551406, 'ffff': 12.98382},
    'D6': {'pppp': 10.83033, 'ppp': 11.129325, 'pp': 11.514703, 'p': 12.172306, 'mp': 12.658848, 'mf': 12.848145, 'f': 12.834215, 'ff': 12.737128, 'fff': 12.679055, 'ffff': 12.632787},
    'D#6': {'pppp': 13.556324, 'ppp': 13.52272, 'pp': 13.480831, 'p': 13.343111, 'mp': 13.292728, 'mf': 13.285545, 'f': 13.927866, 'ff': 15.385878, 'fff': 16.438115, 'ffff': 17.331486},
    'E6': {'pppp': 13.74036, 'ppp': 13.931965, 'pp': 14.175232, 'p': 14.645242, 'mp': 14.883753, 'mf': 14.94863, 'f': 14.748563, 'ff': 14.263624, 'fff': 13.96305, 'ffff': 13.727158},
    'F6': {'pppp': 9.75882, 'ppp': 9.843487, 'pp': 9.950354, 'p': 10.133801, 'mp': 10.22729, 'mf': 10.253119, 'f': 10.178849, 'ff': 9.995535, 'fff': 9.880241, 'ffff': 9.788964},
    'F#6': {'pppp': 8.368573, 'ppp': 8.476951, 'pp': 8.614399, 'p': 8.865331, 'mp': 9.004685, 'mf': 9.047149, 'f': 8.965547, 'ff': 8.75429, 'fff': 8.62383, 'ffff': 8.520862},
    'G6': {'pppp': 8.365064, 'ppp': 8.480612, 'pp': 8.627294, 'p': 8.889015, 'mp': 9.044092, 'mf': 9.094632, 'f': 9.028752, 'ff': 8.845456, 'fff': 8.732895, 'ffff': 8.643879},
    'G#6': {'pppp': 8.352977, 'ppp': 8.539487, 'pp': 8.778493, 'p': 9.226673, 'mp': 9.492925, 'mf': 9.579227, 'f': 9.456796, 'ff': 9.125426, 'fff': 8.923035, 'ffff': 8.76436},
    'A6': {'pppp': 6.308023, 'ppp': 6.283916, 'pp': 6.253912, 'p': 6.157098, 'mp': 6.121808, 'mf': 6.116784, 'f': 6.289383, 'ff': 6.678747, 'fff': 6.937262, 'ffff': 7.151259},
    'A#6': {'pppp': 7.58775, 'ppp': 7.752473, 'pp': 7.963413, 'p': 8.324464, 'mp': 8.580848, 'mf': 8.677853, 'f': 8.664026, 'ff': 8.56785, 'fff': 8.513373, 'ffff': 8.470041},
    'B6': {'pppp': 6.400299, 'ppp': 6.694849, 'pp': 7.082171, 'p': 7.885987, 'mp': 8.319291, 'mf': 8.440733, 'f': 8.078153, 'ff': 7.242563, 'fff': 6.733049, 'ffff': 6.351369},
    'C7': {'pppp': 6.25379, 'ppp': 6.628444, 'pp': 7.128481, 'p': 8.087457, 'mp': 8.726244, 'mf': 8.950984, 'f': 8.733027, 'ff': 8.10566, 'fff': 7.730624, 'ffff': 7.443127},
    'C#7': {'pppp': 6.193731, 'ppp': 6.403113, 'pp': 6.674823, 'p': 7.237534, 'mp': 7.526138, 'mf': 7.603044, 'f': 7.338363, 'ff': 6.727274, 'fff': 6.350187, 'ffff': 6.063794},
    'D7': {'pppp': 6.400417, 'ppp': 6.408098, 'pp': 6.417712, 'p': 6.389232, 'mp': 6.378771, 'mf': 6.377278, 'f': 6.435351, 'ff': 6.561912, 'fff': 6.626553, 'ffff': 6.678724},
    'D#7': {'pppp': 5.780309, 'ppp': 5.74404, 'pp': 5.699025, 'p': 5.572348, 'mp': 5.526391, 'mf': 5.519856, 'f': 5.67899, 'ff': 6.04408, 'fff': 6.288588, 'ffff': 6.491298},
    'E7': {'pppp': 6.945639, 'ppp': 6.969184, 'pp': 6.998728, 'p': 7.042932, 'mp': 7.059288, 'mf': 7.061627, 'f': 6.798224, 'ff': 6.276368, 'fff': 5.950735, 'ffff': 5.702436},
    'F7': {'pppp': 6.318662, 'ppp': 6.535363, 'pp': 6.81672, 'p': 7.373369, 'mp': 7.688168, 'mf': 7.783572, 'f': 7.580323, 'ff': 7.078044, 'fff': 6.768967, 'ffff': 6.531451},
    'F#7': {'pppp': 6.758262, 'ppp': 6.790968, 'pp': 6.832073, 'p': 6.897774, 'mp': 6.922139, 'mf': 6.925626, 'f': 6.790792, 'ff': 6.509995, 'fff': 6.334887, 'ffff': 6.198198},
    'G7': {'pppp': 5.384834, 'ppp': 5.645213, 'pp': 5.988463, 'p': 6.707069, 'mp': 7.091422, 'mf': 7.197556, 'f': 6.862781, 'ff': 6.100247, 'fff': 5.636926, 'ffff': 5.291737},
    'G#7': {'pppp': 6.090089, 'ppp': 6.295097, 'pp': 6.56109, 'p': 6.990646, 'mp': 7.329155, 'mf': 7.495111, 'f': 7.538689, 'ff': 7.555953, 'fff': 7.578661, 'ffff': 7.596876},
    'A7': {'pppp': 4.07113, 'ppp': 4.10255, 'pp': 4.142165, 'p': 4.157399, 'mp': 4.197367, 'mf': 4.253555, 'f': 4.363473, 'ff': 4.537732, 'fff': 4.662649, 'ffff': 4.765055},
    'A#7': {'pppp': 3.433554, 'ppp': 3.560476, 'pp': 3.725747, 'p': 4.03711, 'mp': 4.233718, 'mf': 4.300569, 'f': 4.226875, 'ff': 4.01826, 'fff': 3.892039, 'ffff': 3.793923},
    'B7': {'pppp': 5.066237, 'ppp': 5.036408, 'pp': 4.999369, 'p': 4.914478, 'mp': 4.849872, 'mf': 4.811925, 'f': 4.791885, 'ff': 4.783086, 'fff': 4.765576, 'ffff': 4.751614},
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
