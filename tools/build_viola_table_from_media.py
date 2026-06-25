"""Build viola spectral_data from VIOLA_Media for module update."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from microtonal import note_to_midi_strict, InvalidPitchNotation
from tools.generate_instrument_modules import load_spectral_data_from_media


def build_viola_spectral_data(workbook: Path) -> dict[str, dict[str, float]]:
    table = load_spectral_data_from_media(workbook, "VIOLA_Media")
    cleaned: dict[str, dict[str, float]] = {}
    for note, dynamics in table.items():
        try:
            note_to_midi_strict(note)
        except InvalidPitchNotation:
            continue
        cleaned[note] = dynamics
    return cleaned


if __name__ == "__main__":
    wb = Path(r"D:\CORDAS\ViOLA_Zenodo_collections_media.xlsx")
    table = build_viola_spectral_data(wb)
    notes = sorted(table, key=note_to_midi_strict)
    assert len(notes) == 49, len(notes)
    assert notes[0] == "C3" and notes[-1] == "C7"
    assert "F4" in table
    for note in notes:
        d = table[note]
        print(f"    '{note}': {{'pp': {d['pp']}, 'mf': {d['mf']}, 'ff': {d['ff']}}},")
