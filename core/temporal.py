"""
Temporal vertical-slice segmentation (Phase 6).

Groups timed InstrumentEvent objects into VerticalSlice collections at
onset boundaries. Full MusicXML division parsing is deferred; custom XML
and MIDI supply timing metadata.
"""

from __future__ import annotations

from typing import Literal

from core.models import InstrumentEvent, VerticalSlice

TemporalMode = Literal["event_boundary", "instantaneous"]


def resolve_event_offset(event: InstrumentEvent) -> float | None:
    """Return event offset in seconds when inferable."""
    if event.offset is not None:
        return float(event.offset)
    if event.onset is not None and event.duration is not None and event.duration > 0:
        return float(event.onset) + float(event.duration)
    return None


def resolve_event_duration(event: InstrumentEvent) -> float | None:
    """Return event duration in seconds when inferable."""
    if event.duration is not None and event.duration > 0:
        return float(event.duration)
    if event.onset is not None and event.offset is not None:
        dur = float(event.offset) - float(event.onset)
        return dur if dur > 0 else None
    return None


def normalize_event_timing(events: list[InstrumentEvent]) -> list[InstrumentEvent]:
    """Fill missing offset/duration fields from available timing data."""
    normalized: list[InstrumentEvent] = []
    for event in events:
        onset = event.onset
        offset = event.offset
        duration = event.duration
        if onset is not None and duration is not None and offset is None:
            offset = float(onset) + float(duration)
        elif onset is not None and offset is not None and (duration is None or duration <= 0):
            duration = max(0.0, float(offset) - float(onset))
        normalized.append(
            InstrumentEvent(
                event_id=event.event_id,
                instrument_id=event.instrument_id,
                instrument_name=event.instrument_name,
                family=event.family,
                sounding_pitch=event.sounding_pitch,
                written_pitch=event.written_pitch,
                dynamic=event.dynamic,
                dynamic_weight=event.dynamic_weight,
                player_count=event.player_count,
                articulation=event.articulation,
                technique=event.technique,
                mute=event.mute,
                harmonic_type=event.harmonic_type,
                playing_position=event.playing_position,
                register_label=event.register_label,
                onset=onset,
                offset=offset,
                duration=duration,
                voice_id=event.voice_id,
                staff_id=event.staff_id,
                part_id=event.part_id,
                source_measure=event.source_measure,
                source_beat=event.source_beat,
                metadata=dict(event.metadata),
            )
        )
    return normalized


def event_is_active_at(event: InstrumentEvent, time: float, *, epsilon: float = 1e-9) -> bool:
    """True if event sounds at instant ``time`` (half-open [onset, offset))."""
    if event.onset is None:
        return False
    offset = resolve_event_offset(event)
    if offset is None:
        return abs(float(event.onset) - time) <= epsilon
    return float(event.onset) <= time + epsilon < float(offset)


def events_have_timing(events: list[InstrumentEvent]) -> bool:
    return any(ev.onset is not None for ev in events)


def group_events_into_slices(
    events: list[InstrumentEvent],
    *,
    mode: TemporalMode = "event_boundary",
) -> list[VerticalSlice]:
    """
    Build vertical slices from timed events.

    ``event_boundary``: one slice at each distinct event onset; active set is
    all events sounding at that instant.

    ``instantaneous`` / untimed input: single slice containing all events.
    """
    if not events:
        return []

    if mode == "instantaneous" or not events_have_timing(events):
        return [
            VerticalSlice(
                slice_id="slice_0",
                events=list(events),
                source_metadata={"temporal_mode": "instantaneous"},
            )
        ]

    normalized = normalize_event_timing(events)
    boundary_times = sorted({float(ev.onset) for ev in normalized if ev.onset is not None})

    slices: list[VerticalSlice] = []
    for idx, boundary_time in enumerate(boundary_times):
        active = [ev for ev in normalized if event_is_active_at(ev, boundary_time)]
        if not active:
            continue
        next_time = (
            boundary_times[idx + 1] if idx + 1 < len(boundary_times) else None
        )
        slice_duration = (
            float(next_time) - float(boundary_time) if next_time is not None else None
        )
        slices.append(
            VerticalSlice(
                slice_id=f"slice_{idx}",
                time=boundary_time,
                duration=slice_duration,
                events=active,
                source_metadata={
                    "temporal_mode": mode,
                    "boundary_time": boundary_time,
                },
            )
        )

    if not slices:
        return [
            VerticalSlice(
                slice_id="slice_0",
                events=list(events),
                source_metadata={"temporal_mode": "instantaneous_fallback"},
            )
        ]
    return slices


def summarize_time_series(
    entries: list[dict],
) -> dict[str, float]:
    """Summary statistics over a time series of scalar metrics."""
    if not entries:
        return {}
    totals = [float(e["density_total"]) for e in entries if e.get("density_total") is not None]
    if not totals:
        return {"slice_count": float(len(entries))}
    import numpy as np

    arr = np.asarray(totals, dtype=float)
    return {
        "slice_count": float(len(entries)),
        "density_total_mean": float(np.mean(arr)),
        "density_total_median": float(np.median(arr)),
        "density_total_max": float(np.max(arr)),
        "density_total_min": float(np.min(arr)),
        "density_total_variance": float(np.var(arr)),
    }
