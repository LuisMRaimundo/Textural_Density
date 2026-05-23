"""
Aggregate simultaneous events by exact MIDI pitch bin.

Exact unison doublings merge into one bin; microtonally distinct pitches remain separate.
Orchestral/event mass uses raw events; pitch-structural metrics use aggregated bins.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from microtonal import note_to_midi

DEFAULT_PITCH_TOLERANCE = 1e-6


@dataclass(frozen=True)
class PitchBin:
    """One distinct pitch bin after aggregation."""

    midi: float
    event_count: int
    total_weight: float
    total_player_count: int
    original_event_indices: tuple[int, ...]
    representative_note: str
    dynamics: tuple[str, ...]
    instruments: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "midi": float(self.midi),
            "event_count": int(self.event_count),
            "total_weight": float(self.total_weight),
            "total_player_count": int(self.total_player_count),
            "original_event_indices": list(self.original_event_indices),
            "representative_note": self.representative_note,
            "dynamics": list(self.dynamics),
            "instruments": list(self.instruments),
        }


@dataclass(frozen=True)
class PitchAggregationResult:
    """Summary of pitch aggregation for a vertical slice."""

    event_count: int
    distinct_pitch_count: int
    doubling_count: int
    pitch_bins: tuple[PitchBin, ...]
    pitch_aggregation_tolerance: float
    distinct_pitch_ratio: float
    pitch_differentiation_ratio: float
    interval_pairs_count_distinct: int
    total_player_count: int

    @property
    def player_count(self) -> int:
        """Total players (sum of Qty); alias for total_player_count."""
        return self.total_player_count

    @property
    def pitch_polyphony(self) -> int:
        """Simultaneous distinct pitch bins — not player count."""
        return self.distinct_pitch_count

    @property
    def event_doubling_count(self) -> int:
        """Extra symbolic rows beyond distinct pitches."""
        return self.doubling_count

    @property
    def player_doubling_count(self) -> int:
        """Players beyond one per distinct pitch bin."""
        return max(0, self.total_player_count - self.distinct_pitch_count)

    @property
    def bin_midis(self) -> list[float]:
        return [b.midi for b in self.pitch_bins]

    @property
    def bin_weights(self) -> list[float]:
        return [b.total_weight for b in self.pitch_bins]

    @property
    def bin_player_counts(self) -> list[int]:
        return [b.total_player_count for b in self.pitch_bins]

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_count": self.event_count,
            "player_count": int(self.total_player_count),
            "total_player_count": int(self.total_player_count),
            "distinct_pitch_count": self.distinct_pitch_count,
            "pitch_polyphony": int(self.pitch_polyphony),
            "doubling_count": self.doubling_count,
            "event_doubling_count": int(self.event_doubling_count),
            "player_doubling_count": int(self.player_doubling_count),
            "distinct_pitch_ratio": float(self.distinct_pitch_ratio),
            "pitch_differentiation_ratio": float(self.pitch_differentiation_ratio),
            "pitch_aggregation_applied": True,
            "pitch_aggregation_tolerance": float(self.pitch_aggregation_tolerance),
            "interval_pairs_count_distinct": int(self.interval_pairs_count_distinct),
            "unison_doublings_excluded_from_interval_structure": True,
            "qty_affects_pitch_structure": False,
            "pitch_bins": [b.to_dict() for b in self.pitch_bins],
        }


def _find_bin_index(midi: float, bin_midis: list[float], tolerance: float) -> int | None:
    for idx, existing in enumerate(bin_midis):
        if abs(existing - midi) <= tolerance:
            return idx
    return None


def aggregate_events_by_pitch(
    notas: Sequence[str],
    *,
    weights: Sequence[float] | None = None,
    player_counts: Sequence[int] | None = None,
    dynamics: Sequence[str] | None = None,
    instruments: Sequence[str] | None = None,
    tolerance: float = DEFAULT_PITCH_TOLERANCE,
) -> PitchAggregationResult:
    """
    Merge events sharing the same MIDI pitch (within tolerance) into pitch bins.

    Parameters
    ----------
    notas:
        Note names per simultaneous event.
    weights:
        Per-event symbolic/acoustic weights (e.g. instrument densities).
    player_counts:
        Per-event player counts for mass/texture summaries.
    """
    n = len(notas)
    if weights is None:
        weights = [1.0] * n
    if player_counts is None:
        player_counts = [1] * n
    if dynamics is None:
        dynamics = ["mf"] * n
    if instruments is None:
        instruments = ["flauta"] * n

    bin_midis: list[float] = []
    bin_event_counts: list[int] = []
    bin_weights: list[float] = []
    bin_players: list[int] = []
    bin_indices: list[list[int]] = []
    bin_notes: list[str] = []
    bin_dynamics: list[list[str]] = []
    bin_instruments: list[list[str]] = []

    for i, note in enumerate(notas):
        if not note:
            continue
        midi = float(note_to_midi(note))
        w = float(weights[i]) if i < len(weights) else 1.0
        pc = max(1, int(player_counts[i])) if i < len(player_counts) else 1
        dyn = str(dynamics[i]) if i < len(dynamics) else "mf"
        inst = str(instruments[i]) if i < len(instruments) else "flauta"

        idx = _find_bin_index(midi, bin_midis, tolerance)
        if idx is None:
            bin_midis.append(midi)
            bin_event_counts.append(1)
            bin_weights.append(w)
            bin_players.append(pc)
            bin_indices.append([i])
            bin_notes.append(note)
            bin_dynamics.append([dyn])
            bin_instruments.append([inst])
        else:
            bin_event_counts[idx] += 1
            bin_weights[idx] += w
            bin_players[idx] += pc
            bin_indices[idx].append(i)
            bin_dynamics[idx].append(dyn)
            bin_instruments[idx].append(inst)

    pitch_bins = tuple(
        PitchBin(
            midi=bin_midis[k],
            event_count=bin_event_counts[k],
            total_weight=bin_weights[k],
            total_player_count=bin_players[k],
            original_event_indices=tuple(bin_indices[k]),
            representative_note=bin_notes[k],
            dynamics=tuple(bin_dynamics[k]),
            instruments=tuple(bin_instruments[k]),
        )
        for k in range(len(bin_midis))
    )

    event_count = n
    distinct = len(pitch_bins)
    doubling = max(0, event_count - distinct)
    total_players = sum(max(1, int(player_counts[i])) for i in range(n))
    distinct_ratio = distinct / event_count if event_count else 0.0
    diff_ratio = (distinct - 1) / max(event_count - 1, 1) if event_count > 1 else 0.0
    pairs = distinct * (distinct - 1) // 2 if distinct >= 2 else 0

    return PitchAggregationResult(
        event_count=event_count,
        distinct_pitch_count=distinct,
        doubling_count=doubling,
        pitch_bins=pitch_bins,
        pitch_aggregation_tolerance=float(tolerance),
        distinct_pitch_ratio=float(distinct_ratio),
        pitch_differentiation_ratio=float(diff_ratio),
        interval_pairs_count_distinct=int(pairs),
        total_player_count=int(total_players),
    )
