"""Shared GUI constants and row counts (no Tkinter)."""

from __future__ import annotations

from instrumentos.registry import list_profiles

NUM_NOTE_ROWS = 60

SUSTENIDO_MUSICAL = "\u266f"
QUARTO_TOM_GUI = "\u2193"

OCTAVE_LIST = [str(i) for i in range(10)]
DYNAMIC_LEVELS = ["pppp", "ppp", "pp", "p", "mp", "mf", "f", "ff", "fff", "ffff"]


def _active_instrument_names() -> list[str]:
    """GUI-selectable instruments: only those backed by a dedicated script.

    An instrument is "active" when its registry profile declares a
    ``module_name`` (a committed ``instrumentos/<module>.py`` acoustic table).
    Coarse-default profiles (no script) are intentionally excluded so the GUI
    only offers instruments with real acoustic metadata. Registry insertion
    order is preserved.
    """
    return [p.display_name for p in list_profiles() if p.module_name]


INSTRUMENTS = _active_instrument_names()
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
    "NOTAS_BASE",
    "NUM_NOTE_ROWS",
    "OCTAVE_LIST",
]
