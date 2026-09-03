# instrumentos/cello_sul_ponticello.py
"""
Cello (arco sul ponticello) instrument density module.

The ``spectral_data`` table stores a committed 10-dynamic Combined Density
Metric (CDM) ladder from the ``Results`` sheet of
``Cello_Zenodo_collections_sul_ponticello_Dynamics10.xlsx``
(measured pp/mf/ff anchors; remaining levels committed from that workbook —
no runtime dynamic extrapolation).

Runtime analysis does not ingest audio; it maps notated pitch + dynamic to
these pre-loaded acoustic metadata tables.
"""

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="external_acoustic_metadata",
    citation=(
        "Cello arco_sul_ponticello CDM ladder: measured pp/mf/ff anchors with "
        "committed Results sheet values for all 10 dynamic levels from "
        "Cello_Zenodo_collections_sul_ponticello_Dynamics10.xlsx "
        "(dest Zenodo Cello_sul ponticello Media (IOWA+Orchidea average); Dynamics_predicter Results ladder)."
    ),
    source_url_or_identifier='docs/instrument_acoustic_sources.md#cello-sul-ponticello',
    extraction_method=(
        "Committed full dynamic ladder from Dynamics extrapolator v1.5.2.1 Results sheet "
        "(PCHIP interiors, tapered outers r=0.80) on measured pp/mf/ff anchors; "
        "interior cells clamped into their measured segment where the workbook "
        "marginally overshoots; pitch lookup via MIDI-space spectral_lookup"
    ),
    dynamic_levels=('pppp', 'ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', 'ffff'),
    pitch_range=(36, 81),
    uncertainty="high",
    version="2026-09-03",
    source_technique="arco_sul_ponticello",
    table_supported_techniques=("arco_sul_ponticello",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("cello_sul_ponticello")

# Full 10-dynamic CDM ladder (Results sheet). Anchors pp/mf/ff match measured
# workbook midpoints; other levels are workbook-committed.
spectral_data = {
    'C2': {'pppp': 64.177811, 'ppp': 64.257386, 'pp': 64.356995, 'p': 64.335961, 'mp': 64.269604, 'mf': 64.153127, 'f': 61.03772, 'ff': 55.154723, 'fff': 51.533183, 'ffff': 48.807928},
    'C#2': {'pppp': 23.938391, 'ppp': 23.839432, 'pp': 23.716309, 'p': 23.31965, 'mp': 23.175191, 'mf': 23.154627, 'f': 24.611036, 'ff': 28.003968, 'fff': 30.444349, 'ffff': 32.548906},
    'D2': {'pppp': 25.017187, 'ppp': 25.934883, 'pp': 27.129486, 'p': 29.427983, 'mp': 30.853166, 'mf': 31.329143, 'f': 30.729694, 'ff': 29.088496, 'fff': 28.088882, 'ffff': 27.31398},
    'D#2': {'pppp': 28.841099, 'ppp': 30.159426, 'pp': 31.892397, 'p': 35.16806, 'mp': 37.361394, 'mf': 38.143724, 'f': 37.545153, 'ff': 35.670905, 'fff': 34.551225, 'ffff': 33.680839},
    'E2': {'pppp': 43.518142, 'ppp': 42.537161, 'pp': 41.341973, 'p': 38.611576, 'mp': 37.651746, 'mf': 37.51659, 'f': 40.332282, 'ff': 47.342834, 'fff': 52.656557, 'ffff': 57.333839},
    'F2': {'pppp': 38.369247, 'ppp': 39.635379, 'pp': 41.27696, 'p': 44.154487, 'mp': 46.266053, 'mf': 47.081625, 'f': 46.989541, 'ff': 46.349979, 'fff': 45.937276, 'ffff': 45.609761},
    'F#2': {'pppp': 33.850962, 'ppp': 35.4925, 'pp': 37.656812, 'p': 41.779006, 'mp': 44.529051, 'mf': 45.50496, 'f': 44.698204, 'ff': 42.239894, 'fff': 40.772462, 'ffff': 39.635307},
    'G2': {'pppp': 27.355059, 'ppp': 27.809875, 'pp': 28.389043, 'p': 29.663537, 'mp': 30.148425, 'mf': 30.218858, 'f': 29.343394, 'ff': 27.429034, 'fff': 26.238773, 'ffff': 25.323862},
    'G#2': {'pppp': 40.356132, 'ppp': 40.602998, 'pp': 40.913704, 'p': 41.324421, 'mp': 41.476775, 'mf': 41.498586, 'f': 40.809116, 'ff': 39.356185, 'fff': 38.405879, 'ffff': 37.662182},
    'A2': {'pppp': 36.568825, 'ppp': 37.505227, 'pp': 38.70952, 'p': 39.869228, 'mp': 41.227444, 'mf': 42.764459, 'f': 44.547065, 'ff': 46.619666, 'fff': 48.347055, 'ffff': 49.774937},
    'A#2': {'pppp': 28.750754, 'ppp': 29.586257, 'pp': 30.664862, 'p': 32.773278, 'mp': 33.98411, 'mf': 34.359889, 'f': 33.657341, 'ff': 31.869701, 'fff': 30.767336, 'ffff': 29.912961},
    'B2': {'pppp': 31.205924, 'ppp': 32.784684, 'pp': 34.870923, 'p': 39.404509, 'mp': 41.735833, 'mf': 42.33927, 'f': 40.005477, 'ff': 34.860482, 'fff': 31.8011, 'ffff': 29.548073},
    'C3': {'pppp': 36.729434, 'ppp': 38.066512, 'pp': 39.806513, 'p': 43.259004, 'mp': 45.265885, 'mf': 45.891914, 'f': 44.71841, 'ff': 41.762332, 'fff': 39.958034, 'ffff': 38.570885},
    'C#3': {'pppp': 32.976567, 'ppp': 33.607913, 'pp': 34.41412, 'p': 34.953608, 'mp': 35.862854, 'mf': 37.019351, 'f': 38.647859, 'ff': 40.883154, 'fff': 42.6254, 'ffff': 44.072504},
    'D3': {'pppp': 49.819627, 'ppp': 50.459226, 'pp': 51.270285, 'p': 51.61796, 'mp': 52.504914, 'mf': 53.697464, 'f': 55.657982, 'ff': 58.606359, 'fff': 60.712171, 'ffff': 62.45117},
    'D#3': {'pppp': 27.901373, 'ppp': 29.008202, 'pp': 30.453684, 'p': 32.658488, 'mp': 34.481521, 'mf': 35.642915, 'f': 36.314447, 'ff': 36.618405, 'fff': 36.989749, 'ffff': 37.289533},
    'E3': {'pppp': 29.973794, 'ppp': 31.185351, 'pp': 32.768893, 'p': 35.647731, 'mp': 37.685106, 'mf': 38.448649, 'f': 38.197372, 'ff': 37.068013, 'fff': 36.404672, 'ffff': 35.882557},
    'F3': {'pppp': 36.177661, 'ppp': 37.025405, 'pp': 38.113074, 'p': 39.586806, 'mp': 40.838774, 'mf': 41.788119, 'f': 42.486423, 'ff': 42.947132, 'fff': 43.343365, 'ffff': 43.662982},
    'F#3': {'pppp': 23.267615, 'ppp': 23.606858, 'pp': 24.037876, 'p': 24.759671, 'mp': 25.207328, 'mf': 25.359624, 'f': 25.218594, 'ff': 24.791707, 'fff': 24.489821, 'ffff': 24.25096},
    'G3': {'pppp': 53.164138, 'ppp': 52.773505, 'pp': 52.289247, 'p': 50.905696, 'mp': 50.405246, 'mf': 50.334156, 'f': 52.951929, 'ff': 59.06238, 'fff': 63.309558, 'ffff': 66.926167},
    'G#3': {'pppp': 39.482001, 'ppp': 39.043715, 'pp': 38.502694, 'p': 37.10784, 'mp': 36.436146, 'mf': 36.257489, 'f': 36.814948, 'ff': 38.235176, 'fff': 39.004726, 'ffff': 39.631503},
    'A3': {'pppp': 31.694508, 'ppp': 32.365591, 'pp': 33.22446, 'p': 34.770446, 'mp': 35.742984, 'mf': 36.076423, 'f': 35.771382, 'ff': 34.850443, 'fff': 34.258743, 'ffff': 33.792624},
    'A#3': {'pppp': 29.716466, 'ppp': 30.340893, 'pp': 31.139911, 'p': 32.359218, 'mp': 33.310291, 'mf': 33.811954, 'f': 33.996443, 'ff': 34.072523, 'fff': 34.083769, 'ffff': 34.092769},
    'B3': {'pppp': 27.816138, 'ppp': 28.28484, 'pp': 28.881839, 'p': 30.014123, 'mp': 30.609322, 'mf': 30.778266, 'f': 30.329709, 'ff': 29.227606, 'fff': 28.523925, 'ffff': 27.973199},
    'C4': {'pppp': 25.975178, 'ppp': 25.538434, 'pp': 25.002815, 'p': 23.662482, 'mp': 23.186997, 'mf': 23.119855, 'f': 23.995302, 'ff': 26.129893, 'fff': 27.54689, 'ffff': 28.735617},
    'C#4': {'pppp': 29.662596, 'ppp': 29.651251, 'pp': 29.637076, 'p': 29.267808, 'mp': 29.080456, 'mf': 29.027955, 'f': 29.166077, 'ff': 29.517853, 'fff': 29.585688, 'ffff': 29.640067},
    'D4': {'pppp': 31.185679, 'ppp': 31.419885, 'pp': 31.715118, 'p': 32.202634, 'mp': 32.384128, 'mf': 32.410139, 'f': 31.754146, 'ff': 30.366226, 'fff': 29.478852, 'ffff': 28.787659},
    'D#4': {'pppp': 39.38049, 'ppp': 38.998333, 'pp': 38.525847, 'p': 38.088558, 'mp': 37.388508, 'mf': 36.543616, 'f': 35.434627, 'ff': 34.042712, 'fff': 32.950407, 'ffff': 32.101853},
    'E4': {'pppp': 34.322818, 'ppp': 34.713652, 'pp': 35.208459, 'p': 35.948476, 'mp': 36.416308, 'mf': 36.578586, 'f': 36.460077, 'ff': 36.073642, 'fff': 35.750284, 'ffff': 35.493685},
    'F4': {'pppp': 22.519011, 'ppp': 23.32118, 'pp': 24.364193, 'p': 26.404351, 'mp': 27.620799, 'mf': 28.011364, 'f': 27.385167, 'ff': 25.757803, 'fff': 24.763858, 'ffff': 23.99639},
    'F#4': {'pppp': 18.176642, 'ppp': 18.543154, 'pp': 19.011703, 'p': 19.937965, 'mp': 20.414086, 'mf': 20.544509, 'f': 20.146383, 'ff': 19.190759, 'fff': 18.592028, 'ffff': 18.126522},
    'G4': {'pppp': 26.405203, 'ppp': 26.726715, 'pp': 27.134116, 'p': 27.982905, 'mp': 28.302266, 'mf': 28.348185, 'f': 27.178324, 'ff': 24.789051, 'fff': 23.319702, 'ffff': 22.207183},
    'G#4': {'pppp': 17.01381, 'ppp': 17.485054, 'pp': 18.092506, 'p': 19.185127, 'mp': 19.920497, 'mf': 20.1867, 'f': 20.05026, 'ff': 19.548984, 'fff': 19.237286, 'ffff': 18.991509},
    'A4': {'pppp': 25.844494, 'ppp': 25.910056, 'pp': 25.992243, 'p': 25.981946, 'mp': 25.950583, 'mf': 25.897483, 'f': 25.43834, 'ff': 24.566548, 'fff': 23.979314, 'ffff': 23.51965},
    'A#4': {'pppp': 25.829187, 'ppp': 25.688441, 'pp': 25.513586, 'p': 24.890295, 'mp': 24.622428, 'mf': 24.563684, 'f': 24.888155, 'ff': 25.675541, 'fff': 26.066761, 'ffff': 26.384025},
    'B4': {'pppp': 25.728757, 'ppp': 25.719107, 'pp': 25.70705, 'p': 25.375412, 'mp': 25.239571, 'mf': 25.212959, 'f': 25.403422, 'ff': 25.855021, 'fff': 26.006325, 'ffff': 26.128005},
    'C5': {'pppp': 23.537046, 'ppp': 23.373921, 'pp': 23.171604, 'p': 22.718206, 'mp': 22.352984, 'mf': 22.087684, 'f': 21.898687, 'ff': 21.776958, 'fff': 21.582382, 'ffff': 21.427974},
    'C#5': {'pppp': 20.044134, 'ppp': 20.364483, 'pp': 20.772127, 'p': 21.663997, 'mp': 22.002148, 'mf': 22.050884, 'f': 21.382748, 'ff': 19.936532, 'fff': 19.038251, 'ffff': 18.348855},
    'D5': {'pppp': 18.88723, 'ppp': 18.86041, 'pp': 18.826939, 'p': 18.716878, 'mp': 18.566184, 'mf': 18.389401, 'f': 18.16999, 'ff': 17.903471, 'fff': 17.654136, 'ffff': 17.45717},
    'D#5': {'pppp': 14.510005, 'ppp': 14.730292, 'pp': 15.010361, 'p': 15.50448, 'mp': 15.789346, 'mf': 15.879557, 'f': 15.737714, 'ff': 15.358224, 'fff': 15.105266, 'ffff': 14.905902},
    'E5': {'pppp': 17.738561, 'ppp': 18.056558, 'pp': 18.462084, 'p': 19.359836, 'mp': 19.701481, 'mf': 19.750777, 'f': 18.460057, 'ff': 15.931897, 'fff': 14.419784, 'ffff': 13.314099},
    'F5': {'pppp': 18.243339, 'ppp': 18.382745, 'pp': 18.558501, 'p': 18.728101, 'mp': 18.839559, 'mf': 18.879578, 'f': 18.863492, 'ff': 18.797027, 'fff': 18.681747, 'ffff': 18.590033},
    'F#5': {'pppp': 13.667723, 'ppp': 13.882792, 'pp': 14.156392, 'p': 14.744338, 'mp': 14.975137, 'mf': 15.012403, 'f': 14.624061, 'ff': 13.766161, 'fff': 13.230291, 'ffff': 12.816653},
    'G5': {'pppp': 15.8669, 'ppp': 16.223982, 'pp': 16.681658, 'p': 17.357436, 'mp': 17.89801, 'mf': 18.225985, 'f': 18.401673, 'ff': 18.479475, 'fff': 18.537238, 'ffff': 18.583578},
    'G#5': {'pppp': 15.701552, 'ppp': 15.629555, 'pp': 15.540022, 'p': 15.381097, 'mp': 15.19664, 'mf': 14.994125, 'f': 14.766046, 'ff': 14.510768, 'fff': 14.275438, 'ffff': 14.089924},
    'A5': {'pppp': 17.863957, 'ppp': 17.777483, 'pp': 17.669979, 'p': 17.285783, 'mp': 17.074273, 'mf': 17.008872, 'f': 17.114357, 'ff': 17.40347, 'fff': 17.502888, 'ffff': 17.582831},
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
