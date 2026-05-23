"""
Synthetic verification case definitions (Phase 8).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

_DEFAULT_OPTIONS: dict[str, Any] = {
    "weight_factor": 0.5,
    "save_results": False,
    "show_graphs": False,
}


def base_input(
    notes: list[str],
    *,
    dynamics: list[str] | None = None,
    instruments: list[str] | None = None,
    num_instruments: list[int] | None = None,
    **options: Any,
) -> dict[str, Any]:
    n = len(notes)
    data = dict(_DEFAULT_OPTIONS)
    data.update(options)
    data.update(
        {
            "notes": notes,
            "dynamics": dynamics or ["mf"] * n,
            "instruments": instruments or ["flauta"] * n,
            "num_instruments": num_instruments or [1] * n,
        }
    )
    return data


@dataclass
class SyntheticCase:
    case_id: str
    description: str
    input_data: dict[str, Any]
    tags: list[str] = field(default_factory=list)


def all_synthetic_cases() -> list[SyntheticCase]:
    return [
        SyntheticCase("unison", "Unison doubling", base_input(["C4", "C4"])),
        SyntheticCase("octave_doubling", "Octave doubling", base_input(["C3", "C4"])),
        SyntheticCase(
            "chromatic_cluster",
            "Chromatic semitone cluster",
            base_input(["C4", "C#4", "D4", "D#4", "E4"]),
        ),
        SyntheticCase(
            "whole_tone_cluster",
            "Whole-tone spaced cluster",
            base_input(["C4", "D4", "E4", "F#4", "G#4"]),
        ),
        SyntheticCase(
            "diatonic_tertian",
            "Diatonic tertian chord",
            base_input(["C4", "E4", "G4"]),
        ),
        SyntheticCase(
            "wide_spaced",
            "Wide-spaced chord",
            base_input(["C3", "G3", "D4", "A4", "E5"]),
        ),
        SyntheticCase(
            "dense_low_register",
            "Dense low-register cluster",
            base_input(["C2", "C#2", "D2", "D#2", "E2"]),
        ),
        SyntheticCase(
            "dense_high_register",
            "Dense high-register cluster",
            base_input(["C6", "C#6", "D6", "D#6", "E6"]),
        ),
        SyntheticCase(
            "same_pitches_different_orchestration",
            "Same pitches, different orchestration",
            base_input(
                ["C4", "E4", "G4"],
                instruments=["flauta", "clarinete", "flauta"],
            ),
        ),
        SyntheticCase(
            "same_orchestration_wide_spread",
            "Same orchestration, wider registral spread",
            base_input(
                ["C3", "E4", "G5"],
                instruments=["flauta", "flauta", "flauta"],
            ),
        ),
        SyntheticCase(
            "same_chord_loud_dynamics",
            "Same chord with louder dynamics",
            base_input(["C4", "E4", "G4"], dynamics=["pp", "mf", "ff"]),
        ),
        SyntheticCase(
            "microtonal_cluster",
            "Microtonal cluster",
            base_input(["C4", "C4+25c", "C4+50c"]),
        ),
        SyntheticCase(
            "large_orchestra_unison",
            "Large orchestra unison",
            base_input(
                ["C4"] * 4,
                instruments=["violino", "viola", "violoncelo", "flauta"],
                num_instruments=[8, 6, 4, 2],
            ),
        ),
        SyntheticCase(
            "sparse_high_texture",
            "Sparse high-register texture",
            base_input(["C6", "E6"], dynamics=["p", "p"]),
        ),
        SyntheticCase(
            "percussion_heavy",
            "Percussion-heavy vertical (nominal pitches)",
            base_input(
                ["C3", "G3", "D4"],
                instruments=["timpanos", "bombo", "pratos"],
                dynamics=["ff", "ff", "ff"],
            ),
        ),
    ]
