"""Compatibility adapters — not imported by core pipeline internals."""

from adapters.gui_adapter import build_analysis_request, calculate_from_gui_request
from adapters.legacy_input import legacy_dict_to_request

__all__ = [
    "build_analysis_request",
    "calculate_from_gui_request",
    "legacy_dict_to_request",
]
