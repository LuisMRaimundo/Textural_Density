"""Shared GUI constants and row counts (no Tkinter)."""

from __future__ import annotations

from core.unpitched_routing import UNPITCHED_INSTRUMENT_GROUP_LABEL
from instrumentos.registry import list_profiles

NUM_NOTE_ROWS = 60

SUSTENIDO_MUSICAL = "\u266f"
QUARTO_TOM_GUI = "\u2193"

OCTAVE_LIST = [str(i) for i in range(10)]
DYNAMIC_LEVELS = ["pppp", "ppp", "pp", "p", "mp", "mf", "f", "ff", "fff", "ffff"]


def _active_profiles():
    """Profiles backed by a dedicated acoustic module (GUI-selectable)."""
    return [p for p in list_profiles() if p.module_name]


def _active_instrument_names() -> list[str]:
    """Flat list of GUI instrument display names (pitched then unpitched)."""
    pitched = [p.display_name for p in _active_profiles() if not p.unpitched]
    unpitched = [p.display_name for p in _active_profiles() if p.unpitched]
    return pitched + unpitched


def instrument_dropdown_values() -> list[str]:
    """Combobox values with an Unpitched percussion group header."""
    pitched = [p.display_name for p in _active_profiles() if not p.unpitched]
    unpitched = [p.display_name for p in _active_profiles() if p.unpitched]
    if not unpitched:
        return pitched
    return pitched + [UNPITCHED_INSTRUMENT_GROUP_LABEL] + unpitched


INSTRUMENTS = _active_instrument_names()
INSTRUMENT_DROPDOWN_VALUES = instrument_dropdown_values()
CENTS_VALUES = ["0"] + [f"+{i}" for i in range(1, 51)] + [f"-{i}" for i in range(1, 51)]
NOTAS_BASE = [
    "C",
    f"C{QUARTO_TOM_GUI}",
    f"C{SUSTENIDO_MUSICAL}",
    f"C{SUSTENIDO_MUSICAL}{QUARTO_TOM_GUI}",
    "D",
    f"D{QUARTO_TOM_GUI}",
    f"D{SUSTENIDO_MUSICAL}",
    f"D{SUSTENIDO_MUSICAL}{QUARTO_TOM_GUI}",
    "E",
    f"E{QUARTO_TOM_GUI}",
    "F",
    f"F{QUARTO_TOM_GUI}",
    f"F{SUSTENIDO_MUSICAL}",
    f"F{SUSTENIDO_MUSICAL}{QUARTO_TOM_GUI}",
    "G",
    f"G{QUARTO_TOM_GUI}",
    f"G{SUSTENIDO_MUSICAL}",
    f"G{SUSTENIDO_MUSICAL}{QUARTO_TOM_GUI}",
    "A",
    f"A{QUARTO_TOM_GUI}",
    f"A{SUSTENIDO_MUSICAL}",
    f"A{SUSTENIDO_MUSICAL}{QUARTO_TOM_GUI}",
    "B",
    f"B{QUARTO_TOM_GUI}",
]

__all__ = [
    "CENTS_VALUES",
    "DYNAMIC_LEVELS",
    "INSTRUMENTS",
    "INSTRUMENT_DROPDOWN_VALUES",
    "NOTAS_BASE",
    "NUM_NOTE_ROWS",
    "OCTAVE_LIST",
    "instrument_dropdown_values",
]
