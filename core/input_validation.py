"""
Validate analytical input — reject removed perceptual and combination-tone options.
"""

from __future__ import annotations

from typing import Any

from error_handler import InputError

REMOVED_STEVENS_KEYS: frozenset[str] = frozenset({"use_stevens", "alpha", "beta"})

REMOVED_PSYCHOACOUSTIC_KEYS: frozenset[str] = frozenset({"use_psychoacoustic"})

REMOVED_PERCEPTUAL_WEIGHTING_KEYS: frozenset[str] = frozenset({"use_perceptual_weighting"})

REMOVED_COMBINATION_TONE_KEYS: frozenset[str] = frozenset(
    {
        "calculate_combination_tones",
        "combination_tones",
        "resultant_tones",
        "include_resultants",
        "include_combination_tones",
        "virtual_tones",
        "generated_tones",
    }
)

REMOVED_ANALYTICAL_KEYS: frozenset[str] = (
    REMOVED_STEVENS_KEYS
    | REMOVED_PSYCHOACOUSTIC_KEYS
    | REMOVED_PERCEPTUAL_WEIGHTING_KEYS
    | REMOVED_COMBINATION_TONE_KEYS
)

REMOVED_GUI_PREFERENCE_KEYS: frozenset[str] = REMOVED_ANALYTICAL_KEYS

_REMOVED_MESSAGES: dict[str, str] = {
    "use_stevens": (
        "Removed option: use_stevens. SDA is now strictly symbolic and no longer "
        "implements Stevens-law or power-law density compression."
    ),
    "alpha": (
        "Removed option: alpha. SDA is now strictly symbolic and no longer "
        "implements Stevens-law or power-law density compression."
    ),
    "beta": (
        "Removed option: beta. SDA is now strictly symbolic and no longer "
        "implements Stevens-law or power-law density compression."
    ),
    "use_psychoacoustic": (
        "Removed option: use_psychoacoustic. SDA is now strictly symbolic and no longer "
        "implements psychoacoustic corrections (masking, roughness, loudness, Bark)."
    ),
    "use_perceptual_weighting": (
        "Removed option: use_perceptual_weighting. SDA is now strictly symbolic and no longer "
        "implements perceptual interval weighting."
    ),
    "calculate_combination_tones": (
        "Removed option: calculate_combination_tones. SDA is now strictly symbolic and "
        "no longer generates virtual/resultant tones."
    ),
    "combination_tones": (
        "Removed option: combination_tones. SDA is now strictly symbolic and "
        "no longer generates virtual/resultant tones."
    ),
    "resultant_tones": (
        "Removed option: resultant_tones. SDA is now strictly symbolic and "
        "no longer generates virtual/resultant tones."
    ),
    "include_resultants": (
        "Removed option: include_resultants. SDA is now strictly symbolic and "
        "no longer generates virtual/resultant tones."
    ),
    "include_combination_tones": (
        "Removed option: include_combination_tones. SDA is now strictly symbolic and "
        "no longer generates virtual/resultant tones."
    ),
    "virtual_tones": (
        "Removed option: virtual_tones. SDA is now strictly symbolic and "
        "no longer generates virtual/resultant tones."
    ),
    "generated_tones": (
        "Removed option: generated_tones. SDA is now strictly symbolic and "
        "no longer generates virtual/resultant tones."
    ),
}


def validate_no_removed_options(input_data: dict[str, Any]) -> None:
    """Raise InputError if removed analytical keys are present."""
    for key in REMOVED_ANALYTICAL_KEYS:
        if key in input_data:
            raise InputError(_REMOVED_MESSAGES[key], field=key)


def validate_no_removed_perceptual_options(input_data: dict[str, Any]) -> None:
    """Backward-compatible alias for validate_no_removed_options."""
    validate_no_removed_options(input_data)


def strip_removed_gui_preference_keys(
    raw: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    """
    Remove legacy GUI preference keys without passing them to the calculation pipeline.

    Returns (cleaned dict, list of stripped key names).
    """
    stripped = [k for k in REMOVED_GUI_PREFERENCE_KEYS if k in raw]
    if not stripped:
        return dict(raw), []
    cleaned = {k: v for k, v in raw.items() if k not in REMOVED_GUI_PREFERENCE_KEYS}
    return cleaned, stripped
