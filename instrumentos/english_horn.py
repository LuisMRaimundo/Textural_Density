# instrumentos/english_horn.py
"""
English horn instrument density module.

The ``spectral_data`` table stores a committed 10-dynamic Combined Density
Metric (CDM) ladder from the Dynamics_predicter ``Results`` sheet
(IOWA + ORCH ordinary sustain anchors at pp/mf/ff; remaining levels
committed from that workbook — no runtime dynamic extrapolation).

Runtime analysis does not ingest audio; it maps notated pitch + dynamic to
these pre-loaded acoustic metadata tables.
"""

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="external_acoustic_metadata",
    citation=(
        "English horn CDM ladder: IOWA+ORCH measured pp/mf/ff anchors with "
        "committed Dynamics_predicter Results sheet values for all 10 "
        "dynamic levels (not re-extrapolated at runtime)."
    ),
    source_url_or_identifier='docs/instrument_acoustic_sources.md#english-horn',
    extraction_method=(
        "Committed full dynamic ladder from English_horn_Zenodo_collections_ordinario_Dynamics10.xlsx / sheet 'Results'; "
        "pitch lookup via MIDI-space spectral_lookup"
    ),
    dynamic_levels=('pppp', 'ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', 'ffff'),
    pitch_range=(58, 92),
    uncertainty="medium",
    version="2026-09-03",
    source_technique="ordinary_sustain",
    table_supported_techniques=("ordinary_sustain",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("english_horn")

# Full 10-dynamic CDM ladder (Results sheet). Anchors pp/mf/ff match measured
# IOWA+ORCH midpoints; other levels are workbook-committed.
spectral_data = {
    'A#3': {'pppp': 23.5337918, 'ppp': 24.3647998, 'pp': 25.4449453, 'p': 26.1906216, 'mp': 27.3566808, 'mf': 28.8402256, 'f': 30.9025476, 'ff': 33.7388268, 'fff': 36.3129173, 'ffff': 38.5128867},
    'B3': {'pppp': 24.1600252, 'ppp': 25.6239917, 'pp': 27.5793188, 'p': 31.7917875, 'mp': 34.0844194, 'mf': 34.7197228, 'f': 32.68906, 'ff': 28.1699297, 'fff': 25.8751835, 'ffff': 24.1747271},
    'C4': {'pppp': 24.9697466, 'ppp': 25.0852859, 'pp': 25.230462, 'p': 25.0738918, 'mp': 25.0164533, 'mf': 25.0082585, 'f': 27.481667, 'ff': 33.4585474, 'fff': 38.1060705, 'ffff': 42.2847566},
    'C#4': {'pppp': 21.4748021, 'ppp': 22.1895581, 'pp': 23.1165495, 'p': 23.5393509, 'mp': 24.5751035, 'mf': 25.9841444, 'f': 28.2684332, 'ff': 31.8208925, 'fff': 34.9289706, 'ffff': 37.6326266},
    'D4': {'pppp': 35.2754797, 'ppp': 35.4311931, 'pp': 35.6268018, 'p': 35.5664103, 'mp': 35.3838888, 'mf': 35.0782023, 'f': 32.7515926, 'ff': 28.6760261, 'fff': 26.6666241, 'ffff': 25.1609652},
    'D#4': {'pppp': 26.9419518, 'ppp': 26.6163964, 'pp': 26.2149786, 'p': 24.7077165, 'mp': 24.1745258, 'mf': 24.0993008, 'f': 25.7341977, 'ff': 29.7484271, 'fff': 32.7511241, 'ffff': 35.3700743},
    'E4': {'pppp': 30.9301217, 'ppp': 29.8667793, 'pp': 28.5888606, 'p': 25.4546236, 'mp': 24.2137975, 'mf': 23.9563437, 'f': 25.5215383, 'ff': 29.6393242, 'fff': 32.7072009, 'ffff': 35.3886051},
    'F4': {'pppp': 28.2631773, 'ppp': 26.7389687, 'pp': 24.9487757, 'p': 21.1999625, 'mp': 19.6910045, 'mf': 19.3516756, 'f': 20.9863622, 'ff': 25.4917368, 'fff': 28.964853, 'ffff': 32.0810704},
    'F#4': {'pppp': 19.8539269, 'ppp': 20.6399434, 'pp': 21.6663677, 'p': 22.5477148, 'mp': 23.6734757, 'mf': 25.0168239, 'f': 26.6898731, 'ff': 28.7791675, 'fff': 30.7590904, 'ffff': 32.4406611},
    'G4': {'pppp': 16.3428782, 'ppp': 16.775637, 'pp': 17.3327358, 'p': 17.6317153, 'mp': 18.1675029, 'mf': 18.8594693, 'f': 19.861833, 'ff': 21.2734125, 'fff': 22.5436111, 'ffff': 23.6141622},
    'G#4': {'pppp': 19.2647439, 'ppp': 19.5770413, 'pp': 19.9745419, 'p': 20.0466745, 'mp': 20.2270933, 'mf': 20.463963, 'f': 20.8309999, 'ff': 21.3612423, 'fff': 21.9894143, 'ffff': 22.5052264},
    'A4': {'pppp': 23.1883642, 'ppp': 23.1290812, 'pp': 23.0551906, 'p': 22.8716528, 'mp': 22.4155338, 'mf': 21.8283484, 'f': 20.9235961, 'ff': 19.6872607, 'fff': 19.1048079, 'ffff': 18.6512774},
    'A#4': {'pppp': 20.9904315, 'ppp': 19.7420554, 'pp': 18.2854695, 'p': 15.2492315, 'mp': 14.2624769, 'mf': 14.1268237, 'f': 18.0849778, 'ff': 31.017743, 'fff': 44.8960435, 'ffff': 60.3512642},
    'B4': {'pppp': 20.1724475, 'ppp': 19.7287514, 'pp': 19.1878299, 'p': 17.7077039, 'mp': 16.9543323, 'mf': 16.7341628, 'f': 17.1679858, 'ff': 18.3611399, 'fff': 19.2410999, 'ffff': 19.9753362},
    'C5': {'pppp': 18.4215296, 'ppp': 19.7753574, 'pp': 21.6084024, 'p': 25.3214491, 'mp': 27.8033948, 'mf': 28.6694273, 'f': 27.682231, 'ff': 25.0034607, 'fff': 23.7122147, 'ffff': 22.7273979},
    'C#5': {'pppp': 14.3657754, 'ppp': 15.2197676, 'pp': 16.3589984, 'p': 17.8464963, 'mp': 19.258468, 'mf': 20.5420541, 'f': 21.6786183, 'ff': 22.6428559, 'fff': 23.7725007, 'ffff': 24.716661},
    'D5': {'pppp': 9.28465217, 'ppp': 10.6367061, 'pp': 12.6069219, 'p': 16.6021452, 'mp': 20.2859819, 'mf': 21.9201046, 'f': 21.9045839, 'ff': 21.7962466, 'fff': 21.856778, 'ffff': 21.9053242},
    'D#5': {'pppp': 6.70020903, 'ppp': 7.50241603, 'pp': 8.64155966, 'p': 10.3400059, 'mp': 12.0436902, 'mf': 13.6109602, 'f': 14.9879482, 'ff': 16.1053639, 'fff': 17.4565301, 'ffff': 18.6186345},
    'E5': {'pppp': 8.28160452, 'ppp': 9.07168216, 'pp': 10.1661029, 'p': 11.5626186, 'mp': 13.0536377, 'mf': 14.6325007, 'f': 16.2794213, 'ff': 17.9733709, 'fff': 19.8043501, 'ffff': 21.4025461},
    'F5': {'pppp': 11.7248811, 'ppp': 12.1148668, 'pp': 12.6206402, 'p': 12.8695025, 'mp': 13.4288365, 'mf': 14.183131, 'f': 15.3774511, 'ff': 17.2007437, 'fff': 18.8007811, 'ffff': 20.1873273},
    'F#5': {'pppp': 14.7887536, 'ppp': 14.0241769, 'pp': 13.1238013, 'p': 11.3355975, 'mp': 10.445473, 'mf': 10.1834101, 'f': 10.6172584, 'ff': 11.8834788, 'fff': 12.7883244, 'ffff': 13.5615611},
    'G5': {'pppp': 10.3144212, 'ppp': 10.5085714, 'pp': 10.7564064, 'p': 10.8274103, 'mp': 11.0252615, 'mf': 11.329175, 'f': 12.20143, 'ff': 13.8252631, 'fff': 15.1368527, 'ffff': 16.2751623},
    'G#5': {'pppp': 7.58455588, 'ppp': 8.06797089, 'pp': 8.71579549, 'p': 9.53851389, 'mp': 10.3490741, 'mf': 11.130523, 'f': 11.868407, 'ff': 12.5474864, 'fff': 13.300844, 'ffff': 13.9359691},
    'A5': {'pppp': 11.6189761, 'ppp': 12.108614, 'pp': 12.749779, 'p': 13.2360706, 'mp': 13.9628216, 'mf': 14.8842623, 'f': 16.1489504, 'ff': 17.8785479, 'fff': 19.4690505, 'ffff': 20.8427391},
    'A#5': {'pppp': 12.269879, 'ppp': 12.7272801, 'pp': 13.3230835, 'p': 13.5990907, 'mp': 14.2901862, 'mf': 15.2388169, 'f': 16.7999037, 'ff': 19.2736243, 'fff': 21.464865, 'ffff': 23.3959119},
    'B5': {'pppp': 9.50743247, 'ppp': 10.3727457, 'pp': 11.5659639, 'p': 14.1567846, 'mp': 15.8215689, 'mf': 16.3687612, 'f': 15.4006935, 'ff': 13.0943057, 'fff': 11.914715, 'ffff': 11.0480239},
    'C6': {'pppp': 9.42780906, 'ppp': 10.221514, 'pp': 11.30826, 'p': 13.4454343, 'mp': 15.0478467, 'mf': 15.6647446, 'f': 15.402846, 'ff': 14.3839241, 'fff': 13.9518559, 'ffff': 13.6155648},
    'C#6': {'pppp': 8.001558, 'ppp': 9.13147685, 'pp': 10.7708283, 'p': 14.2224049, 'mp': 17.1425424, 'mf': 18.3542191, 'f': 18.0809932, 'ff': 16.5940249, 'fff': 15.9347976, 'ffff': 15.4263223},
    'D6': {'pppp': 7.01710952, 'ppp': 7.81136945, 'pp': 8.9317865, 'p': 11.2819142, 'mp': 13.067701, 'mf': 13.7519783, 'f': 13.3068816, 'ff': 11.8898427, 'fff': 11.1993964, 'ffff': 10.676021},
    'D#6': {'pppp': 6.2964564, 'ppp': 7.10616487, 'pp': 8.26626126, 'p': 10.7215282, 'mp': 12.6783959, 'mf': 13.4542814, 'f': 13.0773858, 'ff': 11.7272186, 'fff': 11.0788387, 'ffff': 10.586042},
    'E6': {'pppp': 6.3194571, 'ppp': 7.03500586, 'pp': 8.04443099, 'p': 10.1350213, 'mp': 11.7619694, 'mf': 12.3988864, 'f': 12.0888321, 'ff': 10.9716299, 'fff': 10.4455528, 'ffff': 10.0429119},
    'F6': {'pppp': 7.19509456, 'ppp': 7.74293679, 'pp': 8.48676592, 'p': 10.0279222, 'mp': 11.0296405, 'mf': 11.3683941, 'f': 10.8860684, 'ff': 9.65484736, 'fff': 9.04332125, 'ffff': 8.58210841},
    'F#6': {'pppp': 7.26325892, 'ppp': 8.08970214, 'pp': 9.25622254, 'p': 11.6973047, 'mp': 13.5651265, 'mf': 14.2851254, 'f': 13.8471827, 'ff': 12.4150284, 'fff': 11.7217249, 'ffff': 11.1950638},
    'G6': {'pppp': 5.24305668, 'ppp': 6.01567427, 'pp': 7.1434665, 'p': 9.52474654, 'mp': 11.5772045, 'mf': 12.4399471, 'f': 12.295054, 'ff': 11.3358527, 'fff': 10.9225831, 'ffff': 10.602842},
    'G#6': {'pppp': 4.60418321, 'ppp': 5.24875358, 'pp': 6.18280668, 'p': 8.27728756, 'mp': 9.85015181, 'mf': 10.4348571, 'f': 9.8219346, 'ff': 8.20886147, 'fff': 7.38834175, 'ffff': 6.79138287},
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
