# instrumentos/double_bass_harmonics.py
"""
Double bass (arco harmonics) instrument density module.

The ``spectral_data`` table stores a committed 10-dynamic Combined Density
Metric (CDM) ladder from the ``Results`` sheet of
``DoubleBass_harmonics_dynamics.xlsx``
(measured pp/mf/ff anchors; remaining levels committed from that workbook —
no runtime dynamic extrapolation).

Runtime analysis does not ingest audio; it maps notated pitch + dynamic to
these pre-loaded acoustic metadata tables.
"""

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="external_acoustic_metadata",
    citation=(
        "Double bass arco_harmonic CDM ladder: measured pp/mf/ff anchors with "
        "committed Results sheet values for all 10 dynamic levels from "
        "DoubleBass_harmonics_dynamics.xlsx "
        "(dest Zenodo DoubleBass_harmonics Media (IOWA+Orchidea average); Dynamics_predicter Results ladder)."
    ),
    source_url_or_identifier='docs/instrument_acoustic_sources.md#double-bass-harmonics',
    extraction_method=(
        "Committed full dynamic ladder from Dynamics extrapolator v1.5.2.1 Results sheet "
        "(PCHIP interiors, tapered outers r=0.80) on measured pp/mf/ff anchors; "
        "interior cells clamped into their measured segment where the workbook "
        "marginally overshoots; pitch lookup via MIDI-space spectral_lookup"
    ),
    dynamic_levels=('pppp', 'ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', 'ffff'),
    pitch_range=(28, 67),
    uncertainty="high",
    version="2026-08-27",
    source_technique="arco_harmonic",
    table_supported_techniques=("arco_harmonic",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("double_bass_harmonics")

# Full 10-dynamic CDM ladder (Results sheet). Anchors pp/mf/ff match measured
# workbook midpoints; other levels are workbook-committed.
spectral_data = {
    'E1': {'pppp': 39.174591, 'ppp': 39.147493, 'pp': 39.113648, 'p': 38.978257, 'mp': 38.928494, 'mf': 38.921391, 'f': 39.459415, 'ff': 40.621258, 'fff': 41.438419, 'ffff': 42.103968},
    'F1': {'pppp': 36.818617, 'ppp': 37.418755, 'pp': 38.182702, 'p': 39.664742, 'mp': 40.496821, 'mf': 40.752257, 'f': 40.27172, 'ff': 39.030123, 'fff': 38.301449, 'ffff': 37.728318},
    'F#1': {'pppp': 29.855961, 'ppp': 30.183659, 'pp': 30.598343, 'p': 30.776137, 'mp': 31.251297, 'mf': 31.938736, 'f': 33.425297, 'ff': 35.908751, 'fff': 37.965485, 'ffff': 39.695371},
    'G1': {'pppp': 26.848826, 'ppp': 26.588561, 'pp': 26.266775, 'p': 25.546541, 'mp': 25.286199, 'mf': 25.249225, 'f': 26.285276, 'ff': 28.690941, 'fff': 30.489476, 'ffff': 32.009147},
    'G#1': {'pppp': 26.308669, 'ppp': 26.18871, 'pp': 26.039529, 'p': 25.953736, 'mp': 25.750865, 'mf': 25.490531, 'f': 25.101995, 'ff': 24.566048, 'fff': 24.209075, 'ffff': 23.927234},
    'A1': {'pppp': 28.441497, 'ppp': 28.506107, 'pp': 28.587077, 'p': 28.698096, 'mp': 28.774044, 'mf': 28.802175, 'f': 28.797971, 'ff': 28.768561, 'fff': 28.847479, 'ffff': 28.910769},
    'A#1': {'pppp': 37.878083, 'ppp': 37.068746, 'pp': 36.081349, 'p': 34.346487, 'mp': 33.356141, 'mf': 33.035496, 'f': 33.383587, 'ff': 34.428325, 'fff': 35.122912, 'ffff': 35.688659},
    'B1': {'pppp': 26.555413, 'ppp': 27.658411, 'pp': 29.101806, 'p': 31.501549, 'mp': 33.391398, 'mf': 34.205759, 'f': 34.277028, 'ff': 34.30355, 'fff': 34.372894, 'ffff': 34.42847},
    'C2': {'pppp': 29.720645, 'ppp': 29.579005, 'pp': 29.402905, 'p': 28.965964, 'mp': 28.806628, 'mf': 28.783937, 'f': 29.320475, 'ff': 30.533548, 'fff': 31.388649, 'ffff': 32.08994},
    'C#2': {'pppp': 24.3072, 'ppp': 24.238252, 'pp': 24.152342, 'p': 24.104997, 'mp': 23.981693, 'mf': 23.810661, 'f': 23.480723, 'ff': 22.980704, 'fff': 22.669857, 'ffff': 22.42421},
    'D2': {'pppp': 27.064454, 'ppp': 26.821043, 'pp': 26.519855, 'p': 25.82771, 'mp': 25.577288, 'mf': 25.541712, 'f': 26.218904, 'ff': 27.790203, 'fff': 28.919765, 'ffff': 29.856383},
    'D#2': {'pppp': 24.848845, 'ppp': 24.922022, 'pp': 25.013796, 'p': 25.20839, 'mp': 25.280463, 'mf': 25.290776, 'f': 24.886566, 'ff': 24.040409, 'fff': 23.54541, 'ffff': 23.156759},
    'E2': {'pppp': 27.471728, 'ppp': 26.981926, 'pp': 26.381936, 'p': 25.771392, 'mp': 25.144925, 'mf': 24.50905, 'f': 23.859417, 'ff': 23.195974, 'fff': 22.630041, 'ffff': 22.187253},
    'F2': {'pppp': 24.136735, 'ppp': 24.209172, 'pp': 24.300024, 'p': 24.493202, 'mp': 24.564759, 'mf': 24.574999, 'f': 24.189431, 'ff': 23.380857, 'fff': 22.909091, 'ffff': 22.538541},
    'F#2': {'pppp': 23.010642, 'ppp': 23.058811, 'pp': 23.119163, 'p': 23.236215, 'mp': 23.279489, 'mf': 23.285678, 'f': 23.069739, 'ff': 22.610979, 'fff': 22.378783, 'ffff': 22.194745},
    'G2': {'pppp': 20.709268, 'ppp': 20.990562, 'pp': 21.347559, 'p': 21.869994, 'mp': 22.292002, 'mf': 22.572686, 'f': 22.751588, 'ff': 22.8423, 'fff': 22.992807, 'ffff': 23.113926},
    'G#2': {'pppp': 18.910673, 'ppp': 19.053019, 'pp': 19.232458, 'p': 19.635445, 'mp': 19.786033, 'mf': 19.80764, 'f': 19.20643, 'ff': 17.961068, 'fff': 17.179267, 'ffff': 16.5784},
    'A2': {'pppp': 21.214421, 'ppp': 21.390394, 'pp': 21.612415, 'p': 22.108771, 'mp': 22.294499, 'mf': 22.321159, 'f': 21.434998, 'ff': 19.640216, 'fff': 18.507872, 'ffff': 17.649185},
    'A#2': {'pppp': 20.958854, 'ppp': 21.156084, 'pp': 21.405235, 'p': 21.960464, 'mp': 22.168633, 'mf': 22.198532, 'f': 21.059457, 'ff': 18.806687, 'fff': 17.392385, 'ffff': 16.337914},
    'B2': {'pppp': 21.853164, 'ppp': 21.78272, 'pp': 21.694984, 'p': 21.47969, 'mp': 21.400911, 'mf': 21.389681, 'f': 22.064868, 'ff': 23.57029, 'fff': 24.667617, 'ffff': 25.582147},
    'C3': {'pppp': 19.995878, 'ppp': 20.325063, 'pp': 20.744175, 'p': 21.601618, 'mp': 22.0295, 'mf': 22.142528, 'f': 21.755463, 'ff': 20.833186, 'fff': 20.270457, 'ffff': 19.831237},
    'C#3': {'pppp': 20.907111, 'ppp': 20.871384, 'pp': 20.82681, 'p': 20.695955, 'mp': 20.647953, 'mf': 20.641104, 'f': 20.978027, 'ff': 21.715405, 'fff': 22.233838, 'ffff': 22.657482},
    'D3': {'pppp': 22.706494, 'ppp': 22.90185, 'pp': 23.148411, 'p': 23.582616, 'mp': 23.885047, 'mf': 23.998295, 'f': 23.9828, 'ff': 23.874618, 'fff': 23.865388, 'ffff': 23.858006},
    'D#3': {'pppp': 19.904758, 'ppp': 20.061471, 'pp': 20.259098, 'p': 20.614541, 'mp': 20.850331, 'mf': 20.935473, 'f': 20.902598, 'ff': 20.764426, 'fff': 20.729991, 'ffff': 20.702484},
    'E3': {'pppp': 21.538562, 'ppp': 22.042723, 'pp': 22.689552, 'p': 24.059063, 'mp': 24.69965, 'mf': 24.849935, 'f': 24.120371, 'ff': 22.462325, 'fff': 21.425336, 'ffff': 20.630322},
    'F3': {'pppp': 19.883024, 'ppp': 19.820521, 'pp': 19.742668, 'p': 19.546091, 'mp': 19.474163, 'mf': 19.463909, 'f': 19.943201, 'ff': 21.007314, 'fff': 21.768694, 'ffff': 22.397619},
    'F#3': {'pppp': 18.065153, 'ppp': 18.079174, 'pp': 18.096716, 'p': 18.098976, 'mp': 18.106031, 'mf': 18.118303, 'f': 18.321176, 'ff': 18.73557, 'fff': 19.034257, 'ffff': 19.276631},
    'G3': {'pppp': 19.02377, 'ppp': 18.951975, 'pp': 18.862612, 'p': 18.812875, 'mp': 18.687703, 'mf': 18.52316, 'f': 18.259327, 'ff': 17.88391, 'fff': 17.641768, 'ffff': 17.450417},
    'G#3': {'pppp': 14.318199, 'ppp': 14.299691, 'pp': 14.276589, 'p': 14.198137, 'mp': 14.169342, 'mf': 14.165234, 'f': 14.317387, 'ff': 14.650401, 'fff': 14.886322, 'ffff': 15.077791},
    'A3': {'pppp': 16.067378, 'ppp': 16.245751, 'pp': 16.471505, 'p': 16.952004, 'mp': 17.170423, 'mf': 17.220614, 'f': 16.967576, 'ff': 16.378967, 'fff': 16.027385, 'ffff': 15.751561},
    'A#3': {'pppp': 18.499943, 'ppp': 18.673713, 'pp': 18.893222, 'p': 18.996961, 'mp': 19.260134, 'mf': 19.610688, 'f': 20.173691, 'ff': 21.006857, 'fff': 21.699427, 'ffff': 22.269886},
    'B3': {'pppp': 19.978778, 'ppp': 19.862146, 'pp': 19.717313, 'p': 19.383007, 'mp': 19.261276, 'mf': 19.243948, 'f': 19.998086, 'ff': 21.714183, 'fff': 22.991055, 'ffff': 24.066404},
    'C4': {'pppp': 17.535394, 'ppp': 18.139801, 'pp': 18.924689, 'p': 19.483055, 'mp': 20.398981, 'mf': 21.579963, 'f': 23.261736, 'ff': 25.626001, 'fff': 27.852113, 'ffff': 29.77145},
    'C#4': {'pppp': 17.938176, 'ppp': 18.575598, 'pp': 19.404321, 'p': 20.297142, 'mp': 21.24291, 'mf': 22.243637, 'f': 23.304995, 'ff': 24.43191, 'fff': 25.564723, 'ffff': 26.508676},
    'D4': {'pppp': 18.546808, 'ppp': 18.798169, 'pp': 19.117166, 'p': 19.257666, 'mp': 19.628114, 'mf': 20.153477, 'f': 21.190797, 'ff': 22.882335, 'fff': 24.311985, 'ffff': 25.519753},
    'D#4': {'pppp': 25.426808, 'ppp': 23.879407, 'pp': 22.076902, 'p': 18.925961, 'mp': 17.640893, 'mf': 17.347932, 'f': 18.712517, 'ff': 22.447512, 'fff': 25.467963, 'ffff': 28.174421},
    'E4': {'pppp': 12.803029, 'ppp': 13.742994, 'pp': 15.015581, 'p': 17.555923, 'mp': 19.176085, 'mf': 19.715767, 'f': 18.89603, 'ff': 16.824231, 'fff': 15.577531, 'ffff': 14.647022},
    'F4': {'pppp': 17.678224, 'ppp': 17.754204, 'pp': 17.849638, 'p': 17.889219, 'mp': 17.995694, 'mf': 18.150898, 'f': 18.507965, 'ff': 19.098169, 'fff': 19.557993, 'ffff': 19.933811},
    'F#4': {'pppp': 19.805326, 'ppp': 19.998385, 'pp': 20.242358, 'p': 20.349874, 'mp': 20.632908, 'mf': 21.033062, 'f': 21.824456, 'ff': 23.098378, 'fff': 24.144635, 'ffff': 25.01566},
    'G4': {'pppp': 14.504901, 'ppp': 14.310903, 'pp': 14.072051, 'p': 13.562769, 'mp': 13.37982, 'mf': 13.353887, 'f': 14.751362, 'ff': 18.236405, 'fff': 21.219649, 'ffff': 23.953963},
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
