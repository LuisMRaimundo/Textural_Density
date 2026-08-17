# instrumentos/violin_sordina.py
"""
Violin (arco con sordina) instrument density module.

The ``spectral_data`` table stores a committed 10-dynamic Combined Density
Metric (CDM) ladder from the ``Results`` sheet of
``OK_VIOLIN_con sordina_dynamics extrapolation.xlsx``
(measured pp/mf/ff anchors; remaining levels committed from that workbook —
no runtime dynamic extrapolation).

Runtime analysis does not ingest audio; it maps notated pitch + dynamic to
these pre-loaded acoustic metadata tables.
"""

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="external_acoustic_metadata",
    citation=(
        "Violin arco_sordina CDM ladder: measured pp/mf/ff anchors with "
        "committed Results sheet values for all 10 dynamic levels from "
        "OK_VIOLIN_con sordina_dynamics extrapolation.xlsx "
        "(CDM Technique Extrapolator METApool, IOWA+ORCHIDEA collections)."
    ),
    source_url_or_identifier='docs/instrument_acoustic_sources.md#violin-sordina',
    extraction_method=(
        "Committed full dynamic ladder from Dynamics extrapolator v1.5.2.1 Results sheet "
        "(PCHIP interiors, tapered outers r=0.80) on measured pp/mf/ff anchors; "
        "interior cells clamped into their measured segment where the workbook "
        "marginally overshoots; pitch lookup via MIDI-space spectral_lookup"
    ),
    dynamic_levels=('pppp', 'ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', 'ffff'),
    pitch_range=(55, 103),
    uncertainty="high",
    version="2026-08-11",
    source_technique="arco_sordina",
    table_supported_techniques=("arco_sordina",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("violin_sordina")

# Full 10-dynamic CDM ladder (Results sheet). Anchors pp/mf/ff match measured
# workbook midpoints; other levels are workbook-committed.
spectral_data = {
    'G3': {'pppp': 37.469864, 'ppp': 38.780734, 'pp': 40.484, 'p': 41.254805, 'mp': 43.260679, 'mf': 46.0477, 'f': 50.835744, 'ff': 58.5903, 'fff': 66.150772, 'ffff': 72.895762},
    'G#3': {'pppp': 21.749799, 'ppp': 22.632152, 'pp': 23.7856, 'p': 24.966888, 'mp': 26.287321, 'mf': 27.7482, 'f': 29.384651, 'ff': 31.2253, 'fff': 33.577515, 'ffff': 35.586239},
    'A3': {'pppp': 32.142416, 'ppp': 31.384643, 'pp': 30.4625, 'p': 27.923054, 'mp': 27.041802, 'mf': 26.9182, 'f': 31.362937, 'ff': 43.6288, 'fff': 54.682019, 'ffff': 65.509089},
    'A#3': {'pppp': 28.1826, 'ppp': 28.344728, 'pp': 28.5487, 'p': 28.47315, 'mp': 28.445367, 'mf': 28.4414, 'f': 31.552524, 'ff': 39.1594, 'fff': 45.652235, 'ffff': 51.613447},
    'B3': {'pppp': 29.564047, 'ppp': 30.202591, 'pp': 31.0202, 'p': 31.461099, 'mp': 32.164891, 'mf': 33.0471, 'f': 34.257299, 'ff': 35.8801, 'fff': 38.195225, 'ffff': 40.154426},
    'C4': {'pppp': 21.536511, 'ppp': 21.391451, 'pp': 21.2115, 'p': 20.310588, 'mp': 19.988407, 'mf': 19.9428, 'f': 21.657076, 'ff': 25.866, 'fff': 29.433269, 'ffff': 32.638177},
    'C#4': {'pppp': 18.282267, 'ppp': 17.987583, 'pp': 17.6259, 'p': 16.506638, 'mp': 16.11244, 'mf': 16.0569, 'f': 18.50806, 'ff': 25.0991, 'fff': 30.939351, 'ffff': 36.575783},
    'D4': {'pppp': 19.081304, 'ppp': 19.650273, 'pp': 20.3854, 'p': 20.671119, 'mp': 21.462565, 'mf': 22.675, 'f': 25.848122, 'ff': 32.0084, 'fff': 37.745901, 'ffff': 43.067976},
    'D#4': {'pppp': 24.817346, 'ppp': 24.25031, 'pp': 23.5597, 'p': 21.544614, 'mp': 20.846471, 'mf': 20.7486, 'f': 23.07555, 'ff': 29.1534, 'fff': 34.316792, 'ffff': 39.09855},
    'E4': {'pppp': 23.094906, 'ppp': 23.18955, 'pp': 23.3084, 'p': 22.892704, 'mp': 22.741429, 'mf': 22.7199, 'f': 23.449162, 'ff': 25.1052, 'fff': 26.92165, 'ffff': 28.46899},
    'F4': {'pppp': 18.749796, 'ppp': 18.880561, 'pp': 19.0453, 'p': 19.048311, 'mp': 19.057944, 'mf': 19.0751, 'f': 21.140762, 'ff': 26.147, 'fff': 30.425691, 'ffff': 34.347515},
    'F#4': {'pppp': 15.092459, 'ppp': 15.596419, 'pp': 16.2501, 'p': 16.542177, 'mp': 17.301132, 'mf': 18.3531, 'f': 20.155971, 'ff': 23.0595, 'fff': 25.901853, 'ffff': 28.42599},
    'G4': {'pppp': 17.84299, 'ppp': 18.433118, 'pp': 19.1983, 'p': 19.522916, 'mp': 20.391519, 'mf': 21.6554, 'f': 24.240891, 'ff': 28.7862, 'fff': 33.09512, 'ffff': 37.00221},
    'G#4': {'pppp': 12.478436, 'ppp': 13.068261, 'pp': 13.8449, 'p': 14.568507, 'mp': 15.498424, 'mf': 16.6207, 'f': 18.035379, 'ff': 19.8286, 'fff': 21.804162, 'ffff': 23.525415},
    'A4': {'pppp': 14.006478, 'ppp': 14.511347, 'pp': 15.1681, 'p': 15.444052, 'mp': 16.197915, 'mf': 17.3315, 'f': 19.957606, 'ff': 24.921, 'fff': 29.630351, 'ffff': 34.030934},
    'A#4': {'pppp': 15.885277, 'ppp': 16.239886, 'pp': 16.6943, 'p': 16.848012, 'mp': 17.278635, 'mf': 17.9465, 'f': 19.910099, 'ff': 23.719, 'fff': 27.199606, 'ffff': 30.348386},
    'B4': {'pppp': 18.379493, 'ppp': 18.921568, 'pp': 19.6217, 'p': 19.95197, 'mp': 20.725042, 'mf': 21.7667, 'f': 23.423666, 'ff': 25.9497, 'fff': 28.550371, 'ffff': 30.817349},
    'C5': {'pppp': 18.188608, 'ppp': 17.309584, 'pp': 16.2703, 'p': 13.909215, 'mp': 12.98747, 'mf': 12.7925, 'f': 13.902954, 'ff': 16.9396, 'fff': 19.450436, 'ffff': 21.724526},
    'C#5': {'pppp': 14.819628, 'ppp': 14.57723, 'pp': 14.2798, 'p': 13.2793, 'mp': 12.928634, 'mf': 12.8793, 'f': 13.997118, 'ff': 16.8155, 'fff': 19.187757, 'ffff': 21.324348},
    'D5': {'pppp': 14.050232, 'ppp': 14.449552, 'pp': 14.9647, 'p': 15.372489, 'mp': 15.890035, 'mf': 16.4995, 'f': 17.247923, 'ff': 18.1661, 'fff': 19.407388, 'ffff': 20.461214},
    'D#5': {'pppp': 15.488644, 'ppp': 15.439505, 'pp': 15.3783, 'p': 14.863977, 'mp': 14.678857, 'mf': 14.6526, 'f': 15.727573, 'ff': 18.3094, 'fff': 20.526651, 'ffff': 22.492269},
    'E5': {'pppp': 16.562068, 'ppp': 17.161929, 'pp': 17.9424, 'p': 18.263259, 'mp': 19.151888, 'mf': 20.5159, 'f': 23.99288, 'ff': 30.8839, 'fff': 37.463539, 'ffff': 43.723018},
    'F5': {'pppp': 13.026942, 'ppp': 13.488623, 'pp': 14.0888, 'p': 14.385283, 'mp': 15.09244, 'mf': 16.0573, 'f': 17.621866, 'ff': 20.0688, 'fff': 22.493643, 'ffff': 24.642826},
    'F#5': {'pppp': 12.497494, 'ppp': 12.871806, 'pp': 13.3555, 'p': 13.540074, 'mp': 14.058291, 'mf': 14.8675, 'f': 17.212134, 'ff': 21.9774, 'fff': 26.439173, 'ffff': 30.652445},
    'G5': {'pppp': 9.80888, 'ppp': 10.511717, 'pp': 11.4615, 'p': 12.536837, 'mp': 13.779677, 'mf': 15.2074, 'f': 16.868425, 'ff': 18.8128, 'fff': 20.985776, 'ffff': 22.903524},
    'G#5': {'pppp': 9.688326, 'ppp': 10.156056, 'pp': 10.7726, 'p': 11.364069, 'mp': 12.105183, 'mf': 12.9893, 'f': 14.084122, 'ff': 15.4484, 'fff': 16.965795, 'ffff': 18.28634},
    'A5': {'pppp': 9.7423, 'ppp': 10.272871, 'pp': 10.9769, 'p': 11.771587, 'mp': 12.642469, 'mf': 13.5952, 'f': 14.642174, 'ff': 15.7954, 'fff': 17.180657, 'ffff': 18.375835},
    'A#5': {'pppp': 8.134408, 'ppp': 8.641151, 'pp': 9.3192, 'p': 9.877001, 'mp': 10.743547, 'mf': 11.8841, 'f': 13.527633, 'ff': 15.9125, 'fff': 18.358613, 'ffff': 20.583585},
    'B5': {'pppp': 9.929642, 'ppp': 10.397105, 'pp': 11.0125, 'p': 11.692855, 'mp': 12.427771, 'mf': 13.2205, 'f': 14.078517, 'ff': 15.0088, 'fff': 16.184948, 'ffff': 17.191888},
    'C6': {'pppp': 8.71462, 'ppp': 9.222263, 'pp': 9.8986, 'p': 10.457859, 'mp': 11.311013, 'mf': 12.4226, 'f': 14.000546, 'ff': 16.2525, 'fff': 18.565102, 'ffff': 20.649954},
    'C#6': {'pppp': 8.600177, 'ppp': 8.738005, 'pp': 8.9134, 'p': 8.959926, 'mp': 9.098674, 'mf': 9.3304, 'f': 10.651462, 'ff': 13.6402, 'fff': 16.318029, 'ffff': 18.834118},
    'D6': {'pppp': 7.653887, 'ppp': 8.222202, 'pp': 8.9923, 'p': 10.059158, 'mp': 11.104953, 'mf': 12.0901, 'f': 12.992616, 'ff': 13.7866, 'fff': 14.86854, 'ffff': 15.794913},
    'D#6': {'pppp': 7.895263, 'ppp': 8.491619, 'pp': 9.3008, 'p': 10.02311, 'mp': 11.090242, 'mf': 12.4921, 'f': 14.483231, 'ff': 17.3511, 'fff': 20.344391, 'ffff': 23.106748},
    'E6': {'pppp': 9.047543, 'ppp': 9.377492, 'pp': 9.8069, 'p': 10.009337, 'mp': 10.522406, 'mf': 11.2277, 'f': 12.392549, 'ff': 14.2444, 'fff': 16.063161, 'ffff': 17.683999},
    'F6': {'pppp': 7.133129, 'ppp': 7.267574, 'pp': 7.4392, 'p': 7.490386, 'mp': 7.637103, 'mf': 7.8711, 'f': 8.719844, 'ff': 10.4394, 'fff': 11.987914, 'ffff': 13.390539},
    'F#6': {'pppp': 6.200931, 'ppp': 6.600311, 'pp': 7.1359, 'p': 7.957253, 'mp': 8.687827, 'mf': 9.2395, 'f': 9.635493, 'ff': 9.8768, 'fff': 10.391304, 'ffff': 10.822139},
    'G6': {'pppp': 5.740524, 'ppp': 6.142835, 'pp': 6.6856, 'p': 7.602906, 'mp': 8.390101, 'mf': 8.8735, 'f': 9.115372, 'ff': 9.2216, 'fff': 9.592511, 'ffff': 9.899952},
    'G#6': {'pppp': 5.214544, 'ppp': 5.549577, 'pp': 5.9988, 'p': 6.37099, 'mp': 6.948141, 'mf': 7.7091, 'f': 8.8072, 'ff': 10.4046, 'fff': 12.045542, 'ffff': 13.542757},
    'A6': {'pppp': 5.31118, 'ppp': 5.689003, 'pp': 6.1993, 'p': 6.733974, 'mp': 7.398561, 'mf': 8.2011, 'f': 9.201621, 'ff': 10.4623, 'fff': 11.823693, 'ffff': 13.039289},
    'A#6': {'pppp': 4.45097, 'ppp': 4.726657, 'pp': 5.0954, 'p': 5.520699, 'mp': 5.99005, 'mf': 6.5074, 'f': 7.079923, 'ff': 7.7149, 'fff': 8.457483, 'ffff': 9.102691},
    'B6': {'pppp': 4.539116, 'ppp': 4.793533, 'pp': 5.1317, 'p': 5.426076, 'mp': 5.848099, 'mf': 6.3855, 'f': 7.119558, 'ff': 8.1284, 'fff': 9.178088, 'ffff': 10.114629},
    'C7': {'pppp': 3.380387, 'ppp': 3.780198, 'pp': 4.3471, 'p': 5.518909, 'mp': 6.528275, 'mf': 6.9562, 'f': 6.921397, 'ff': 6.6826, 'fff': 6.694223, 'ffff': 6.703536},
    'C#7': {'pppp': 4.315621, 'ppp': 4.539938, 'pp': 4.8368, 'p': 5.015456, 'mp': 5.391568, 'mf': 5.911, 'f': 6.750459, 'ff': 8.0908, 'fff': 9.421735, 'ffff': 10.642469},
    'D7': {'pppp': 5.305663, 'ppp': 5.287954, 'pp': 5.2659, 'p': 5.12777, 'mp': 5.077799, 'mf': 5.0707, 'f': 5.893716, 'ff': 8.0861, 'fff': 10.046852, 'ffff': 11.95261},
    'D#7': {'pppp': 3.472136, 'ppp': 3.672918, 'pp': 3.9403, 'p': 4.06346, 'mp': 4.402016, 'mf': 4.9179, 'f': 6.065264, 'ff': 8.3563, 'fff': 10.715243, 'ffff': 13.073516},
    'E7': {'pppp': 4.393852, 'ppp': 4.463014, 'pp': 4.551, 'p': 4.572273, 'mp': 4.632433, 'mf': 4.7265, 'f': 5.034606, 'ff': 5.617, 'fff': 6.177857, 'ffff': 6.666602},
    'F7': {'pppp': 3.67822, 'ppp': 3.857526, 'pp': 4.094, 'p': 4.25888, 'mp': 4.550557, 'mf': 4.94, 'f': 5.525734, 'ff': 6.4006, 'fff': 7.281086, 'ffff': 8.071915},
    'F#7': {'pppp': 6.578185, 'ppp': 6.319686, 'pp': 6.0108, 'p': 5.284021, 'mp': 4.963059, 'mf': 4.8821, 'f': 5.161172, 'ff': 5.9177, 'fff': 6.548003, 'ffff': 7.100249},
    'G7': {'pppp': 3.142439, 'ppp': 3.294913, 'pp': 3.588697, 'p': 3.835305, 'mp': 4.496646, 'mf': 4.496646, 'f': 4.894345, 'ff': 5.475548, 'fff': 5.888729, 'ffff': 6.245549},
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
