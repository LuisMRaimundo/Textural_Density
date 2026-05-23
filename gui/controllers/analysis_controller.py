"""
Analysis controller: GUI state → typed request → core pipeline → formatted output.

Approved GUI calculation path:
  GuiAnalysisInput → adapters.gui_adapter → AnalysisRequest → core.pipeline.calculate_metrics

No Tkinter imports; safe to test without a display.
"""

from __future__ import annotations

from typing import Any

from adapters.gui_adapter import build_analysis_request, calculate_from_gui_request
from core import format_output_string
from core.request import AnalysisRequest
from gui.types import AnalysisResult, GuiAnalysisInput


class AnalysisController:
    """Orchestrates the score-only analysis path for the GUI."""

    @staticmethod
    def build_request(raw: GuiAnalysisInput) -> AnalysisRequest:
        return build_analysis_request(dict(raw))

    @staticmethod
    def analyze(raw: GuiAnalysisInput) -> AnalysisResult:
        return calculate_from_gui_request(dict(raw))

    @staticmethod
    def format_results(resultados: dict[str, Any]) -> str:
        return format_output_string(resultados)
