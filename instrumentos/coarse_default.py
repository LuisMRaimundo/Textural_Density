"""
Coarse-default instrument density module (Phase 7).

Used when no dedicated acoustic-source script exists. Does not embed external
acoustic amplitude tables — register comfort, brightness, attack, and symbolic
dynamics only.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING

from microtonal import note_to_midi_strict

if TYPE_CHECKING:
    from instrumentos.registry import InstrumentProfile

_BRIGHTNESS = {
    "dark": 0.85,
    "neutral": 1.0,
    "bright": 1.12,
    "very_bright": 1.25,
}

_ATTACK = {
    "soft": 0.88,
    "medium": 1.0,
    "hard": 1.15,
}

_SUSTAIN = {
    "sustained": 1.0,
    "decaying": 0.92,
    "percussive": 0.8,
}


def _comfort_factor(midi: float, comfortable: tuple[float, float]) -> float:
    low, high = comfortable
    if low <= midi <= high:
        return 1.0
    if midi < low:
        return max(0.45, 1.0 - (low - midi) / 24.0)
    return max(0.45, 1.0 - (midi - high) / 24.0)


def _dynamic_weight(profile: InstrumentProfile, dynamic: str) -> float:
    dyn = (dynamic or "mf").strip().lower()
    return profile.default_dynamic_response_curve.get(dyn, 1.0)


def calcular_densidade_for_profile(profile: InstrumentProfile, nota: str, dinamica: str) -> float:
    """Coarse symbolic density for one note/dynamic pair."""
    midi = note_to_midi_strict(nota)
    base = 8.0
    comfort = _comfort_factor(midi, profile.comfortable_range)
    brightness = _BRIGHTNESS.get(profile.generic_brightness_class, 1.0)
    attack = _ATTACK.get(profile.attack_class, 1.0)
    sustain = _SUSTAIN.get(profile.sustain_decay_class, 1.0)
    dynamic = _dynamic_weight(profile, dinamica)
    if profile.family == "percussion":
        sustain = _SUSTAIN["percussive"]
    return float(base * comfort * brightness * attack * sustain * dynamic)


def build_coarse_module(profile: InstrumentProfile) -> SimpleNamespace:
    """Return a module-like namespace bound to ``profile``."""

    def calcular_densidade(nota, dinamica):
        return calcular_densidade_for_profile(profile, nota, dinamica)

    return SimpleNamespace(
        calcular_densidade=calcular_densidade,
        PROFILE=profile,
        IS_COARSE_DEFAULT=True,
    )
