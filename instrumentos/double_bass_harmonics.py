# instrumentos/double_bass_harmonics.py
"""
Double bass (arco harmonics) instrument density module.

The ``spectral_data`` table stores a committed 10-dynamic Combined Density
Metric (CDM) ladder from the ``Results`` sheet of
``DoubleBass_Dynamics10_harmonics.xlsx``
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
        "DoubleBass_Dynamics10_harmonics.xlsx "
        "(dest Zenodo DoubleBass_harmonics Media (IOWA+Orchidea average); Dynamics_predicter Results ladder)."
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
    version="2026-08-27",
    source_technique="arco_harmonic",
    table_supported_techniques=("arco_harmonic",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("double_bass_harmonics")

# Full 10-dynamic CDM ladder (Results sheet). Anchors pp/mf/ff match measured
# workbook midpoints; other levels are workbook-committed.
spectral_data = {
    'E3': {'pppp': 29.306511, 'ppp': 28.826826, 'pp': 28.238245, 'p': 27.287892, 'mp': 26.47037, 'mf': 25.779643, 'f': 25.20179, 'ff': 24.728162, 'fff': 24.352221, 'ffff': 24.055587},
    'F3': {'pppp': 21.556539, 'ppp': 22.072862, 'pp': 22.735691, 'p': 24.114028, 'mp': 24.719883, 'mf': 24.846013, 'f': 24.036339, 'ff': 22.234689, 'fff': 21.218946, 'ffff': 20.439865},
    'F#3': {'pppp': 15.600676, 'ppp': 15.80328, 'pp': 16.060239, 'p': 16.227266, 'mp': 16.434852, 'mf': 16.67378, 'f': 16.959413, 'ff': 17.299123, 'fff': 17.60051, 'ffff': 17.845396},
    'G3': {'pppp': 14.043571, 'ppp': 14.369253, 'pp': 14.786997, 'p': 15.313075, 'mp': 15.761099, 'mf': 16.104824, 'f': 16.361077, 'ff': 16.534143, 'fff': 16.752791, 'ffff': 16.92979},
    'G#3': {'pppp': 14.836732, 'ppp': 14.416602, 'pp': 13.90813, 'p': 12.890683, 'mp': 12.316288, 'mf': 12.130565, 'f': 12.316259, 'ff': 12.890595, 'fff': 13.258685, 'ffff': 13.560711},
    'A3': {'pppp': 12.910902, 'ppp': 13.272685, 'pp': 13.739204, 'p': 14.747143, 'mp': 15.182327, 'mf': 15.268123, 'f': 14.648844, 'ff': 13.297058, 'fff': 12.52396, 'ffff': 11.937971},
    'A#3': {'pppp': 13.377015, 'ppp': 13.547603, 'pp': 13.763901, 'p': 13.888875, 'mp': 14.065832, 'mf': 14.279182, 'f': 14.55357, 'ff': 14.900763, 'fff': 15.195668, 'ffff': 15.435789},
    'B3': {'pppp': 17.460189, 'ppp': 17.712715, 'pp': 18.033515, 'p': 18.271576, 'mp': 18.551245, 'mf': 18.865148, 'f': 19.226954, 'ff': 19.643582, 'fff': 20.015995, 'ffff': 20.319002},
    'C4': {'pppp': 20.672631, 'ppp': 21.14, 'pp': 21.739098, 'p': 22.097753, 'mp': 22.761708, 'mf': 23.623452, 'f': 24.88582, 'ff': 26.678536, 'fff': 28.1814, 'ffff': 29.444421},
    'C#4': {'pppp': 18.550355, 'ppp': 19.240997, 'pp': 20.14057, 'p': 21.698203, 'mp': 22.845217, 'mf': 23.28893, 'f': 23.236366, 'ff': 22.871727, 'fff': 22.738441, 'ffff': 22.632371},
    'D4': {'pppp': 17.213821, 'ppp': 17.460413, 'pp': 17.773626, 'p': 18.009188, 'mp': 18.279167, 'mf': 18.578098, 'f': 18.916351, 'ff': 19.29918, 'fff': 19.646181, 'ffff': 19.928268},
    'D#4': {'pppp': 23.431394, 'ppp': 22.979581, 'pp': 22.427046, 'p': 20.999608, 'mp': 20.49219, 'mf': 20.418381, 'f': 21.329614, 'ff': 23.580041, 'fff': 25.170319, 'ffff': 26.519421},
    'E4': {'pppp': 15.212388, 'ppp': 15.679459, 'pp': 16.283517, 'p': 17.30332, 'mp': 18.042533, 'mf': 18.325779, 'f': 18.289651, 'ff': 18.038744, 'fff': 17.957614, 'ffff': 17.892972},
    'F4': {'pppp': 15.296566, 'ppp': 15.723447, 'pp': 16.273838, 'p': 17.040875, 'mp': 17.671785, 'mf': 18.095078, 'f': 18.365588, 'ff': 18.501509, 'fff': 18.714176, 'ffff': 18.886069},
    'F#4': {'pppp': 24.34737, 'ppp': 23.90538, 'pp': 23.364159, 'p': 21.94327, 'mp': 21.441852, 'mf': 21.371163, 'f': 22.340374, 'ff': 24.721125, 'fff': 26.406107, 'ffff': 27.836414},
    'G4': {'pppp': 10.20435, 'ppp': 10.749515, 'pp': 11.472109, 'p': 12.783998, 'mp': 13.756739, 'mf': 14.132962, 'f': 14.06766, 'ff': 13.63808, 'fff': 13.443577, 'ffff': 13.289974},
    'G#4': {'pppp': 12.434411, 'ppp': 12.839504, 'pp': 13.36448, 'p': 14.016947, 'mp': 14.616022, 'mf': 15.146912, 'f': 15.607693, 'ff': 15.993522, 'fff': 16.402722, 'ffff': 16.737606},
    'A4': {'pppp': 16.624901, 'ppp': 17.219312, 'pp': 17.992302, 'p': 19.277851, 'mp': 20.278077, 'mf': 20.691052, 'f': 20.706589, 'ff': 20.712276, 'fff': 20.763826, 'ffff': 20.805158},
    'A#4': {'pppp': 14.923931, 'ppp': 15.478116, 'pp': 16.199875, 'p': 17.634061, 'mp': 18.441997, 'mf': 18.684887, 'f': 18.144059, 'ff': 16.822261, 'fff': 16.078249, 'ffff': 15.506803},
    'B4': {'pppp': 19.13068, 'ppp': 19.674703, 'pp': 20.376538, 'p': 21.338633, 'mp': 22.141139, 'mf': 22.707319, 'f': 23.090825, 'ff': 23.308198, 'fff': 23.614574, 'ffff': 23.862572},
    'C5': {'pppp': 11.93012, 'ppp': 12.354691, 'pp': 12.906716, 'p': 13.838158, 'mp': 14.548367, 'mf': 14.830095, 'f': 14.819794, 'ff': 14.747887, 'fff': 14.743111, 'ffff': 14.739292},
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
