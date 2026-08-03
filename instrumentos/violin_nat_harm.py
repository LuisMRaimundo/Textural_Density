# instrumentos/violin_nat_harm.py
"""
Violin (arco natural harmonic) instrument density module.

Dynamic resolution chain (per note):

1. **Workbook anchors:** ``pp``, ``mf`` and ``ff`` imported from Strings Techniques
   Extrapolation Excel exports (``Violin_pp_hamro.xlsx`` / ``Violin_mf_harmo.xlsx`` /
   ``Violin_ff_harmo.xlsx``), column ``estimate_mean`` / ``All_Results``.
2. **GPR-modelled dynamics:** intermediate / extreme markings predicted by GPR
   on the pp/mf/ff triple.

These workbook values are calibrated / assumption-based harmonic descriptor
lookups from Strings Techniques Extrapolation (not Zenodo ordinary CDM rows).
Uncertainty is therefore high.

Runtime analysis does not ingest audio; it maps notated pitch + dynamic to these
pre-loaded tables.
"""

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="external_acoustic_metadata",
    citation=(
        "Violin natural_harmonic EWSD table from Strings_techniques_extrapolation "
        "workbooks Violin_pp_hamro.xlsx / Violin_mf_harmo.xlsx / Violin_ff_harmo.xlsx "
        "(calibrated harmonic descriptor lookup / assumption-based dynamic transfer)."
    ),
    source_url_or_identifier="docs/instrument_acoustic_sources.md#violin-nat-harm",
    extraction_method=(
        "monotone log-CDM ladder enforcement (2026-08-03): pp/mf/ff anchors isotonic-clamped then full DYNAMIC_LEVELS rebuilt via offline internal_default log-linear + adaptive tails; estimate_mean from All_Results for dynamics pp, mf and ff; "
        "duplicate sounding pitches averaged; GPR interpolation by pitch/dynamic"
    ),
    dynamic_levels=('pppp', 'ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', 'ffff'),
    pitch_range=(67, 107),
    uncertainty="high",
    version="2026-07-24",
    source_technique="arco_natural_harmonic",
    table_supported_techniques=("arco_natural_harmonic",),
)

import logging

from utils.notes import normalize_note_string

logger = logging.getLogger("violin_nat_harm")

# Workbook pp / mf / ff anchors (20 chromatic sounding rows, G4–B7).
PP_MEASURED: dict[str, float] = {
    'G4': 39.248633,
    'D5': 24.609864,
    'G5': 19.741886,
    'A5': 26.939531,
    'B5': 28.864082,
    'D6': 21.371125,
    'E6': 46.240676,
    'F6': 13.355519,
    'F#6': 12.299651,
    'G6': 16.538657,
    'A6': 12.712892,
    'B6': 10.856259,
    'C7': 10.856259,
    'C#7': 6.958172,
    'D7': 6.958172,
    'E7': 7.307855,
    'G7': 13.312156,
    'G#7': 13.718422,
    'A7': 13.718422,
    'B7': 2.950661,
}

MF_MEASURED: dict[str, float] = {
    'G4': 39.248633,
    'D5': 24.609864,
    'G5': 19.741886,
    'A5': 26.939531,
    'B5': 28.864082,
    'D6': 21.371125,
    'E6': 46.240676,
    'F6': 13.355519,
    'F#6': 12.299651,
    'G6': 16.538657,
    'A6': 12.712892,
    'B6': 10.856259,
    'C7': 10.856259,
    'C#7': 6.958172,
    'D7': 6.958172,
    'E7': 7.307855,
    'G7': 13.312156,
    'G#7': 13.718422,
    'A7': 13.718422,
    'B7': 2.950661,
}

FF_MEASURED: dict[str, float] = {
    'G4': 39.248633,
    'D5': 24.609864,
    'G5': 19.741886,
    'A5': 26.939531,
    'B5': 28.864082,
    'D6': 21.371125,
    'E6': 46.240676,
    'F6': 13.355519,
    'F#6': 12.299651,
    'G6': 16.538657,
    'A6': 12.712892,
    'B6': 10.856259,
    'C7': 10.856259,
    'C#7': 6.958172,
    'D7': 6.958172,
    'E7': 7.307855,
    'G7': 13.312156,
    'G#7': 13.718422,
    'A7': 13.718422,
    'B7': 2.950661,
}

# GPR anchors: pp/mf/ff from Excel harmonic workbooks.
spectral_data = {
    'G4': {'pppp': 39.248633, 'ppp': 39.248633, 'pp': 39.248633, 'p': 39.248633, 'mp': 39.248633, 'mf': 39.248633, 'f': 39.248633, 'ff': 39.248633, 'fff': 39.248633, 'ffff': 39.248633},
    'D5': {'pppp': 24.609864, 'ppp': 24.609864, 'pp': 24.609864, 'p': 24.609864, 'mp': 24.609864, 'mf': 24.609864, 'f': 24.609864, 'ff': 24.609864, 'fff': 24.609864, 'ffff': 24.609864},
    'G5': {'pppp': 19.741886, 'ppp': 19.741886, 'pp': 19.741886, 'p': 19.741886, 'mp': 19.741886, 'mf': 19.741886, 'f': 19.741886, 'ff': 19.741886, 'fff': 19.741886, 'ffff': 19.741886},
    'A5': {'pppp': 26.939531, 'ppp': 26.939531, 'pp': 26.939531, 'p': 26.939531, 'mp': 26.939531, 'mf': 26.939531, 'f': 26.939531, 'ff': 26.939531, 'fff': 26.939531, 'ffff': 26.939531},
    'B5': {'pppp': 28.864082, 'ppp': 28.864082, 'pp': 28.864082, 'p': 28.864082, 'mp': 28.864082, 'mf': 28.864082, 'f': 28.864082, 'ff': 28.864082, 'fff': 28.864082, 'ffff': 28.864082},
    'D6': {'pppp': 21.371125, 'ppp': 21.371125, 'pp': 21.371125, 'p': 21.371125, 'mp': 21.371125, 'mf': 21.371125, 'f': 21.371125, 'ff': 21.371125, 'fff': 21.371125, 'ffff': 21.371125},
    'E6': {'pppp': 46.240676, 'ppp': 46.240676, 'pp': 46.240676, 'p': 46.240676, 'mp': 46.240676, 'mf': 46.240676, 'f': 46.240676, 'ff': 46.240676, 'fff': 46.240676, 'ffff': 46.240676},
    'F6': {'pppp': 13.355519, 'ppp': 13.355519, 'pp': 13.355519, 'p': 13.355519, 'mp': 13.355519, 'mf': 13.355519, 'f': 13.355519, 'ff': 13.355519, 'fff': 13.355519, 'ffff': 13.355519},
    'F#6': {'pppp': 12.299651, 'ppp': 12.299651, 'pp': 12.299651, 'p': 12.299651, 'mp': 12.299651, 'mf': 12.299651, 'f': 12.299651, 'ff': 12.299651, 'fff': 12.299651, 'ffff': 12.299651},
    'G6': {'pppp': 16.538657, 'ppp': 16.538657, 'pp': 16.538657, 'p': 16.538657, 'mp': 16.538657, 'mf': 16.538657, 'f': 16.538657, 'ff': 16.538657, 'fff': 16.538657, 'ffff': 16.538657},
    'A6': {'pppp': 12.712892, 'ppp': 12.712892, 'pp': 12.712892, 'p': 12.712892, 'mp': 12.712892, 'mf': 12.712892, 'f': 12.712892, 'ff': 12.712892, 'fff': 12.712892, 'ffff': 12.712892},
    'B6': {'pppp': 10.856259, 'ppp': 10.856259, 'pp': 10.856259, 'p': 10.856259, 'mp': 10.856259, 'mf': 10.856259, 'f': 10.856259, 'ff': 10.856259, 'fff': 10.856259, 'ffff': 10.856259},
    'C7': {'pppp': 10.856259, 'ppp': 10.856259, 'pp': 10.856259, 'p': 10.856259, 'mp': 10.856259, 'mf': 10.856259, 'f': 10.856259, 'ff': 10.856259, 'fff': 10.856259, 'ffff': 10.856259},
    'C#7': {'pppp': 6.958172, 'ppp': 6.958172, 'pp': 6.958172, 'p': 6.958172, 'mp': 6.958172, 'mf': 6.958172, 'f': 6.958172, 'ff': 6.958172, 'fff': 6.958172, 'ffff': 6.958172},
    'D7': {'pppp': 6.958172, 'ppp': 6.958172, 'pp': 6.958172, 'p': 6.958172, 'mp': 6.958172, 'mf': 6.958172, 'f': 6.958172, 'ff': 6.958172, 'fff': 6.958172, 'ffff': 6.958172},
    'E7': {'pppp': 7.307855, 'ppp': 7.307855, 'pp': 7.307855, 'p': 7.307855, 'mp': 7.307855, 'mf': 7.307855, 'f': 7.307855, 'ff': 7.307855, 'fff': 7.307855, 'ffff': 7.307855},
    'G7': {'pppp': 13.312156, 'ppp': 13.312156, 'pp': 13.312156, 'p': 13.312156, 'mp': 13.312156, 'mf': 13.312156, 'f': 13.312156, 'ff': 13.312156, 'fff': 13.312156, 'ffff': 13.312156},
    'G#7': {'pppp': 13.718422, 'ppp': 13.718422, 'pp': 13.718422, 'p': 13.718422, 'mp': 13.718422, 'mf': 13.718422, 'f': 13.718422, 'ff': 13.718422, 'fff': 13.718422, 'ffff': 13.718422},
    'A7': {'pppp': 13.718422, 'ppp': 13.718422, 'pp': 13.718422, 'p': 13.718422, 'mp': 13.718422, 'mf': 13.718422, 'f': 13.718422, 'ff': 13.718422, 'fff': 13.718422, 'ffff': 13.718422},
    'B7': {'pppp': 2.950661, 'ppp': 2.950661, 'pp': 2.950661, 'p': 2.950661, 'mp': 2.950661, 'mf': 2.950661, 'f': 2.950661, 'ff': 2.950661, 'fff': 2.950661, 'ffff': 2.950661},
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
