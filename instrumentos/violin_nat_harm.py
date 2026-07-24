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
        "estimate_mean from All_Results for dynamics pp, mf and ff; "
        "duplicate sounding pitches averaged; GPR interpolation by pitch/dynamic"
    ),
    dynamic_levels=("pp", "mf", "ff"),
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
    'G4': {'pp': 39.248633, 'mf': 39.248633, 'ff': 39.248633},
    'D5': {'pp': 24.609864, 'mf': 24.609864, 'ff': 24.609864},
    'G5': {'pp': 19.741886, 'mf': 19.741886, 'ff': 19.741886},
    'A5': {'pp': 26.939531, 'mf': 26.939531, 'ff': 26.939531},
    'B5': {'pp': 28.864082, 'mf': 28.864082, 'ff': 28.864082},
    'D6': {'pp': 21.371125, 'mf': 21.371125, 'ff': 21.371125},
    'E6': {'pp': 46.240676, 'mf': 46.240676, 'ff': 46.240676},
    'F6': {'pp': 13.355519, 'mf': 13.355519, 'ff': 13.355519},
    'F#6': {'pp': 12.299651, 'mf': 12.299651, 'ff': 12.299651},
    'G6': {'pp': 16.538657, 'mf': 16.538657, 'ff': 16.538657},
    'A6': {'pp': 12.712892, 'mf': 12.712892, 'ff': 12.712892},
    'B6': {'pp': 10.856259, 'mf': 10.856259, 'ff': 10.856259},
    'C7': {'pp': 10.856259, 'mf': 10.856259, 'ff': 10.856259},
    'C#7': {'pp': 6.958172, 'mf': 6.958172, 'ff': 6.958172},
    'D7': {'pp': 6.958172, 'mf': 6.958172, 'ff': 6.958172},
    'E7': {'pp': 7.307855, 'mf': 7.307855, 'ff': 7.307855},
    'G7': {'pp': 13.312156, 'mf': 13.312156, 'ff': 13.312156},
    'G#7': {'pp': 13.718422, 'mf': 13.718422, 'ff': 13.718422},
    'A7': {'pp': 13.718422, 'mf': 13.718422, 'ff': 13.718422},
    'B7': {'pp': 2.950661, 'mf': 2.950661, 'ff': 2.950661},
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


def predict_intermediate_dynamics(pitches, pp_values, mf_values, ff_values):
    """Predict intermediate dynamics using Gaussian Process Regression."""
    from instrumentos.gpr_dynamic_interpolation import predict_intermediate_dynamics_gpr

    return predict_intermediate_dynamics_gpr(pp_values, mf_values, ff_values, logger=logger)
