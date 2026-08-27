# instrumentos/cello_harmonics.py
"""
Cello (arco harmonics) instrument density module.

The ``spectral_data`` table stores a committed 10-dynamic Combined Density
Metric (CDM) ladder from the ``Results`` sheet of
``Cello_harmonics_dynamics.xlsx``
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
        "Cello_harmonics_dynamics.xlsx "
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
    pitch_range=(60, 100),
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
    'C4': {'pppp': 25.550583, 'ppp': 24.903368, 'pp': 24.117355, 'p': 22.2227, 'mp': 21.505699, 'mf': 21.377169, 'f': 22.462127, 'ff': 25.204519, 'fff': 27.027928, 'ffff': 28.581186},
    'C#4': {'pppp': 25.207444, 'ppp': 24.41115, 'pp': 23.451062, 'p': 21.382427, 'mp': 20.462433, 'mf': 20.234609, 'f': 21.096591, 'ff': 23.356724, 'fff': 24.816404, 'ffff': 26.04956},
    'D4': {'pppp': 19.544124, 'ppp': 20.220627, 'pp': 21.099278, 'p': 22.640936, 'mp': 23.735353, 'mf': 24.147574, 'f': 24.047566, 'ff': 23.513479, 'fff': 23.156268, 'ffff': 22.87441},
    'D#4': {'pppp': 18.546606, 'ppp': 18.966469, 'pp': 19.504689, 'p': 20.680252, 'mp': 21.130993, 'mf': 21.196181, 'f': 19.872908, 'ff': 17.234988, 'fff': 15.68056, 'ffff': 14.538582},
    'E4': {'pppp': 19.046397, 'ppp': 19.479818, 'pp': 20.035491, 'p': 21.044745, 'mp': 21.604894, 'mf': 21.773658, 'f': 21.420004, 'ff': 20.527826, 'fff': 19.945392, 'ffff': 19.491365},
    'F4': {'pppp': 17.640904, 'ppp': 18.250387, 'pp': 19.041936, 'p': 20.558252, 'mp': 21.466993, 'mf': 21.760822, 'f': 21.311795, 'ff': 20.131118, 'fff': 19.398864, 'ffff': 18.832286},
    'F#4': {'pppp': 18.410088, 'ppp': 18.650859, 'pp': 18.956255, 'p': 19.359595, 'mp': 19.576095, 'mf': 19.6398, 'f': 19.497235, 'ff': 19.134788, 'fff': 18.829447, 'ffff': 18.588685},
    'G4': {'pppp': 20.929972, 'ppp': 21.357287, 'pp': 21.90372, 'p': 23.069085, 'mp': 23.513887, 'mf': 23.578127, 'f': 22.40889, 'ff': 20.010692, 'fff': 18.570984, 'ffff': 17.494163},
    'G#4': {'pppp': 19.172304, 'ppp': 19.385094, 'pp': 19.654407, 'p': 19.733104, 'mp': 19.932245, 'mf': 20.196402, 'f': 20.618159, 'ff': 21.236621, 'fff': 21.528579, 'ffff': 21.765034},
    'A4': {'pppp': 20.142774, 'ppp': 20.343614, 'pp': 20.597482, 'p': 20.946849, 'mp': 21.077052, 'mf': 21.095718, 'f': 20.568584, 'ff': 19.467694, 'fff': 18.756387, 'ffff': 18.206099},
    'A#4': {'pppp': 18.811651, 'ppp': 19.179145, 'pp': 19.648624, 'p': 20.499715, 'mp': 20.930022, 'mf': 21.04566, 'f': 20.670698, 'ff': 19.773349, 'fff': 19.185822, 'ffff': 18.728395},
    'B4': {'pppp': 20.846478, 'ppp': 21.038219, 'pp': 21.280377, 'p': 21.353378, 'mp': 21.40371, 'mf': 21.422458, 'f': 21.420009, 'ff': 21.402867, 'fff': 21.215287, 'ffff': 21.066407},
    'C5': {'pppp': 16.99701, 'ppp': 17.023674, 'pp': 17.057063, 'p': 17.00476, 'mp': 16.873196, 'mf': 16.7004, 'f': 16.4235, 'ff': 16.030437, 'fff': 15.686111, 'ffff': 15.415983},
    'C#5': {'pppp': 15.77473, 'ppp': 15.687763, 'pp': 15.579728, 'p': 15.133611, 'mp': 14.849007, 'mf': 14.748388, 'f': 14.787525, 'ff': 14.953006, 'fff': 14.941682, 'ffff': 14.932629},
    'D5': {'pppp': 19.32964, 'ppp': 18.9939, 'pp': 18.582414, 'p': 17.587181, 'mp': 17.026278, 'mf': 16.846453, 'f': 17.054257, 'ff': 17.67094, 'fff': 17.94474, 'ffff': 18.166831},
    'D#5': {'pppp': 15.243431, 'ppp': 15.335195, 'pp': 15.450678, 'p': 15.402217, 'mp': 15.384402, 'mf': 15.381858, 'f': 15.517008, 'ff': 15.808746, 'fff': 15.847894, 'ffff': 15.879282},
    'E5': {'pppp': 16.3596, 'ppp': 16.644319, 'pp': 17.007197, 'p': 17.756265, 'mp': 18.040478, 'mf': 18.08145, 'f': 16.930527, 'ff': 14.676399, 'fff': 13.348195, 'ffff': 12.372714},
    'F5': {'pppp': 15.014764, 'ppp': 15.258429, 'pp': 15.568578, 'p': 16.063505, 'mp': 16.328789, 'mf': 16.406265, 'f': 16.224589, 'ff': 15.768676, 'fff': 15.440377, 'ffff': 15.182667},
    'F#5': {'pppp': 15.340521, 'ppp': 15.603123, 'pp': 15.937706, 'p': 16.59365, 'mp': 16.850538, 'mf': 16.891754, 'f': 16.457545, 'ff': 15.498371, 'fff': 14.890343, 'ffff': 14.421141},
    'G5': {'pppp': 13.465241, 'ppp': 13.924218, 'pp': 14.520002, 'p': 15.570567, 'mp': 16.305474, 'mf': 16.579185, 'f': 16.489618, 'ff': 16.084853, 'fff': 15.816377, 'ffff': 15.604825},
    'G#5': {'pppp': 15.328563, 'ppp': 15.267818, 'pp': 15.192226, 'p': 14.924166, 'mp': 14.690664, 'mf': 14.491609, 'f': 14.323939, 'ff': 14.186007, 'fff': 13.986368, 'ffff': 13.828682},
    'A5': {'pppp': 14.635127, 'ppp': 14.82229, 'pp': 15.059612, 'p': 15.43575, 'mp': 15.585311, 'mf': 15.61106, 'f': 15.372054, 'ff': 14.832474, 'fff': 14.457866, 'ffff': 14.165003},
    'A#5': {'pppp': 13.822928, 'ppp': 13.916637, 'pp': 14.034667, 'p': 14.127176, 'mp': 14.161412, 'mf': 14.16631, 'f': 13.724256, 'ff': 12.837428, 'fff': 12.278018, 'ffff': 11.848094},
    'B5': {'pppp': 11.437763, 'ppp': 11.810223, 'pp': 12.292902, 'p': 13.30449, 'mp': 13.799506, 'mf': 13.922439, 'f': 13.403031, 'ff': 12.228227, 'fff': 11.516484, 'ffff': 10.977035},
    'C6': {'pppp': 11.709459, 'ppp': 11.993821, 'pp': 12.359005, 'p': 13.104741, 'mp': 13.445806, 'mf': 13.522634, 'f': 13.110376, 'ff': 12.180932, 'fff': 11.606325, 'ffff': 11.166218},
    'C#6': {'pppp': 10.235303, 'ppp': 10.690532, 'pp': 11.288146, 'p': 12.575106, 'mp': 13.230759, 'mf': 13.400038, 'f': 12.746795, 'ff': 11.289691, 'fff': 10.426394, 'ffff': 9.783535},
    'D6': {'pppp': 9.361556, 'ppp': 9.913021, 'pp': 10.648257, 'p': 12.253929, 'mp': 13.116923, 'mf': 13.352125, 'f': 12.561109, 'ff': 10.810949, 'fff': 9.794592, 'ffff': 9.050745},
    'D#6': {'pppp': 8.669145, 'ppp': 9.241327, 'pp': 10.009951, 'p': 11.681033, 'mp': 12.620178, 'mf': 12.889808, 'f': 12.114885, 'ff': 10.378405, 'fff': 9.375199, 'ffff': 8.642918},
    'E6': {'pppp': 8.475699, 'ppp': 8.86481, 'pp': 9.376413, 'p': 10.403323, 'mp': 11.0139, 'mf': 11.207192, 'f': 10.858419, 'ff': 9.984018, 'fff': 9.457964, 'ffff': 9.057149},
    'F6': {'pppp': 7.610195, 'ppp': 8.097517, 'pp': 8.750783, 'p': 10.09547, 'mp': 10.93132, 'mf': 11.203901, 'f': 10.751221, 'ff': 9.621652, 'fff': 8.957689, 'ffff': 8.459663},
    'F#6': {'pppp': 7.444521, 'ppp': 7.744319, 'pp': 8.136101, 'p': 8.832451, 'mp': 9.338949, 'mf': 9.532881, 'f': 9.501739, 'ff': 9.286575, 'fff': 9.148472, 'ffff': 9.039469},
    'G6': {'pppp': 6.36776, 'ppp': 6.862479, 'pp': 7.535272, 'p': 8.885854, 'mp': 9.822474, 'mf': 10.160108, 'f': 9.856453, 'ff': 8.975091, 'fff': 8.462422, 'ffff': 8.073453},
    'G#6': {'pppp': 5.996072, 'ppp': 6.403127, 'pp': 6.951023, 'p': 7.975973, 'mp': 8.758032, 'mf': 9.065599, 'f': 9.017034, 'ff': 8.684289, 'fff': 8.495869, 'ffff': 8.348081},
    'A6': {'pppp': 5.058307, 'ppp': 5.610341, 'pp': 6.38586, 'p': 7.975956, 'mp': 9.177223, 'mf': 9.636672, 'f': 9.347543, 'ff': 8.411852, 'fff': 7.883054, 'ffff': 7.484053},
    'A#6': {'pppp': 4.513108, 'ppp': 5.061663, 'pp': 5.842048, 'p': 7.442878, 'mp': 8.709397, 'mf': 9.210756, 'f': 8.989157, 'ff': 8.155916, 'fff': 7.693327, 'ffff': 7.342219},
    'B6': {'pppp': 4.306408, 'ppp': 4.731192, 'pp': 5.32157, 'p': 6.386665, 'mp': 7.312669, 'mf': 7.776487, 'f': 7.876072, 'ff': 7.914972, 'fff': 7.959956, 'ffff': 7.996128},
    'C7': {'pppp': 3.820382, 'ppp': 4.238515, 'pp': 4.826112, 'p': 5.84145, 'mp': 6.755508, 'mf': 7.316064, 'f': 7.575332, 'ff': 7.68778, 'fff': 7.848415, 'ffff': 7.979337},
    'C#7': {'pppp': 3.267592, 'ppp': 3.781659, 'pp': 4.539423, 'p': 6.112372, 'mp': 7.499518, 'mf': 8.092168, 'f': 8.012092, 'ff': 7.473313, 'fff': 7.188175, 'ffff': 6.967918},
    'D7': {'pppp': 3.376575, 'ppp': 3.79401, 'pp': 4.389105, 'p': 5.462161, 'mp': 6.438044, 'mf': 6.993491, 'f': 7.189551, 'ff': 7.270711, 'fff': 7.387934, 'ffff': 7.483072},
    'D#7': {'pppp': 3.164326, 'ppp': 3.575455, 'pp': 4.165278, 'p': 5.229556, 'mp': 6.208022, 'mf': 6.780232, 'f': 6.998525, 'ff': 7.090055, 'fff': 7.22478, 'ffff': 7.334401},
    'E7': {'pppp': 2.961745, 'ppp': 3.364553, 'pp': 3.945953, 'p': 4.98956, 'mp': 5.961002, 'mf': 6.554878, 'f': 6.811861, 'ff': 6.922138, 'fff': 7.087059, 'ffff': 7.221819},
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
