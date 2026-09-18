# instrumentos/double_bass_harmonics.py
"""
Double bass (arco harmonics) instrument density module.

The ``spectral_data`` table stores a committed 10-dynamic Combined Density
Metric (CDM) ladder from the ``Results`` sheet of
``Double_bass_Zenodo_collections_harmonics_Dynamics10.xlsx``
(measured pp/mf/ff anchors; remaining levels committed from that workbook —
no runtime dynamic extrapolation).

Runtime analysis does not ingest audio; it maps notated pitch + dynamic to
these pre-loaded acoustic metadata tables.
"""

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="external_acoustic_metadata",
    citation=(
        "Double bass arco_harmonic CDM ladder: measured pp/mf/ff anchors with "
        "committed Results sheet values for all 10 dynamic levels from "
        "Double_bass_Zenodo_collections_harmonics_Dynamics10.xlsx "
        "(dest Zenodo DoubleBass_harmonics Media (IOWA+Orchidea average); Dynamics_predicter Results ladder (CORDAS_4))."
    ),
    source_url_or_identifier='docs/instrument_acoustic_sources.md#double-bass-harmonics',
    extraction_method=(
        "Committed full dynamic ladder from Dynamics extrapolator v1.5.2.1 Results sheet "
        "(PCHIP interiors, tapered outers r=0.80) on measured pp/mf/ff anchors; "
        "interior cells clamped into their measured segment where the workbook "
        "marginally overshoots; pitch lookup via MIDI-space spectral_lookup"
    ),
    dynamic_levels=('pppp', 'ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', 'ffff'),
    pitch_range=(52, 72),
    uncertainty="high",
    version="2026-09-18",
    source_technique="arco_harmonic",
    table_supported_techniques=("arco_harmonic",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("double_bass_harmonics")

# Full 10-dynamic CDM ladder (Results sheet). Anchors pp/mf/ff match measured
# workbook midpoints; other levels are workbook-committed.
spectral_data = {
    'E3': {'pppp': 30.818247, 'ppp': 30.104802, 'pp': 29.236176, 'p': 27.871262, 'mp': 26.840022, 'mf': 26.191633, 'f': 25.794957, 'ff': 25.602048, 'fff': 25.482323, 'ffff': 25.386946},
    'F3': {'pppp': 29.172836, 'ppp': 27.54538, 'pp': 25.638133, 'p': 22.208651, 'mp': 20.697695, 'mf': 20.313655, 'f': 21.583905, 'ff': 25.073173, 'fff': 27.724717, 'ffff': 30.046465},
    'F#3': {'pppp': 19.367999, 'ppp': 19.134377, 'pp': 18.846309, 'p': 18.106593, 'mp': 17.841446, 'mf': 17.803886, 'f': 18.544313, 'ff': 20.300109, 'fff': 21.589413, 'ffff': 22.67957},
    'G3': {'pppp': 17.513135, 'ppp': 17.515387, 'pp': 17.518202, 'p': 17.442501, 'mp': 17.414694, 'mf': 17.410725, 'f': 18.086704, 'ff': 19.588052, 'fff': 20.691372, 'ffff': 21.618608},
    'G#3': {'pppp': 18.652743, 'ppp': 17.609298, 'pp': 16.38669, 'p': 14.274134, 'mp': 13.245611, 'mf': 12.950983, 'f': 13.532689, 'ff': 15.18782, 'fff': 16.392059, 'ffff': 17.423842},
    'A3': {'pppp': 15.889286, 'ppp': 15.984022, 'pp': 16.103236, 'p': 16.316811, 'mp': 16.396209, 'mf': 16.407583, 'f': 16.145667, 'ff': 15.585012, 'fff': 15.374291, 'ffff': 15.207767},
    'A#3': {'pppp': 13.912384, 'ppp': 14.496291, 'pp': 15.260757, 'p': 16.777026, 'mp': 17.722904, 'mf': 18.039032, 'f': 17.62906, 'ff': 16.521256, 'fff': 15.932234, 'ffff': 15.476173},
    'B3': {'pppp': 17.388031, 'ppp': 17.605982, 'pp': 17.882267, 'p': 18.166199, 'mp': 18.467432, 'mf': 18.784685, 'f': 19.121224, 'ff': 19.478831, 'fff': 19.890648, 'ffff': 20.226362},
    'C4': {'pppp': 16.292233, 'ppp': 17.012006, 'pp': 17.956602, 'p': 19.464547, 'mp': 20.710158, 'mf': 21.469377, 'f': 21.862995, 'ff': 22.036602, 'fff': 22.376966, 'ffff': 22.653039},
    'C#4': {'pppp': 16.76675, 'ppp': 17.538597, 'pp': 18.553562, 'p': 20.484015, 'mp': 21.816831, 'mf': 22.304741, 'f': 22.030354, 'ff': 21.069512, 'fff': 20.608274, 'ffff': 20.246563},
    'D4': {'pppp': 17.6512, 'ppp': 17.821311, 'pp': 18.036255, 'p': 18.182534, 'mp': 18.412309, 'mf': 18.69677, 'f': 19.080378, 'ff': 19.584351, 'fff': 20.080953, 'ffff': 20.487286},
    'D#4': {'pppp': 24.034612, 'ppp': 23.306383, 'pp': 22.427046, 'p': 20.530711, 'mp': 19.822847, 'mf': 19.699044, 'f': 20.794568, 'ff': 23.580041, 'fff': 25.671376, 'ffff': 27.477221},
    'E4': {'pppp': 15.558195, 'ppp': 15.876484, 'pp': 16.283517, 'p': 16.889694, 'mp': 17.384884, 'mf': 17.717143, 'f': 17.930196, 'ff': 18.038744, 'fff': 18.277289, 'ffff': 18.470395},
    'F4': {'pppp': 15.711452, 'ppp': 15.958961, 'pp': 16.273838, 'p': 16.547036, 'mp': 16.904756, 'mf': 17.327855, 'f': 17.853259, 'ff': 18.501509, 'fff': 19.117818, 'ffff': 19.625614},
    'F#4': {'pppp': 25.219247, 'ppp': 24.377243, 'pp': 23.364159, 'p': 21.210467, 'mp': 20.415428, 'mf': 20.27853, 'f': 21.525157, 'ff': 24.721125, 'fff': 27.149793, 'ffff': 29.263424},
    'G4': {'pppp': 10.611105, 'ppp': 10.985494, 'pp': 11.472109, 'p': 12.216238, 'mp': 12.835278, 'mf': 13.249165, 'f': 13.510994, 'ff': 13.63808, 'fff': 13.869618, 'ffff': 14.057676},
    'G#4': {'pppp': 12.940448, 'ppp': 13.12722, 'pp': 13.36448, 'p': 13.468333, 'mp': 13.743426, 'mf': 14.136413, 'f': 14.932308, 'ff': 16.247333, 'fff': 17.341622, 'ffff': 18.269886},
    'A4': {'pppp': 17.436734, 'ppp': 17.681503, 'pp': 17.992302, 'p': 18.125062, 'mp': 18.480972, 'mf': 18.998668, 'f': 20.130294, 'ff': 22.052222, 'fff': 23.64311, 'ffff': 24.998065},
    'A#4': {'pppp': 15.746036, 'ppp': 15.946151, 'pp': 16.199875, 'p': 16.409654, 'mp': 16.691209, 'mf': 17.026102, 'f': 17.44645, 'ff': 17.968866, 'fff': 18.478269, 'ffff': 18.896169},
    'B4': {'pppp': 20.491484, 'ppp': 20.440317, 'pp': 20.376538, 'p': 20.168021, 'mp': 20.091738, 'mf': 20.080864, 'f': 21.60595, 'ff': 25.191374, 'fff': 27.980763, 'ffff': 30.433066},
    'C5': {'pppp': 12.874416, 'ppp': 12.888762, 'pp': 12.906716, 'p': 12.907121, 'mp': 12.90842, 'mf': 12.910739, 'f': 13.895453, 'ff': 16.183903, 'fff': 17.962786, 'ffff': 19.525675},
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
