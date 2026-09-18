# instrumentos/violin_sordina.py
"""
Violin (arco con sordino) instrument density module.

The ``spectral_data`` table stores a committed 10-dynamic Combined Density
Metric (CDM) ladder from the ``Results`` sheet of
``Violin_Zenodo_collections_con_sordino_Dynamics10.xlsx``
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
        "Violin_Zenodo_collections_con_sordino_Dynamics10.xlsx "
        "(dest Zenodo Violin_con sordino Media (IOWA+Orchidea average); Dynamics_predicter Results ladder (CORDAS_4))."
    ),
    source_url_or_identifier='docs/instrument_acoustic_sources.md#violin-sordina',
    extraction_method=(
        "Committed full dynamic ladder from Dynamics extrapolator v1.5.2.1 Results sheet "
        "(PCHIP interiors, tapered outers r=0.80) on measured pp/mf/ff anchors; "
        "interior cells clamped into their measured segment where the workbook "
        "marginally overshoots; pitch lookup via MIDI-space spectral_lookup"
    ),
    dynamic_levels=('pppp', 'ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', 'ffff'),
    pitch_range=(55, 96),
    uncertainty="high",
    version="2026-09-18",
    source_technique="arco_sordina",
    table_supported_techniques=("arco_sordina",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("violin_sordina")

# Full 10-dynamic CDM ladder (Results sheet). Anchors pp/mf/ff match measured
# workbook midpoints; other levels are workbook-committed.
spectral_data = {
    'G3': {'pppp': 32.794302, 'ppp': 33.147092, 'pp': 33.593421, 'p': 34.274374, 'mp': 34.730601, 'mf': 34.896525, 'f': 34.840453, 'ff': 34.589008, 'fff': 34.690457, 'ffff': 34.771831},
    'G#3': {'pppp': 16.318065, 'ppp': 17.141898, 'pp': 18.230423, 'p': 20.548068, 'mp': 21.816291, 'mf': 22.17598, 'f': 21.133055, 'ff': 18.740673, 'fff': 17.37201, 'ffff': 16.349406},
    'A3': {'pppp': 28.895418, 'ppp': 29.482272, 'pp': 30.232629, 'p': 30.571535, 'mp': 31.458858, 'mf': 32.704354, 'f': 35.015733, 'ff': 38.769367, 'fff': 41.964492, 'ffff': 44.709168},
    'A#3': {'pppp': 27.710116, 'ppp': 28.078572, 'pp': 28.54604, 'p': 28.717001, 'mp': 29.210373, 'mf': 30.003195, 'f': 33.091252, 'ff': 39.394191, 'fff': 44.732571, 'ffff': 49.519608},
    'B3': {'pppp': 29.161981, 'ppp': 29.291546, 'pp': 29.454313, 'p': 29.511325, 'mp': 29.532357, 'mf': 29.535363, 'f': 29.45943, 'ff': 29.294089, 'fff': 29.456851, 'ffff': 29.587712},
    'C4': {'pppp': 22.868206, 'ppp': 23.532143, 'pp': 24.389235, 'p': 25.251876, 'mp': 26.245431, 'mf': 27.361432, 'f': 28.64096, 'ff': 30.113106, 'fff': 31.51502, 'ffff': 32.683399},
    'C#4': {'pppp': 19.665412, 'ppp': 19.691578, 'pp': 19.724334, 'p': 19.653899, 'mp': 19.628012, 'mf': 19.624317, 'f': 20.104003, 'ff': 21.149092, 'fff': 21.908732, 'ffff': 22.536043},
    'D4': {'pppp': 20.278148, 'ppp': 20.282877, 'pp': 20.288789, 'p': 20.187267, 'mp': 20.149992, 'mf': 20.144673, 'f': 20.995966, 'ff': 22.897467, 'fff': 24.276016, 'ffff': 25.438378},
    'D#4': {'pppp': 21.980826, 'ppp': 21.885427, 'pp': 21.76676, 'p': 21.386366, 'mp': 21.247903, 'mf': 21.228196, 'f': 22.35581, 'ff': 24.956866, 'fff': 26.881276, 'ffff': 28.527109},
    'E4': {'pppp': 19.10428, 'ppp': 19.233772, 'pp': 19.396872, 'p': 19.449027, 'mp': 19.588765, 'mf': 19.791338, 'f': 20.244242, 'ff': 20.989567, 'fff': 21.603302, 'ffff': 22.107186},
    'F4': {'pppp': 15.683161, 'ppp': 16.381999, 'pp': 17.299499, 'p': 18.598705, 'mp': 19.745434, 'mf': 20.65312, 'f': 21.346714, 'ff': 21.825341, 'fff': 22.433508, 'ffff': 22.932221},
    'F#4': {'pppp': 17.055797, 'ppp': 17.395675, 'pp': 17.830063, 'p': 18.268352, 'mp': 18.755719, 'mf': 19.288189, 'f': 19.878565, 'ff': 20.534771, 'fff': 21.17311, 'ffff': 21.698039},
    'G4': {'pppp': 15.695531, 'ppp': 16.674384, 'pp': 17.984239, 'p': 20.04723, 'mp': 21.813821, 'mf': 22.970686, 'f': 23.654158, 'ff': 23.966451, 'fff': 24.492013, 'ffff': 24.920748},
    'G#4': {'pppp': 16.359247, 'ppp': 16.464947, 'pp': 16.598034, 'p': 16.639277, 'mp': 16.746913, 'mf': 16.896938, 'f': 17.183245, 'ff': 17.629513, 'fff': 18.028267, 'ffff': 18.353754},
    'A4': {'pppp': 17.506807, 'ppp': 17.360468, 'pp': 17.179263, 'p': 16.701525, 'mp': 16.528885, 'mf': 16.504368, 'f': 17.660992, 'ff': 20.412463, 'fff': 22.522241, 'ffff': 24.366018},
    'A#4': {'pppp': 15.77566, 'ppp': 16.421464, 'pp': 17.266021, 'p': 18.709865, 'mp': 19.854615, 'mf': 20.378872, 'f': 20.465815, 'ff': 20.499066, 'fff': 20.621742, 'ffff': 20.720412},
    'B4': {'pppp': 21.268757, 'ppp': 21.985381, 'pp': 22.915212, 'p': 23.821664, 'mp': 24.911542, 'mf': 26.170515, 'f': 27.66804, 'ff': 29.455927, 'fff': 31.148857, 'ffff': 32.572992},
    'C5': {'pppp': 15.783672, 'ppp': 16.272716, 'pp': 16.905386, 'p': 18.108712, 'mp': 18.876004, 'mf': 19.140328, 'f': 18.888195, 'ff': 18.142574, 'fff': 17.782067, 'ffff': 17.498825},
    'C#5': {'pppp': 12.049432, 'ppp': 12.735039, 'pp': 13.647164, 'p': 14.704614, 'mp': 15.826407, 'mf': 17.016664, 'f': 18.275556, 'ff': 19.60423, 'fff': 20.971718, 'ffff': 22.134075},
    'D5': {'pppp': 11.601888, 'ppp': 12.078604, 'pp': 12.702138, 'p': 13.008287, 'mp': 13.791901, 'mf': 14.880055, 'f': 16.704312, 'ff': 19.666478, 'fff': 22.443913, 'ffff': 24.945727},
    'D#5': {'pppp': 11.21949, 'ppp': 12.022547, 'pp': 13.107675, 'p': 14.905115, 'mp': 16.433796, 'mf': 17.325683, 'f': 17.715936, 'ff': 17.882626, 'fff': 18.184243, 'ffff': 18.429195},
    'E5': {'pppp': 16.779917, 'ppp': 17.512602, 'pp': 18.473609, 'p': 19.15031, 'mp': 20.322517, 'mf': 21.870954, 'f': 24.161742, 'ff': 27.519035, 'fff': 30.67804, 'ffff': 33.464407},
    'F5': {'pppp': 15.151487, 'ppp': 15.595896, 'pp': 16.169781, 'p': 16.719685, 'mp': 17.386289, 'mf': 18.157232, 'f': 19.077416, 'ff': 20.178432, 'fff': 21.211207, 'ffff': 22.075358},
    'F#5': {'pppp': 20.205607, 'ppp': 19.598609, 'pp': 18.865439, 'p': 17.273015, 'mp': 16.720839, 'mf': 16.643412, 'f': 18.414368, 'ff': 23.011546, 'fff': 26.826053, 'ffff': 30.328126},
    'G5': {'pppp': 15.775189, 'ppp': 16.130881, 'pp': 16.586794, 'p': 17.231959, 'mp': 17.771691, 'mf': 18.163001, 'f': 18.436956, 'ff': 18.602898, 'fff': 18.871331, 'ffff': 19.088863},
    'G#5': {'pppp': 12.343504, 'ppp': 12.539121, 'pp': 12.788007, 'p': 12.89279, 'mp': 13.174157, 'mf': 13.584585, 'f': 14.486881, 'ff': 16.032624, 'fff': 17.31258, 'ffff': 18.409735},
    'A5': {'pppp': 16.627379, 'ppp': 16.59796, 'pp': 16.561259, 'p': 16.454991, 'mp': 16.32499, 'mf': 16.178444, 'f': 16.007363, 'ff': 15.809592, 'fff': 15.770788, 'ffff': 15.739814},
    'A#5': {'pppp': 13.84587, 'ppp': 14.019307, 'pp': 14.239162, 'p': 14.319331, 'mp': 14.550089, 'mf': 14.919535, 'f': 16.32706, 'ff': 19.159958, 'fff': 21.525134, 'ffff': 23.625821},
    'B5': {'pppp': 18.93301, 'ppp': 18.439129, 'pp': 17.839854, 'p': 16.910807, 'mp': 16.212515, 'mf': 15.775276, 'f': 15.508544, 'ff': 15.379156, 'fff': 15.26876, 'ffff': 15.181014},
    'C6': {'pppp': 13.858157, 'ppp': 14.027721, 'pp': 14.242596, 'p': 14.407633, 'mp': 14.633445, 'mf': 14.903468, 'f': 15.245545, 'ff': 15.673708, 'fff': 16.077297, 'ffff': 16.407638},
    'C#6': {'pppp': 17.024888, 'ppp': 16.744223, 'pp': 16.399889, 'p': 15.642572, 'mp': 15.237224, 'mf': 15.114127, 'f': 15.323415, 'ff': 15.899983, 'fff': 16.310873, 'ffff': 16.647217},
    'D6': {'pppp': 14.42183, 'ppp': 14.506724, 'pp': 14.613544, 'p': 14.802648, 'mp': 14.872933, 'mf': 14.883001, 'f': 14.19352, 'ff': 12.837808, 'fff': 12.081324, 'ffff': 11.50836},
    'D#6': {'pppp': 15.284276, 'ppp': 15.244541, 'pp': 15.195017, 'p': 14.965684, 'mp': 14.804923, 'mf': 14.744233, 'f': 14.747848, 'ff': 14.773179, 'fff': 14.887835, 'ffff': 14.9802},
    'E6': {'pppp': 16.478158, 'ppp': 16.330734, 'pp': 16.148306, 'p': 15.612832, 'mp': 15.42006, 'mf': 15.392716, 'f': 15.797024, 'ff': 16.753131, 'fff': 17.436165, 'ffff': 18.002588},
    'F6': {'pppp': 12.430262, 'ppp': 12.133062, 'pp': 11.771534, 'p': 11.001374, 'mp': 10.65319, 'mf': 10.566577, 'f': 10.895954, 'ff': 11.74256, 'fff': 12.342555, 'ffff': 12.84455},
    'F#6': {'pppp': 10.837536, 'ppp': 11.009361, 'pp': 11.227979, 'p': 11.719243, 'mp': 11.905605, 'mf': 11.932468, 'f': 11.56216, 'ff': 10.761989, 'fff': 10.326661, 'ffff': 9.991113},
    'G6': {'pppp': 12.976047, 'ppp': 12.836072, 'pp': 12.663226, 'p': 12.332088, 'mp': 12.073461, 'mf': 11.899949, 'f': 11.786419, 'ff': 11.723575, 'fff': 11.714578, 'ffff': 11.707386},
    'G#6': {'pppp': 9.676586, 'ppp': 9.968783, 'pp': 10.346469, 'p': 11.115574, 'mp': 11.538254, 'mf': 11.662526, 'f': 11.363941, 'ff': 10.636575, 'fff': 10.240802, 'ffff': 9.934814},
    'A6': {'pppp': 9.878942, 'ppp': 10.003035, 'pp': 10.160347, 'p': 10.5007, 'mp': 10.628947, 'mf': 10.647396, 'f': 10.342301, 'ff': 9.689645, 'fff': 9.342702, 'ffff': 9.074113},
    'A#6': {'pppp': 9.052221, 'ppp': 8.972356, 'pp': 8.873515, 'p': 8.615663, 'mp': 8.465576, 'mf': 8.416436, 'f': 8.468283, 'ff': 8.623636, 'fff': 8.753821, 'ffff': 8.859382},
    'B6': {'pppp': 7.622359, 'ppp': 7.712588, 'pp': 7.826878, 'p': 7.871252, 'mp': 7.993264, 'mf': 8.177139, 'f': 8.658297, 'ff': 9.516802, 'fff': 10.207059, 'ffff': 10.795141},
    'C7': {'pppp': 7.871864, 'ppp': 8.164875, 'pp': 8.546523, 'p': 9.4526, 'mp': 9.817484, 'mf': 9.874407, 'f': 9.242893, 'ff': 7.938909, 'fff': 7.191664, 'ffff': 6.644836},
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
