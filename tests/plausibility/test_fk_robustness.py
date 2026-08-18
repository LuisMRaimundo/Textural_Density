"""F-K — Robustness and serialisation (HARD)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.pipeline import calculate_metrics
from error_handler import InputError
from tests.plausibility.conftest import record_hard
from tests.plausibility.helpers import REPO_ROOT, assert_jsonable, slice_input


API_KEYS = (
    "mode",
    "normalization_ref",
    "weight_factor",
    "formula",
    "use_log_compression",
    "d_blend",
    "blend_term_contributions",
)


class TestFKRobustness:
    def test_empty_input_documented_error(self):
        """HARD: empty input raises a documented error."""
        with pytest.raises((InputError, ValueError, KeyError)):
            calculate_metrics({"notes": [], "dynamics": [], "instruments": [], "num_instruments": []})
        record_hard(family="F-K", test_id="FK.empty")

    def test_one_note_finite_json(self):
        """HARD: one note — finite outputs; JSON allow_nan=False."""
        r, _, _ = calculate_metrics(slice_input(["A4"], instruments="flauta"))
        text = assert_jsonable(r, label="FK.one")
        assert "NaN" not in text
        record_hard(family="F-K", test_id="FK.one", total=r["density"]["total"])

    def test_200_note_cluster(self):
        """HARD: 200-note cluster completes with finite total."""
        from microtonal import midi_to_note_name

        notes = [midi_to_note_name(float(55 + (i % 37))) for i in range(200)]  # G3–G6
        inst = ["violino"] * 200
        r, _, _ = calculate_metrics(slice_input(notes, instruments=inst, dynamics="mf"))
        assert_jsonable(r, label="FK.200")
        assert r["density"]["total"] == r["density"]["total"]  # not NaN
        record_hard(family="F-K", test_id="FK.200", total=r["density"]["total"], n=200)

    def test_extreme_dynamics_and_mixed(self):
        """HARD: extreme dynamics and mixed pitched/unpitched stay finite."""
        r, _, _ = calculate_metrics(
            {
                "notes": ["C4", "G4", "C4", "E2"],
                "dynamics": ["pppp", "ffff", "mf", "ff"],
                "instruments": ["flauta", "trompete", "pratos", "trombone"],
                "num_instruments": [1, 1, 1, 1],
            }
        )
        assert_jsonable(r, label="FK.mixed")
        record_hard(family="F-K", test_id="FK.mixed", total=r["density"]["total"])

    def test_determinism(self):
        """HARD: two runs on identical input are byte-identical after JSON serialisation."""
        payload = slice_input(["C4", "E4", "G4"], instruments="clarinete")
        a, _, _ = calculate_metrics(payload)
        b, _, _ = calculate_metrics(payload)
        sa = json.dumps(a, allow_nan=False, sort_keys=True, default=lambda o: o.item() if hasattr(o, "item") else str(o))
        sb = json.dumps(b, allow_nan=False, sort_keys=True, default=lambda o: o.item() if hasattr(o, "item") else str(o))
        assert sa == sb
        record_hard(family="F-K", test_id="FK.determinism")

    def test_composite_meta_keys_match_api(self):
        """HARD: composite_meta keys match docs/API.md (mode, REF, weight_factor, formula, …)."""
        r, _, _ = calculate_metrics(slice_input(["C4", "G4"], instruments="oboe"))
        meta = r["composite_meta"]
        for key in API_KEYS:
            assert key in meta, key
        api = (REPO_ROOT / "docs" / "API.md").read_text(encoding="utf-8")
        for key in API_KEYS:
            assert key in api
        contrib = meta["blend_term_contributions"]
        for key in ("instrument_term", "interval_term", "instrument_to_interval_ratio"):
            assert key in contrib
        record_hard(family="F-K", test_id="FK.composite_meta", keys=list(meta))
