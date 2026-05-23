# data_processor.py — backward-compatibility shim only.
# Canonical pipeline: core.pipeline.calculate_metrics

from core.composite import compute_weighted_density_normalized as calcular_densidade_ponderada_normalizada
from core.formatting import format_output_string
from core.orchestration_mass import compute_orchestration_mass as calcular_massa_sonora
from core.pipeline import calcular_metricas, calculate_metrics, load_instrument_module

# Legacy helpers retained for tests and GUI validation text
from data_processor_legacy import (  # noqa: F401
    _normalize_notes_to_sustenido,
    _validate_and_extract_input,
    calcular_densidade_fundida,
    calcular_densidade_intervalar_com_cents,
    generate_validation_text,
    save_results,
)

__all__ = [
    "calculate_metrics",
    "calcular_metricas",
    "calcular_densidade_ponderada_normalizada",
    "calcular_massa_sonora",
    "format_output_string",
    "load_instrument_module",
    "save_results",
    "generate_validation_text",
    "_validate_and_extract_input",
    "_normalize_notes_to_sustenido",
    "calcular_densidade_intervalar_com_cents",
    "calcular_densidade_fundida",
]
