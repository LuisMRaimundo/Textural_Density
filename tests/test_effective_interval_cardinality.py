"""Effective interval cardinality (n_eff − 1) — T1–T7."""

from __future__ import annotations

import math
import random

import pytest

from core.pipeline import calculate_metrics
from core.pitch_structure import (
    calculate_interval_density_from_distinct_midis,
    effective_interval_cardinality,
)
from densidade_intervalar import load_calibrated_parameters
from microtonal import midi_to_note_name, note_to_midi_strict


def _dv_from_midis(midis: list[float]) -> float:
    distinct = sorted(set(float(m) for m in midis))
    raw = calculate_interval_density_from_distinct_midis(distinct)
    return effective_interval_cardinality(raw, len(distinct))


def _metrics(notes, instruments=None, dynamics=None, qty=None):
    n = len(notes)
    payload = {
        "notes": notes,
        "instruments": instruments or ["flauta"] * n,
        "dynamics": dynamics or ["mf"] * n,
        "num_instruments": qty or [1] * n,
        "weight_factor": 0.5,
    }
    resultados, _, _ = calculate_metrics(payload)
    return resultados["density"]


def test_t1_adding_distinct_pitch_strictly_increases_dv():
    rng = random.Random(20260918)
    for _ in range(200):
        n = rng.randint(1, 12)
        midis = []
        while len(midis) < n:
            m = rng.uniform(48.0, 84.0)
            if rng.random() < 0.25:
                m = round(m * 2.0) / 2.0  # include quarter-tones
            if all(abs(m - existing) > 1e-9 for existing in midis):
                midis.append(m)
        extra = midis[0] + rng.choice([0.5, 1.0, 2.0, 3.5, 7.0, 12.0])
        while any(abs(extra - existing) < 1e-9 for existing in midis):
            extra += 0.5
        before = _dv_from_midis(midis)
        after = _dv_from_midis(midis + [extra])
        if n < 2:
            assert before == 0.0
            assert after > 0.0
        else:
            assert after > before + 1e-15


def test_t2_compactness_scale_intervals():
    for n, step in ((3, 2.0), (4, 2.0), (6, 1.0)):
        base = [60.0 + i * step for i in range(n)]
        tighter = [60.0 + i * (step * 0.5) for i in range(n)]
        wider = [60.0 + i * (step * 2.0) for i in range(n)]
        dv_base = _dv_from_midis(base)
        assert _dv_from_midis(tighter) > dv_base
        assert _dv_from_midis(wider) < dv_base


def test_t3_singleton_zero_and_unison_invariance():
    assert _dv_from_midis([60.0]) == 0.0
    assert _metrics(["C4"])["interval"] == 0.0
    one = _metrics(["C4"], qty=[1])
    four = _metrics(["C4"], qty=[4])
    two_inst = _metrics(["C4", "C4"], instruments=["flauta", "clarinete"], qty=[1, 1])
    assert one["interval"] == pytest.approx(0.0)
    assert four["interval"] == pytest.approx(one["interval"])
    assert two_inst["interval"] == pytest.approx(one["interval"])
    triad = _metrics(["C4", "E4", "G4"])
    doubled = _metrics(["C4", "C4", "E4", "G4"], qty=[1, 3, 1, 1])
    assert doubled["interval"] == pytest.approx(triad["interval"], abs=1e-12)


def test_t4_adjacent_cluster_approaches_n_minus_1():
    for n in (3, 6, 12):
        midis = [60.0 + i * 0.001 for i in range(n)]
        dv = _dv_from_midis(midis)
        assert dv == pytest.approx(n - 1, abs=1e-2)


def test_t5_reference_values_lambda_005():
    assert float(load_calibrated_parameters()) == pytest.approx(0.05, abs=1e-15)
    chromatic = ["C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", "B4"]
    expected = {2: 0.94, 3: 1.85, 4: 2.73, 6: 4.42, 12: 8.92}
    for n, target in expected.items():
        dv = _metrics(chromatic[:n])["interval"]
        assert dv == pytest.approx(target, abs=0.01), f"n={n} got {dv}"

    octaves = [midi_to_note_name(note_to_midi_strict("C2") + 12 * i) for i in range(6)]
    assert _metrics(octaves, instruments=["piano"] * 6)["interval"] == pytest.approx(
        1.55, abs=0.01
    )

    dyad = _metrics(["C4", "C#4"])["interval"]
    far = _metrics(["C4", "C#4", "C8"], instruments=["piano"] * 3)["interval"]
    assert dyad == pytest.approx(0.94, abs=0.01)
    assert far == pytest.approx(0.95, abs=0.01)
    assert far >= dyad


def test_t6_production_total_and_weighted_monotone_on_added_pitch():
    rng = random.Random(20260918)
    instruments = ["flauta", "oboe", "clarinete", "violino", "trompete"]
    dynamics = ["pp", "mf", "ff"]
    failures = []
    for _ in range(40):
        n = rng.randint(1, 6)
        inst = rng.choice(instruments)
        dyn = rng.choice(dynamics)
        midis = []
        while len(midis) < n:
            m = float(rng.randint(60, 72))
            if m not in midis:
                midis.append(m)
        extra = midis[-1] + rng.choice([1.0, 2.0, 3.0, 5.0])
        while extra in midis or extra > 84:
            extra = midis[0] + rng.choice([1.0, 2.0, 4.0])
        notes_a = [midi_to_note_name(m) for m in midis]
        notes_b = notes_a + [midi_to_note_name(extra)]
        a = _metrics(notes_a, instruments=[inst] * len(notes_a), dynamics=[dyn] * len(notes_a))
        b = _metrics(notes_b, instruments=[inst] * len(notes_b), dynamics=[dyn] * len(notes_b))
        if b["interval"] <= a["interval"] + 1e-15 and len(notes_a) >= 1:
            failures.append(("interval", notes_a, notes_b, inst, dyn, a, b))
        if b["weighted"] < a["weighted"] - 1e-12:
            failures.append(("weighted", notes_a, notes_b, inst, dyn, a, b))
        if b["total"] < a["total"] - 1e-12:
            failures.append(("total", notes_a, notes_b, inst, dyn, a, b))
    assert not failures, failures[:3]


def test_t7_violin_spacing_order():
    def four(notes):
        return _metrics(notes, instruments=["violino"] * 4)

    cluster = four(["C4", "C#4", "D4", "D#4"])
    thirds = four(["C4", "E4", "G#4", "C5"])
    fifths = four(["C4", "G4", "D5", "A5"])
    octaves = four(["G3", "G4", "G5", "G6"])
    assert cluster["total"] > thirds["total"] > fifths["total"]
    print(
        "T7 totals:",
        {
            "cluster": cluster["total"],
            "thirds": thirds["total"],
            "fifths": fifths["total"],
            "octaves_G3_G6": octaves["total"],
        },
    )
