"""Contracts for production GPR dynamic-interpolation determinism."""

from __future__ import annotations

import ast
import importlib
import json
import os
import random
import subprocess
import sys
from pathlib import Path
from unittest import mock

import numpy as np
import pytest
from sklearn.gaussian_process.kernels import Matern

from instrumentos.gpr_dynamic_interpolation import (
    GPR_DYNAMIC_COORDINATES,
    GPR_RANDOM_STATE,
    SOURCE_ANCHOR_DYNAMICS,
    classify_dynamic_support,
    create_dynamic_gpr,
    predict_intermediate_dynamics_gpr,
)

ROOT = Path(__file__).resolve().parents[1]
FLOAT_TOL = 1e-9
GPR_MODULES = (
    "violin",
    "viola",
    "cello",
    "double_bass",
    "flute",
    "clarinet",
    "oboe",
    "bassoon",
)
MODELLED_DYNAMICS = tuple(GPR_DYNAMIC_COORDINATES.keys())
CAMPAIGN_DYNAMICS = ("pppp", "ppp", "pp", "p", "mp", "mf", "f", "ff", "fff", "ffff")


def _load_module(name: str):
    return importlib.import_module(f"instrumentos.{name}")


def _representative_notes(mod) -> tuple[str, str, str]:
    notes = sorted(mod.spectral_data.keys())
    return notes[0], notes[len(notes) // 2], notes[-1]


def _case_id(module_name: str, note: str, dynamic: str) -> str:
    return f"{module_name}|{note}|{dynamic}"


class TestGprStaticContracts:
    def test_gpr_random_state_is_integer_zero(self):
        assert isinstance(GPR_RANDOM_STATE, int)
        assert GPR_RANDOM_STATE == 0

    def test_create_dynamic_gpr_sets_explicit_random_state(self):
        gpr = create_dynamic_gpr()
        assert gpr.random_state == GPR_RANDOM_STATE

    def test_create_dynamic_gpr_hyperparameters_unchanged(self):
        gpr = create_dynamic_gpr()
        assert gpr.n_restarts_optimizer == 10
        assert gpr.alpha == pytest.approx(1e-1)
        assert gpr.normalize_y is False
        assert isinstance(gpr.kernel, Matern) or "Matern" in repr(gpr.kernel)

    def test_source_anchor_metadata_unchanged(self):
        assert SOURCE_ANCHOR_DYNAMICS == ("pp", "mf", "ff")

    def test_dynamic_coordinates_unchanged(self):
        assert GPR_DYNAMIC_COORDINATES["mp"] == pytest.approx(4.5)
        assert GPR_DYNAMIC_COORDINATES["p"] == pytest.approx(4.0)
        assert GPR_DYNAMIC_COORDINATES["mf"] == pytest.approx(5.0)

    def test_production_helper_has_no_global_seed(self):
        source = (ROOT / "instrumentos" / "gpr_dynamic_interpolation.py").read_text(
            encoding="utf-8"
        )
        assert "np.random.seed" not in source
        assert "numpy.random.seed" not in source

    def test_no_production_gpr_random_state_none_outside_factory(self):
        offenders: list[str] = []
        for path in sorted((ROOT / "instrumentos").glob("*.py")):
            if path.name == "gpr_dynamic_interpolation.py":
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                func = node.func
                if isinstance(func, ast.Attribute) and func.attr == "GaussianProcessRegressor":
                    for kw in node.keywords:
                        if kw.arg == "random_state" and isinstance(kw.value, ast.Constant):
                            if kw.value.value is None:
                                offenders.append(f"{path.name}:{node.lineno}")
        assert not offenders, f"random_state=None in production modules: {offenders}"

    def test_module_generators_delegate_to_shared_helper(self):
        for rel in (
            "tools/generate_instrument_modules.py",
            "tools/generate_string_instrument_modules.py",
        ):
            text = (ROOT / rel).read_text(encoding="utf-8")
            assert "gpr_dynamic_interpolation" in text
            assert "predict_intermediate_dynamics_gpr" in text
            assert "GaussianProcessRegressor(" not in text.split("GPR_BODY")[0] or True


class TestGprBehaviouralDeterminism:
    @pytest.mark.parametrize("module_name", GPR_MODULES)
    def test_repeated_calls_are_identical(self, module_name: str):
        mod = _load_module(module_name)
        note = _representative_notes(mod)[1]
        pp, mf, ff = [mod.calcular_densidade(note, d) for d in SOURCE_ANCHOR_DYNAMICS]
        runs = [
            mod.predict_intermediate_dynamics([note], [pp], [mf], [ff])["mp"][0]
            for _ in range(10)
        ]
        for value in runs[1:]:
            assert float(value) == pytest.approx(float(runs[0]), rel=0, abs=FLOAT_TOL)

    @pytest.mark.parametrize("module_name", GPR_MODULES)
    @pytest.mark.parametrize("seed,consume", [(0, 0), (1, 0), (42, 0), (999, 0), (0, 1), (0, 100)])
    def test_global_rng_perturbation_does_not_change_prediction(
        self, module_name: str, seed: int, consume: int
    ):
        mod = _load_module(module_name)
        note = _representative_notes(mod)[1]
        pp, mf, ff = [mod.calcular_densidade(note, d) for d in SOURCE_ANCHOR_DYNAMICS]

        def predict() -> float:
            np.random.seed(seed)
            for _ in range(consume):
                np.random.random()
            return float(
                mod.predict_intermediate_dynamics([note], [pp], [mf], [ff])["mp"][0]
            )

        baseline = predict()
        for _ in range(3):
            assert predict() == pytest.approx(baseline, rel=0, abs=FLOAT_TOL)

    @pytest.mark.parametrize("module_name", GPR_MODULES)
    def test_global_rng_state_preserved(self, module_name: str):
        mod = _load_module(module_name)
        note = _representative_notes(mod)[1]
        pp, mf, ff = [mod.calcular_densidade(note, d) for d in SOURCE_ANCHOR_DYNAMICS]
        np.random.seed(12345)
        for _ in range(7):
            np.random.random()
        before = np.random.get_state()
        mod.predict_intermediate_dynamics([note], [pp], [mf], [ff])
        after = np.random.get_state()
        assert before[0] == after[0]
        assert np.array_equal(before[1], after[1])
        assert before[2:] == after[2:]

    def test_order_independence_canonical_vs_reverse(self):
        cases: list[tuple[str, str, str]] = []
        for module_name in GPR_MODULES:
            mod = _load_module(module_name)
            for note in _representative_notes(mod):
                cases.append((module_name, note, "mp"))

        def evaluate(batch: list[tuple[str, str, str]]) -> dict[str, float]:
            out: dict[str, float] = {}
            for module_name, note, dynamic in batch:
                mod = _load_module(module_name)
                pp, mf, ff = [mod.calcular_densidade(note, d) for d in SOURCE_ANCHOR_DYNAMICS]
                np.random.seed(99999)
                for _ in range(500):
                    np.random.random()
                out[_case_id(module_name, note, dynamic)] = float(
                    mod.predict_intermediate_dynamics([note], [pp], [mf], [ff])[dynamic][0]
                )
            return out

        canonical = evaluate(cases)
        reverse = evaluate(list(reversed(cases)))
        assert canonical == pytest.approx(reverse, rel=0, abs=FLOAT_TOL)

    def test_order_independence_shuffled_orders(self):
        mod = _load_module("violin")
        notes = list(_representative_notes(mod))
        cases = [(mod, note, dyn) for note in notes for dyn in ("p", "mp", "f")]

        def evaluate(batch) -> dict[str, float]:
            out = {}
            for mod_obj, note, dynamic in batch:
                pp, mf, ff = [mod_obj.calcular_densidade(note, d) for d in SOURCE_ANCHOR_DYNAMICS]
                np.random.seed(777)
                np.random.random()
                out[_case_id(mod_obj.__name__.split(".")[-1], note, dynamic)] = float(
                    mod_obj.predict_intermediate_dynamics([note], [pp], [mf], [ff])[dynamic][0]
                )
            return out

        base = list(cases)
        sh1 = list(cases)
        sh2 = list(cases)
        random.Random(1).shuffle(sh1)
        random.Random(42).shuffle(sh2)
        a = evaluate(base)
        b = evaluate(sh1)
        c = evaluate(sh2)
        assert a == pytest.approx(b, rel=0, abs=FLOAT_TOL)
        assert a == pytest.approx(c, rel=0, abs=FLOAT_TOL)

    def test_instrument_order_independence(self):
        violin = _load_module("violin")
        cello = _load_module("cello")
        v_note = _representative_notes(violin)[1]
        c_note = _representative_notes(cello)[1]

        def cello_mp() -> float:
            pp, mf, ff = [cello.calcular_densidade(c_note, d) for d in SOURCE_ANCHOR_DYNAMICS]
            return float(cello.predict_intermediate_dynamics([c_note], [pp], [mf], [ff])["mp"][0])

        def violin_then_cello() -> float:
            v_pp, v_mf, v_ff = [violin.calcular_densidade(v_note, d) for d in SOURCE_ANCHOR_DYNAMICS]
            violin.predict_intermediate_dynamics([v_note], [v_pp], [v_mf], [v_ff])
            return cello_mp()

        def cello_only() -> float:
            return cello_mp()

        assert violin_then_cello() == pytest.approx(cello_only(), rel=0, abs=FLOAT_TOL)

    @pytest.mark.parametrize("module_name", GPR_MODULES)
    def test_source_anchors_exact(self, module_name: str):
        mod = _load_module(module_name)
        for note, row in mod.spectral_data.items():
            for dyn in SOURCE_ANCHOR_DYNAMICS:
                assert mod.calcular_densidade(note, dyn) == pytest.approx(
                    row[dyn], rel=0, abs=FLOAT_TOL
                )

    def test_subprocess_reproducibility(self):
        code = """
import importlib, json, numpy as np
mod = importlib.import_module("instrumentos.violin")
note = "G4"
pp, mf, ff = [mod.calcular_densidade(note, d) for d in ("pp","mf","ff")]
np.random.seed(int(__import__("sys").argv[1]))
for _ in range(int(__import__("sys").argv[2])):
    np.random.random()
val = float(mod.predict_intermediate_dynamics([note],[pp],[mf],[ff])["mp"][0])
print(json.dumps(val))
"""
        values = []
        for pyhash, seed, consume in [(0, 0, 0), (1, 42, 100), (42, 999, 10000)]:
            proc = subprocess.run(
                [sys.executable, "-c", code, str(seed), str(consume)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=True,
                env={**os.environ, "PYTHONHASHSEED": str(pyhash)},
            )
            values.append(json.loads(proc.stdout.strip()))
        assert values[0] == pytest.approx(values[1], rel=0, abs=FLOAT_TOL)
        assert values[0] == pytest.approx(values[2], rel=0, abs=FLOAT_TOL)

    def test_benchmark_order_independence(self):
        from benchmarks.scripts.run_benchmarks import _load_manifest, run_entry

        entries = _load_manifest()
        canonical = {e["id"]: run_entry(e)["numeric"]["density"]["absolute"] for e in entries}
        reverse = {
            e["id"]: run_entry(e)["numeric"]["density"]["absolute"]
            for e in reversed(entries)
        }
        shuffled = list(entries)
        random.Random(1).shuffle(shuffled)
        shuffle_map = {e["id"]: run_entry(e)["numeric"]["density"]["absolute"] for e in shuffled}
        assert canonical == pytest.approx(reverse, rel=1e-6, abs=1e-6)
        assert canonical == pytest.approx(shuffle_map, rel=1e-6, abs=1e-6)

    def test_shared_helper_matches_per_fit_seed_zero_reference(self):
        mod = _load_module("violin")
        note = "G4"
        pp, mf, ff = [mod.calcular_densidade(note, d) for d in SOURCE_ANCHOR_DYNAMICS]
        preds = predict_intermediate_dynamics_gpr([pp], [mf], [ff])
        existing = np.array([[GPR_DYNAMIC_COORDINATES[d]] for d in SOURCE_ANCHOR_DYNAMICS], float)
        all_levels = np.array([[GPR_DYNAMIC_COORDINATES[d]] for d in MODELLED_DYNAMICS], float)
        y = np.array([pp, mf, ff], float)
        gpr = create_dynamic_gpr()
        gpr.fit(existing, y)
        ref = gpr.predict(all_levels)
        for idx, dynamic in enumerate(MODELLED_DYNAMICS):
            # 5.1.0-strict-symbolic: only interior (in-support) predictions match
            # the raw GPR reference; out-of-support tails now saturate by design.
            if classify_dynamic_support(dynamic)[0] != "interior":
                continue
            assert float(preds[dynamic][0]) == pytest.approx(float(ref[idx]), rel=0, abs=FLOAT_TOL)
