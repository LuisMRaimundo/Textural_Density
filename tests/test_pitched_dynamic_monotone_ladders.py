"""Committed pitched CDM ladders: completeness + data-faithful hygiene.

Since 2026-08 every pitched table-backed module ships **all 10 dynamic levels
per pitch** committed from the Dynamics_predicter ``Results`` sheet (no runtime
GPR / tail extrapolation; unpitched percussion keeps its own DYNAMIC_CDM).

Measured anchors (pp/mf/ff) are committed verbatim, so ladders are **not**
required to be globally soft→loud monotone — real measurements are sometimes
non-monotone (e.g. violin G7 mf > f). Instead we enforce the predictor's
hygiene contract:

1. completeness — every note has all 10 finite, positive dynamic levels;
2. interiors stay within their measured segment (p, mp within [pp, mf];
   f within [mf, ff]);
3. outer levels do not zigzag (pppp→ppp→pp and ff→fff→ffff are each
   one-directional);
4. outer excursions are bounded by the adjacent measured segment's log-step
   (geometric taper: 1 step for the first outer, 1.8 steps for the second,
   plus a small enrichment allowance for near-flat segments).
"""

from __future__ import annotations

import importlib
import math

import pytest

from config import DYNAMIC_LEVELS
from instrumentos.registry import list_profiles
from microtonal import midi_to_note_name, note_to_midi_strict

REL = 1e-9
INTERIOR_REL_TOL = 1e-6
# Empirical headroom over the predictor's tapered-outer geometry (see probe:
# worst observed excesses were 0.047 and 0.085 in log space).
OUTER1_LOG_ALLOWANCE = 0.10
OUTER2_LOG_ALLOWANCE = 0.15


def _pitched_modules() -> list[str]:
    names: list[str] = []
    seen: set[str] = set()
    for p in list_profiles():
        if p.module_name and not p.unpitched and p.module_name not in seen:
            seen.add(p.module_name)
            names.append(p.module_name)
    return names


def _sample_pitches(spectral: dict[str, dict[str, float]], n: int = 3) -> list[str]:
    notes = sorted(spectral.keys(), key=lambda k: note_to_midi_strict(k))
    if len(notes) <= n:
        return notes
    idxs = [0, len(notes) // 2, len(notes) - 1]
    return [notes[i] for i in idxs]


def _one_directional(seq: list[float]) -> bool:
    inc = all(b >= a * (1 - REL) for a, b in zip(seq, seq[1:]))
    dec = all(b <= a * (1 + REL) for a, b in zip(seq, seq[1:]))
    return inc or dec


@pytest.mark.parametrize("module_name", _pitched_modules())
def test_pitched_module_full_ladder_committed(module_name: str):
    """All 10 dynamic levels committed per pitch — no runtime extrapolation."""
    mod = importlib.import_module(f"instrumentos.{module_name}")
    spectral = mod.spectral_data
    assert spectral, f"{module_name}: empty spectral_data"
    levels = tuple(DYNAMIC_LEVELS)
    assert mod.INSTRUMENT_SOURCE.dynamic_levels == levels
    for note, row in spectral.items():
        missing = [d for d in levels if d not in row]
        assert not missing, f"{module_name} {note}: missing levels {missing}"
        for d in levels:
            x = float(row[d])
            assert math.isfinite(x) and x > 0.0, f"{module_name} {note}: {d}={x}"


@pytest.mark.parametrize("module_name", _pitched_modules())
def test_pitched_module_ladder_hygiene(module_name: str):
    """Interiors within measured segments; outers tapered, no zigzag."""
    mod = importlib.import_module(f"instrumentos.{module_name}")
    for note, row in mod.spectral_data.items():
        v = {d: float(row[d]) for d in DYNAMIC_LEVELS}
        pp, mf, ff = v["pp"], v["mf"], v["ff"]

        # interiors stay inside their measured segment
        lo, hi = min(pp, mf), max(pp, mf)
        for d in ("p", "mp"):
            over = max(lo - v[d], v[d] - hi) / max(hi, 1e-12)
            assert over <= INTERIOR_REL_TOL, (
                f"{module_name} {note}: {d}={v[d]} outside measured segment [{lo}, {hi}]"
            )
        lo, hi = min(mf, ff), max(mf, ff)
        over = max(lo - v["f"], v["f"] - hi) / max(hi, 1e-12)
        assert over <= INTERIOR_REL_TOL, (
            f"{module_name} {note}: f={v['f']} outside measured segment [{lo}, {hi}]"
        )

        # outer levels do not zigzag
        assert _one_directional([v["pppp"], v["ppp"], v["pp"]]), (
            f"{module_name} {note}: soft outers zigzag {[v['pppp'], v['ppp'], v['pp']]}"
        )
        assert _one_directional([v["ff"], v["fff"], v["ffff"]]), (
            f"{module_name} {note}: loud outers zigzag {[v['ff'], v['fff'], v['ffff']]}"
        )

        # outer excursions bounded by the adjacent measured log-step
        seg_soft = abs(math.log(mf / pp))
        seg_loud = abs(math.log(ff / mf))
        checks = (
            ("ppp", abs(math.log(v["ppp"] / pp)), seg_soft + OUTER1_LOG_ALLOWANCE),
            ("pppp", abs(math.log(v["pppp"] / pp)), 1.8 * seg_soft + OUTER2_LOG_ALLOWANCE),
            ("fff", abs(math.log(v["fff"] / ff)), seg_loud + OUTER1_LOG_ALLOWANCE),
            ("ffff", abs(math.log(v["ffff"] / ff)), 1.8 * seg_loud + OUTER2_LOG_ALLOWANCE),
        )
        for d, excursion, bound in checks:
            assert excursion <= bound, (
                f"{module_name} {note}: {d} log-excursion {excursion:.4f} exceeds bound {bound:.4f}"
            )


def test_registry_pitched_modules_cover_three_sample_notes():
    """Sanity: sample pitch helper returns MIDI-ordered keys."""
    mod = importlib.import_module("instrumentos.violin")
    samples = _sample_pitches(mod.spectral_data, 3)
    assert len(samples) == 3
    midis = [note_to_midi_strict(n) for n in samples]
    assert midis == sorted(midis)
    # Midpoint sample is a real table key
    assert samples[1] in mod.spectral_data
    assert midi_to_note_name(float(midis[0]))  # import path stays warm
