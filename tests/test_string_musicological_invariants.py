"""Pitch, dynamic GPR, and data-quality diagnostics for string GPR modules."""

from __future__ import annotations

import importlib
import logging
import math
import statistics
import numpy as np
import pytest
from instrumentos import get_instrument_profile
from instrumentos.pitch_interpolation import resolve_density_from_table
from instrumentos.spectral_lookup import lookup_spectral_density_detailed
from microtonal import note_to_midi_strict
from tests.string_constants import SOURCE_DYNAMICS, STRING_INSTRUMENTS, StringInstrumentSpec

logger = logging.getLogger("test.string.musicological")


def _mod(spec: StringInstrumentSpec):
    return importlib.import_module(f"instrumentos.{spec.module_name}")


def _comfortable_table_pitch(spec: StringInstrumentSpec) -> str:
    mod = _mod(spec)
    profile = get_instrument_profile(spec.registry_ids[0])
    low, high = profile.comfortable_range
    for pitch in sorted(mod.spectral_data, key=note_to_midi_strict):
        midi = float(note_to_midi_strict(pitch))
        if low <= midi <= high:
            return pitch
    for candidate in spec.open_strings:
        if candidate in mod.spectral_data:
            return candidate
    return next(iter(mod.spectral_data))


@pytest.mark.musicological
class TestStringPitchSpellingAndMicrotonal:
    @pytest.mark.parametrize("spec", STRING_INSTRUMENTS, ids=lambda s: s.module_name)
    def test_enharmonic_ascii_unicode_equivalence(self, spec: StringInstrumentSpec):
        mod = _mod(spec)
        table = mod.spectral_data
        if "C#4" in table and "Db4" in table:
            pytest.skip("table contains both spellings for same pitch class")
        anchor = next(p for p in table if "#" in p and p.endswith("4"))
        sharp_pitch = anchor
        flat_pitch = anchor.replace("#", "b").replace("♯", "b")
        if flat_pitch == sharp_pitch:
            pytest.skip("no enharmonic pair in mid register")
        r_sharp = resolve_density_from_table(table, sharp_pitch, "mf", logger=logger)
        r_flat = resolve_density_from_table(table, flat_pitch, "mf", logger=logger)
        if r_sharp.provenance == "exact" and r_flat.provenance == "exact":
            assert r_sharp.value == pytest.approx(r_flat.value, rel=1e-4)

    @pytest.mark.parametrize("spec", STRING_INSTRUMENTS, ids=lambda s: s.module_name)
    def test_microtonal_c4_plus_50c_interpolated_mid_register(self, spec: StringInstrumentSpec):
        mod = _mod(spec)
        if "C4" not in mod.spectral_data or "C#4" not in mod.spectral_data:
            pytest.skip("C4/C#4 anchors unavailable")
        c4 = mod.calcular_densidade("C4", "mf")
        c_sharp = mod.calcular_densidade("C#4", "mf")
        mid = mod.calcular_densidade("C4+50c", "mf")
        assert min(c4, c_sharp) <= mid <= max(c4, c_sharp)
        detail = lookup_spectral_density_detailed(mod.spectral_data, "C4+50c", "mf", logger=logger)
        assert detail.provenance == "interpolated"

    @pytest.mark.parametrize("spec", STRING_INSTRUMENTS, ids=lambda s: s.module_name)
    def test_exact_anchor_precedence_over_interpolation(self, spec: StringInstrumentSpec):
        mod = _mod(spec)
        pitch = mod.spectral_data.keys().__iter__().__next__()
        detail = lookup_spectral_density_detailed(mod.spectral_data, pitch, "mf", logger=logger)
        assert detail.provenance in ("exact", "normalized_exact")

    @pytest.mark.parametrize("spec", STRING_INSTRUMENTS, ids=lambda s: s.module_name)
    def test_octave_safe_no_collapse(self, spec: StringInstrumentSpec):
        mod = _mod(spec)
        notes = sorted(mod.spectral_data, key=note_to_midi_strict)
        low, high = notes[0], notes[-1]
        d_low = mod.calcular_densidade(low, "mf")
        d_high = mod.calcular_densidade(high, "mf")
        assert d_low != pytest.approx(d_high) or low == high


@pytest.mark.musicological
class TestStringCommittedDynamics:
    @pytest.mark.parametrize("spec", STRING_INSTRUMENTS, ids=lambda s: s.module_name)
    def test_no_runtime_gpr_helper(self, spec: StringInstrumentSpec):
        assert not hasattr(_mod(spec), "predict_intermediate_dynamics")

    @pytest.mark.parametrize("spec", STRING_INSTRUMENTS, ids=lambda s: s.module_name)
    def test_anchor_lookups_are_finite(self, spec: StringInstrumentSpec):
        mod = _mod(spec)
        pitch = _comfortable_table_pitch(spec)
        for dyn in ("pp", "mf", "ff"):
            val = mod.calcular_densidade(pitch, dyn)
            assert math.isfinite(val)
            assert val > 0.0

    def test_violin_pipeline_uses_committed_non_anchor(self):
        from config import DYNAMIC_LEVELS
        from core.converters import make_instrument_event
        from core.orchestration import compute_event_one_player_density

        mod = _mod(next(s for s in STRING_INSTRUMENTS if s.module_name == "violin"))
        pitch = _comfortable_table_pitch(
            next(s for s in STRING_INSTRUMENTS if s.module_name == "violin")
        )
        assert mod.INSTRUMENT_SOURCE.dynamic_levels == tuple(DYNAMIC_LEVELS)
        event = make_instrument_event(
            idx=0,
            note=pitch,
            dynamic="p",
            instrument_name="violino",
            player_count=1,
        )
        density = compute_event_one_player_density(event, lambda _: mod)
        assert density == pytest.approx(mod.spectral_data[pitch]["p"])


@pytest.mark.musicological
class TestStringDataQualityDiagnostics:
    """Non-blocking statistical summaries — review candidates, not pass thresholds."""

    @pytest.mark.parametrize("spec", STRING_INSTRUMENTS, ids=lambda s: s.module_name)
    def test_emit_table_quality_summary(self, spec: StringInstrumentSpec, capsys):
        mod = _mod(spec)
        for dyn in SOURCE_DYNAMICS:
            values = [row[dyn] for row in mod.spectral_data.values()]
            adjacent = [
                abs(b - a)
                for a, b in zip(values, values[1:])
            ]
            non_monotonic = sum(
                1
                for row in mod.spectral_data.values()
                if not (row["pp"] <= row["mf"] <= row["ff"])
                and not (row["pp"] >= row["mf"] >= row["ff"])
            )
            summary = {
                "module": spec.module_name,
                "dynamic": dyn,
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "stdev": statistics.pstdev(values),
                "mad": statistics.median([abs(v - statistics.median(values)) for v in values]),
                "max_adjacent_jump": max(adjacent) if adjacent else 0.0,
                "non_monotonic_triplets": non_monotonic,
            }
            print(json_dumps_safe(summary))
            assert summary["count"] == spec.documented_row_count
            assert summary["min"] > 0


def json_dumps_safe(obj: dict) -> str:
    import json

    return json.dumps(obj, sort_keys=True)
