# instrumentos/cello_nat_harm.py
"""Cello natural harmonics — registry/modal placeholder; no acoustic calibration."""

from instrumentos.provenance import InstrumentSource
from instrumentos.uncalibrated_harmonic import (
    ACCEPTANCE_STATUS_UNCALIBRATED,
    FF_MEASURED,
    MF_MEASURED,
    PP_MEASURED,
    spectral_data,
    unavailable_density,
    unavailable_gpr,
)

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="unavailable_calibration",
    citation=(
        "No same-instrument cello natural_harmonic EWSD table in "
        "Strings_techniques_extrapolation measured calibration yet."
    ),
    source_url_or_identifier="docs/instrument_acoustic_sources.md#cello-nat-harm",
    extraction_method="none — implemented_but_uncalibrated",
    dynamic_levels=(),
    pitch_range=(36, 84),
    uncertainty="high",
    version="2026-07-24",
    source_technique="arco_natural_harmonic",
    table_supported_techniques=(),
)

ACCEPTANCE_STATUS = ACCEPTANCE_STATUS_UNCALIBRATED

calcular_densidade = unavailable_density
predict_intermediate_dynamics = unavailable_gpr

__all__ = [
    "ACCEPTANCE_STATUS",
    "FF_MEASURED",
    "INSTRUMENT_SOURCE",
    "MF_MEASURED",
    "PP_MEASURED",
    "calcular_densidade",
    "predict_intermediate_dynamics",
    "spectral_data",
]
