"""
Analytical core entry points for Simultaneity Density Analyser.

Import from this package for GUI-independent analysis. The vertical-slice
pipeline is implemented in ``core.pipeline`` (core-native).
"""

from core.composite import compute_weighted_density_normalized as calcular_densidade_ponderada_normalizada
from core.converters import (
    analysis_config_from_input,
    legacy_input_to_vertical_slice,
    make_instrument_event,
    note_string_to_pitch,
    vertical_slice_to_legacy_lists,
)
from core.formatting import format_output_string
from core.metrics_metadata import (
    attach_metric_metadata,
    build_metric_metadata,
    metric_result_to_dict,
)
from core.models import (
    AnalysisConfig,
    InstrumentEvent,
    MetricResult,
    Pitch,
    ScoreAnalysisResult,
    VerticalSlice,
    VerticalSliceAnalysis,
)
from core.orchestration_mass import compute_orchestration_mass as calcular_massa_sonora
from core.pipeline import calcular_metricas, calculate_metrics, load_instrument_module
from core.request import AnalysisRequest
from core.reporting import (
    explain_score_slice,
    explain_vertical_slice,
    format_interpretability_report,
    format_sensitivity_report,
    run_sensitivity_analysis,
)
from core.score_analysis import analyze_score, load_timed_events_from_path
from core.subindices import (
    SubindexContext,
    attach_density_subindices,
    build_density_subindices,
)
from core.temporal import group_events_into_slices

__all__ = [
    "calculate_metrics",
    "calcular_metricas",
    "AnalysisRequest",
    "calcular_densidade_ponderada_normalizada",
    "calcular_massa_sonora",
    "format_output_string",
    "load_instrument_module",
    "legacy_input_to_vertical_slice",
    "vertical_slice_to_legacy_lists",
    "note_string_to_pitch",
    "analysis_config_from_input",
    "Pitch",
    "InstrumentEvent",
    "VerticalSlice",
    "AnalysisConfig",
    "MetricResult",
    "VerticalSliceAnalysis",
    "ScoreAnalysisResult",
    "attach_metric_metadata",
    "build_metric_metadata",
    "metric_result_to_dict",
    "SubindexContext",
    "attach_density_subindices",
    "build_density_subindices",
    "analyze_score",
    "load_timed_events_from_path",
    "group_events_into_slices",
    "make_instrument_event",
    "explain_score_slice",
    "explain_vertical_slice",
    "format_interpretability_report",
    "format_sensitivity_report",
    "run_sensitivity_analysis",
]
