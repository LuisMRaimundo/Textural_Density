"""
GUI → core analysis adapter (delegates to adapters.gui_adapter).
"""

from __future__ import annotations

from adapters.gui_adapter import build_analysis_request, calculate_from_gui_request
from gui.types import AnalysisResult, GuiAnalysisInput

# Backward-compatible aliases
normalize_gui_input_data = build_analysis_request
calculate_from_gui = calculate_from_gui_request

__all__ = [
    "AnalysisResult",
    "GuiAnalysisInput",
    "build_analysis_request",
    "calculate_from_gui",
    "calculate_from_gui_request",
    "normalize_gui_input_data",
]
