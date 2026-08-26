# instrumentos/viola_harmonics.py
"""
Viola (arco harmonics) instrument density module.

The ``spectral_data`` table stores a committed 10-dynamic Combined Density
Metric (CDM) ladder from the ``Results`` sheet of
``Viola_harmonics_dynamics.xlsx``
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
        "Viola_harmonics_dynamics.xlsx "
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
    pitch_range=(72, 107),
    uncertainty="high",
    version="2026-08-26",
    source_technique="arco_harmonic",
    table_supported_techniques=("arco_harmonic",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("viola_harmonics")

# Full 10-dynamic CDM ladder (Results sheet). Anchors pp/mf/ff match measured
# workbook midpoints; other levels are workbook-committed.
spectral_data = {
    'C5': {'pppp': 16.386839, 'ppp': 16.916217, 'pp': 17.602052, 'p': 18.955247, 'mp': 19.755997, 'mf': 20.01178, 'f': 19.595069, 'ff': 18.511896, 'fff': 17.915777, 'ffff': 17.452733},
    'C#5': {'pppp': 16.778318, 'ppp': 16.940795, 'pp': 17.146104, 'p': 17.386274, 'mp': 17.594376, 'mf': 17.76529, 'f': 17.902958, 'ff': 18.008396, 'fff': 18.194592, 'ffff': 18.344935},
    'D5': {'pppp': 17.182859, 'ppp': 17.330198, 'pp': 17.516151, 'p': 17.588501, 'mp': 17.783015, 'mf': 18.066644, 'f': 18.709704, 'ff': 19.78664, 'fff': 20.639768, 'ffff': 21.348679},
    'D#5': {'pppp': 20.45871, 'ppp': 19.678062, 'pp': 18.744006, 'p': 16.99642, 'mp': 16.172765, 'mf': 15.950859, 'f': 16.568325, 'ff': 18.22737, 'fff': 19.41832, 'ffff': 20.426867},
    'E5': {'pppp': 18.344187, 'ppp': 17.595294, 'pp': 16.702023, 'p': 15.064411, 'mp': 14.277949, 'mf': 14.060338, 'f': 14.597873, 'ff': 16.062002, 'fff': 17.110568, 'ffff': 17.998496},
    'F5': {'pppp': 15.814348, 'ppp': 15.715778, 'pp': 15.593429, 'p': 15.235763, 'mp': 15.060248, 'mf': 15.012815, 'f': 15.154475, 'ff': 15.513235, 'fff': 15.788284, 'ffff': 16.011829},
    'F#5': {'pppp': 10.667901, 'ppp': 11.177722, 'pp': 11.849396, 'p': 13.126563, 'mp': 13.989635, 'mf': 14.299556, 'f': 14.074404, 'ff': 13.358042, 'fff': 12.974039, 'ffff': 12.6748},
    'G5': {'pppp': 13.112939, 'ppp': 13.553223, 'pp': 14.124423, 'p': 15.33537, 'mp': 15.952377, 'mf': 16.115058, 'f': 15.535834, 'ff': 14.205096, 'fff': 13.435109, 'ffff': 12.849281},
    'G#5': {'pppp': 13.521836, 'ppp': 13.845938, 'pp': 14.262011, 'p': 15.008171, 'mp': 15.527723, 'mf': 15.72123, 'f': 15.670815, 'ff': 15.41187, 'fff': 15.332058, 'ffff': 15.268507},
    'A5': {'pppp': 12.996457, 'ppp': 13.291962, 'pp': 13.670809, 'p': 14.498085, 'mp': 14.871279, 'mf': 14.953159, 'f': 14.485707, 'ff': 13.43688, 'fff': 12.839105, 'ffff': 12.380089},
    'A#5': {'pppp': 15.595484, 'ppp': 15.603303, 'pp': 15.613083, 'p': 15.531513, 'mp': 15.4635, 'mf': 15.410853, 'f': 15.37086, 'ff': 15.342519, 'fff': 15.418947, 'ffff': 15.480363},
    'B5': {'pppp': 16.422959, 'ppp': 16.122405, 'pp': 15.754436, 'p': 15.02288, 'mp': 14.582907, 'mf': 14.433901, 'f': 14.536418, 'ff': 14.884717, 'fff': 15.131251, 'ffff': 15.331415},
    'C6': {'pppp': 14.170434, 'ppp': 14.325753, 'pp': 14.522298, 'p': 14.86207, 'mp': 15.068461, 'mf': 15.137504, 'f': 15.065051, 'ff': 14.85234, 'fff': 14.808103, 'ffff': 14.772808},
    'C#6': {'pppp': 12.950997, 'ppp': 13.147182, 'pp': 13.396598, 'p': 13.960968, 'mp': 14.174834, 'mf': 14.205653, 'f': 13.693192, 'ff': 12.611082, 'fff': 11.992133, 'ffff': 11.518918},
    'D6': {'pppp': 14.612926, 'ppp': 14.372288, 'pp': 14.077055, 'p': 13.484178, 'mp': 13.110699, 'mf': 12.979584, 'f': 13.031433, 'ff': 13.249625, 'fff': 13.412821, 'ffff': 13.544823},
    'D#6': {'pppp': 13.188722, 'ppp': 13.271258, 'pp': 13.375155, 'p': 13.509048, 'mp': 13.589752, 'mf': 13.616676, 'f': 13.589017, 'ff': 13.506935, 'fff': 13.548527, 'ffff': 13.581893},
    'E6': {'pppp': 12.962432, 'ppp': 13.069303, 'pp': 13.204131, 'p': 13.257471, 'mp': 13.39817, 'mf': 13.597608, 'f': 13.999522, 'ff': 14.645213, 'fff': 15.164479, 'ffff': 15.593117},
    'F6': {'pppp': 10.159422, 'ppp': 10.03356, 'pp': 9.878423, 'p': 9.483844, 'mp': 9.34248, 'mf': 9.322458, 'f': 9.646409, 'ff': 10.417356, 'fff': 10.970183, 'ffff': 11.433494},
    'F#6': {'pppp': 11.093869, 'ppp': 10.826302, 'pp': 10.500899, 'p': 9.775791, 'mp': 9.521456, 'mf': 9.485667, 'f': 10.154772, 'ff': 11.82173, 'fff': 13.114247, 'ffff': 14.249289},
    'G6': {'pppp': 10.47928, 'ppp': 10.244616, 'pp': 9.958662, 'p': 9.305966, 'mp': 9.076435, 'mf': 9.044111, 'f': 9.516181, 'ff': 10.681859, 'fff': 11.549459, 'ffff': 12.294009},
    'G#6': {'pppp': 9.09059, 'ppp': 9.051916, 'pp': 9.003805, 'p': 8.836786, 'mp': 8.776037, 'mf': 8.767392, 'f': 8.959004, 'ff': 9.39606, 'fff': 9.708058, 'ffff': 9.965099},
    'A6': {'pppp': 9.484321, 'ppp': 9.497834, 'pp': 9.514754, 'p': 9.482449, 'mp': 9.470575, 'mf': 9.46888, 'f': 9.579446, 'ff': 9.818093, 'fff': 10.008085, 'ffff': 10.162723},
    'A#6': {'pppp': 9.218786, 'ppp': 9.142426, 'pp': 9.047864, 'p': 8.864531, 'mp': 8.718924, 'mf': 8.617214, 'f': 8.547748, 'ff': 8.506172, 'fff': 8.500873, 'ffff': 8.496637},
    'B6': {'pppp': 7.676613, 'ppp': 7.804673, 'pp': 7.967757, 'p': 8.204126, 'mp': 8.395259, 'mf': 8.521102, 'f': 8.600221, 'ff': 8.638991, 'fff': 8.722959, 'ffff': 8.79072},
    'C7': {'pppp': 8.142618, 'ppp': 7.88441, 'pp': 7.573134, 'p': 6.923527, 'mp': 6.672946, 'mf': 6.625384, 'f': 6.981839, 'ff': 7.892115, 'fff': 8.571978, 'ffff': 9.157801},
    'C#7': {'pppp': 6.639617, 'ppp': 6.615146, 'pp': 6.584684, 'p': 6.496293, 'mp': 6.464028, 'mf': 6.459432, 'f': 6.916869, 'ff': 7.988793, 'fff': 8.815575, 'ffff': 9.538196},
    'D7': {'pppp': 5.856944, 'ppp': 5.929121, 'pp': 6.020594, 'p': 6.056519, 'mp': 6.156243, 'mf': 6.30855, 'f': 6.735014, 'ff': 7.516147, 'fff': 8.153109, 'ffff': 8.701329},
    'D#7': {'pppp': 4.810851, 'ppp': 5.095868, 'pp': 5.476, 'p': 6.109166, 'mp': 6.632454, 'mf': 6.911427, 'f': 7.00575, 'ff': 7.044333, 'fff': 7.119875, 'ffff': 7.180892},
    'E7': {'pppp': 4.349725, 'ppp': 4.608555, 'pp': 4.953857, 'p': 5.476294, 'mp': 5.929178, 'mf': 6.248877, 'f': 6.461764, 'ff': 6.574507, 'fff': 6.742131, 'ffff': 6.879302},
    'F7': {'pppp': 3.972789, 'ppp': 4.181022, 'pp': 4.456729, 'p': 4.792942, 'mp': 5.129463, 'mf': 5.463723, 'f': 5.791229, 'ff': 6.107862, 'fff': 6.442186, 'ffff': 6.722774},
    'F#7': {'pppp': 3.437553, 'ppp': 3.671623, 'pp': 3.98675, 'p': 4.433522, 'mp': 4.84326, 'mf': 5.181999, 'f': 5.451193, 'ff': 5.645608, 'fff': 5.884656, 'ffff': 6.083161},
    'G7': {'pppp': 2.966261, 'ppp': 3.211031, 'pp': 3.545591, 'p': 4.064624, 'mp': 4.527556, 'mf': 4.857229, 'f': 5.07624, 'ff': 5.188956, 'fff': 5.359699, 'ffff': 5.500329},
    'G#7': {'pppp': 2.534706, 'ppp': 2.785615, 'pp': 3.134463, 'p': 3.726228, 'mp': 4.247953, 'mf': 4.554813, 'f': 4.684098, 'ff': 4.739087, 'fff': 4.834795, 'ffff': 4.912751},
    'A7': {'pppp': 2.252604, 'ppp': 2.463106, 'pp': 2.754108, 'p': 3.178519, 'mp': 3.579173, 'mf': 3.915279, 'f': 4.184163, 'ff': 4.377107, 'fff': 4.619857, 'ffff': 4.823715},
    'A#7': {'pppp': 1.883901, 'ppp': 2.099807, 'pp': 2.404811, 'p': 2.882384, 'mp': 3.332138, 'mf': 3.679856, 'f': 3.930548, 'ff': 4.078479, 'fff': 4.287784, 'ffff': 4.462936},
    'B7': {'pppp': 1.590063, 'ppp': 1.819082, 'pp': 2.152284, 'p': 2.749172, 'mp': 3.30757, 'mf': 3.64271, 'f': 3.777974, 'ff': 3.8353, 'fff': 3.934833, 'ffff': 4.016315},
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
