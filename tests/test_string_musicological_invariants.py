"""Pitch, dynamic GPR, and data-quality diagnostics for string GPR modules."""

from __future__ import annotations

import importlib
import logging
import math
import statistics
from unittest import mock

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
class TestStringGprIntermediateDynamics:
    @pytest.mark.parametrize("spec", STRING_INSTRUMENTS, ids=lambda s: s.module_name)
    def test_predict_intermediate_dynamics_contract(self, spec: StringInstrumentSpec):
        mod = _mod(spec)
        pitch = _comfortable_table_pitch(spec)
        pp = mod.calcular_densidade(pitch, "pp")
        mf = mod.calcular_densidade(pitch, "mf")
        ff = mod.calcular_densidade(pitch, "ff")
        pp_in = [pp]
        mf_in = [mf]
        ff_in = [ff]
        preds = mod.predict_intermediate_dynamics([pitch], pp_in, mf_in, ff_in)
        expected_labels = ("pppp", "ppp", "pp", "p", "mp", "mf", "f", "ff", "fff", "ffff")
        assert tuple(preds.keys()) == expected_labels
        for label in expected_labels:
            arr = preds[label]
            assert len(arr) == 1
            assert math.isfinite(float(arr[0]))
        assert pp_in == [pp]
        assert mf_in == [mf]
        assert ff_in == [ff]

    @pytest.mark.parametrize("spec", STRING_INSTRUMENTS, ids=lambda s: s.module_name)
    def test_gpr_repeated_calls_are_deterministic(self, spec: StringInstrumentSpec):
        np.random.seed(0)
        mod = _mod(spec)
        pitch = _comfortable_table_pitch(spec)
        pp = mod.calcular_densidade(pitch, "pp")
        mf = mod.calcular_densidade(pitch, "mf")
        ff = mod.calcular_densidade(pitch, "ff")
        runs = [
            mod.predict_intermediate_dynamics([pitch], [pp], [mf], [ff])["p"][0]
            for _ in range(3)
        ]
        assert runs[0] == pytest.approx(runs[1])
        assert runs[1] == pytest.approx(runs[2])

    @pytest.mark.parametrize("spec", STRING_INSTRUMENTS, ids=lambda s: s.module_name)
    def test_empty_training_data_returns_zeros(self, spec: StringInstrumentSpec):
        mod = _mod(spec)
        preds = mod.predict_intermediate_dynamics([], [], [], [])
        for values in preds.values():
            assert len(values) == 0

    @pytest.mark.parametrize("spec", STRING_INSTRUMENTS, ids=lambda s: s.module_name)
    def test_pipeline_uses_gpr_for_intermediate_dynamic(self, spec: StringInstrumentSpec):
        from core.converters import make_instrument_event
        from core.orchestration import compute_event_one_player_density

        mod = _mod(spec)
        pitch = _comfortable_table_pitch(spec)
        event = make_instrument_event(
            idx=0,
            note=pitch,
            dynamic="p",
            instrument_name=spec.registry_ids[0],
            player_count=1,
        )

        def _loader(_name: str):
            return mod

        with mock.patch.object(
            mod, "predict_intermediate_dynamics", wraps=mod.predict_intermediate_dynamics
        ) as gpr_mock:
            density = compute_event_one_player_density(event, _loader)
            gpr_mock.assert_called_once()
        assert math.isfinite(density)
        assert density > 0.0


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
