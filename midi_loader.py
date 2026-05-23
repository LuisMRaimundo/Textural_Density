# midi_loader.py
# Load note list from a MIDI file for use with calcular_metricas (same shape as xml_loader output).

import logging
from pathlib import Path
from typing import Any

from core.converters import make_instrument_event
from core.defaults import RESEARCH_ANALYSIS_DEFAULTS
from core.models import InstrumentEvent
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


def parse_midi_to_events(filepath: str) -> tuple[list[InstrumentEvent], dict[str, Any], list[str]]:
    """
    Parse MIDI into timed InstrumentEvent objects (Phase 6).

    Returns (events, analysis_options, warnings).
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
        "MIDI channel/program are not mapped to orchestral instruments; using generic 'flauta'.",
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
            }
        elif msg.type == "note_off" or (
            msg.type == "note_on" and getattr(msg, "velocity", 0) == 0
        ):
            key = (msg.channel, msg.note)
            if key not in active:
                continue
            info = active.pop(key)
            note_name = midi_to_note_name(float(msg.note))
            events.append(
                make_instrument_event(
                    idx=len(events),
                    note=note_name,
                    dynamic=_velocity_to_dynamic(info["velocity"]),
                    instrument_name="flauta",
                    player_count=1,
                    onset=float(info["onset"]),
                    offset=float(time_sec),
                    duration=max(0.0, float(time_sec) - float(info["onset"])),
                    part_id=f"channel_{info['channel']}",
                    metadata={"midi_channel": info["channel"], "velocity": info["velocity"]},
                )
            )

    if not events:
        raise ValueError("MIDI file contains no paired note_on/note_off events.")

    logger.info("MIDI loaded (timed): %s, %d event(s).", path.name, len(events))
    return events, _default_midi_options(), warnings


def parse_midi(filepath: str) -> dict:
    """
    Parse a MIDI file and return a dict compatible with load_from_xml_data / get_input_data:
    notes, dynamics, instruments, num_instruments, weight_factor, and options.
    Uses note_on messages; velocity maps to dynamics; instrument defaults to 'flauta'.
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
    mid = mido.MidiFile(path)
    notes = []
    dynamics = []
    # Collect (note_num, velocity) from note_on with velocity > 0
    for track in mid.tracks:
        for msg in track:
            if msg.type == "note_on" and getattr(msg, "velocity", 0) > 0:
                note_num = msg.note
                vel = getattr(msg, "velocity", 64)
                notes.append(midi_to_note_name(float(note_num)))
                dynamics.append(_velocity_to_dynamic(vel))
    if not notes:
        raise ValueError("O ficheiro MIDI não contém notas (note_on com velocity > 0).")
    n = len(notes)
    out = {
        "notes": notes,
        "dynamics": dynamics,
        "instruments": ["flauta"] * n,
        "num_instruments": [1] * n,
        **RESEARCH_ANALYSIS_DEFAULTS,
        "show_graphs": True,
    }
    logger.info(f"MIDI carregado: {path.name}, {n} nota(s).")
    return out
