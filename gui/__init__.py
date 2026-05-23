"""GUI package — typed adapter to the analytical core (no Tkinter here)."""

from gui.analysis_adapter import calculate_from_gui, normalize_gui_input_data
from gui.types import AnalysisResult, GuiAnalysisInput, SymbolicSliceInput

__all__ = [
    "AnalysisResult",
    "GuiAnalysisInput",
    "SymbolicSliceInput",
    "calculate_from_gui",
    "normalize_gui_input_data",
]
