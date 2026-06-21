"""
Converters between legacy dict input and typed score-event models.
"""

from __future__ import annotations

from typing import Any

from error_handler import InputError
from microtonal import (
    converter_para_sustenido,
    extract_cents,
    format_cents_suffix,
    midi_to_hz,
    parse_pitch_strict,
)

from core.input_validation import validate_no_removed_perceptual_options
from core.models import AnalysisConfig, InstrumentEvent, Pitch, VerticalSlice
from instrumentos.registry import resolve_profile


def _normalize_note_string(note: str) -> str:
    base, cents = extract_cents(note)
    normalized_base = converter_para_sustenido(base)
    return f"{normalized_base}{format_cents_suffix(cents)}"


def _infer_family(instrument_name: str) -> str:
    profile = resolve_profile(instrument_name)
    if profile is not None:
        return profile.family
    return "unknown"


def note_string_to_pitch(note: str) -> Pitch:
    """Build a Pitch from a note string (supports cents)."""
    parsed = parse_pitch_strict(note)
    midi = float(parsed.midi)
    normalized = _normalize_note_string(note)
    return Pitch(
        midi=midi,
        note_name=normalized,
        cents_offset=float(parsed.cents),
        frequency_hz=midi_to_hz(midi),
        spelling=note,
        pitch_class=int(round(midi)) % 12,
    )


def make_instrument_event(
    *,
    idx: int,
    note: str,
    dynamic: str,
    instrument_name: str,
    player_count: int,
    written_note: str | None = None,
    onset: float | None = None,
    offset: float | None = None,
    duration: float | None = None,
    part_id: str | None = None,
    voice_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> InstrumentEvent:
    """Build an InstrumentEvent from score fields."""
    inst_name = str(instrument_name).strip()
    profile = resolve_profile(inst_name)
    if profile is not None:
        inst_id = profile.instrument_id
        family = profile.family
    else:
        inst_id = inst_name.lower()
        family = "unknown"
    sounding_pitch = note_string_to_pitch(str(note))
    written_pitch = (
        note_string_to_pitch(str(written_note))
        if written_note is not None
        else None
    )
    return InstrumentEvent(
        event_id=f"evt_{idx}",
        instrument_id=inst_id,
        instrument_name=inst_name,
        family=family,
        sounding_pitch=sounding_pitch,
        written_pitch=written_pitch,
        dynamic=str(dynamic).strip().lower(),
        player_count=player_count,
        onset=onset,
        offset=offset,
        duration=duration,
        part_id=part_id,
        voice_id=voice_id,
        metadata=metadata or {"legacy_index": idx},
    )


def legacy_input_to_vertical_slice(
    input_data: dict[str, Any],
    *,
    slice_id: str | None = None,
    time: float | None = None,
) -> VerticalSlice:
    """
    Convert legacy parallel lists to a VerticalSlice with per-event instruments.

    Expected keys: notes, dynamics, instruments, num_instruments (equal length).

    Raises:
        InputError: If lists are missing, empty, or length-mismatched.
    """
    notas = input_data.get("notes", [])
    dinamicas = input_data.get("dynamics", [])
    instrumentos = input_data.get("instruments", [])
    numeros_instr = input_data.get("num_instruments", [])
    onsets = input_data.get("onsets")
    offsets = input_data.get("offsets")
    durations = input_data.get("durations")
    part_ids = input_data.get("part_ids")

    if not (notas and dinamicas and instrumentos and numeros_instr):
        raise InputError("Notes, dynamics, instruments and quantities are required.")
    if not (
        len(notas) == len(dinamicas) == len(instrumentos) == len(numeros_instr)
    ):
        raise InputError("Input lists must have the same length.")
    for optional_name, optional_list in (
        ("onsets", onsets),
        ("offsets", offsets),
        ("durations", durations),
        ("part_ids", part_ids),
    ):
        if optional_list is not None and len(optional_list) != len(notas):
            raise InputError(
                f"Optional list '{optional_name}' must match notes length.",
                field=optional_name,
            )

    events: list[InstrumentEvent] = []
    for idx, (nota, dyn, inst, num) in enumerate(
        zip(notas, dinamicas, instrumentos, numeros_instr)
    ):
        try:
            player_count = int(num)
        except (TypeError, ValueError) as exc:
            raise InputError(
                f"Invalid player count at index {idx}: {num!r}",
                field="num_instruments",
            ) from exc
        if player_count < 1:
            raise InputError(
                f"player_count must be >= 1 at index {idx}",
                field="num_instruments",
            )

        onset = float(onsets[idx]) if onsets is not None else None
        offset = float(offsets[idx]) if offsets is not None else None
        duration = float(durations[idx]) if durations is not None else None
        part_id = str(part_ids[idx]) if part_ids is not None else None

        events.append(
            make_instrument_event(
                idx=idx,
                note=str(nota),
                dynamic=str(dyn),
                instrument_name=str(inst),
                player_count=player_count,
                onset=onset,
                offset=offset,
                duration=duration,
                part_id=part_id,
                metadata={"legacy_index": idx},
            )
        )

    return VerticalSlice(
        slice_id=slice_id,
        time=time,
        events=events,
        source_metadata={"input_format": "legacy_parallel_lists"},
    )


def vertical_slice_to_legacy_lists(
    vertical_slice: VerticalSlice,
) -> tuple[list[str], list[str], list[str], list[int]]:
    """Extract legacy parallel lists from a VerticalSlice (round-trip helper)."""
    notas: list[str] = []
    dinamicas: list[str] = []
    instrumentos: list[str] = []
    numeros: list[int] = []
    for event in vertical_slice.events:
        pitch = event.sounding_pitch
        notas.append(pitch.note_name or str(pitch.midi))
        dinamicas.append(event.dynamic or "mf")
        instrumentos.append(event.instrument_name)
        numeros.append(event.player_count)
    return notas, dinamicas, instrumentos, numeros


def analysis_config_from_input(input_data: dict[str, Any]) -> AnalysisConfig:
    validate_no_removed_perceptual_options(input_data)
    return AnalysisConfig.from_input_dict(input_data)
