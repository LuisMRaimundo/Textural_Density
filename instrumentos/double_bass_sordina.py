# instrumentos/double_bass_sordina.py
"""
Double bass (arco con sordino) instrument density module.

The ``spectral_data`` table stores a committed 10-dynamic Combined Density
Metric (CDM) ladder from the ``Results`` sheet of
``DoubleBass_con_sordino_dynamics.xlsx``
(measured pp/mf/ff anchors; remaining levels committed from that workbook —
no runtime dynamic extrapolation).

Runtime analysis does not ingest audio; it maps notated pitch + dynamic to
these pre-loaded acoustic metadata tables.
"""

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="external_acoustic_metadata",
    citation=(
        "Double bass arco_sordina CDM ladder: measured pp/mf/ff anchors with "
        "committed Results sheet values for all 10 dynamic levels from "
        "DoubleBass_con_sordino_dynamics.xlsx "
        "(dest Zenodo DoubleBass_con sordino Media (IOWA+Orchidea average); Dynamics_predicter Results ladder)."
    ),
    source_url_or_identifier='docs/instrument_acoustic_sources.md#double-bass-sordina',
    extraction_method=(
        "Committed full dynamic ladder from Dynamics extrapolator v1.5.2.1 Results sheet "
        "(PCHIP interiors, tapered outers r=0.80) on measured pp/mf/ff anchors; "
        "interior cells clamped into their measured segment where the workbook "
        "marginally overshoots; pitch lookup via MIDI-space spectral_lookup"
    ),
    dynamic_levels=('pppp', 'ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', 'ffff'),
    pitch_range=(29, 67),
    uncertainty="high",
    version="2026-08-27",
    source_technique="arco_sordina",
    table_supported_techniques=("arco_sordina",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("double_bass_sordina")

# Full 10-dynamic CDM ladder (Results sheet). Anchors pp/mf/ff match measured
# workbook midpoints; other levels are workbook-committed.
spectral_data = {
    'F1': {'pppp': 41.340752, 'ppp': 42.608522, 'pp': 44.248046, 'p': 48.375104, 'mp': 50.152717, 'mf': 50.492454, 'f': 47.873455, 'ff': 42.28358, 'fff': 39.262151, 'ffff': 37.001213},
    'F#1': {'pppp': 35.786242, 'ppp': 36.259473, 'pp': 36.859821, 'p': 38.550811, 'mp': 39.282705, 'mf': 39.432766, 'f': 38.44152, 'ff': 36.210216, 'fff': 35.217871, 'ffff': 34.443612},
    'G1': {'pppp': 33.839941, 'ppp': 33.37133, 'pp': 32.794681, 'p': 31.566788, 'mp': 31.126088, 'mf': 31.063636, 'f': 31.988098, 'ff': 34.186598, 'fff': 35.859138, 'ffff': 37.255896},
    'G#1': {'pppp': 31.674312, 'ppp': 31.558961, 'pp': 31.415363, 'p': 31.397268, 'mp': 31.342369, 'mf': 31.249843, 'f': 30.505854, 'ff': 29.112336, 'fff': 28.62539, 'ffff': 28.241703},
    'A1': {'pppp': 37.97643, 'ppp': 37.501084, 'pp': 36.915259, 'p': 35.689118, 'mp': 35.247721, 'mf': 35.185112, 'f': 36.887536, 'ff': 40.89194, 'fff': 43.90723, 'ffff': 46.478778},
    'A#1': {'pppp': 47.639767, 'ppp': 46.385689, 'pp': 44.864414, 'p': 41.960802, 'mp': 40.581788, 'mf': 40.214178, 'f': 41.317601, 'ff': 44.200314, 'fff': 46.338174, 'ffff': 48.122676},
    'B1': {'pppp': 41.461047, 'ppp': 41.411402, 'pp': 41.349429, 'p': 41.36414, 'mp': 41.410475, 'mf': 41.491803, 'f': 43.425454, 'ff': 47.629075, 'fff': 50.838397, 'ffff': 53.560869},
    'C2': {'pppp': 37.247881, 'ppp': 36.826827, 'pp': 36.307197, 'p': 35.234153, 'mp': 34.846865, 'mf': 34.791887, 'f': 35.539821, 'ff': 37.307766, 'fff': 38.723721, 'ffff': 39.895081},
    'C#2': {'pppp': 27.684229, 'ppp': 27.767175, 'pp': 27.871207, 'p': 28.386744, 'mp': 28.623218, 'mf': 28.678996, 'f': 28.417505, 'ff': 27.800418, 'fff': 27.792429, 'ffff': 27.78604},
    'D2': {'pppp': 31.528771, 'ppp': 31.3558, 'pp': 31.14092, 'p': 31.084136, 'mp': 30.919301, 'mf': 30.655416, 'f': 29.491764, 'ff': 27.471064, 'fff': 26.493856, 'ffff': 25.737177},
    'D#2': {'pppp': 30.973514, 'ppp': 30.815194, 'pp': 30.618431, 'p': 30.356668, 'mp': 30.260794, 'mf': 30.247122, 'f': 30.817016, 'ff': 32.075296, 'fff': 33.165921, 'ffff': 34.065061},
    'E2': {'pppp': 31.623109, 'ppp': 31.211508, 'pp': 30.704533, 'p': 29.64419, 'mp': 29.262836, 'mf': 29.208759, 'f': 31.570917, 'ff': 37.29563, 'fff': 41.793391, 'ffff': 45.779108},
    'F2': {'pppp': 26.401286, 'ppp': 26.779839, 'pp': 27.260673, 'p': 28.600394, 'mp': 29.110404, 'mf': 29.184001, 'f': 27.823904, 'ff': 25.022656, 'fff': 23.55678, 'ffff': 22.446155},
    'F#2': {'pppp': 28.859224, 'ppp': 28.619117, 'pp': 28.32179, 'p': 27.854524, 'mp': 27.620171, 'mf': 27.555286, 'f': 27.733441, 'ff': 28.186353, 'fff': 28.76982, 'ffff': 29.245278},
    'G2': {'pppp': 24.821617, 'ppp': 25.048343, 'pp': 25.334665, 'p': 26.230633, 'mp': 26.568656, 'mf': 26.617299, 'f': 25.791778, 'ff': 24.036071, 'fff': 23.216275, 'ffff': 22.580616},
    'G#2': {'pppp': 24.07386, 'ppp': 23.917162, 'pp': 23.722724, 'p': 23.66175, 'mp': 23.501076, 'mf': 23.274384, 'f': 22.804158, 'ff': 22.081131, 'fff': 21.873331, 'ffff': 21.708499},
    'A2': {'pppp': 30.251758, 'ppp': 29.555543, 'pp': 28.707763, 'p': 26.884, 'mp': 26.231923, 'mf': 26.135264, 'f': 27.291445, 'ff': 30.147668, 'fff': 32.27851, 'ffff': 34.091122},
    'A#2': {'pppp': 29.509667, 'ppp': 28.898818, 'pp': 28.153007, 'p': 26.548052, 'mp': 25.9801, 'mf': 25.899962, 'f': 27.317237, 'ff': 30.775654, 'fff': 33.38785, 'ffff': 35.636364},
    'B2': {'pppp': 32.871393, 'ppp': 31.43141, 'pp': 29.719812, 'p': 26.216691, 'mp': 25.03287, 'mf': 24.868174, 'f': 27.420213, 'ff': 34.207946, 'fff': 39.781659, 'ffff': 44.887727},
    'C3': {'pppp': 32.408058, 'ppp': 31.2116, 'pp': 29.777951, 'p': 26.81147, 'mp': 25.794679, 'mf': 25.652606, 'f': 28.572032, 'ff': 36.291383, 'fff': 42.754977, 'ffff': 48.745351},
    'C#3': {'pppp': 27.210406, 'ppp': 26.634686, 'pp': 25.932134, 'p': 24.433561, 'mp': 23.903558, 'mf': 23.828787, 'f': 25.654694, 'ff': 30.166922, 'fff': 33.691787, 'ffff': 36.805988},
    'D3': {'pppp': 23.793322, 'ppp': 24.321272, 'pp': 24.997713, 'p': 26.806471, 'mp': 27.505358, 'mf': 27.606675, 'f': 26.258249, 'ff': 23.424708, 'fff': 21.913804, 'ffff': 20.775556},
    'D#3': {'pppp': 32.749005, 'ppp': 31.144422, 'pp': 29.248795, 'p': 25.447258, 'mp': 24.174844, 'mf': 23.99834, 'f': 27.602743, 'ff': 37.66882, 'fff': 46.683228, 'ffff': 55.424778},
    'E3': {'pppp': 36.347909, 'ppp': 34.102488, 'pp': 31.489759, 'p': 26.398188, 'mp': 24.737444, 'mf': 24.508882, 'f': 28.394463, 'ff': 39.548847, 'fff': 49.707723, 'ffff': 59.683722},
    'F3': {'pppp': 26.711717, 'ppp': 25.928231, 'pp': 24.98111, 'p': 22.971483, 'mp': 22.260176, 'mf': 22.154294, 'f': 23.410364, 'ff': 26.576642, 'fff': 28.969494, 'ffff': 31.037988},
    'F#3': {'pppp': 24.298983, 'ppp': 23.653316, 'pp': 22.870304, 'p': 21.211752, 'mp': 20.631503, 'mf': 20.549916, 'f': 22.359528, 'ff': 26.937203, 'fff': 30.588411, 'ffff': 33.862612},
    'G3': {'pppp': 24.631132, 'ppp': 23.997084, 'pp': 23.227425, 'p': 21.589561, 'mp': 21.015696, 'mf': 20.93497, 'f': 22.547984, 'ff': 26.588066, 'fff': 29.747775, 'ffff': 32.543832},
    'G#3': {'pppp': 23.850379, 'ppp': 22.368596, 'pp': 20.645149, 'p': 17.684375, 'mp': 16.322112, 'mf': 15.953123, 'f': 16.886005, 'ff': 19.51067, 'fff': 21.484064, 'ffff': 23.205549},
    'A3': {'pppp': 18.446212, 'ppp': 18.549506, 'pp': 18.679437, 'p': 19.07632, 'mp': 19.224656, 'mf': 19.24594, 'f': 17.924827, 'ff': 15.416299, 'fff': 14.068882, 'ffff': 13.076247},
    'A#3': {'pppp': 18.106285, 'ppp': 18.643696, 'pp': 19.337945, 'p': 21.127903, 'mp': 21.828342, 'mf': 21.930282, 'f': 20.383883, 'ff': 17.287251, 'fff': 15.594332, 'ffff': 14.360165},
    'B3': {'pppp': 20.365066, 'ppp': 20.592187, 'pp': 20.879653, 'p': 21.318759, 'mp': 21.767387, 'mf': 22.225717, 'f': 22.694007, 'ff': 23.172496, 'fff': 23.784601, 'ffff': 24.285907},
    'C4': {'pppp': 18.667539, 'ppp': 19.263202, 'pp': 20.034581, 'p': 21.997741, 'mp': 22.813971, 'mf': 22.955593, 'f': 21.647421, 'ff': 18.898133, 'fff': 17.402317, 'ffff': 16.29137},
    'C#4': {'pppp': 17.077013, 'ppp': 18.17566, 'pp': 19.648891, 'p': 23.250917, 'mp': 24.961167, 'mf': 25.327329, 'f': 23.038368, 'ff': 18.437587, 'fff': 15.9517, 'ffff': 14.206571},
    'D4': {'pppp': 21.152964, 'ppp': 21.124382, 'pp': 21.08871, 'p': 21.098818, 'mp': 21.130124, 'mf': 21.184153, 'f': 21.863028, 'ff': 23.276722, 'fff': 24.399289, 'ffff': 25.336199},
    'D#4': {'pppp': 22.338772, 'ppp': 21.599172, 'pp': 20.709011, 'p': 20.088425, 'mp': 19.154565, 'mf': 18.071658, 'f': 16.727445, 'ff': 15.144557, 'fff': 14.065324, 'ffff': 13.257582},
    'E4': {'pppp': 21.47078, 'ppp': 20.757031, 'pp': 19.898118, 'p': 18.098168, 'mp': 17.476884, 'mf': 17.389887, 'f': 18.978553, 'ff': 23.073732, 'fff': 26.362728, 'ffff': 29.328399},
    'F4': {'pppp': 21.170763, 'ppp': 20.377234, 'pp': 19.427017, 'p': 17.448404, 'mp': 16.771377, 'mf': 16.676827, 'f': 18.125593, 'ff': 21.88931, 'fff': 24.88849, 'ffff': 27.581109},
    'F#4': {'pppp': 26.644465, 'ppp': 25.02649, 'pp': 23.141478, 'p': 19.48164, 'mp': 18.247023, 'mf': 18.058917, 'f': 20.186288, 'ff': 26.094708, 'fff': 31.095656, 'ffff': 35.778122},
    'G4': {'pppp': 16.281699, 'ppp': 16.71852, 'pp': 17.281063, 'p': 18.065774, 'mp': 18.825482, 'mf': 19.555547, 'f': 20.248286, 'ff': 20.89714, 'fff': 21.646185, 'ffff': 22.264706},
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
