# instrumentos/oboe.py
"""
Oboe instrument density module.

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
        "Oboe CDM ladder: IOWA+ORCH measured pp/mf/ff anchors with "
        "committed Dynamics_predicter Results sheet values for all 10 "
        "dynamic levels (not re-extrapolated at runtime)."
    ),
    source_url_or_identifier='docs/instrument_acoustic_sources.md#oboe',
    extraction_method=(
        "monotone log-CDM ladder enforcement (2026-08-03): pp/mf/ff anchors isotonic-clamped then full DYNAMIC_LEVELS rebuilt via offline internal_default log-linear + adaptive tails; Committed full dynamic ladder from Oboe_iowa_orchidea_dynamics.xlsx / sheet 'Results'; "
        "pitch lookup via MIDI-space spectral_lookup"
    ),
    dynamic_levels=('pppp', 'ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', 'ffff'),
    pitch_range=(58, 93),
    uncertainty="medium",
    version="2026-08-03",
    source_technique="ordinary_sustain",
    table_supported_techniques=("ordinary_sustain",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("oboe")

# Full 10-dynamic CDM ladder (Results sheet). Anchors pp/mf/ff match measured
# IOWA+ORCH midpoints; other levels are workbook-committed.
spectral_data = {
    'A#3': {'pppp': 20.7731538, 'ppp': 20.7968877, 'pp': 20.8444369, 'p': 20.9877377, 'mp': 21.0597571, 'mf': 21.1320237, 'f': 21.9952392, 'ff': 22.893716, 'fff': 23.3566252, 'ffff': 23.591578},
    'B3': {'pppp': 20.2838972, 'ppp': 20.2838972, 'pp': 20.2838972, 'p': 20.2838972, 'mp': 20.2838972, 'mf': 20.2838972, 'f': 20.2838972, 'ff': 20.2838972, 'fff': 20.2838972, 'ffff': 20.2838972},
    'C4': {'pppp': 20.3395047, 'ppp': 20.3395047, 'pp': 20.3395047, 'p': 20.3395047, 'mp': 20.3395047, 'mf': 20.3395047, 'f': 21.9348615, 'ff': 23.6553523, 'fff': 24.5655608, 'ffff': 25.0337156},
    'C#4': {'pppp': 27.9569772, 'ppp': 27.9569772, 'pp': 27.9569772, 'p': 27.9569772, 'mp': 27.9569772, 'mf': 27.9569772, 'f': 27.9569772, 'ff': 27.9569772, 'fff': 27.9569772, 'ffff': 27.9569772},
    'D4': {'pppp': 17.8614155, 'ppp': 17.914829, 'pp': 18.0221357, 'p': 18.3479276, 'mp': 18.5130255, 'mf': 18.679609, 'f': 19.7006197, 'ff': 20.7774379, 'fff': 21.3377217, 'ffff': 21.6235041},
    'D#4': {'pppp': 15.0694367, 'ppp': 15.2057215, 'pp': 15.4819997, 'p': 16.3413197, 'mp': 16.7887036, 'mf': 17.2483357, 'f': 17.6096995, 'ff': 17.9786342, 'fff': 18.16599, 'ffff': 18.2603988},
    'E4': {'pppp': 16.1979905, 'ppp': 16.1979905, 'pp': 16.1979905, 'p': 16.1979905, 'mp': 16.1979905, 'mf': 16.1979905, 'f': 17.0427305, 'ff': 17.9315244, 'fff': 18.3931549, 'ffff': 18.6284079},
    'F4': {'pppp': 14.0997923, 'ppp': 14.3260184, 'pp': 14.7894182, 'p': 16.2715094, 'mp': 17.0673548, 'mf': 17.9021253, 'f': 17.9021253, 'ff': 17.9021253, 'fff': 17.9021253, 'ffff': 17.9021253},
    'F#4': {'pppp': 18.910898, 'ppp': 18.910898, 'pp': 18.910898, 'p': 18.910898, 'mp': 18.910898, 'mf': 18.910898, 'f': 19.4624011, 'ff': 20.0299879, 'fff': 20.3199587, 'ffff': 20.4665145},
    'G4': {'pppp': 17.4298527, 'ppp': 17.4298527, 'pp': 17.4298527, 'p': 17.4298527, 'mp': 17.4298527, 'mf': 17.4298527, 'f': 20.9454283, 'ff': 25.1700902, 'fff': 27.591959, 'ffff': 28.8889274},
    'G#4': {'pppp': 15.0518984, 'ppp': 15.1695444, 'pp': 15.4076022, 'p': 16.1444263, 'mp': 16.5259485, 'mf': 16.9164868, 'f': 19.8006733, 'ff': 23.1766009, 'fff': 25.0746358, 'ffff': 26.0811706},
    'A4': {'pppp': 10.5375028, 'ppp': 10.8278734, 'pp': 11.4328393, 'p': 13.4581972, 'mp': 14.6016954, 'mf': 15.8423527, 'f': 16.767876, 'ff': 17.7474692, 'fff': 18.258522, 'ffff': 18.5195408},
    'A#4': {'pppp': 9.2007556, 'ppp': 9.4543123, 'pp': 9.9825811, 'p': 11.7511822, 'mp': 12.7497278, 'mf': 13.833124, 'f': 13.833124, 'ff': 13.833124, 'fff': 13.833124, 'ffff': 13.833124},
    'B4': {'pppp': 10.6677275, 'ppp': 10.8886027, 'pp': 11.3441675, 'p': 12.8284464, 'mp': 13.6418975, 'mf': 14.5069295, 'f': 15.6034638, 'ff': 16.7828817, 'fff': 17.4056117, 'ffff': 17.7255888},
    'C5': {'pppp': 7.1849153, 'ppp': 7.3697401, 'pp': 7.7537754, 'p': 9.0301787, 'mp': 9.745136, 'mf': 10.5166996, 'f': 13.1502187, 'ff': 16.4432053, 'fff': 18.3870997, 'ffff': 19.4435969},
    'C#5': {'pppp': 6.4639632, 'ppp': 6.6098512, 'pp': 6.9115791, 'p': 7.9019468, 'mp': 8.44914, 'mf': 9.0342253, 'f': 10.4062869, 'ff': 11.9867286, 'fff': 12.8648021, 'ffff': 13.3276731},
    'D5': {'pppp': 5.6382748, 'ppp': 5.8140516, 'pp': 6.1822161, 'p': 7.432588, 'mp': 8.149632, 'mf': 8.9358514, 'f': 9.2362645, 'ff': 9.5467772, 'fff': 9.7059265, 'ffff': 9.7864933},
    'D#5': {'pppp': 5.2301724, 'ppp': 5.3177374, 'pp': 5.4972901, 'p': 6.0731491, 'mp': 6.3833196, 'mf': 6.7093313, 'f': 7.44822, 'ff': 8.2684814, 'fff': 8.7118901, 'ffff': 8.9424331},
    'E5': {'pppp': 4.0412079, 'ppp': 4.1835133, 'pp': 4.4833338, 'p': 5.5179892, 'mp': 6.1216815, 'mf': 6.7914205, 'f': 6.7914205, 'ff': 6.7914205, 'fff': 6.7914205, 'ffff': 6.7914205},
    'F5': {'pppp': 6.8343887, 'ppp': 6.8343887, 'pp': 6.8343887, 'p': 6.8343887, 'mp': 6.8343887, 'mf': 6.8343887, 'f': 6.8343887, 'ff': 6.8343887, 'fff': 6.8343887, 'ffff': 6.8343887},
    'F#5': {'pppp': 6.1718467, 'ppp': 6.224548, 'pp': 6.3313044, 'p': 6.6626857, 'mp': 6.8348249, 'mf': 7.0114116, 'f': 8.5846132, 'ff': 10.5108056, 'fff': 11.6303729, 'ffff': 12.2341121},
    'G5': {'pppp': 4.9050437, 'ppp': 4.991537, 'pp': 5.169126, 'p': 5.7407097, 'mp': 6.0497834, 'mf': 6.3754972, 'f': 8.2196427, 'ff': 10.5972169, 'fff': 12.0326495, 'ffff': 12.821711},
    'G#5': {'pppp': 4.0504902, 'ppp': 4.1649568, 'pp': 4.4036859, 'p': 5.205157, 'mp': 5.6590377, 'mf': 6.152496, 'f': 7.4341228, 'ff': 8.9827254, 'fff': 9.8740954, 'ffff': 10.3524208},
    'A5': {'pppp': 5.733516, 'ppp': 5.733516, 'pp': 5.733516, 'p': 5.733516, 'mp': 5.733516, 'mf': 5.733516, 'f': 6.5488403, 'ff': 7.4801065, 'fff': 7.994282, 'ffff': 8.2644758},
    'A#5': {'pppp': 4.9722095, 'ppp': 4.9862865, 'pp': 5.0145601, 'p': 5.1003464, 'mp': 5.1437884, 'mf': 5.1876004, 'f': 6.0536525, 'ff': 7.064289, 'fff': 7.6312195, 'ffff': 7.9315248},
    'B5': {'pppp': 4.852681, 'ppp': 4.9725924, 'pp': 5.2213774, 'p': 6.0449367, 'mp': 6.5042181, 'mf': 6.9983947, 'f': 7.5590715, 'ff': 8.164667, 'fff': 8.4854228, 'ffff': 8.6504956},
    'C6': {'pppp': 4.845415, 'ppp': 4.928711, 'pp': 5.0996233, 'p': 5.6487496, 'mp': 5.9451037, 'mf': 6.2570057, 'f': 6.5825688, 'ff': 6.9250715, 'fff': 7.1029489, 'ffff': 7.1935937},
    'C#6': {'pppp': 4.3208594, 'ppp': 4.4106119, 'pp': 4.5957487, 'p': 5.1991045, 'mp': 5.529867, 'mf': 5.8816723, 'f': 6.8654887, 'ff': 8.0138662, 'fff': 8.6581957, 'ffff': 8.9995347},
    'D6': {'pppp': 4.7267767, 'ppp': 4.770274, 'pp': 4.8584731, 'p': 5.132976, 'mp': 5.2759898, 'mf': 5.4229883, 'f': 5.6198532, 'ff': 5.8238646, 'fff': 5.928631, 'ffff': 5.9817189},
    'D#6': {'pppp': 4.5625343, 'ppp': 4.6432073, 'pp': 4.8088579, 'p': 5.3421188, 'mp': 5.6305309, 'mf': 5.9345138, 'f': 6.1561027, 'ff': 6.3859654, 'fff': 6.5040956, 'ffff': 6.5639776},
    'E6': {'pppp': 3.1113416, 'ppp': 3.2057955, 'pp': 3.4033926, 'p': 4.0723095, 'mp': 4.4545633, 'mf': 4.872698, 'f': 5.5656605, 'ff': 6.3571714, 'fff': 6.7941875, 'ffff': 7.0238355},
    'F6': {'pppp': 4.9465639, 'ppp': 4.9465639, 'pp': 4.9465639, 'p': 4.9465639, 'mp': 4.9465639, 'mf': 4.9465639, 'f': 5.0464325, 'ff': 5.1483173, 'fff': 5.2000285, 'ffff': 5.2260786},
    'F#6': {'pppp': 4.9268447, 'ppp': 4.9615891, 'pp': 5.0318148, 'p': 5.2485122, 'mp': 5.3603357, 'mf': 5.4745418, 'f': 5.9147668, 'ff': 6.3903917, 'fff': 6.64236, 'ffff': 6.7720455},
    'G6': {'pppp': 5.2488847, 'ppp': 5.2625849, 'pp': 5.2900926, 'p': 5.3734815, 'mp': 5.4156676, 'mf': 5.4581849, 'f': 6.1833106, 'ff': 7.0047701, 'fff': 7.4555604, 'ffff': 7.6917205},
    'G#6': {'pppp': 2.7666963, 'ppp': 2.8693662, 'pp': 3.0862775, 'p': 3.8404484, 'mp': 4.2840587, 'mf': 4.7789104, 'f': 4.7789104, 'ff': 4.7789104, 'fff': 4.7789104, 'ffff': 4.7789104},
    'A6': {'pppp': 4.139896, 'ppp': 4.2375559, 'pp': 4.4398415, 'p': 5.1065025, 'mp': 5.4764811, 'mf': 5.8732655, 'f': 5.8732655, 'ff': 5.8732655, 'fff': 5.8732655, 'ffff': 5.8732655},
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
