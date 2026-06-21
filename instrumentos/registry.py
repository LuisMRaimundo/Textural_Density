"""
Orchestral instrument registry (Phase 7).

Profiles document register, family, and dynamic-response metadata. Where
``module_name`` is set, per-note instrument density uses sparse GPR tables in
``instrumentos/<module>.py`` built from **externally obtained acoustic
metadata** (literature / measurement summaries — not runtime audio analysis).
Instruments without such tables use ``coarse_default`` register/dynamic models.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

ProfileStatus = Literal[
    "empirical_source",
    "empirical_profile",
    "literature_derived",
    "literature_informed",
    "coarse_default",
    "symbolic_default",
]
UncertaintyLevel = Literal["low", "medium", "high"]

# Ordinal dynamic weights (symbolic — not SPL).
_DEFAULT_DYNAMIC_CURVE: dict[str, float] = {
    "pppp": 0.2,
    "ppp": 0.3,
    "pp": 0.4,
    "p": 0.6,
    "mp": 0.8,
    "mf": 1.0,
    "f": 1.5,
    "ff": 2.0,
    "fff": 2.5,
    "ffff": 3.0,
}


@dataclass(frozen=True)
class InstrumentProfile:
    instrument_id: str
    display_name: str
    family: str
    transposition: int
    sounding_range: tuple[float, float]
    comfortable_range: tuple[float, float]
    register_bands: dict[str, tuple[float, float]]
    default_dynamic_response_curve: dict[str, float]
    generic_brightness_class: str
    sustain_decay_class: str
    attack_class: str
    supported_techniques: tuple[str, ...]
    unsupported_techniques: tuple[str, ...]
    profile_status: ProfileStatus
    uncertainty: UncertaintyLevel
    source_notes: str
    missing_data_warnings: tuple[str, ...] = field(default_factory=tuple)
    module_name: str | None = None
    aliases: tuple[str, ...] = field(default_factory=tuple)


def _bands(low: float, mid: float, high: float) -> dict[str, tuple[float, float]]:
    return {
        "low": (low, mid),
        "mid": (mid, high),
        "high": (high, 127.0),
    }


def _profile(
    instrument_id: str,
    display_name: str,
    family: str,
    sounding: tuple[float, float],
    comfortable: tuple[float, float],
    brightness: str = "neutral",
    sustain: str = "sustained",
    attack: str = "medium",
    status: ProfileStatus = "coarse_default",
    uncertainty: UncertaintyLevel = "high",
    module_name: str | None = None,
    transposition: int = 0,
    supported: tuple[str, ...] = ("arco",),
    unsupported: tuple[str, ...] = (),
    source_notes: str = "Coarse register/dynamic model; no externally sourced acoustic amplitude table.",
    warnings: tuple[str, ...] = ("Spectral density is a coarse fallback without external acoustic metadata.",),
    aliases: tuple[str, ...] = (),
) -> InstrumentProfile:
    low, high = sounding
    mid = low + (high - low) / 3
    upper_mid = low + 2 * (high - low) / 3
    return InstrumentProfile(
        instrument_id=instrument_id,
        display_name=display_name,
        family=family,
        transposition=transposition,
        sounding_range=sounding,
        comfortable_range=comfortable,
        register_bands=_bands(low, mid, upper_mid),
        default_dynamic_response_curve=dict(_DEFAULT_DYNAMIC_CURVE),
        generic_brightness_class=brightness,
        sustain_decay_class=sustain,
        attack_class=attack,
        supported_techniques=supported,
        unsupported_techniques=unsupported,
        profile_status=status,
        uncertainty=uncertainty,
        source_notes=source_notes,
        missing_data_warnings=warnings,
        module_name=module_name,
        aliases=aliases,
    )


REGISTRY: dict[str, InstrumentProfile] = {}

# --- Woodwinds ---
REGISTRY["flauta"] = _profile(
    "flauta",
    "Flute",
    "woodwinds",
    sounding=(60, 96),
    comfortable=(62, 88),
    brightness="bright",
    status="literature_derived",
    uncertainty="medium",
    module_name="flute",
    supported=("legato", "staccato", "flutter_tongue"),
    unsupported=("multiphonic",),
    source_notes=(
        "Sparse GPR table in instrumentos/flute.py from IOWA+ORCH sustain CDM medians "
        "(pp/mf/ff); not a full measured spectrum."
    ),
    warnings=(
        "Instrument density uses externally sourced sparse acoustic tables interpolated by GPR.",
    ),
    aliases=("flute", "flute_traverso"),
)

REGISTRY["flautim"] = _profile(
    "flautim",
    "Piccolo",
    "woodwinds",
    sounding=(74, 108),
    comfortable=(76, 100),
    brightness="very_bright",
    attack="hard",
    supported=("legato", "staccato"),
    aliases=("piccolo",),
)

REGISTRY["oboe"] = _profile(
    "oboe",
    "Oboe",
    "woodwinds",
    sounding=(58, 88),
    comfortable=(60, 81),
    brightness="neutral",
    status="literature_derived",
    uncertainty="medium",
    module_name="oboe",
    supported=("legato", "staccato", "flutter_tongue"),
    source_notes=(
        "Sparse GPR table in instrumentos/oboe.py from IOWA+ORCH sustain CDM medians "
        "(pp/mf/ff); not a full measured spectrum."
    ),
    warnings=(
        "Instrument density uses externally sourced sparse acoustic tables interpolated by GPR.",
    ),
    aliases=("oboe",),
)

REGISTRY["cor_anglais"] = _profile(
    "cor_anglais",
    "English horn",
    "woodwinds",
    sounding=(52, 76),
    comfortable=(55, 72),
    brightness="dark",
    transposition=7,
    supported=("legato", "staccato"),
    aliases=("corne_ingles", "english_horn", "cor anglais", "cor_anglais"),
)

REGISTRY["clarinete"] = _profile(
    "clarinete",
    "Clarinet",
    "woodwinds",
    sounding=(50, 88),
    comfortable=(55, 80),
    brightness="neutral",
    status="literature_derived",
    uncertainty="medium",
    module_name="clarinet",
    supported=("legato", "staccato", "flutter_tongue"),
    source_notes="Sparse GPR table in instrumentos/clarinet.py from externally sourced acoustic amplitude metadata.",
    warnings=("Clarinet density uses externally sourced sparse acoustic tables; not full measured spectra.",),
    aliases=("clarinet", "clarinete"),
)

REGISTRY["clarinete_baixo"] = _profile(
    "clarinete_baixo",
    "Bass clarinet",
    "woodwinds",
    sounding=(34, 72),
    comfortable=(40, 65),
    brightness="dark",
    transposition=14,
    supported=("legato", "staccato"),
    aliases=("bass_clarinet", "clarinete baixo", "clarinete_baixo"),
)

REGISTRY["fagote"] = _profile(
    "fagote",
    "Bassoon",
    "woodwinds",
    sounding=(34, 72),
    comfortable=(40, 65),
    brightness="dark",
    supported=("legato", "staccato", "flutter_tongue"),
    aliases=("bassoon", "fagot"),
)

REGISTRY["contrafagote"] = _profile(
    "contrafagote",
    "Contrabassoon",
    "woodwinds",
    sounding=(22, 58),
    comfortable=(28, 50),
    brightness="dark",
    sustain="sustained",
    aliases=("contrabassoon",),
)

# --- Strings (GPR modules: IOWA+ORCH CDM medians at pp/mf/ff) ---
for _id, _name, _module, _sound, _comfort, _aliases in (
    ("violino", "Violin", "violin", (55, 103), (55, 76), ("violin",)),
    ("viola", "Viola", "viola", (48, 76), (50, 69), ("viola",)),
    ("violoncelo", "Cello", "cello", (36, 84), (40, 65), ("cello", "violoncello")),
    ("contrabaixo", "Double bass", "double_bass", (28, 72), (31, 55), ("double_bass", "contrabass", "baixo")),
):
    REGISTRY[_id] = _profile(
        _id,
        _name,
        "strings",
        sounding=_sound,
        comfortable=_comfort,
        brightness="neutral",
        sustain="sustained",
        attack="soft",
        status="literature_derived",
        uncertainty="medium",
        module_name=_module,
        supported=("arco", "pizzicato", "tremolo", "harmonic", "mute"),
        unsupported=("sul_ponticello", "sul_tasto"),
        source_notes=(
            f"Sparse GPR table in instrumentos/{_module}.py from IOWA+ORCH arco sustain "
            "Combined Density Metric medians (pp/mf/ff); not a full measured spectrum."
        ),
        warnings=(
            "String density uses externally sourced sparse CDM tables interpolated by GPR.",
        ),
        aliases=_aliases,
    )

# --- Brass ---
REGISTRY["trompa"] = _profile(
    "trompa",
    "Horn",
    "brass",
    sounding=(41, 77),
    comfortable=(45, 72),
    brightness="neutral",
    transposition=7,
    supported=("legato", "staccato", "stopped", "mute"),
    aliases=("horn", "french_horn", "trompa"),
)

REGISTRY["trompete"] = _profile(
    "trompete",
    "Trumpet",
    "brass",
    sounding=(55, 84),
    comfortable=(58, 80),
    brightness="bright",
    attack="hard",
    transposition=2,
    supported=("legato", "staccato", "mute", "flutter_tongue"),
    aliases=("trumpet",),
)

REGISTRY["trombone"] = _profile(
    "trombone",
    "Trombone",
    "brass",
    sounding=(40, 72),
    comfortable=(43, 65),
    brightness="neutral",
    aliases=("trombone",),
)

REGISTRY["trombone_baixo"] = _profile(
    "trombone_baixo",
    "Bass trombone",
    "brass",
    sounding=(34, 65),
    comfortable=(36, 58),
    brightness="dark",
    aliases=("bass_trombone", "trombone baixo"),
)

REGISTRY["tuba"] = _profile(
    "tuba",
    "Tuba",
    "brass",
    sounding=(28, 58),
    comfortable=(30, 50),
    brightness="dark",
    aliases=("tuba",),
)

# --- Keyboard / harp ---
REGISTRY["piano"] = _profile(
    "piano",
    "Piano",
    "keyboard_harp",
    sounding=(21, 108),
    comfortable=(36, 96),
    brightness="neutral",
    attack="hard",
    sustain="decaying",
    supported=("struck", "pedal"),
    aliases=("piano", "fortepiano"),
)

REGISTRY["celesta"] = _profile(
    "celesta",
    "Celesta",
    "keyboard_harp",
    sounding=(60, 96),
    comfortable=(65, 88),
    brightness="bright",
    attack="hard",
    sustain="decaying",
    supported=("struck",),
    aliases=("celesta",),
)

REGISTRY["harpa"] = _profile(
    "harpa",
    "Harp",
    "keyboard_harp",
    sounding=(23, 96),
    comfortable=(40, 88),
    brightness="bright",
    attack="soft",
    sustain="decaying",
    supported=("plucked", "glissando", "harmonic"),
    aliases=("harp",),
)

# --- Percussion (pitch where applicable) ---
_PERCUSSION = (
    ("timpanos", "Timpani", (36, 60), ("timpani", "timbales")),
    ("bombo", "Bass drum", (28, 48), ("bass_drum",)),
    ("caixa", "Snare drum", (60, 72), ("snare_drum", "snare")),
    ("pratos", "Cymbals", (60, 84), ("cymbals",)),
    ("tamtam", "Tam-tam", (24, 48), ("tam_tam", "tam-tam")),
    ("vibrafone", "Vibraphone", (53, 84), ("vibraphone",)),
    ("marimba", "Marimba", (45, 84), ("marimba",)),
    ("metalofone", "Glockenspiel", (72, 108), ("glockenspiel", "glock")),
)

for _id, _name, _sound, _aliases in _PERCUSSION:
    REGISTRY[_id] = _profile(
        _id,
        _name,
        "percussion",
        sounding=_sound,
        comfortable=_sound,
        brightness="bright",
        attack="hard",
        sustain="decaying",
        supported=("struck", "rolled"),
        unsupported=("damped",),
        source_notes="Percussion profile uses nominal pitch range when pitched; unpitched events need manual pitch metadata.",
        warnings=(
            "Percussion spectral density is a coarse proxy; unpitched strokes may lack pitch metadata.",
        ),
        aliases=_aliases,
    )

def _normalize_key(name: str) -> str:
    return name.strip().lower().replace(" ", "_").replace("-", "_")


# Build alias lookup
_ALIAS_TO_ID: dict[str, str] = {}
for profile in REGISTRY.values():
    _ALIAS_TO_ID[profile.instrument_id] = profile.instrument_id
    _ALIAS_TO_ID[_normalize_key(profile.display_name)] = profile.instrument_id
    for alias in profile.aliases:
        key = _normalize_key(alias)
        _ALIAS_TO_ID[key] = profile.instrument_id


def resolve_profile(name: str) -> InstrumentProfile | None:
    """Resolve instrument name or alias to a profile, or None if unknown."""
    key = _normalize_key(name)
    instrument_id = _ALIAS_TO_ID.get(key)
    if instrument_id is None:
        return None
    return REGISTRY.get(instrument_id)


def list_profiles() -> list[InstrumentProfile]:
    return list(REGISTRY.values())


def list_instrument_ids() -> list[str]:
    return sorted(REGISTRY.keys())


def profile_for_event(instrument_name: str) -> InstrumentProfile:
    """Return profile for instrument name; unknown instruments get a generic fallback."""
    profile = resolve_profile(instrument_name)
    if profile is not None:
        return profile
    return _UNKNOWN_PROFILE


_UNKNOWN_PROFILE = InstrumentProfile(
    instrument_id="unknown",
    display_name="Unknown instrument",
    family="unknown",
    transposition=0,
    sounding_range=(36, 84),
    comfortable_range=(48, 72),
    register_bands=_bands(36, 60, 72),
    default_dynamic_response_curve=dict(_DEFAULT_DYNAMIC_CURVE),
    generic_brightness_class="neutral",
    sustain_decay_class="sustained",
    attack_class="medium",
    supported_techniques=(),
    unsupported_techniques=(),
    profile_status="coarse_default",
    uncertainty="high",
    source_notes="Unregistered instrument; generic coarse proxy applied.",
    missing_data_warnings=(
        "Instrument not in registry; density uses generic coarse proxy.",
    ),
)
