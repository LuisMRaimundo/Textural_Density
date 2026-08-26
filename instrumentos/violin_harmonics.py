# instrumentos/violin_harmonics.py
"""
Violin (arco harmonics) instrument density module.

The ``spectral_data`` table stores a committed 10-dynamic Combined Density
Metric (CDM) ladder from the ``Results`` sheet of
``Violin_harmonics_dynamics.xlsx``
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
        "Violin_harmonics_dynamics.xlsx "
        "(dest Zenodo Violin_harmonics Media (IOWA+Orchidea average); Dynamics_predicter Results ladder)."
    ),
    source_url_or_identifier='docs/instrument_acoustic_sources.md#violin-harmonics',
    extraction_method=(
        "Committed full dynamic ladder from Dynamics extrapolator v1.5.2.1 Results sheet "
        "(PCHIP interiors, tapered outers r=0.80) on measured pp/mf/ff anchors; "
        "interior cells clamped into their measured segment where the workbook "
        "marginally overshoots; pitch lookup via MIDI-space spectral_lookup"
    ),
    dynamic_levels=('pppp', 'ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', 'ffff'),
    pitch_range=(72, 107),
    uncertainty="high",
    version="2026-08-26",
    source_technique="arco_harmonic",
    table_supported_techniques=("arco_harmonic",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("violin_harmonics")

# Full 10-dynamic CDM ladder (Results sheet). Anchors pp/mf/ff match measured
# workbook midpoints; other levels are workbook-committed.
spectral_data = {
    'C5': {'pppp': 10.758577, 'ppp': 10.950532, 'pp': 11.1953, 'p': 11.604963, 'mp': 11.905878, 'mf': 12.022602, 'f': 12.016341, 'ff': 11.9726, 'fff': 11.943431, 'ffff': 11.920146},
    'C#5': {'pppp': 17.499214, 'ppp': 16.916258, 'pp': 16.214797, 'p': 15.124852, 'mp': 14.435369, 'mf': 14.191482, 'f': 14.247451, 'ff': 14.562111, 'fff': 14.738588, 'ffff': 14.881308},
    'D5': {'pppp': 19.638521, 'ppp': 19.887681, 'pp': 20.203582, 'p': 20.77121, 'mp': 21.131591, 'mf': 21.256815, 'f': 21.164144, 'ff': 20.863933, 'fff': 20.675273, 'ffff': 20.525574},
    'D#5': {'pppp': 20.446361, 'ppp': 20.495881, 'pp': 20.557951, 'p': 20.608133, 'mp': 20.670714, 'mf': 20.742369, 'f': 20.82765, 'ff': 20.928312, 'fff': 20.97693, 'ffff': 21.015906},
    'E5': {'pppp': 19.634576, 'ppp': 19.745138, 'pp': 19.884216, 'p': 20.194303, 'mp': 20.30976, 'mf': 20.326308, 'f': 19.947521, 'ff': 19.139998, 'fff': 18.606203, 'ffff': 18.189905},
    'F5': {'pppp': 18.935617, 'ppp': 18.958107, 'pp': 18.986256, 'p': 18.998965, 'mp': 19.013599, 'mf': 19.029721, 'f': 19.047905, 'ff': 19.068359, 'fff': 19.045668, 'ffff': 19.027534},
    'F#5': {'pppp': 15.832033, 'ppp': 16.08172, 'pp': 16.399374, 'p': 16.94052, 'mp': 17.32392, 'mf': 17.468987, 'f': 17.450862, 'ff': 17.324514, 'fff': 17.249338, 'ffff': 17.189432},
    'G5': {'pppp': 17.760552, 'ppp': 17.80935, 'pp': 17.870536, 'p': 17.894282, 'mp': 17.959397, 'mf': 18.056815, 'f': 18.313523, 'ff': 18.749847, 'fff': 19.05214, 'ffff': 19.297479},
    'G#5': {'pppp': 18.959271, 'ppp': 18.85221, 'pp': 18.719233, 'p': 18.668059, 'mp': 18.523074, 'mf': 18.297876, 'f': 17.508993, 'ff': 16.191304, 'fff': 15.270155, 'ffff': 14.571113},
    'A5': {'pppp': 19.838406, 'ppp': 18.172621, 'pp': 16.285686, 'p': 13.155455, 'mp': 11.94445, 'mf': 11.677015, 'f': 12.992689, 'ff': 16.781011, 'fff': 20.075283, 'ffff': 23.170559},
    'A#5': {'pppp': 13.331905, 'ppp': 13.144653, 'pp': 12.914282, 'p': 12.823335, 'mp': 12.578559, 'mf': 12.224088, 'f': 11.363362, 'ff': 10.066483, 'fff': 9.159148, 'ffff': 8.492527},
    'B5': {'pppp': 13.416358, 'ppp': 13.616357, 'pp': 13.870553, 'p': 14.360687, 'mp': 14.628342, 'mf': 14.708101, 'f': 14.536079, 'ff': 14.100161, 'fff': 13.81863, 'ffff': 13.597458},
    'C6': {'pppp': 15.818622, 'ppp': 15.42212, 'pp': 14.940438, 'p': 13.985316, 'mp': 13.609479, 'mf': 13.537217, 'f': 14.067561, 'ff': 15.391277, 'fff': 16.374714, 'ffff': 17.206517},
    'C#6': {'pppp': 15.482986, 'ppp': 14.677054, 'pp': 13.728373, 'p': 12.064233, 'mp': 11.35857, 'mf': 11.19102, 'f': 11.894335, 'ff': 13.785415, 'fff': 15.269346, 'ffff': 16.570703},
    'D6': {'pppp': 10.71582, 'ppp': 11.091313, 'pp': 11.579235, 'p': 12.431168, 'mp': 13.024418, 'mf': 13.244531, 'f': 13.165098, 'ff': 12.823686, 'fff': 12.623404, 'ffff': 12.465433},
    'D#6': {'pppp': 11.751571, 'ppp': 12.067244, 'pp': 12.473786, 'p': 13.204276, 'mp': 13.674978, 'mf': 13.839269, 'f': 13.707159, 'ff': 13.294391, 'fff': 13.03847, 'ffff': 12.837285},
    'E6': {'pppp': 12.770968, 'ppp': 12.822157, 'pp': 12.886433, 'p': 13.026239, 'mp': 13.078127, 'mf': 13.085557, 'f': 12.685177, 'ff': 11.873645, 'fff': 11.338391, 'ffff': 10.927614},
    'F6': {'pppp': 10.102587, 'ppp': 10.093639, 'pp': 10.082464, 'p': 10.038251, 'mp': 10.018187, 'mf': 10.013438, 'f': 10.035219, 'ff': 10.087713, 'fff': 10.102949, 'ffff': 10.115154},
    'F#6': {'pppp': 10.871276, 'ppp': 10.676354, 'pp': 10.437609, 'p': 10.114986, 'mp': 9.864184, 'mf': 9.696624, 'f': 9.587339, 'ff': 9.527046, 'fff': 9.444906, 'ffff': 9.379703},
    'G6': {'pppp': 8.802272, 'ppp': 8.707644, 'pp': 8.590789, 'p': 8.331405, 'mp': 8.23783, 'mf': 8.224548, 'f': 8.408838, 'ff': 8.844328, 'fff': 9.149152, 'ffff': 9.400558},
    'G#6': {'pppp': 9.051113, 'ppp': 9.133706, 'pp': 9.238008, 'p': 9.468988, 'mp': 9.555534, 'mf': 9.567962, 'f': 9.159201, 'ff': 8.335124, 'fff': 7.799318, 'ffff': 7.39558},
    'A6': {'pppp': 11.561839, 'ppp': 10.125825, 'pp': 8.578962, 'p': 6.311483, 'mp': 5.415907, 'mf': 5.195356, 'f': 5.885462, 'ff': 8.028196, 'fff': 9.961301, 'ffff': 11.837896},
    'A#6': {'pppp': 6.42211, 'ppp': 6.704882, 'pp': 7.075919, 'p': 7.762759, 'mp': 8.204031, 'mf': 8.355876, 'f': 8.197538, 'ff': 7.744994, 'fff': 7.463532, 'ffff': 7.245744},
    'B6': {'pppp': 7.460491, 'ppp': 7.730593, 'pp': 8.082013, 'p': 8.811203, 'mp': 9.174208, 'mf': 9.266274, 'f': 8.897752, 'ff': 8.064621, 'fff': 7.536146, 'ffff': 7.138412},
    'C7': {'pppp': 5.601053, 'ppp': 6.088566, 'pp': 6.758055, 'p': 8.154335, 'mp': 9.011692, 'mf': 9.281229, 'f': 8.710821, 'ff': 7.391213, 'fff': 6.605737, 'ffff': 6.037898},
    'C#7': {'pppp': 7.805342, 'ppp': 7.790108, 'pp': 7.771108, 'p': 7.763309, 'mp': 7.740414, 'mf': 7.703236, 'f': 7.518294, 'ff': 7.186211, 'fff': 6.956271, 'ffff': 6.777628},
    'D7': {'pppp': 8.438548, 'ppp': 8.279262, 'pp': 8.084376, 'p': 7.758986, 'mp': 7.55524, 'mf': 7.484072, 'f': 7.515774, 'ff': 7.642286, 'fff': 7.714061, 'ffff': 7.771967},
    'D#7': {'pppp': 6.80927, 'ppp': 6.734487, 'pp': 6.642162, 'p': 6.444125, 'mp': 6.372661, 'mf': 6.362517, 'f': 6.768713, 'ff': 7.731146, 'fff': 8.495315, 'ffff': 9.160686},
    'E7': {'pppp': 5.495366, 'ppp': 5.797726, 'pp': 6.199177, 'p': 7.146693, 'mp': 7.538569, 'mf': 7.599957, 'f': 6.921913, 'ff': 5.582897, 'fff': 4.7955, 'ffff': 4.246325},
    'F7': {'pppp': 6.050409, 'ppp': 6.037542, 'pp': 6.021496, 'p': 5.983121, 'mp': 5.969045, 'mf': 5.967037, 'f': 6.168169, 'ff': 6.613989, 'fff': 6.93962, 'ffff': 7.21163},
    'F#7': {'pppp': 5.219249, 'ppp': 5.459975, 'pp': 5.776555, 'p': 6.350605, 'mp': 6.736779, 'mf': 6.875206, 'f': 6.776224, 'ff': 6.4588, 'fff': 6.264887, 'ffff': 6.113957},
    'G7': {'pppp': 4.989538, 'ppp': 5.24263, 'pp': 5.577125, 'p': 6.183327, 'mp': 6.598329, 'mf': 6.748998, 'f': 6.652295, 'ff': 6.330799, 'fff': 6.135985, 'ffff': 5.984459},
    'G#7': {'pppp': 4.295517, 'ppp': 4.7014, 'pp': 5.263103, 'p': 6.413365, 'mp': 7.165595, 'mf': 7.418148, 'f': 7.019926, 'ff': 6.043322, 'fff': 5.461906, 'ffff': 5.037314},
    'A7': {'pppp': 5.241222, 'ppp': 5.159415, 'pp': 5.05895, 'p': 4.846664, 'mp': 4.770719, 'mf': 4.759967, 'f': 5.0804, 'ff': 5.852963, 'fff': 6.470834, 'ffff': 7.011773},
    'A#7': {'pppp': 5.238139, 'ppp': 5.081216, 'pp': 4.891658, 'p': 4.506607, 'mp': 4.372517, 'mf': 4.35369, 'f': 4.732596, 'ff': 5.695879, 'fff': 6.497178, 'ffff': 7.21865},
    'B7': {'pppp': 4.675688, 'ppp': 4.710252, 'pp': 4.753817, 'p': 4.770523, 'mp': 4.817643, 'mf': 4.890979, 'f': 5.127863, 'ff': 5.565677, 'fff': 5.918654, 'ffff': 6.217086},
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
