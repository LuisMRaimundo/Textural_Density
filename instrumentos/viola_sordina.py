# instrumentos/viola_sordina.py
"""
Viola (arco con sordina) instrument density module.

The ``spectral_data`` table stores a committed 10-dynamic Combined Density
Metric (CDM) ladder from the ``Results`` sheet of
``OK_VIOLA_con sordina_dynamics extrapolation.xlsx``
(measured pp/mf/ff anchors; remaining levels committed from that workbook —
no runtime dynamic extrapolation).

Runtime analysis does not ingest audio; it maps notated pitch + dynamic to
these pre-loaded acoustic metadata tables.
"""

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="external_acoustic_metadata",
    citation=(
        "Viola arco_sordina CDM ladder: measured pp/mf/ff anchors with "
        "committed Results sheet values for all 10 dynamic levels from "
        "OK_VIOLA_con sordina_dynamics extrapolation.xlsx "
        "(CDM Technique Extrapolator METApool, IOWA+ORCHIDEA collections)."
    ),
    source_url_or_identifier='docs/instrument_acoustic_sources.md#viola-sordina',
    extraction_method=(
        "Committed full dynamic ladder from Dynamics extrapolator v1.5.2.1 Results sheet "
        "(PCHIP interiors, tapered outers r=0.80) on measured pp/mf/ff anchors; "
        "interior cells clamped into their measured segment where the workbook "
        "marginally overshoots; pitch lookup via MIDI-space spectral_lookup"
    ),
    dynamic_levels=('pppp', 'ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', 'ffff'),
    pitch_range=(48, 96),
    uncertainty="high",
    version="2026-08-11",
    source_technique="arco_sordina",
    table_supported_techniques=("arco_sordina",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("viola_sordina")

# Full 10-dynamic CDM ladder (Results sheet). Anchors pp/mf/ff match measured
# workbook midpoints; other levels are workbook-committed.
spectral_data = {
    'C3': {'pppp': 35.661328, 'ppp': 35.682019, 'pp': 35.7079, 'p': 35.273373, 'mp': 35.114621, 'mf': 35.092, 'f': 36.729811, 'ff': 40.451881, 'fff': 43.1286, 'ffff': 45.39695},
    'C#3': {'pppp': 31.693206, 'ppp': 31.748609, 'pp': 31.818, 'p': 31.534932, 'mp': 31.43128, 'mf': 31.4165, 'f': 32.852021, 'ff': 36.093497, 'fff': 38.421686, 'ffff': 40.391909},
    'D3': {'pppp': 27.685219, 'ppp': 27.765864, 'pp': 27.867, 'p': 27.710593, 'mp': 27.653191, 'mf': 27.645, 'f': 28.881152, 'ff': 31.653956, 'fff': 33.643318, 'ffff': 35.324455},
    'D#3': {'pppp': 28.982714, 'ppp': 29.100763, 'pp': 29.249, 'p': 29.18113, 'mp': 29.156165, 'mf': 29.1526, 'f': 30.427716, 'ff': 33.268307, 'fff': 35.304381, 'ffff': 37.022602},
    'E3': {'pppp': 25.907722, 'ppp': 26.041989, 'pp': 26.2108, 'p': 26.214535, 'mp': 26.226424, 'mf': 26.2475, 'f': 27.376727, 'ff': 29.852619, 'fff': 31.632804, 'ffff': 33.133087},
    'F3': {'pppp': 21.78886, 'ppp': 21.923513, 'pp': 22.093, 'p': 22.107309, 'mp': 22.151617, 'mf': 22.2281, 'f': 23.18131, 'ff': 25.196352, 'fff': 26.663383, 'ffff': 27.898272},
    'F#3': {'pppp': 22.630566, 'ppp': 22.793096, 'pp': 22.9979, 'p': 23.025374, 'mp': 23.10827, 'mf': 23.2476, 'f': 24.240181, 'ff': 26.263524, 'fff': 27.755624, 'ffff': 29.010111},
    'G3': {'pppp': 27.41416, 'ppp': 27.638584, 'pp': 27.9217, 'p': 27.971465, 'mp': 28.117989, 'mf': 28.3578, 'f': 29.561927, 'ff': 31.929248, 'fff': 33.698177, 'ffff': 35.183625},
    'G#3': {'pppp': 16.140554, 'ppp': 16.288965, 'pp': 16.4764, 'p': 16.516128, 'mp': 16.630436, 'mf': 16.8126, 'f': 17.521763, 'ff': 18.866522, 'fff': 19.885098, 'ffff': 20.739413},
    'A3': {'pppp': 15.283056, 'ppp': 15.439057, 'pp': 15.6363, 'p': 15.684483, 'mp': 15.820125, 'mf': 16.0306, 'f': 16.701505, 'ff': 17.928605, 'fff': 18.871169, 'ffff': 19.660776},
    'A#3': {'pppp': 14.164046, 'ppp': 14.322999, 'pp': 14.5242, 'p': 14.579272, 'mp': 14.731145, 'mf': 14.9606, 'f': 15.581097, 'ff': 16.675785, 'fff': 17.528874, 'ffff': 18.242661},
    'B3': {'pppp': 15.095832, 'ppp': 15.280581, 'pp': 15.5147, 'p': 15.585154, 'mp': 15.775697, 'mf': 16.056, 'f': 16.715154, 'ff': 17.836835, 'fff': 18.724085, 'ffff': 19.465558},
    'C4': {'pppp': 16.30089, 'ppp': 16.517056, 'pp': 16.7913, 'p': 16.880853, 'mp': 17.118604, 'mf': 17.4591, 'f': 18.167657, 'ff': 19.330404, 'fff': 20.264494, 'ffff': 21.044162},
    'C#4': {'pppp': 12.795836, 'ppp': 12.97863, 'pp': 13.2108, 'p': 13.292241, 'mp': 13.504693, 'mf': 13.8009, 'f': 14.353911, 'ff': 15.22893, 'fff': 15.943244, 'ffff': 16.538745},
    'D4': {'pppp': 15.383731, 'ppp': 15.619326, 'pp': 15.9189, 'p': 16.030932, 'mp': 16.318342, 'mf': 16.7084, 'f': 17.368537, 'ff': 18.375347, 'fff': 19.211106, 'ffff': 19.907},
    'D#4': {'pppp': 12.337155, 'ppp': 12.538801, 'pp': 12.7955, 'p': 12.901778, 'mp': 13.156362, 'mf': 13.4933, 'f': 14.018252, 'ff': 14.789785, 'fff': 15.441471, 'ffff': 15.983435},
    'E4': {'pppp': 11.169387, 'ppp': 11.363504, 'pp': 11.6109, 'p': 11.736734, 'mp': 11.982793, 'mf': 12.3018, 'f': 12.772371, 'ff': 13.438508, 'fff': 14.011507, 'ffff': 14.487449},
    'F4': {'pppp': 9.48532, 'ppp': 9.660009, 'pp': 9.8829, 'p': 10.015462, 'mp': 10.238186, 'mf': 10.5203, 'f': 10.915402, 'ff': 11.453837, 'fff': 11.925905, 'ffff': 12.317529},
    'F#4': {'pppp': 10.229886, 'ppp': 10.428935, 'pp': 10.6832, 'p': 10.854512, 'mp': 11.110162, 'mf': 11.4258, 'f': 11.846443, 'ff': 12.397932, 'fff': 12.891239, 'ffff': 13.29998},
    'G4': {'pppp': 10.945924, 'ppp': 11.170322, 'pp': 11.4573, 'p': 11.671564, 'mp': 11.962266, 'mf': 12.3114, 'f': 12.755003, 'ff': 13.314118, 'fff': 13.824924, 'ffff': 14.247642},
    'G#4': {'pppp': 9.89373, 'ppp': 10.106929, 'pp': 10.3799, 'p': 10.602211, 'mp': 10.881103, 'mf': 11.2063, 'f': 11.600806, 'ff': 12.078348, 'fff': 12.524512, 'ffff': 12.89328},
    'A4': {'pppp': 11.717846, 'ppp': 11.982656, 'pp': 12.3221, 'p': 12.620012, 'mp': 12.970118, 'mf': 13.3658, 'f': 13.824674, 'ff': 14.35756, 'fff': 14.867423, 'ffff': 15.28832},
    'A#4': {'pppp': 8.937054, 'ppp': 9.148432, 'pp': 9.4197, 'p': 9.673866, 'mp': 9.956538, 'mf': 10.2657, 'f': 10.608761, 'ff': 10.990468, 'fff': 11.365082, 'ffff': 11.673947},
    'B4': {'pppp': 9.522056, 'ppp': 9.757324, 'pp': 10.0596, 'p': 10.359718, 'mp': 10.67816, 'mf': 11.0147, 'f': 11.372234, 'ff': 11.75277, 'fff': 12.136572, 'ffff': 12.452617},
    'C5': {'pppp': 7.498022, 'ppp': 7.691206, 'pp': 7.9397, 'p': 8.199541, 'mp': 8.464344, 'mf': 8.7344, 'f': 9.009195, 'ff': 9.288465, 'fff': 9.578541, 'ffff': 9.817112},
    'C#5': {'pppp': 7.444659, 'ppp': 7.644387, 'pp': 7.9016, 'p': 8.183508, 'mp': 8.46091, 'mf': 8.7335, 'f': 8.999137, 'ff': 9.256273, 'fff': 9.532077, 'ffff': 9.758625},
    'D5': {'pppp': 8.147523, 'ppp': 8.374786, 'pp': 8.6678, 'p': 9.002978, 'mp': 9.322935, 'mf': 9.6255, 'f': 9.907834, 'ff': 10.167449, 'fff': 10.455862, 'ffff': 10.692473},
    'D#5': {'pppp': 6.803729, 'ppp': 7.000763, 'pp': 7.2551, 'p': 7.557656, 'mp': 7.838937, 'mf': 8.0946, 'f': 8.322944, 'ff': 8.521747, 'fff': 8.751317, 'ffff': 8.939419},
    'E5': {'pppp': 6.195574, 'ppp': 6.38164, 'pp': 6.6221, 'p': 6.918724, 'mp': 7.188159, 'mf': 7.4232, 'f': 7.623922, 'ff': 7.788643, 'fff': 7.987292, 'ffff': 8.149853},
    'F5': {'pppp': 5.365142, 'ppp': 5.532048, 'pp': 5.748, 'p': 6.023523, 'mp': 6.26875, 'mf': 6.4738, 'f': 6.641036, 'ff': 6.769716, 'fff': 6.932684, 'ffff': 7.065878},
    'F#5': {'pppp': 4.180287, 'ppp': 4.314824, 'pp': 4.4891, 'p': 4.71852, 'mp': 4.919111, 'mf': 5.0797, 'f': 5.204612, 'ff': 5.294146, 'fff': 5.414041, 'ffff': 5.511909},
    'G5': {'pppp': 5.64536, 'ppp': 5.833152, 'pp': 6.0767, 'p': 6.406906, 'mp': 6.691112, 'mf': 6.9086, 'f': 7.069561, 'ff': 7.176039, 'fff': 7.328247, 'ffff': 7.452335},
    'G#5': {'pppp': 5.644119, 'ppp': 5.837981, 'pp': 6.0897, 'p': 6.440569, 'mp': 6.738417, 'mf': 6.956, 'f': 7.108833, 'ff': 7.201042, 'fff': 7.343465, 'ffff': 7.459428},
    'A5': {'pppp': 4.415366, 'ppp': 4.571817, 'pp': 4.7752, 'p': 5.06621, 'mp': 5.310263, 'mf': 5.4802, 'f': 5.593116, 'ff': 5.654222, 'fff': 5.757949, 'ffff': 5.842299},
    'A#5': {'pppp': 5.174098, 'ppp': 5.363061, 'pp': 5.609, 'p': 5.969723, 'mp': 6.26904, 'mf': 6.4674, 'f': 6.59158, 'ff': 6.650425, 'fff': 6.76291, 'ffff': 6.854267},
    'B5': {'pppp': 4.792582, 'ppp': 4.972829, 'pp': 5.2077, 'p': 5.56041, 'mp': 5.850351, 'mf': 6.0329, 'f': 6.136271, 'ff': 6.182788, 'fff': 6.278489, 'ffff': 6.356115},
    'C6': {'pppp': 3.846537, 'ppp': 3.99544, 'pp': 4.1897, 'p': 4.48808, 'mp': 4.73136, 'mf': 4.8766, 'f': 4.949216, 'ff': 4.980951, 'fff': 5.050888, 'ffff': 5.107543},
    'C#6': {'pppp': 4.040682, 'ppp': 4.20152, 'pp': 4.4116, 'p': 4.741279, 'mp': 5.008175, 'mf': 5.159, 'f': 5.224091, 'ff': 5.251714, 'fff': 5.317921, 'ffff': 5.371487},
    'D6': {'pppp': 3.930142, 'ppp': 4.090889, 'pp': 4.3011, 'p': 4.637823, 'mp': 4.908752, 'mf': 5.0534, 'f': 5.105535, 'ff': 5.127017, 'fff': 5.184323, 'ffff': 5.230629},
    'D#6': {'pppp': 3.635649, 'ppp': 3.788377, 'pp': 3.98834, 'p': 4.315065, 'mp': 4.576555, 'mf': 4.7081, 'f': 4.745607, 'ff': 4.760606, 'fff': 4.806965, 'ffff': 4.844377},
    'E6': {'pppp': 4.277616, 'ppp': 4.462026, 'pp': 4.703757, 'p': 5.10628, 'mp': 5.426986, 'mf': 5.5787, 'f': 5.609951, 'ff': 5.622079, 'fff': 5.668799, 'ffff': 5.706455},
    'F6': {'pppp': 2.853736, 'ppp': 2.979935, 'pp': 3.14556, 'p': 3.426481, 'mp': 3.649444, 'mf': 3.7483, 'f': 3.760225, 'ff': 3.764714, 'fff': 3.790574, 'ffff': 3.811391},
    'F#6': {'pppp': 3.54535, 'ppp': 3.706065, 'pp': 3.917244, 'p': 4.281811, 'mp': 4.570247, 'mf': 4.6898, 'f': 4.6933, 'ff': 4.694578, 'fff': 4.72011, 'ffff': 4.740635},
    'G6': {'pppp': 3.012752, 'ppp': 3.152841, 'pp': 3.337148, 'p': 3.658643, 'mp': 3.91171, 'mf': 4.0141, 'f': 4.012928, 'ff': 4.004732, 'fff': 4.020494, 'ffff': 4.033149},
    'G#6': {'pppp': 2.747583, 'ppp': 2.878645, 'pp': 3.051298, 'p': 3.354595, 'mp': 3.591963, 'mf': 3.6876, 'f': 3.68497, 'ff': 3.666609, 'fff': 3.675376, 'ffff': 3.682405},
    'A6': {'pppp': 3.609295, 'ppp': 3.785805, 'pp': 4.01863, 'p': 4.430362, 'mp': 4.750875, 'mf': 4.8795, 'f': 4.873976, 'ff': 4.835483, 'fff': 4.839595, 'ffff': 4.842888},
    'A#6': {'pppp': 2.540386, 'ppp': 2.667691, 'pp': 2.83583, 'p': 3.135058, 'mp': 3.366837, 'mf': 3.4595, 'f': 3.454138, 'ff': 3.416835, 'fff': 3.414473, 'ffff': 3.412585},
    'B6': {'pppp': 2.210166, 'ppp': 2.323628, 'pp': 2.473681, 'p': 2.742355, 'mp': 2.949491, 'mf': 3.032, 'f': 3.02602, 'ff': 2.984486, 'fff': 2.97776, 'ffff': 2.972391},
    'C7': {'pppp': 2.226621, 'ppp': 2.34365, 'pp': 2.498624, 'p': 2.77772, 'mp': 2.991957, 'mf': 3.077, 'f': 3.069641, 'ff': 3.018622, 'fff': 3.007131, 'ffff': 2.997969},
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
