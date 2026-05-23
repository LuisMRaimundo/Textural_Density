"""Typed GUI ↔ core analysis boundaries."""

from __future__ import annotations

from typing import Any, TypedDict


class SymbolicSliceInput(TypedDict):
    """Required fields for a vertical-slice analysis request from the GUI."""

    notes: list[str]
    dynamics: list[str]
    instruments: list[str]
    num_instruments: list[int]


class GuiAnalysisInput(SymbolicSliceInput, total=False):
    """GUI-collected options merged with research defaults before analysis."""

    weight_factor: float
    save_results: bool
    show_graphs: bool
    onsets: list[float]
    offsets: list[float]
    durations: list[float]
    part_ids: list[str]


AnalysisResult = tuple[dict[str, Any], list[float], list[float]]

__all__ = [
    "AnalysisResult",
    "GuiAnalysisInput",
    "SymbolicSliceInput",
]
