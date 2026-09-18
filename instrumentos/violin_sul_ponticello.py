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
        "(dest Zenodo Violin_sul ponticello Media (IOWA+Orchidea average); Dynamics_predicter Results ladder (CORDAS_4))."
    ),
    source_url_or_identifier='docs/instrument_acoustic_sources.md#violin-sul-ponticello',
    extraction_method=(
        "Committed full dynamic ladder from Dynamics extrapolator v1.5.2.1 Results sheet "
        "(PCHIP interiors, tapered outers r=0.80) on measured pp/mf/ff anchors; "
        "interior cells clamped into their measured segment where the workbook "
        "marginally overshoots; pitch lookup via MIDI-space spectral_lookup"
    ),
    dynamic_levels=('pppp', 'ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', 'ffff'),
    pitch_range=(55, 93),
    uncertainty="high",
    version="2026-09-18",
    source_technique="arco_sul_ponticello",
    table_supported_techniques=("arco_sul_ponticello",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("violin_sul_ponticello")

# Full 10-dynamic CDM ladder (Results sheet). Anchors pp/mf/ff match measured
# workbook midpoints; other levels are workbook-committed.
spectral_data = {
    'G3': {'pppp': 32.606817, 'ppp': 33.25706, 'pp': 34.08813, 'p': 34.784314, 'mp': 35.705007, 'mf': 36.801923, 'f': 38.177002, 'ff': 39.891084, 'fff': 41.431847, 'ffff': 42.707196},
    'G#3': {'pppp': 39.995479, 'ppp': 40.515144, 'pp': 41.174229, 'p': 41.562799, 'mp': 42.252424, 'mf': 43.129796, 'f': 44.375835, 'ff': 46.083944, 'fff': 47.555672, 'ffff': 48.766824},
    'A3': {'pppp': 24.825002, 'ppp': 25.987392, 'pp': 27.517214, 'p': 28.550587, 'mp': 30.427473, 'mf': 32.939491, 'f': 36.746826, 'ff': 42.461285, 'fff': 47.870261, 'ffff': 52.689482},
    'A#3': {'pppp': 34.262351, 'ppp': 34.718614, 'pp': 35.297496, 'p': 35.505758, 'mp': 36.10428, 'mf': 37.060938, 'f': 40.644084, 'ff': 47.853499, 'fff': 53.86964, 'ffff': 59.222722},
    'B3': {'pppp': 38.675366, 'ppp': 38.010573, 'pp': 37.195628, 'p': 35.259877, 'mp': 34.407717, 'mf': 34.20698, 'f': 35.113406, 'ff': 37.393328, 'fff': 38.985768, 'ffff': 40.30841},
    'C4': {'pppp': 40.966946, 'ppp': 40.759624, 'pp': 40.501946, 'p': 39.652712, 'mp': 39.344345, 'mf': 39.300488, 'f': 41.318761, 'ff': 45.989672, 'fff': 49.404933, 'ffff': 52.318864},
    'C#4': {'pppp': 21.027431, 'ppp': 21.179608, 'pp': 21.37138, 'p': 21.425526, 'mp': 21.565888, 'mf': 21.759492, 'f': 22.11489, 'ff': 22.661354, 'fff': 23.140703, 'ffff': 23.531474},
    'D4': {'pppp': 19.717169, 'ppp': 20.601966, 'pp': 21.764004, 'p': 22.813918, 'mp': 24.20307, 'mf': 25.898301, 'f': 28.074569, 'ff': 30.879759, 'fff': 33.543405, 'ffff': 35.838823},
    'D#4': {'pppp': 24.950346, 'ppp': 25.908689, 'pp': 27.158545, 'p': 28.729223, 'mp': 30.220659, 'mf': 31.607872, 'f': 32.874887, 'ff': 34.004352, 'fff': 35.217268, 'ffff': 36.218676},
    'E4': {'pppp': 23.782119, 'ppp': 24.598771, 'pp': 25.659133, 'p': 26.76069, 'mp': 27.994902, 'mf': 29.359787, 'f': 30.89025, 'ff': 32.613079, 'fff': 34.265153, 'ffff': 35.646868},
    'F4': {'pppp': 26.400819, 'ppp': 26.949093, 'pp': 27.650474, 'p': 28.349893, 'mp': 29.122546, 'mf': 29.963161, 'f': 30.890032, 'ff': 31.914623, 'fff': 32.89648, 'ffff': 33.703671},
    'F#4': {'pppp': 25.649225, 'ppp': 26.345448, 'pp': 27.242362, 'p': 28.7921, 'mp': 29.929505, 'mf': 30.369545, 'f': 30.329804, 'ff': 30.053066, 'fff': 30.034955, 'ffff': 30.020475},
    'G4': {'pppp': 23.045743, 'ppp': 24.192421, 'pp': 25.706331, 'p': 28.282611, 'mp': 30.359713, 'mf': 31.351427, 'f': 31.558843, 'ff': 31.639468, 'fff': 31.853561, 'ffff': 32.025878},
    'G#4': {'pppp': 32.767595, 'ppp': 33.026362, 'pp': 33.352695, 'p': 33.45375, 'mp': 33.728427, 'mf': 34.134956, 'f': 35.132346, 'ff': 36.826842, 'fff': 38.149433, 'ffff': 39.241624},
    'A4': {'pppp': 30.737949, 'ppp': 30.465232, 'pp': 30.127735, 'p': 29.209475, 'mp': 28.87827, 'mf': 28.831263, 'f': 30.779731, 'ff': 35.416947, 'fff': 38.93205, 'ffff': 41.993706},
    'A#4': {'pppp': 21.420737, 'ppp': 21.734611, 'pp': 22.133429, 'p': 22.305129, 'mp': 22.749313, 'mf': 23.360515, 'f': 24.439811, 'ff': 26.122875, 'fff': 27.501916, 'ffff': 28.657384},
    'B4': {'pppp': 28.123641, 'ppp': 28.414351, 'pp': 28.781967, 'p': 29.47054, 'mp': 29.732832, 'mf': 29.772704, 'f': 29.313058, 'ff': 28.282616, 'fff': 27.82626, 'ffff': 27.466482},
    'C5': {'pppp': 22.079569, 'ppp': 22.563434, 'pp': 23.183204, 'p': 23.95345, 'mp': 24.649711, 'mf': 25.257625, 'f': 25.778347, 'ff': 26.209028, 'fff': 26.717919, 'ffff': 27.132137},
    'C#5': {'pppp': 16.909315, 'ppp': 17.177056, 'pp': 17.517702, 'p': 17.767368, 'mp': 18.133666, 'mf': 18.582729, 'f': 19.174696, 'ff': 19.942537, 'fff': 20.619937, 'ffff': 21.178386},
    'D5': {'pppp': 10.948666, 'ppp': 11.062518, 'pp': 11.2065, 'p': 11.260794, 'mp': 11.403749, 'mf': 11.605877, 'f': 12.00704, 'ff': 12.651589, 'fff': 13.166456, 'ffff': 13.593396},
    'D#5': {'pppp': 16.477432, 'ppp': 16.860264, 'pp': 17.351335, 'p': 17.938278, 'mp': 18.491282, 'mf': 19.006014, 'f': 19.478419, 'ff': 19.904687, 'fff': 20.369835, 'ffff': 20.749768},
    'E5': {'pppp': 22.780539, 'ppp': 23.195005, 'pp': 23.723709, 'p': 24.279256, 'mp': 24.847992, 'mf': 25.430214, 'f': 26.026271, 'ff': 26.636508, 'fff': 27.260619, 'ffff': 27.77042},
    'F5': {'pppp': 19.372708, 'ppp': 19.660088, 'pp': 20.025314, 'p': 20.538976, 'mp': 20.935248, 'mf': 21.143344, 'f': 21.22037, 'ff': 21.252139, 'fff': 21.404574, 'ffff': 21.527309},
    'F#5': {'pppp': 18.733406, 'ppp': 19.115668, 'pp': 19.604483, 'p': 20.266087, 'mp': 20.820087, 'mf': 21.226956, 'f': 21.516302, 'ff': 21.697005, 'fff': 21.983309, 'ffff': 22.215071},
    'G5': {'pppp': 18.09105, 'ppp': 18.385514, 'pp': 18.760343, 'p': 19.071002, 'mp': 19.470611, 'mf': 19.939779, 'f': 20.515944, 'ff': 21.219736, 'fff': 21.86206, 'ffff': 22.38989},
    'G#5': {'pppp': 17.36279, 'ppp': 17.444771, 'pp': 17.547792, 'p': 17.582817, 'mp': 17.595739, 'mf': 17.597585, 'f': 17.431179, 'ff': 17.085611, 'fff': 17.006461, 'ffff': 16.943405},
    'A5': {'pppp': 16.877812, 'ppp': 17.151118, 'pp': 17.498983, 'p': 18.053814, 'mp': 18.446503, 'mf': 18.595, 'f': 18.576457, 'ff': 18.447173, 'fff': 18.479105, 'ffff': 18.50469},
    'A#5': {'pppp': 14.981269, 'ppp': 15.120126, 'pp': 15.295508, 'p': 15.62803, 'mp': 15.752352, 'mf': 15.770193, 'f': 15.199112, 'ff': 14.034182, 'fff': 13.396796, 'ffff': 12.907793},
    'B5': {'pppp': 15.494845, 'ppp': 15.654449, 'pp': 15.856268, 'p': 16.120211, 'mp': 16.29897, 'mf': 16.364562, 'f': 16.347909, 'ff': 16.260668, 'fff': 16.318756, 'ffff': 16.365376},
    'C6': {'pppp': 13.151129, 'ppp': 13.481667, 'pp': 13.906547, 'p': 14.503141, 'mp': 15.002937, 'mf': 15.363913, 'f': 15.61528, 'ff': 15.765738, 'fff': 15.996484, 'ffff': 16.183509},
    'C#6': {'pppp': 15.69259, 'ppp': 15.885136, 'pp': 16.129145, 'p': 16.350318, 'mp': 16.583948, 'mf': 16.829036, 'f': 17.087884, 'ff': 17.361695, 'fff': 17.661563, 'ffff': 17.905183},
    'D6': {'pppp': 16.974038, 'ppp': 17.163249, 'pp': 17.402732, 'p': 17.512854, 'mp': 17.756928, 'mf': 18.075671, 'f': 18.558642, 'ff': 19.250242, 'fff': 19.836226, 'ffff': 20.31783},
    'D#6': {'pppp': 14.912376, 'ppp': 15.006037, 'pp': 15.123941, 'p': 15.154163, 'mp': 15.242286, 'mf': 15.384922, 'f': 16.024216, 'ff': 17.261184, 'fff': 18.186403, 'ffff': 18.962158},
    'E6': {'pppp': 17.080432, 'ppp': 17.399875, 'pp': 17.807593, 'p': 18.611921, 'mp': 19.018194, 'mf': 19.127084, 'f': 18.770326, 'ff': 17.918635, 'fff': 17.490535, 'ffff': 17.15543},
    'F6': {'pppp': 10.060459, 'ppp': 10.218159, 'pp': 10.418763, 'p': 10.801964, 'mp': 10.993583, 'mf': 11.044518, 'f': 10.87422, 'ff': 10.466071, 'fff': 10.274692, 'ffff': 10.124112},
    'F#6': {'pppp': 11.547474, 'ppp': 11.701751, 'pp': 11.897499, 'p': 12.233484, 'mp': 12.420728, 'mf': 12.478031, 'f': 12.370437, 'ff': 12.090705, 'fff': 11.994052, 'ffff': 11.917287},
    'G6': {'pppp': 12.923187, 'ppp': 13.019841, 'pp': 13.141676, 'p': 13.216183, 'mp': 13.286704, 'mf': 13.353354, 'f': 13.415833, 'ff': 13.473995, 'fff': 13.606041, 'ffff': 13.712609},
    'G#6': {'pppp': 12.252853, 'ppp': 12.53016, 'pp': 12.885636, 'p': 13.553528, 'mp': 13.949497, 'mf': 14.077539, 'f': 13.892853, 'ff': 13.394886, 'fff': 13.160865, 'ffff': 12.976594},
    'A6': {'pppp': 11.345064, 'ppp': 11.683378, 'pp': 12.120493, 'p': 12.942589, 'mp': 13.462545, 'mf': 13.640517, 'f': 13.462999, 'ff': 12.943853, 'fff': 12.691938, 'ffff': 12.493941},
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
