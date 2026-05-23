"""Tests for core/event_density.py extraction."""

from __future__ import annotations

from core.converters import legacy_input_to_vertical_slice
from core.event_density import compute_event_density


def test_event_density_matches_subindices_count():
    inp = {
        "notes": ["C4", "E4", "G4", "C5"],
        "dynamics": ["mf"] * 4,
        "instruments": ["flauta"] * 4,
        "num_instruments": [1, 2, 1, 1],
    }
    vs = legacy_input_to_vertical_slice(inp)
    ed = compute_event_density(vs)
    assert ed["event_count"] == 4
    assert ed["player_weighted_count"] == 5.0
    assert ed["source_type"] == "score_derived"
    assert ed["validation_status"] == "verified_only"
