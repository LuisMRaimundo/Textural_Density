# instrumentos/trumpet.py
"""
Trumpet (Bb) instrument density module.

The ``spectral_data`` table stores sparse Combined Density Metric (CDM) values
from **external acoustic sources** (IOWA + ORCH sustain collections,
midpoint summary at pp/mf/ff). Intermediate dynamics are interpolated via GPR.

Runtime analysis does not ingest audio; it maps notated pitch + dynamic to these
pre-loaded acoustic metadata tables.
"""

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="external_acoustic_metadata",
    citation=(
        "Median/midpoint summary of trumpet sustained-note Combined Density Metrics across IOWA and ORCH sound collections (pp, mf, ff)."
    ),
    source_url_or_identifier='D:\\METAIS\\Trumpet_Zenodo_collections_media.xlsx',
    extraction_method=(
        "monotone log-CDM ladder enforcement (2026-08-03): pp/mf/ff anchors isotonic-clamped then full DYNAMIC_LEVELS rebuilt via offline internal_default log-linear + adaptive tails; Combined Density Metric midpoint of IOWA/ORCH collections (CDM midpoint pass-through; no rescaling); GPR interpolation by pitch/dynamic"
    ),
    dynamic_levels=('pppp', 'ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', 'ffff'),
    pitch_range=(52, 87),
    uncertainty="medium",
    version="2026-07-11",
    source_technique="ordinary_sustain",
    table_supported_techniques=("ordinary_sustain",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("trumpet")

# CDM medians: (IOWA + ORCH) / 2 per note at pp, mf, ff (sustains (ordinario)).
spectral_data = {
    'E3': {'pppp': 29.6599008, 'ppp': 30.5587345, 'pp': 32.438944, 'p': 38.8025918, 'mp': 42.4382775, 'mf': 46.414616, 'f': 72.9470202, 'ff': 114.646381, 'fff': 143.726466, 'ffff': 160.9255291},
    'F3': {'pppp': 29.8193576, 'ppp': 30.6719083, 'pp': 32.450831, 'p': 38.4309306, 'mp': 41.8223507, 'mf': 45.513054, 'f': 69.0878632, 'ff': 104.87393, 'fff': 129.2112816, 'ffff': 143.422365},
    'F#3': {'pppp': 28.9603213, 'ppp': 29.8407878, 'pp': 31.68284, 'p': 37.9197584, 'mp': 41.4845411, 'mf': 45.384444, 'f': 65.8461798, 'ff': 95.533161, 'fff': 115.0710113, 'ffff': 126.2908311},
    'G3': {'pppp': 27.4403237, 'ppp': 28.4489922, 'pp': 30.578924, 'p': 37.9741568, 'mp': 42.3176078, 'mf': 47.157859, 'f': 68.2058135, 'ff': 98.648096, 'fff': 118.6376032, 'ffff': 130.1035638},
    'G#3': {'pppp': 20.9405493, 'ppp': 21.8193403, 'pp': 23.689108, 'p': 30.3158664, 'mp': 34.2949854, 'mf': 38.796385, 'f': 52.2426887, 'ff': 70.3493, 'fff': 81.6350965, 'ffff': 87.9398004},
    'A3': {'pppp': 19.4922703, 'ppp': 20.0698061, 'pp': 21.27672, 'p': 25.350655, 'mp': 27.6714195, 'mf': 30.204642, 'f': 45.2016137, 'ff': 67.644764, 'fff': 82.7512017, 'ffff': 91.5259765},
    'A#3': {'pppp': 17.8037309, 'ppp': 18.470036, 'pp': 19.878389, 'p': 24.7811532, 'mp': 27.6688862, 'mf': 30.893125, 'f': 45.4006898, 'ff': 66.721079, 'fff': 80.8841388, 'ffff': 89.0560684},
    'B3': {'pppp': 18.4258342, 'ppp': 19.1729306, 'pp': 20.759227, 'p': 26.3499147, 'mp': 29.6867894, 'mf': 33.446236, 'f': 41.3589602, 'ff': 51.14368, 'fff': 56.8726094, 'ffff': 59.9734104},
    'C4': {'pppp': 17.328352, 'ppp': 18.0383889, 'pp': 19.546937, 'p': 24.8726247, 'mp': 28.0571187, 'mf': 31.64933, 'f': 41.943326, 'ff': 55.585461, 'fff': 63.9897458, 'ffff': 68.6570234},
    'C#4': {'pppp': 15.6118412, 'ppp': 16.3844403, 'pp': 18.046234, 'p': 24.1130143, 'mp': 27.873016, 'mf': 32.219324, 'f': 41.6050628, 'ff': 53.72494, 'fff': 61.0507239, 'ffff': 65.0801068},
    'D4': {'pppp': 15.6303066, 'ppp': 16.2630689, 'pp': 17.606479, 'p': 22.339968, 'mp': 25.164457, 'mf': 28.346052, 'f': 36.7826594, 'ff': 47.730246, 'fff': 54.3712035, 'ffff': 58.0305361},
    'D#4': {'pppp': 15.6882796, 'ppp': 16.4134712, 'pp': 17.96597, 'p': 23.5614151, 'mp': 26.9821604, 'mf': 30.899544, 'f': 35.4271501, 'ff': 40.618171, 'fff': 43.4923062, 'ffff': 45.0047624},
    'E4': {'pppp': 13.6776123, 'ppp': 14.332431, 'pp': 15.737618, 'p': 20.8351399, 'mp': 23.9731516, 'mf': 27.583784, 'f': 32.3678964, 'ff': 37.981762, 'fff': 41.143897, 'ffff': 42.8223584},
    'F4': {'pppp': 12.9672282, 'ppp': 13.5085875, 'pp': 14.660052, 'p': 18.7375251, 'mp': 21.1836399, 'mf': 23.949086, 'f': 28.7274247, 'ff': 34.459141, 'fff': 37.7405585, 'ffff': 39.49665},
    'F#4': {'pppp': 12.7977969, 'ppp': 13.2298447, 'pp': 14.13819, 'p': 17.2548431, 'mp': 19.0620505, 'mf': 21.058538, 'f': 27.6705991, 'ff': 36.358747, 'fff': 41.6777323, 'ffff': 44.6222708},
    'G4': {'pppp': 11.148094, 'ppp': 11.7029402, 'pp': 12.896852, 'p': 17.2603623, 'mp': 19.967928, 'mf': 23.100219, 'f': 28.8884439, 'ff': 36.127025, 'fff': 40.4004521, 'ffff': 42.7231473},
    'G#4': {'pppp': 10.2984496, 'ppp': 10.8042982, 'pp': 11.891756, 'p': 15.8560232, 'mp': 18.3091598, 'mf': 21.141829, 'f': 28.795935, 'ff': 39.221104, 'fff': 45.7735008, 'ffff': 49.4494295},
    'A4': {'pppp': 10.6133095, 'ppp': 11.0235968, 'pp': 11.892367, 'p': 14.9314935, 'mp': 16.7309547, 'mf': 18.747277, 'f': 26.5550272, 'ff': 37.614501, 'fff': 44.7671639, 'ffff': 48.8384329},
    'A#4': {'pppp': 10.1801686, 'ppp': 10.6619906, 'pp': 11.695127, 'p': 15.4349378, 'mp': 17.7318828, 'mf': 20.370647, 'f': 27.7401844, 'ff': 37.775817, 'fff': 44.0824909, 'ffff': 47.6203142},
    'B4': {'pppp': 9.3547794, 'ppp': 9.8097973, 'pp': 10.787306, 'p': 14.3440533, 'mp': 16.5406029, 'mf': 19.073517, 'f': 23.6517059, 'ff': 29.328791, 'fff': 32.6595357, 'ffff': 34.4641783},
    'C5': {'pppp': 7.2578848, 'ppp': 7.5127917, 'pp': 8.049778, 'p': 9.9021972, 'mp': 10.982606, 'mf': 12.180896, 'f': 16.825821, 'ff': 23.241989, 'fff': 27.3162957, 'ffff': 29.6139311},
    'C#5': {'pppp': 6.4717795, 'ppp': 6.7542746, 'pp': 7.356796, 'p': 9.5064576, 'mp': 10.8064666, 'mf': 12.284252, 'f': 15.2668173, 'ff': 18.973537, 'fff': 21.151842, 'ffff': 22.3330553},
    'D5': {'pppp': 6.0861948, 'ppp': 6.3563253, 'pp': 6.933087, 'p': 8.9968039, 'mp': 10.2487065, 'mf': 11.674811, 'f': 15.6171888, 'ff': 20.890838, 'fff': 24.1619712, 'ffff': 25.9848738},
    'D#5': {'pppp': 6.7293947, 'ppp': 6.949266, 'pp': 7.410795, 'p': 8.9875724, 'mp': 9.8976297, 'mf': 10.899837, 'f': 13.3652353, 'ff': 16.388274, 'fff': 18.1472791, 'ffff': 19.0963634},
    'E5': {'pppp': 7.7580948, 'ppp': 7.9141837, 'pp': 8.235846, 'p': 9.2814214, 'mp': 9.8529806, 'mf': 10.459737, 'f': 13.6084924, 'ff': 17.705136, 'fff': 20.1950016, 'ffff': 21.5683144},
    'F5': {'pppp': 5.4121299, 'ppp': 5.6605078, 'pp': 6.191983, 'p': 8.1049966, 'mp': 9.2728745, 'mf': 10.609036, 'f': 13.3542036, 'ff': 16.809704, 'fff': 18.8595403, 'ffff': 19.9763721},
    'F#5': {'pppp': 5.8677729, 'ppp': 6.0949426, 'pp': 6.576007, 'p': 8.2592423, 'mp': 9.2561244, 'mf': 10.373329, 'f': 14.1543778, 'ff': 19.313608, 'fff': 22.5605523, 'ffff': 24.3833226},
    'G5': {'pppp': 5.597115, 'ppp': 5.8306747, 'pp': 6.327439, 'p': 8.0864041, 'mp': 9.1415361, 'mf': 10.334344, 'f': 13.1530572, 'ff': 16.74058, 'fff': 18.8861049, 'ffff': 20.0598807},
    'G#5': {'pppp': 6.0225646, 'ppp': 6.2408039, 'pp': 6.701294, 'p': 8.2968469, 'mp': 9.2318828, 'mf': 10.272295, 'f': 12.2869686, 'ff': 14.696774, 'fff': 16.0735072, 'ffff': 16.8095066},
    'A5': {'pppp': 5.3708533, 'ppp': 5.5960198, 'pp': 6.075068, 'p': 7.7726095, 'mp': 8.7917373, 'mf': 9.944491, 'f': 12.816999, 'ff': 16.519243, 'fff': 18.7539191, 'ffff': 19.9821855},
    'A#5': {'pppp': 6.2500743, 'ppp': 6.4393334, 'pp': 6.835218, 'p': 8.1749808, 'mp': 8.9403378, 'mf': 9.777349, 'f': 13.9808503, 'ff': 19.991531, 'fff': 23.9057454, 'ffff': 26.1414941},
    'B5': {'pppp': 5.3891118, 'ppp': 5.567239, 'pp': 5.941351, 'p': 7.2213974, 'mp': 7.9613967, 'mf': 8.777226, 'f': 11.6495099, 'ff': 15.461728, 'fff': 17.812842, 'ffff': 19.1192481},
    'C6': {'pppp': 5.2135875, 'ppp': 5.3983872, 'pp': 5.78787, 'p': 7.1331765, 'mp': 7.9189039, 'mf': 8.79118, 'f': 9.8935493, 'ff': 11.13415, 'fff': 11.811622, 'ffff': 12.1656629},
    'C#6': {'pppp': 4.9860067, 'ppp': 5.1602478, 'pp': 5.52721, 'p': 6.7922268, 'mp': 7.5294853, 'mf': 8.346769, 'f': 10.0478217, 'ff': 12.095545, 'fff': 13.2709558, 'ffff': 13.9008253},
    'D6': {'pppp': 5.9734928, 'ppp': 6.1349553, 'pp': 6.471091, 'p': 7.5940916, 'mp': 8.2266874, 'mf': 8.911979, 'f': 10.0661867, 'ff': 11.369878, 'fff': 12.0837357, 'ffff': 12.4573},
    'D#6': {'pppp': 4.6121327, 'ppp': 4.819401, 'pp': 5.2623, 'p': 6.8505149, 'mp': 7.8162244, 'mf': 8.918069, 'f': 9.5652744, 'ff': 10.259449, 'fff': 10.6252055, 'ffff': 10.8129449},
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
