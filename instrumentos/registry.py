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

from error_handler import InputError

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
    unpitched: bool = False


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
    unpitched: bool = False,
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
        unpitched=unpitched,
    )


REGISTRY: dict[str, InstrumentProfile] = {}

# --- Woodwinds ---
REGISTRY["flauta"] = _profile(
    "flauta",
    "Fl",
    "woodwinds",
    sounding=(59, 98),
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
        "Numerical CDM table covers ordinary_sustain only; other registry supported_techniques "
        "are organological capabilities without technique-specific table rows.",
    ),
    aliases=("flute", "flute_traverso", "fl."),
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
    "Ob",
    "woodwinds",
    sounding=(58, 93),
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
        "Numerical CDM table covers ordinary_sustain only; other registry supported_techniques "
        "are organological capabilities without technique-specific table rows.",
    ),
    aliases=("oboe", "ob."),
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
    "Cl",
    "woodwinds",
    sounding=(50, 96),
    comfortable=(55, 80),
    brightness="neutral",
    status="literature_derived",
    uncertainty="medium",
    module_name="clarinet",
    supported=("legato", "staccato", "flutter_tongue"),
    source_notes=(
        "Sparse GPR table in instrumentos/clarinet.py from IOWA+ORCH sustain CDM medians "
        "(pp/mf/ff); not a full measured spectrum."
    ),
    warnings=(
        "Instrument density uses externally sourced sparse acoustic tables interpolated by GPR.",
        "Numerical CDM table covers ordinary_sustain only; other registry supported_techniques "
        "are organological capabilities without technique-specific table rows.",
    ),
    aliases=("clarinet", "clarinete", "cl.", "clarinet in bb", "clarinet in b♭"),
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
    "Bsn",
    "woodwinds",
    sounding=(34, 75),
    comfortable=(40, 65),
    brightness="dark",
    status="literature_derived",
    uncertainty="medium",
    module_name="bassoon",
    supported=("legato", "staccato", "flutter_tongue"),
    source_notes=(
        "Sparse GPR table in instrumentos/bassoon.py from IOWA+ORCH sustain CDM medians "
        "(pp/mf/ff); not a full measured spectrum."
    ),
    warnings=(
        "Instrument density uses externally sourced sparse acoustic tables interpolated by GPR.",
        "Numerical CDM table covers ordinary_sustain only; other registry supported_techniques "
        "are organological capabilities without technique-specific table rows.",
    ),
    aliases=("bassoon", "fagot", "bsn.", "fg", "fg."),
)

REGISTRY["contrafagote"] = _profile(
    "contrafagote",
    "Contrabassoon",
    "woodwinds",
    sounding=(22, 77),
    comfortable=(28, 65),
    brightness="dark",
    sustain="sustained",
    aliases=("contrabassoon",),
)

# --- Strings (GPR modules: IOWA+ORCH CDM medians at pp/mf/ff) ---
for _id, _name, _module, _sound, _comfort, _aliases in (
    ("violino", "Vl", "violin", (55, 103), (55, 76), ("violin", "vl.", "vln", "vln.")),
    ("violoncelo", "Vc", "cello", (36, 84), (40, 65), ("cello", "violoncello", "vc.", "vcl")),
    ("contrabaixo", "Db", "double_bass", (28, 72), (31, 55), ("double_bass", "double bass", "contrabass", "baixo", "db.", "cb", "cb.")),
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
            "Numerical CDM table covers arco_sustain only; other registry supported_techniques "
            "are organological capabilities without technique-specific table rows.",
        ),
        aliases=_aliases,
    )


REGISTRY["viola"] = _profile(
    "viola",
    "vla",
    "strings",
    sounding=(48, 96),
    comfortable=(50, 69),
    brightness="neutral",
    sustain="sustained",
    attack="soft",
    status="literature_derived",
    uncertainty="medium",
    module_name="viola",
    supported=("arco", "pizzicato", "tremolo", "harmonic", "mute"),
    unsupported=("sul_ponticello", "sul_tasto"),
    source_notes=(
        "Committed 10-dynamic CDM ladder in instrumentos/viola.py from "
        "D:\\CORDAS_2\\Viola_dynamics.xlsx Results sheet "
        "(dest Zenodo VIOLA_Media; measured pp/mf/ff anchors, "
        "PCHIP interiors, tapered equal-log outers)."
    ),
    warnings=(
        "String density uses externally sourced sparse CDM tables interpolated in MIDI space.",
        "Numerical CDM table covers arco_sustain only; other registry supported_techniques "
        "are organological capabilities without technique-specific table rows.",
    ),
    aliases=("viola", "vla", "vla."),
)


REGISTRY["viola_sordina"] = _profile(
    "viola_sordina",
    "vla sord",
    "strings",
    sounding=(48, 94),
    comfortable=(50, 69),
    brightness="neutral",
    sustain="sustained",
    attack="soft",
    status="literature_derived",
    uncertainty="high",
    module_name="viola_sordina",
    supported=("arco", "mute"),
    unsupported=("pizzicato", "sul_ponticello", "sul_tasto"),
    source_notes=(
        "Committed 10-dynamic CDM ladder in instrumentos/viola_sordina.py from "
        "D:\\CORDAS_2\\Viola_con_sordino_dynamics.xlsx Results sheet "
        "(dest Zenodo con sordino Media; measured pp/mf/ff anchors, "
        "PCHIP interiors, tapered equal-log outers). Table span C3–A#6."
    ),
    warnings=(
        "String density uses externally sourced sparse CDM tables interpolated in note space.",
        "Numerical CDM table covers arco_sordina only; anchors are dest-Zenodo Media "
        "(IOWA+Orchidea average) at pp/mf/ff.",
        "Other registry supported_techniques are organological capabilities without "
        "technique-specific table rows.",
    ),
    aliases=(
        "viola_sordina",
        "Viola_sordina",
        "Viola sordina",
        "viola con sordina",
        "viola_con_sordina",
        "viola con sordino",
        "viola_con_sordino",
        "viola sordina",
        "viola muted",
        "muted viola",
        "vla sord",
        "vla_sord",
        "vla_con_sord",
    ),
)


REGISTRY["viola_sul_ponticello"] = _profile(
    "viola_sul_ponticello",
    "vla sp",
    "strings",
    sounding=(48, 94),
    comfortable=(50, 69),
    brightness="bright",
    sustain="sustained",
    attack="hard",
    status="literature_derived",
    uncertainty="high",
    module_name="viola_sul_ponticello",
    supported=("arco", "sul_ponticello"),
    unsupported=("pizzicato", "mute", "sul_tasto"),
    source_notes=(
        "Committed 10-dynamic CDM ladder in instrumentos/viola_sul_ponticello.py from "
        "D:\\CORDAS_2\\Viola_sul_ponticello_dynamics.xlsx Results sheet "
        "(dest Zenodo sul ponticello Media; measured pp/mf/ff anchors, "
        "PCHIP interiors, tapered equal-log outers). Table span C3–A#6."
    ),
    warnings=(
        "String density uses externally sourced sparse CDM tables interpolated in note space.",
        "Numerical CDM table covers arco_sul_ponticello only; anchors are dest-Zenodo Media "
        "(IOWA+Orchidea average) at pp/mf/ff.",
        "Other registry supported_techniques are organological capabilities without "
        "technique-specific table rows.",
    ),
    aliases=(
        "viola_sul_ponticello",
        "Viola_sul_ponticello",
        "Viola sul ponticello",
        "viola sul pont",
        "viola_sul_pont",
        "viola sul ponticello",
        "sul ponticello viola",
        "sul_ponticello_viola",
        "vla sp",
        "vla_sp",
        "vla_sul_pont",
    ),
)

REGISTRY["violino_sordina"] = _profile(
    "violino_sordina",
    "vl_con_sord",
    "strings",
    sounding=(55, 103),
    comfortable=(55, 76),
    brightness="neutral",
    sustain="sustained",
    attack="soft",
    status="literature_derived",
    uncertainty="high",
    module_name="violin_sordina",
    supported=("arco", "mute"),
    unsupported=("pizzicato", "sul_ponticello", "sul_tasto"),
    source_notes=(
        "Committed 10-dynamic CDM ladder in instrumentos/violin_sordina.py from "
        "D:\\CORDAS_2\\Violin_con_sordino_dynamics.xlsx Results sheet "
        "(dest Zenodo con sordino Media; measured pp/mf/ff anchors, "
        "PCHIP interiors, tapered equal-log outers)."
    ),
    warnings=(
        "String density uses externally sourced sparse CDM tables interpolated in note space.",
        "Numerical CDM table covers arco_sordina only; anchors are dest-Zenodo Media "
        "(IOWA+Orchidea average) at pp/mf/ff.",
        "Other registry supported_techniques are organological capabilities without "
        "technique-specific table rows.",
    ),
    aliases=(
        "violin_sordina",
        "Violin_sordina",
        "Violin sordina",
        "violin con sordina",
        "violin_con_sordina",
        "violin con sordino",
        "violin_con_sordino",
        "violino sordina",
        "violino_sordina",
        "violino con sordina",
        "violino_con_sordina",
        "violin muted",
        "muted violin",
        "vl sord",
        "vl_sord",
        "vl_con_sord",
    ),
)

REGISTRY["violino_sul_ponticello"] = _profile(
    "violino_sul_ponticello",
    "vl_sul_pont",
    "strings",
    sounding=(55, 107),
    comfortable=(55, 76),
    brightness="bright",
    sustain="sustained",
    attack="hard",
    status="literature_derived",
    uncertainty="high",
    module_name="violin_sul_ponticello",
    supported=("arco", "sul_ponticello"),
    unsupported=("pizzicato", "mute", "sul_tasto"),
    source_notes=(
        "Committed 10-dynamic CDM ladder in instrumentos/violin_sul_ponticello.py from "
        "D:\\CORDAS_2\\Violin_sul_ponticello_dynamics.xlsx Results sheet "
        "(dest Zenodo sul ponticello Media; measured pp/mf/ff anchors, "
        "PCHIP interiors, tapered equal-log outers). Table span G3–B7."
    ),
    warnings=(
        "String density uses externally sourced sparse CDM tables interpolated in note space.",
        "Numerical CDM table covers arco_sul_ponticello only; anchors are dest-Zenodo Media "
        "(IOWA+Orchidea average) at pp/mf/ff.",
        "Other registry supported_techniques are organological capabilities without "
        "technique-specific table rows.",
    ),
    aliases=(
        "violin_sul_ponticello",
        "Violin_sul_ponticello",
        "Violin sul ponticello",
        "violin sul pont",
        "violin_sul_pont",
        "violino sul ponticello",
        "violino_sul_ponticello",
        "sul ponticello violin",
        "sul_ponticello_violin",
        "vl sp",
        "vl_sp",
        "vl_sul_pont",
    ),
)


REGISTRY["violino_sul_tasto"] = _profile(
    "violino_sul_tasto",
    "vl_sul_tast",
    "strings",
    sounding=(55, 103),
    comfortable=(55, 76),
    brightness="dark",
    sustain="sustained",
    attack="soft",
    status="literature_derived",
    uncertainty="high",
    module_name="violin_sul_tasto",
    supported=("arco", "sul_tasto"),
    unsupported=("pizzicato", "mute", "sul_ponticello"),
    source_notes=(
        "Committed 10-dynamic CDM ladder in instrumentos/violin_sul_tasto.py from "
        "D:\\CORDAS_2\\Violin_sul_tasto_dynamics.xlsx Results sheet "
        "(dest Zenodo sul tasto Media; measured pp/mf/ff anchors, "
        "PCHIP interiors, tapered equal-log outers)."
    ),
    warnings=(
        "String density uses externally sourced sparse CDM tables interpolated in note space.",
        "Numerical CDM table covers arco_sul_tasto only; anchors are dest-Zenodo Media "
        "(IOWA+Orchidea average) at pp/mf/ff.",
        "Other registry supported_techniques are organological capabilities without "
        "technique-specific table rows.",
    ),
    aliases=(
        "violin_sul_tasto",
        "Violin_sul_tasto",
        "Violin sul tasto",
        "violin sul tasto",
        "violino sul tasto",
        "violino_sul_tasto",
        "sul tasto violin",
        "sul_tasto_violin",
        "vl st",
        "vl_st",
        "vl_sul_tast",
    ),
)

REGISTRY["violino_harm"] = _profile(
    "violino_harm",
    "vl_harm",
    "strings",
    sounding=(72, 107),
    comfortable=(72, 96),
    brightness="bright",
    sustain="sustained",
    attack="soft",
    status="literature_derived",
    uncertainty="high",
    module_name="violin_harmonics",
    supported=("arco", "harmonic"),
    unsupported=("pizzicato", "mute", "sul_ponticello", "sul_tasto"),
    source_notes=(
        "Committed 10-dynamic CDM ladder in instrumentos/violin_harmonics.py from "
        "D:\\CORDAS_2\\Violin_harmonics_dynamics.xlsx Results sheet "
        "(dest Zenodo harmonics Media; measured pp/mf/ff anchors, "
        "PCHIP interiors, tapered equal-log outers). Table span C5–B7."
    ),
    warnings=(
        "String density uses externally sourced sparse CDM tables interpolated in note space.",
        "Numerical CDM table covers arco_harmonic only (pooled harmonics); anchors are "
        "dest-Zenodo Media (IOWA+Orchidea average) at pp/mf/ff.",
        "Table span is the harmonic sounding register (C5–B7); notes outside this range "
        "use controlled pitch extrapolation or fallback.",
        "Other registry supported_techniques are organological capabilities without "
        "technique-specific table rows.",
    ),
    aliases=(
        "violin_harmonics",
        "Violin_harmonics",
        "violin harmonics",
        "violino harmonics",
        "violino_harmonics",
        "violin harm",
        "violin_harm",
        "violino harm",
        "harmonics violin",
        "harmonics_violin",
        "vl harm",
        "vl_harm",
        # Legacy aliases from the retired split nat/art harmonic modules.
        "violin_nat_harm",
        "violin nat harm",
        "violino_nat_harm",
        "violin natural harmonics",
        "violin_art_harm",
        "violin art harm",
        "violino_art_harm",
        "violin artificial harmonics",
    ),
)

REGISTRY["viola_harm"] = _profile(
    "viola_harm",
    "vla harm",
    "strings",
    sounding=(72, 107),
    comfortable=(72, 96),
    brightness="bright",
    sustain="sustained",
    attack="soft",
    status="literature_derived",
    uncertainty="high",
    module_name="viola_harmonics",
    supported=("arco", "harmonic"),
    unsupported=("pizzicato", "mute", "sul_ponticello", "sul_tasto"),
    source_notes=(
        "Committed 10-dynamic CDM ladder in instrumentos/viola_harmonics.py from "
        "D:\\CORDAS_2\\Viola_harmonics_dynamics.xlsx Results sheet "
        "(dest Zenodo harmonics Media; measured pp/mf/ff anchors, "
        "PCHIP interiors, tapered equal-log outers). Table span C5–B7."
    ),
    warnings=(
        "String density uses externally sourced sparse CDM tables interpolated in note space.",
        "Numerical CDM table covers arco_harmonic only (pooled harmonics); anchors are "
        "dest-Zenodo Media (IOWA+Orchidea average) at pp/mf/ff.",
        "Table span is the harmonic sounding register (C5–B7); notes outside this range "
        "use controlled pitch extrapolation or fallback.",
        "Other registry supported_techniques are organological capabilities without "
        "technique-specific table rows.",
    ),
    aliases=(
        "viola_harmonics",
        "Viola_harmonics",
        "viola harmonics",
        "viola harm",
        "viola_harm",
        "harmonics viola",
        "harmonics_viola",
        "vla harm",
        "vla_harm",
    ),
)


# --- Brass ---
REGISTRY["trompa"] = _profile(
    "trompa",
    "Hn",
    "brass",
    sounding=(41, 77),
    comfortable=(45, 72),
    brightness="neutral",
    transposition=7,
    status="literature_derived",
    uncertainty="medium",
    module_name="horn",
    supported=("legato", "staccato", "stopped", "mute"),
    source_notes=(
        "Committed 10-dynamic CDM ladder in instrumentos/horn.py from IOWA+ORCH "
        "sustain medians (pp/mf/ff anchors; Dynamics_predicter Results sheet)."
    ),
    warnings=(
        "Instrument density uses externally sourced acoustic tables (committed full dynamic ladder).",
        "Numerical CDM table covers ordinary_sustain only; other registry supported_techniques "
        "are organological capabilities without technique-specific table rows.",
    ),
    aliases=("horn", "french_horn", "trompa", "hn.", "horn in f"),
)

REGISTRY["trompete"] = _profile(
    "trompete",
    "Tpt",
    "brass",
    sounding=(52, 87),
    comfortable=(58, 80),
    brightness="bright",
    attack="hard",
    transposition=2,
    status="literature_derived",
    uncertainty="medium",
    module_name="trumpet",
    supported=("legato", "staccato", "mute", "flutter_tongue"),
    source_notes=(
        "Sparse GPR table in instrumentos/trumpet.py from IOWA+ORCH sustain CDM medians "
        "(pp/mf/ff); not a full measured spectrum."
    ),
    warnings=(
        "Instrument density uses externally sourced sparse acoustic tables interpolated by GPR.",
        "Numerical CDM table covers ordinary_sustain only; other registry supported_techniques "
        "are organological capabilities without technique-specific table rows.",
    ),
    aliases=("trumpet", "tpt."),
)

REGISTRY["trombone"] = _profile(
    "trombone",
    "Trb",
    "brass",
    sounding=(29, 72),
    comfortable=(43, 65),
    brightness="neutral",
    status="literature_derived",
    uncertainty="medium",
    module_name="trombone",
    supported=("legato", "staccato", "mute"),
    source_notes=(
        "Committed 10-dynamic CDM ladder in instrumentos/trombone.py from "
        "Trombone_dynamics.xlsx Results sheet (Dynamics_predicter, dest Zenodo "
        "IOWA+ORCH anchors, 2026-08-24). sounding_range (MIDI 29–72, F1–C5) "
        "matches the committed table span; C#1–E1 were omitted because dest "
        "books lack a complete pp/mf/ff triad."
    ),
    warnings=(
        "Instrument density uses externally sourced acoustic tables (committed full dynamic ladder).",
        "Numerical CDM table covers ordinary_sustain only; other registry supported_techniques "
        "are organological capabilities without technique-specific table rows.",
    ),
    aliases=("trombone", "Trombone", "trb.", "trombon"),
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
    "Tba",
    "brass",
    sounding=(24, 70),
    comfortable=(30, 50),
    brightness="dark",
    status="literature_derived",
    uncertainty="medium",
    module_name="tuba",
    supported=("legato", "staccato", "mute"),
    source_notes=(
        "Committed 10-dynamic CDM ladder in instrumentos/tuba.py from IOWA+ORCH "
        "sustain medians (pp/mf/ff anchors; Dynamics_predicter Results sheet). "
        "sounding_range (MIDI 24–70, C1–A#4) matches the committed table span."
    ),
    warnings=(
        "Instrument density uses externally sourced acoustic tables (committed full dynamic ladder).",
        "Numerical CDM table covers ordinary_sustain only; other registry supported_techniques "
        "are organological capabilities without technique-specific table rows.",
    ),
    aliases=("tuba", "tba."),
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
# Table-backed unpitched specimens (NonTunPerc Analysis strike composite → CDM).
REGISTRY["bombo"] = _profile(
    "bombo",
    "Bass drum",
    "percussion",
    sounding=(28, 48),
    comfortable=(28, 48),
    brightness="dark",
    attack="hard",
    sustain="decaying",
    status="literature_derived",
    uncertainty="high",
    module_name="bass_drum",
    unpitched=True,
    supported=("struck", "rolled"),
    unsupported=("damped",),
    source_notes=(
        "Sparse GPR table in instrumentos/bass_drum.py from NonTunPerc MC p50 "
        "bassdrum_82cm strike composite_index (ff) with scaled pp/mf; unpitched — "
        "note is notation-lookup convention only."
    ),
    warnings=(
        "Instrument density uses model-derived NonTunPerc CDM proxies interpolated by GPR.",
        "Numerical table covers struck_membrane only; note key excluded from pitch-structure metrics.",
    ),
    aliases=("bass_drum", "bass drum"),
)

REGISTRY["pratos"] = _profile(
    "pratos",
    "Cymbals",
    "percussion",
    sounding=(60, 84),
    comfortable=(60, 84),
    brightness="very_bright",
    attack="hard",
    sustain="decaying",
    status="literature_derived",
    uncertainty="high",
    module_name="cymbals",
    unpitched=True,
    supported=("struck", "rolled"),
    unsupported=("damped",),
    source_notes=(
        "Sparse GPR table in instrumentos/cymbals.py from NonTunPerc MC p50 "
        "cymbal_46cm_medium shimmer composite_index (ff) with scaled pp/mf; "
        "unpitched — note is notation-lookup convention only."
    ),
    warnings=(
        "Instrument density uses model-derived NonTunPerc CDM proxies interpolated by GPR.",
        "Numerical table covers struck_plate only; note key excluded from pitch-structure metrics.",
    ),
    aliases=("cymbals", "cymbal"),
)

REGISTRY["tamtam"] = _profile(
    "tamtam",
    "Tam-tam",
    "percussion",
    sounding=(24, 48),
    comfortable=(24, 48),
    brightness="bright",
    attack="hard",
    sustain="decaying",
    status="literature_derived",
    uncertainty="high",
    module_name="tamtam",
    unpitched=True,
    supported=("struck", "rolled"),
    unsupported=("damped",),
    source_notes=(
        "Sparse GPR table in instrumentos/tamtam.py from NonTunPerc MC p50 "
        "tamtam_80cm_bronze shimmer composite_index (ff) with scaled pp/mf; "
        "unpitched — note is notation-lookup convention only."
    ),
    warnings=(
        "Instrument density uses model-derived NonTunPerc CDM proxies interpolated by GPR.",
        "Numerical table covers struck_plate only; note key excluded from pitch-structure metrics.",
    ),
    aliases=("tam_tam", "tam-tam", "tam tam"),
)

REGISTRY["gongo"] = _profile(
    "gongo",
    "Gong",
    "percussion",
    sounding=(36, 60),
    comfortable=(36, 60),
    brightness="bright",
    attack="hard",
    sustain="decaying",
    status="literature_derived",
    uncertainty="high",
    module_name="gong",
    unpitched=True,
    supported=("struck", "rolled"),
    unsupported=("damped",),
    source_notes=(
        "Sparse GPR table in instrumentos/gong.py from NonTunPerc MC p50 "
        "gong_50cm_bronze shimmer composite_index (ff) with scaled pp/mf; "
        "unpitched — note is notation-lookup convention only."
    ),
    warnings=(
        "Instrument density uses model-derived NonTunPerc CDM proxies interpolated by GPR.",
        "Numerical table covers struck_plate only; note key excluded from pitch-structure metrics.",
    ),
    aliases=("gong",),
)

_PERCUSSION_COARSE = (
    ("timpanos", "Timpani", (36, 60), ("timpani", "timbales")),
    ("caixa", "Snare drum", (60, 72), ("snare_drum", "snare")),
    ("vibrafone", "Vibraphone", (53, 84), ("vibraphone",)),
    ("marimba", "Marimba", (45, 84), ("marimba",)),
    ("metalofone", "Glockenspiel", (72, 108), ("glockenspiel", "glock")),
)

for _id, _name, _sound, _aliases in _PERCUSSION_COARSE:
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


def accepted_instrument_ids_text() -> str:
    """Comma-separated registered ids for fail-closed error messages."""
    return ", ".join(list_instrument_ids())


def unknown_instrument_error(
    instrument_name: str,
    *,
    part_id: str | None = None,
    part_name: str | None = None,
) -> InputError:
    """Build the documented analysis-path error for an unregistered instrument id."""
    ids = accepted_instrument_ids_text()
    loc_bits: list[str] = []
    if part_id:
        loc_bits.append(f"part_id={part_id!r}")
    if part_name:
        loc_bits.append(f"part={part_name!r}")
    loc = f" ({', '.join(loc_bits)})" if loc_bits else ""
    return InputError(
        f"Unknown instrument {instrument_name!r}{loc}. Analysis does not fall back "
        f"to a parent module or to the generic coarse proxy. "
        f"Accepted registry ids: {ids}. "
        f"Display names and aliases also resolve (e.g. Flute→flauta, Violin→violino). "
        f"Withdrawn technique ids (violoncelo_sordina, contrabaixo_sul_tasto, …) "
        f"are not remapped.",
        field="instruments",
    )


def require_registered_instrument(
    instrument_name: str,
    *,
    part_id: str | None = None,
    part_name: str | None = None,
) -> InstrumentProfile:
    """Resolve ``instrument_name`` or raise the fail-closed ``InputError``."""
    profile = resolve_profile(instrument_name)
    if profile is None:
        raise unknown_instrument_error(
            instrument_name,
            part_id=part_id,
            part_name=part_name,
        )
    return profile


# AUDIT-ONLY — ``allow_unknown=True`` is not on any production path
# (``calculate_metrics`` reports a hard ``InputError`` via
# ``profile_for_event`` / ``get_instrument_module`` instead).
# Do not pass that flag from the analysis path.
def profile_for_event(
    instrument_name: str,
    *,
    allow_unknown: bool = False,
    part_id: str | None = None,
    part_name: str | None = None,
) -> InstrumentProfile:
    """Return the registry profile, or raise ``InputError`` if the id is unknown.

    ``allow_unknown=True`` is a non-production audit hook: it is not
    reachable from ``calculate_metrics``. Metadata-audit tools may pass it
    to inspect the generic coarse proxy. The analysis path must not.
    """
    profile = resolve_profile(instrument_name)
    if profile is not None:
        return profile
    if allow_unknown:
        return _UNKNOWN_PROFILE
    raise unknown_instrument_error(
        instrument_name,
        part_id=part_id,
        part_name=part_name,
    )


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
