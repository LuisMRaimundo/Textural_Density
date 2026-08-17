# midi_loader.py
# Load note list from a MIDI file for use with calcular_metricas (same shape as xml_loader output).

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from core.converters import make_instrument_event
from core.defaults import RESEARCH_ANALYSIS_DEFAULTS
from core.models import InstrumentEvent
from core.unpitched_routing import (
    GM_PERCUSSION_CHANNEL,
    canonical_unpitched_note,
    map_gm_percussion_key,
)
from utils.notes import midi_to_note_name

logger = logging.getLogger(__name__)

# Map velocity (0-127) to dynamic level name
VELOCITY_TO_DYNAMIC = [
    "pppp", "pppp", "ppp", "ppp", "pp", "pp", "p", "p",
    "mf", "mf", "mf", "f", "f", "ff", "ff", "ffff",
]
# index = velocity // 8, clamp to 0..15


def _velocity_to_dynamic(velocity: int) -> str:
    v = max(0, min(127, int(velocity)))
    idx = min(v // 8, len(VELOCITY_TO_DYNAMIC) - 1)
    return VELOCITY_TO_DYNAMIC[idx]


def _default_midi_options() -> dict[str, Any]:
    return dict(RESEARCH_ANALYSIS_DEFAULTS)


def _resolve_midi_event(
    *,
    channel: int,
    key: int,
    velocity: int,
    onset: float,
    offset: float,
    idx: int,
    warnings: list[str],
) -> InstrumentEvent | None:
    """
    Build one InstrumentEvent from a MIDI note, or skip with warning.

    Channel 10 (0-based index 9) uses the GM percussion map. Unmapped keys are
    skipped — never promoted to a pitched fallback.
    """
    if int(channel) == GM_PERCUSSION_CHANNEL:
        mapped = map_gm_percussion_key(int(key))
        if mapped is None:
            warnings.append(
                f"Skipped unmappable MIDI channel-10 key {int(key)} "
                f"(no GM→unpitched instrument mapping)."
            )
            return None
        instrument_name, approx = mapped
        if approx:
            warnings.append(
                f"MIDI GM key {int(key)} on channel 10: {approx}."
            )
            logger.info("MIDI GM key %s: %s", key, approx)
        placeholder = canonical_unpitched_note(instrument_name)
        return make_instrument_event(
            idx=idx,
            note=placeholder,
            dynamic=_velocity_to_dynamic(velocity),
            instrument_name=instrument_name,
            player_count=1,
            onset=float(onset),
            offset=float(offset),
            duration=max(0.0, float(offset) - float(onset)),
            part_id=f"channel_{channel}",
            metadata={
                "midi_channel": int(channel),
                "midi_key": int(key),
                "velocity": int(velocity),
                "unpitched": True,
                "gm_percussion": True,
            },
        )

    note_name = midi_to_note_name(float(key))
    return make_instrument_event(
        idx=idx,
        note=note_name,
        dynamic=_velocity_to_dynamic(velocity),
        instrument_name="flute",
        player_count=1,
        onset=float(onset),
        offset=float(offset),
        duration=max(0.0, float(offset) - float(onset)),
        part_id=f"channel_{channel}",
        metadata={"midi_channel": int(channel), "velocity": int(velocity)},
    )


def parse_midi_to_events(filepath: str) -> tuple[list[InstrumentEvent], dict[str, Any], list[str]]:
    """
    Parse MIDI into timed InstrumentEvent objects (Phase 6).

    Returns (events, analysis_options, warnings).
    Channel 10 maps GM keys to unpitched percussion modules; other channels
    default to flute (unchanged pitched path).
    """
    try:
        import mido
    except ImportError as exc:
        raise ImportError(
            "MIDI loading requires 'mido'. Install with: pip install mido"
        ) from exc

    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Ficheiro não encontrado: {filepath}")

    warnings = [
        "Non-percussion MIDI channels are not mapped to orchestral instruments; using generic 'flute'.",
        "MIDI velocity maps to coarse dynamic labels — not measured loudness.",
        "MIDI may lack articulation, extended techniques, and reliable instrumentation.",
    ]

    mid = mido.MidiFile(path)
    ticks_per_beat = mid.ticks_per_beat
    tempo = 500000
    active: dict[tuple[int, int], dict[str, Any]] = {}
    events: list[InstrumentEvent] = []
    abs_tick = 0

    for msg in mido.merge_tracks(mid.tracks):
        abs_tick += msg.time
        if msg.type == "set_tempo":
            tempo = msg.tempo
            continue
        time_sec = mido.tick2second(abs_tick, ticks_per_beat, tempo)
        if msg.type == "note_on" and getattr(msg, "velocity", 0) > 0:
            active[(msg.channel, msg.note)] = {
                "onset": time_sec,
                "velocity": int(msg.velocity),
                "channel": int(msg.channel),
                "key": int(msg.note),
            }
        elif msg.type == "note_off" or (
            msg.type == "note_on" and getattr(msg, "velocity", 0) == 0
        ):
            key = (msg.channel, msg.note)
            if key not in active:
                continue
            info = active.pop(key)
            event = _resolve_midi_event(
                channel=int(info["channel"]),
                key=int(info["key"]),
                velocity=int(info["velocity"]),
                onset=float(info["onset"]),
                offset=float(time_sec),
                idx=len(events),
                warnings=warnings,
            )
            if event is not None:
                events.append(event)

    if not events:
        raise ValueError("MIDI file contains no paired note_on/note_off events.")

    logger.info("MIDI loaded (timed): %s, %d event(s).", path.name, len(events))
    return events, _default_midi_options(), warnings


def parse_midi(filepath: str) -> dict:
    """
    Parse a MIDI file and return a dict compatible with load_from_xml_data / get_input_data.

    Channel 10 uses the GM→unpitched map; other channels default to flute.
    """
    try:
        import mido
    except ImportError:
        raise ImportError(
            "O carregamento de MIDI requer o pacote 'mido'. Instale com: pip install mido"
        )
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Ficheiro não encontrado: {filepath}")

    notes: list[str] = []
    dynamics: list[str] = []
    instruments: list[str] = []
    warnings: list[str] = []

    mid = mido.MidiFile(path)
    for track in mid.tracks:
        for msg in track:
            if msg.type == "note_on" and getattr(msg, "velocity", 0) > 0:
                channel = int(getattr(msg, "channel", 0))
                key = int(msg.note)
                vel = int(getattr(msg, "velocity", 64))
                if channel == GM_PERCUSSION_CHANNEL:
                    mapped = map_gm_percussion_key(key)
                    if mapped is None:
                        warnings.append(
                            f"Skipped unmappable MIDI channel-10 key {key} "
                            f"(no GM→unpitched instrument mapping)."
                        )
                        continue
                    instrument_name, approx = mapped
                    if approx:
                        warnings.append(
                            f"MIDI GM key {key} on channel 10: {approx}."
                        )
                    notes.append(canonical_unpitched_note(instrument_name))
                    instruments.append(instrument_name)
                else:
                    notes.append(midi_to_note_name(float(key)))
                    instruments.append("flute")
                dynamics.append(_velocity_to_dynamic(vel))

    for w in warnings:
        logger.warning(w)
    if not notes:
        raise ValueError("O ficheiro MIDI não contém notas (note_on com velocity > 0).")
    n = len(notes)
    out = {
        "notes": notes,
        "dynamics": dynamics,
        "instruments": instruments,
        "num_instruments": [1] * n,
        **RESEARCH_ANALYSIS_DEFAULTS,
        "show_graphs": True,
    }
    logger.info("MIDI carregado: %s, %d nota(s).", path.name, n)
    return out
