"""
Near-unison semantics — documentation-to-code reconciliation
(5.0.0-strict-symbolic).

Guards the §B statement that the **core distinct-bin path applies no
minimum-interval floor**: sub-cent intervals are treated as real distances,
and genuine float-noise unisons are absorbed *upstream* by the exact-MIDI
pitch aggregation tolerance (1e-6) so duplicate pitches never form a pair.

The legacy 0.25-semitone floor lives only in
``densidade_intervalar.calculate_interval_density`` and is not reachable from
``core.calculate_metrics``; these tests exercise the core distinct-bin path
(``core.pitch_aggregation`` + ``core.pitch_structure``) directly.

lambda is read from config via ``load_calibrated_parameters`` (no hardcoding).
"""

from __future__ import annotations

import math

import pytest

from core.pitch_aggregation import DEFAULT_PITCH_TOLERANCE, aggregate_events_by_pitch
from core.pitch_structure import (
    compute_interval_compactness_distinct,
    compute_pitch_structure_density,
)
from densidade_intervalar import load_calibrated_parameters
from microtonal import format_cents_suffix, note_to_midi

LAMB = load_calibrated_parameters()


def _aggregate(notes):
    return aggregate_events_by_pitch(notes)


def _interval_sum_raw(notes):
    agg = _aggregate(notes)
    raw, _reported = compute_interval_compactness_distinct(agg, lamb=LAMB)
    return agg, raw


def test_subcent_interval_no_floor():
    """(a) [C4, C4+0.5c]: two distinct bins; S == exp(-lambda * 2 * 0.005), unclamped.

    A 0.005-semitone gap must be treated as a real interval. If the legacy
    0.25-semitone floor were reached, S would collapse to exp(-lambda * 0.5),
    which this exact-value assertion rules out.
    """
    notes = ["C4", "C4+0.5c"]
    agg, raw = _interval_sum_raw(notes)

    assert agg.distinct_pitch_count == 2

    delta_semitones = 0.005  # 0.5 cents
    expected_S = math.exp(-LAMB * 2.0 * delta_semitones)
    assert raw == pytest.approx(expected_S, abs=1e-9)

    # Sanity: this is far from the floored value, confirming no clamp.
    floored_S = math.exp(-LAMB * 2.0 * 0.25)
    assert not math.isclose(raw, floored_S, abs_tol=1e-6)


def test_exact_unison_zero_structure():
    """(b) [C4, C4]: one bin after aggregation; S == 0 and PSD == 0."""
    notes = ["C4", "C4"]
    agg, raw = _interval_sum_raw(notes)

    assert agg.distinct_pitch_count == 1
    assert raw == 0.0

    psd = compute_pitch_structure_density(
        interval_sum_raw=raw,
        aggregation=agg,
        spectral_entropy=0.0,
        harmonic_ratio=0.0,
    )
    assert psd == 0.0


def test_below_tolerance_merges_to_one_bin():
    """(c) [C4, C4+1e-7c]-equivalent (below the 1e-6 MIDI merge tolerance).

    A 1e-7-cent offset is ~1e-9 in MIDI, well under the aggregation tolerance,
    so the two events merge into a single bin and contribute no interval pair.
    """
    near = "C4" + format_cents_suffix(1e-7)
    midi_gap = abs(note_to_midi(near, strict=True) - note_to_midi("C4", strict=True))
    assert midi_gap < DEFAULT_PITCH_TOLERANCE  # precondition: below merge tolerance

    agg, raw = _interval_sum_raw(["C4", near])
    assert agg.distinct_pitch_count == 1
    assert raw == 0.0
