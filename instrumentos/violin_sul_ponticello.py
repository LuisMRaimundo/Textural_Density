# instrumentos/violin_sul_ponticello.py
"""
Violin (arco sul ponticello) instrument density module.

The ``spectral_data`` table stores a committed 10-dynamic Combined Density
Metric (CDM) ladder from the ``Results`` sheet of
``Violin_Zenodo_collections_sul_ponticello_Dynamics10.xlsx``
(measured pp/mf/ff anchors; remaining levels committed from that workbook —
no runtime dynamic extrapolation).

Runtime analysis does not ingest audio; it maps notated pitch + dynamic to
these pre-loaded acoustic metadata tables.
"""

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="external_acoustic_metadata",
    citation=(
        "Violin arco_sul_ponticello CDM ladder: measured pp/mf/ff anchors with "
        "committed Results sheet values for all 10 dynamic levels from "
        "Violin_Zenodo_collections_sul_ponticello_Dynamics10.xlsx "
        "(dest Zenodo Violin_sul ponticello Media (IOWA+Orchidea average); Dynamics_predicter Results ladder)."
    ),
    source_url_or_identifier='docs/instrument_acoustic_sources.md#violin-sul-ponticello',
    extraction_method=(
        "Committed full dynamic ladder from Dynamics extrapolator v1.5.2.1 Results sheet "
        "(PCHIP interiors, tapered outers r=0.80) on measured pp/mf/ff anchors; "
        "interior cells clamped into their measured segment where the workbook "
        "marginally overshoots; pitch lookup via MIDI-space spectral_lookup"
    ),
    dynamic_levels=('pppp', 'ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', 'ffff'),
    pitch_range=(55, 96),
    uncertainty="high",
    version="2026-09-03",
    source_technique="arco_sul_ponticello",
    table_supported_techniques=("arco_sul_ponticello",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("violin_sul_ponticello")

# Full 10-dynamic CDM ladder (Results sheet). Anchors pp/mf/ff match measured
# workbook midpoints; other levels are workbook-committed.
spectral_data = {
    'G3': {'pppp': 32.613976, 'ppp': 33.261117, 'pp': 34.08813, 'p': 34.784314, 'mp': 35.705007, 'mf': 36.801923, 'f': 38.177002, 'ff': 39.891084, 'fff': 41.418839, 'ffff': 42.683063},
    'G#3': {'pppp': 40.014294, 'ppp': 40.525731, 'pp': 41.174229, 'p': 41.562799, 'mp': 42.252424, 'mf': 43.129796, 'f': 44.375835, 'ff': 46.083944, 'fff': 47.532694, 'ffff': 48.724417},
    'A3': {'pppp': 24.817616, 'ppp': 25.983097, 'pp': 27.517214, 'p': 28.550587, 'mp': 30.427473, 'mf': 32.939491, 'f': 36.746826, 'ff': 42.461285, 'fff': 47.890171, 'ffff': 52.728934},
    'A#3': {'pppp': 34.270888, 'ppp': 34.723419, 'pp': 35.297496, 'p': 35.505758, 'mp': 36.10428, 'mf': 37.060938, 'f': 40.644084, 'ff': 47.853499, 'fff': 53.896173, 'ffff': 59.27524},
    'B3': {'pppp': 38.718628, 'ppp': 38.034188, 'pp': 37.195628, 'p': 35.259877, 'mp': 34.407717, 'mf': 34.20698, 'f': 35.113406, 'ff': 37.393328, 'fff': 38.976045, 'ffff': 40.290317},
    'C4': {'pppp': 40.999088, 'ppp': 40.777387, 'pp': 40.501946, 'p': 39.652712, 'mp': 39.344345, 'mf': 39.300488, 'f': 41.318761, 'ff': 45.989672, 'fff': 49.409164, 'ffff': 52.326931},
    'C#4': {'pppp': 21.043657, 'ppp': 21.188686, 'pp': 21.37138, 'p': 21.425526, 'mp': 21.565888, 'mf': 21.759492, 'f': 22.11489, 'ff': 22.661354, 'fff': 23.121696, 'ffff': 23.496693},
    'D4': {'pppp': 19.711159, 'ppp': 20.598477, 'pp': 21.764004, 'p': 22.813918, 'mp': 24.20307, 'mf': 25.898301, 'f': 28.074569, 'ff': 30.879759, 'fff': 33.549626, 'ffff': 35.850789},
    'D#4': {'pppp': 24.944575, 'ppp': 25.905359, 'pp': 27.158545, 'p': 28.729223, 'mp': 30.220659, 'mf': 31.607872, 'f': 32.874887, 'ff': 34.004352, 'fff': 35.208042, 'ffff': 36.201601},
    'E4': {'pppp': 23.778698, 'ppp': 24.596805, 'pp': 25.659133, 'p': 26.76069, 'mp': 27.994902, 'mf': 29.359787, 'f': 30.89025, 'ff': 32.613079, 'fff': 34.261314, 'ffff': 35.63968},
    'F4': {'pppp': 26.406479, 'ppp': 26.952302, 'pp': 27.650474, 'p': 28.349893, 'mp': 29.122546, 'mf': 29.963161, 'f': 30.890032, 'ff': 31.914623, 'fff': 32.882477, 'ffff': 33.67785},
    'F#4': {'pppp': 25.651205, 'ppp': 26.346578, 'pp': 27.242362, 'p': 28.7921, 'mp': 29.929505, 'mf': 30.369545, 'f': 30.329804, 'ff': 30.053066, 'fff': 30.009236, 'ffff': 29.974218},
    'G4': {'pppp': 23.034604, 'ppp': 24.185924, 'pp': 25.706331, 'p': 28.282611, 'mp': 30.359713, 'mf': 31.351427, 'f': 31.558843, 'ff': 31.639468, 'fff': 31.835505, 'ffff': 31.993209},
    'G#4': {'pppp': 32.788635, 'ppp': 33.038141, 'pp': 33.352695, 'p': 33.45375, 'mp': 33.728427, 'mf': 34.134956, 'f': 35.132346, 'ff': 36.826842, 'fff': 38.131331, 'ffff': 39.208113},
    'A4': {'pppp': 30.761027, 'ppp': 30.477937, 'pp': 30.127735, 'p': 29.209475, 'mp': 28.87827, 'mf': 28.831263, 'f': 30.779731, 'ff': 35.416947, 'fff': 38.94428, 'ffff': 42.017453},
    'A#4': {'pppp': 21.428038, 'ppp': 21.738726, 'pp': 22.133429, 'p': 22.305129, 'mp': 22.749313, 'mf': 23.360515, 'f': 24.439811, 'ff': 26.122875, 'fff': 27.497779, 'ffff': 28.649624},
    'B4': {'pppp': 28.14076, 'ppp': 28.423958, 'pp': 28.781967, 'p': 29.47054, 'mp': 29.732832, 'mf': 29.772704, 'f': 29.313058, 'ff': 28.282616, 'fff': 27.793584, 'ffff': 27.408454},
    'C5': {'pppp': 22.084245, 'ppp': 22.566089, 'pp': 23.183204, 'p': 23.95345, 'mp': 24.649711, 'mf': 25.257625, 'f': 25.778347, 'ff': 26.209028, 'fff': 26.701746, 'ffff': 27.102581},
    'C#5': {'pppp': 16.915447, 'ppp': 17.180516, 'pp': 17.517702, 'p': 17.767368, 'mp': 18.133666, 'mf': 18.582729, 'f': 19.174696, 'ff': 19.942537, 'fff': 20.61132, 'ffff': 21.162458},
    'D5': {'pppp': 10.954397, 'ppp': 11.065735, 'pp': 11.2065, 'p': 11.260794, 'mp': 11.403749, 'mf': 11.605877, 'f': 12.00704, 'ff': 12.651589, 'fff': 13.161737, 'ffff': 13.584627},
    'D#5': {'pppp': 16.480035, 'ppp': 16.861744, 'pp': 17.351335, 'p': 17.938278, 'mp': 18.491282, 'mf': 19.006014, 'f': 19.478419, 'ff': 19.904687, 'fff': 20.35918, 'ffff': 20.730235},
    'E5': {'pppp': 22.787894, 'ppp': 23.199166, 'pp': 23.723709, 'p': 24.279256, 'mp': 24.847992, 'mf': 25.430214, 'f': 26.026271, 'ff': 26.636508, 'fff': 27.244913, 'ffff': 27.741627},
    'F5': {'pppp': 19.383537, 'ppp': 19.666192, 'pp': 20.025314, 'p': 20.538976, 'mp': 20.935248, 'mf': 21.143344, 'f': 21.22037, 'ff': 21.252139, 'fff': 21.383424, 'ffff': 21.489036},
    'F#5': {'pppp': 18.738828, 'ppp': 19.118741, 'pp': 19.604483, 'p': 20.266087, 'mp': 20.820087, 'mf': 21.226956, 'f': 21.516302, 'ff': 21.697005, 'fff': 21.966946, 'ffff': 22.185315},
    'G5': {'pppp': 18.097593, 'ppp': 18.389208, 'pp': 18.760343, 'p': 19.071002, 'mp': 19.470611, 'mf': 19.939779, 'f': 20.515944, 'ff': 21.219736, 'fff': 21.851655, 'ffff': 22.370712},
    'G#5': {'pppp': 17.378534, 'ppp': 17.453557, 'pp': 17.547792, 'p': 17.582817, 'mp': 17.595739, 'mf': 17.597585, 'f': 17.431179, 'ff': 17.085611, 'fff': 16.985197, 'ffff': 16.90529},
    'A5': {'pppp': 16.886093, 'ppp': 17.155792, 'pp': 17.498983, 'p': 18.053814, 'mp': 18.446503, 'mf': 18.595, 'f': 18.576457, 'ff': 18.447173, 'fff': 18.460363, 'ffff': 18.470922},
    'A#5': {'pppp': 14.988829, 'ppp': 15.124364, 'pp': 15.295508, 'p': 15.62803, 'mp': 15.752352, 'mf': 15.770193, 'f': 15.199112, 'ff': 14.034182, 'fff': 13.379313, 'ffff': 12.87749},
    'B5': {'pppp': 15.50657, 'ppp': 15.661029, 'pp': 15.856268, 'p': 16.120211, 'mp': 16.29897, 'mf': 16.364562, 'f': 16.347909, 'ff': 16.260668, 'fff': 16.300205, 'ffff': 16.331905},
    'C6': {'pppp': 13.152739, 'ppp': 13.482584, 'pp': 13.906547, 'p': 14.503141, 'mp': 15.002937, 'mf': 15.363913, 'f': 15.61528, 'ff': 15.765738, 'fff': 15.986013, 'ffff': 16.164447},
    'C#6': {'pppp': 15.701785, 'ppp': 15.890307, 'pp': 16.129145, 'p': 16.350318, 'mp': 16.583948, 'mf': 16.829036, 'f': 17.087884, 'ff': 17.361695, 'fff': 17.64746, 'ffff': 17.879456},
    'D6': {'pppp': 16.983324, 'ppp': 17.168465, 'pp': 17.402732, 'p': 17.512854, 'mp': 17.756928, 'mf': 18.075671, 'f': 18.558642, 'ff': 19.250242, 'fff': 19.82561, 'ffff': 20.298261},
    'D#6': {'pppp': 14.921497, 'ppp': 15.011135, 'pp': 15.123941, 'p': 15.154163, 'mp': 15.242286, 'mf': 15.384922, 'f': 16.024216, 'ff': 17.261184, 'fff': 18.182973, 'ffff': 18.955722},
    'E6': {'pppp': 17.085154, 'ppp': 17.402547, 'pp': 17.807593, 'p': 18.611921, 'mp': 19.018194, 'mf': 19.127084, 'f': 18.770326, 'ff': 17.918635, 'fff': 17.471615, 'ffff': 17.122042},
    'F6': {'pppp': 10.064465, 'ppp': 10.220419, 'pp': 10.418763, 'p': 10.801964, 'mp': 10.993583, 'mf': 11.044518, 'f': 10.87422, 'ff': 10.466071, 'fff': 10.263404, 'ffff': 10.104099},
    'F#6': {'pppp': 11.553704, 'ppp': 11.705258, 'pp': 11.897499, 'p': 12.233484, 'mp': 12.420728, 'mf': 12.478031, 'f': 12.370437, 'ff': 12.090705, 'fff': 11.98093, 'ffff': 11.893828},
    'G6': {'pppp': 12.934318, 'ppp': 13.02607, 'pp': 13.141676, 'p': 13.216183, 'mp': 13.286704, 'mf': 13.353354, 'f': 13.415833, 'ff': 13.473995, 'fff': 13.590471, 'ffff': 13.684376},
    'G#6': {'pppp': 12.713665, 'ppp': 12.789811, 'pp': 12.885636, 'p': 12.907399, 'mp': 12.963662, 'mf': 13.04092, 'f': 13.181187, 'ff': 13.394886, 'fff': 13.59561, 'ffff': 13.758353},
    'A6': {'pppp': 11.858321, 'ppp': 11.974134, 'pp': 12.120493, 'p': 12.222309, 'mp': 12.356042, 'mf': 12.513154, 'f': 12.707034, 'ff': 12.943853, 'fff': 13.171415, 'ffff': 13.356343},
    'A#6': {'pppp': 10.33418, 'ppp': 10.517618, 'pp': 10.751502, 'p': 11.109744, 'mp': 11.384774, 'mf': 11.517981, 'f': 11.553489, 'ff': 11.567559, 'fff': 11.631654, 'ffff': 11.683185},
    'B6': {'pppp': 11.26392, 'ppp': 11.306288, 'pp': 11.359471, 'p': 11.349786, 'mp': 11.346219, 'mf': 11.34571, 'f': 11.43263, 'ff': 11.616732, 'fff': 11.779343, 'ffff': 11.911069},
    'C7': {'pppp': 8.625692, 'ppp': 8.924458, 'pp': 9.31251, 'p': 9.992116, 'mp': 10.502028, 'mf': 10.702042, 'f': 10.687856, 'ff': 10.589079, 'fff': 10.567986, 'ffff': 10.551142},
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
