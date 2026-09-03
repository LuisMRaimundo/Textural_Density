# instrumentos/viola_harmonics.py
"""
Viola (arco harmonics) instrument density module.

The ``spectral_data`` table stores a committed 10-dynamic Combined Density
Metric (CDM) ladder from the ``Results`` sheet of
``Viola_Zenodo_collections_harmonics_Dynamics10.xlsx``
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
        "Viola_Zenodo_collections_harmonics_Dynamics10.xlsx "
        "(dest Zenodo Viola_harmonics Media (IOWA+Orchidea average); Dynamics_predicter Results ladder)."
    ),
    source_url_or_identifier='docs/instrument_acoustic_sources.md#viola-harmonics',
    extraction_method=(
        "Committed full dynamic ladder from Dynamics extrapolator v1.5.2.1 Results sheet "
        "(PCHIP interiors, tapered outers r=0.80) on measured pp/mf/ff anchors; "
        "interior cells clamped into their measured segment where the workbook "
        "marginally overshoots; pitch lookup via MIDI-space spectral_lookup"
    ),
    dynamic_levels=('pppp', 'ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', 'ffff'),
    pitch_range=(72, 94),
    uncertainty="high",
    version="2026-09-03",
    source_technique="arco_harmonic",
    table_supported_techniques=("arco_harmonic",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("viola_harmonics")

# Full 10-dynamic CDM ladder (Results sheet). Anchors pp/mf/ff match measured
# workbook midpoints; other levels are workbook-committed.
spectral_data = {
    'C5': {'pppp': 17.902099, 'ppp': 18.283873, 'pp': 18.772559, 'p': 19.751102, 'mp': 20.409564, 'mf': 20.64832, 'f': 20.535659, 'ff': 20.106271, 'fff': 19.965889, 'ffff': 19.854291},
    'C#5': {'pppp': 16.236556, 'ppp': 16.536471, 'pp': 16.919166, 'p': 17.287463, 'mp': 17.766379, 'mf': 18.333771, 'f': 19.03851, 'ff': 19.910268, 'fff': 20.724734, 'ffff': 21.40023},
    'D5': {'pppp': 11.419882, 'ppp': 11.905253, 'pp': 12.541079, 'p': 13.434817, 'mp': 14.241007, 'mf': 14.916495, 'f': 15.466018, 'ff': 15.883589, 'fff': 16.3904, 'ffff': 16.807468},
    'D#5': {'pppp': 16.339586, 'ppp': 16.256263, 'pp': 16.152705, 'p': 15.936246, 'mp': 15.857231, 'mf': 15.845975, 'f': 16.048408, 'ff': 16.509577, 'fff': 16.88883, 'ffff': 17.198495},
    'E5': {'pppp': 11.341469, 'ppp': 11.205894, 'pp': 11.038701, 'p': 10.815699, 'mp': 10.631218, 'mf': 10.488078, 'f': 10.378735, 'ff': 10.300071, 'fff': 10.285983, 'ffff': 10.274725},
    'F5': {'pppp': 14.463674, 'ppp': 14.519452, 'pp': 14.589477, 'p': 14.722667, 'mp': 14.845882, 'mf': 14.958923, 'f': 15.06145, 'ff': 15.153202, 'fff': 15.342657, 'ffff': 15.495925},
    'F#5': {'pppp': 14.615413, 'ppp': 15.124343, 'pp': 15.785499, 'p': 16.706323, 'mp': 17.538512, 'mf': 18.248511, 'f': 18.83902, 'ff': 19.304269, 'fff': 19.861453, 'ffff': 20.318757},
    'G5': {'pppp': 16.350235, 'ppp': 16.349038, 'pp': 16.347541, 'p': 16.367586, 'mp': 16.410644, 'mf': 16.466028, 'f': 16.54796, 'ff': 16.66187, 'fff': 16.882484, 'ffff': 17.061076},
    'G#5': {'pppp': 16.458746, 'ppp': 16.391656, 'pp': 16.308178, 'p': 16.138765, 'mp': 16.076795, 'mf': 16.067961, 'f': 16.935963, 'ff': 18.920245, 'fff': 20.417434, 'ffff': 21.700047},
    'A5': {'pppp': 18.063351, 'ppp': 17.784621, 'pp': 17.442249, 'p': 16.78438, 'mp': 16.442274, 'mf': 16.342047, 'f': 16.551308, 'ff': 17.108472, 'fff': 17.527183, 'ffff': 17.869518},
    'A#5': {'pppp': 15.308285, 'ppp': 15.194973, 'pp': 15.054513, 'p': 14.74594, 'mp': 14.633857, 'mf': 14.617914, 'f': 14.969555, 'ff': 15.774691, 'fff': 16.370253, 'ffff': 16.862853},
    'B5': {'pppp': 14.507898, 'ppp': 14.234828, 'pp': 13.900707, 'p': 13.38482, 'mp': 13.00686, 'mf': 12.810575, 'f': 12.733256, 'ff': 12.701194, 'fff': 12.722297, 'ffff': 12.739205},
    'C6': {'pppp': 14.034534, 'ppp': 14.026929, 'pp': 14.017428, 'p': 14.034966, 'mp': 14.041433, 'mf': 14.042357, 'f': 13.709318, 'ff': 13.040269, 'fff': 12.723716, 'ffff': 12.476016},
    'C#6': {'pppp': 16.733611, 'ppp': 16.51156, 'pp': 16.238135, 'p': 16.121864, 'mp': 15.817138, 'mf': 15.391718, 'f': 14.517444, 'ff': 13.230877, 'fff': 12.399128, 'ffff': 11.771537},
    'D6': {'pppp': 15.265681, 'ppp': 14.705602, 'pp': 14.034309, 'p': 12.911325, 'mp': 12.255996, 'mf': 12.037552, 'f': 12.189103, 'ff': 12.708464, 'fff': 13.063366, 'ffff': 13.354411},
    'D#6': {'pppp': 14.511944, 'ppp': 14.655481, 'pp': 14.8369, 'p': 14.917979, 'mp': 15.143624, 'mf': 15.4893, 'f': 16.479464, 'ff': 18.295313, 'fff': 19.782342, 'ffff': 21.058527},
    'E6': {'pppp': 12.246884, 'ppp': 12.216204, 'pp': 12.177962, 'p': 12.10453, 'mp': 12.077588, 'mf': 12.073744, 'f': 13.235274, 'ff': 16.03121, 'fff': 18.316917, 'ffff': 20.377986},
    'F6': {'pppp': 8.060317, 'ppp': 8.076231, 'pp': 8.096168, 'p': 8.107398, 'mp': 8.140528, 'mf': 8.19484, 'f': 8.475276, 'ff': 9.022512, 'fff': 9.44338, 'ffff': 9.794165},
    'F#6': {'pppp': 7.638463, 'ppp': 7.546595, 'pp': 7.433312, 'p': 7.188828, 'mp': 7.100795, 'mf': 7.088308, 'f': 7.67332, 'ff': 9.091406, 'fff': 10.223773, 'ffff': 11.230402},
    'G6': {'pppp': 8.675549, 'ppp': 8.4568, 'pp': 8.191104, 'p': 7.62176, 'mp': 7.422128, 'mf': 7.394039, 'f': 7.805058, 'ff': 8.825356, 'fff': 9.598183, 'ffff': 10.264894},
    'G#6': {'pppp': 11.781968, 'ppp': 11.267396, 'pp': 10.655668, 'p': 9.423582, 'mp': 8.998586, 'mf': 8.935587, 'f': 9.686313, 'ff': 11.661814, 'fff': 13.248586, 'ffff': 14.6721},
    'A6': {'pppp': 9.043001, 'ppp': 8.587346, 'pp': 8.049927, 'p': 7.19239, 'mp': 6.696216, 'mf': 6.530833, 'f': 6.626885, 'ff': 6.979013, 'fff': 7.213479, 'ffff': 7.406711},
    'A#6': {'pppp': 10.393666, 'ppp': 9.763191, 'pp': 9.028603, 'p': 7.749687, 'mp': 7.195559, 'mf': 7.057036, 'f': 7.538978, 'ff': 8.868985, 'fff': 9.900233, 'ffff': 10.81092},
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
