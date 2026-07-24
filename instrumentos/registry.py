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
    aliases=("bassoon", "fagot"),
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
    ("violino", "Violin", "violin", (55, 103), (55, 76), ("violin",)),
    ("viola", "Viola", "viola", (48, 96), (50, 69), ("viola",)),
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
            "Numerical CDM table covers arco_sustain only; other registry supported_techniques "
            "are organological capabilities without technique-specific table rows.",
        ),
        aliases=_aliases,
    )


REGISTRY["viola_sordina"] = _profile(
    "viola_sordina",
    "Viola sordina",
    "strings",
    sounding=(48, 96),
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
        "Sparse GPR table in instrumentos/viola_sordina.py from Strings Techniques "
        "Extrapolation Viola_pp.xlsx / Viola_mf.xlsx / Viola_ff.xlsx "
        "(assumption-based EWSD; pp/mf/ff from estimate_mean)."
    ),
    warnings=(
        "String density uses externally sourced sparse CDM tables interpolated by GPR.",
        "Numerical CDM table covers arco_sordina only; pp/mf/ff come from "
        "assumption-based extrapolation workbooks (not Zenodo-measured CDM).",
        "Other registry supported_techniques are organological capabilities without "
        "technique-specific table rows.",
    ),
    aliases=("viola_sordina", "Viola_sordina", "viola con sordina", "viola_con_sordina", "viola sordina", "viola muted", "muted viola"),
)


REGISTRY["viola_sul_tasto"] = _profile(
    "viola_sul_tasto",
    "Viola sul tasto",
    "strings",
    sounding=(48, 96),
    comfortable=(50, 69),
    brightness="dark",
    sustain="sustained",
    attack="soft",
    status="literature_derived",
    uncertainty="high",
    module_name="viola_sul_tasto",
    supported=("arco", "sul_tasto"),
    unsupported=("pizzicato", "mute", "sul_ponticello"),
    source_notes=(
        "Sparse GPR table in instrumentos/viola_sul_tasto.py from Strings Techniques "
        "Extrapolation Viola_pp.xlsx / Viola_mf.xlsx / Viola_ff.xlsx "
        "(assumption-based EWSD; pp/mf/ff from estimate_mean)."
    ),
    warnings=(
        "String density uses externally sourced sparse CDM tables interpolated by GPR.",
        "Numerical CDM table covers arco_sul_tasto only; pp/mf/ff come from "
        "assumption-based extrapolation workbooks (not Zenodo-measured CDM).",
        "Other registry supported_techniques are organological capabilities without "
        "technique-specific table rows.",
    ),
    aliases=("viola_sul_tasto", "Viola_sul_tasto", "viola sul tasto", "sul tasto viola", "sul_tasto_viola"),
)


REGISTRY["viola_sul_ponticello"] = _profile(
    "viola_sul_ponticello",
    "Viola sul ponticello",
    "strings",
    sounding=(48, 96),
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
        "Sparse GPR table in instrumentos/viola_sul_ponticello.py from Strings Techniques "
        "Extrapolation Viola_pp.xlsx / Viola_mf.xlsx / Viola_ff.xlsx "
        "(assumption-based EWSD; pp/mf/ff from estimate_mean)."
    ),
    warnings=(
        "String density uses externally sourced sparse CDM tables interpolated by GPR.",
        "Numerical CDM table covers arco_sul_ponticello only; pp/mf/ff come from "
        "assumption-based extrapolation workbooks (not Zenodo-measured CDM).",
        "Other registry supported_techniques are organological capabilities without "
        "technique-specific table rows.",
    ),
    aliases=("viola_sul_ponticello", "Viola_sul_ponticello", "viola sul pont", "viola_sul_pont", "viola sul ponticello", "sul ponticello viola", "sul_ponticello_viola"),
)

REGISTRY["violino_sordina"] = _profile(
    "violino_sordina",
    "Violin sordina",
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
        "Sparse GPR table in instrumentos/violin_sordina.py from IOWA+ORCH arco sordina "
        "Combined Density Metric combined_sord_collection_raw (pp/mf/ff); not a full measured spectrum."
    ),
    warnings=(
        "String density uses externally sourced sparse CDM tables interpolated by GPR.",
        "Numerical CDM table covers arco_sordina only; other registry supported_techniques "
        "are organological capabilities without technique-specific table rows.",
    ),
    aliases=(
        "violin_sordina",
        "Violin_sordina",
        "violin con sordina",
        "violin_con_sordina",
        "violino sordina",
        "violino_sordina",
        "violino con sordina",
        "violino_con_sordina",
        "violin muted",
        "muted violin",
    ),
)

REGISTRY["violino_sul_ponticello"] = _profile(
    "violino_sul_ponticello",
    "Violin sul ponticello",
    "strings",
    sounding=(55, 103),
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
        "Sparse GPR table in instrumentos/violin_sul_ponticello.py with measured mf CDM "
        "anchor only; pp/ff extrapolated from violin arco per-note dynamic ratios."
    ),
    warnings=(
        "String density uses externally sourced sparse CDM tables interpolated by GPR.",
        "Numerical CDM table covers arco_sul_ponticello only; mf/ff come from assumption-based "
        "extrapolation workbooks; pp anchors are extrapolated from mf using violin arco ratios.",
        "Other registry supported_techniques are organological capabilities without "
        "technique-specific table rows.",
    ),
    aliases=(
        "violin_sul_ponticello",
        "Violin_sul_ponticello",
        "violin sul pont",
        "violin_sul_pont",
        "violino sul ponticello",
        "violino_sul_ponticello",
        "sul ponticello violin",
        "sul_ponticello_violin",
    ),
)


REGISTRY["violino_sul_tasto"] = _profile(
    "violino_sul_tasto",
    "Violin sul tasto",
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
        "Sparse GPR table in instrumentos/violin_sul_tasto.py from Strings Techniques "
        "Extrapolation Violin_mf.xlsx / Violin_ff.xlsx (assumption-based EWSD); "
        "pp derived from violin arco per-note dynamic ratios."
    ),
    warnings=(
        "String density uses externally sourced sparse CDM tables interpolated by GPR.",
        "Numerical CDM table covers arco_sul_tasto only; mf/ff come from assumption-based "
        "extrapolation workbooks; pp anchors are extrapolated from mf using violin arco ratios.",
        "Other registry supported_techniques are organological capabilities without "
        "technique-specific table rows.",
    ),
    aliases=(
        "violin_sul_tasto",
        "Violin_sul_tasto",
        "violin sul tasto",
        "violino sul tasto",
        "violino_sul_tasto",
        "sul tasto violin",
        "sul_tasto_violin",
    ),
)

REGISTRY["violino_art_harm"] = _profile(
    "violino_art_harm",
    "Violin art harm",
    "strings",
    sounding=(79, 103),
    comfortable=(79, 96),
    brightness="bright",
    sustain="sustained",
    attack="soft",
    status="literature_derived",
    uncertainty="high",
    module_name="violin_art_harm",
    supported=("arco", "harmonic"),
    unsupported=("pizzicato", "mute", "sul_ponticello", "sul_tasto"),
    source_notes=(
        "Sparse GPR table in instrumentos/violin_art_harm.py with measured mf CDM "
        "anchor only (G5–G7); pp/ff extrapolated from violin arco per-note dynamic ratios."
    ),
    warnings=(
        "String density uses externally sourced sparse CDM tables interpolated by GPR.",
        "Numerical CDM table covers arco_artificial_harmonic only; pp/ff anchors are "
        "extrapolated from mf using violin arco dynamic ratios.",
        "Table span is upper register only (G5–G7); notes outside this range use "
        "controlled pitch extrapolation or fallback.",
        "Other registry supported_techniques are organological capabilities without "
        "technique-specific table rows.",
    ),
    aliases=(
        "violin_art_harm",
        "Violin_art_harm",
        "violin artificial harmonics",
        "violin_artificial_harmonics",
        "violino art harm",
        "violino_art_harm",
        "violino artificial harmonics",
        "art harm violin",
        "art_harm_violin",
    ),
)


REGISTRY["violoncelo_sordina"] = _profile(
    "violoncelo_sordina",
    "Cello sordina",
    "strings",
    sounding=(36, 84),
    comfortable=(40, 65),
    brightness="neutral",
    sustain="sustained",
    attack="soft",
    status="literature_derived",
    uncertainty="high",
    module_name="cello_sordina",
    supported=("arco", "mute"),
    unsupported=("pizzicato", "sul_ponticello", "sul_tasto"),
    source_notes=(
        "Sparse GPR table in instrumentos/cello_sordina.py from Strings Techniques "
        "Extrapolation Cello_pp.xlsx / Cello_mf.xlsx / Cello_ff.xlsx "
        "(assumption-based EWSD; pp/mf/ff from estimate_mean)."
    ),
    warnings=(
        "String density uses externally sourced sparse CDM tables interpolated by GPR.",
        "Numerical CDM table covers arco_sordina only; pp/mf/ff come from "
        "assumption-based extrapolation workbooks (not Zenodo-measured CDM).",
        "Other registry supported_techniques are organological capabilities without "
        "technique-specific table rows.",
    ),
    aliases=("cello_sordina", "Cello_sordina", "cello con sordina", "cello_con_sordina", "cello sordina", "violoncelo sordina", "violoncelo_sordina", "cello muted", "muted cello"),
)


REGISTRY["violoncelo_sul_tasto"] = _profile(
    "violoncelo_sul_tasto",
    "Cello sul tasto",
    "strings",
    sounding=(36, 84),
    comfortable=(40, 65),
    brightness="dark",
    sustain="sustained",
    attack="soft",
    status="literature_derived",
    uncertainty="high",
    module_name="cello_sul_tasto",
    supported=("arco", "sul_tasto"),
    unsupported=("pizzicato", "mute", "sul_ponticello"),
    source_notes=(
        "Sparse GPR table in instrumentos/cello_sul_tasto.py from Strings Techniques "
        "Extrapolation Cello_pp.xlsx / Cello_mf.xlsx / Cello_ff.xlsx "
        "(assumption-based EWSD; pp/mf/ff from estimate_mean)."
    ),
    warnings=(
        "String density uses externally sourced sparse CDM tables interpolated by GPR.",
        "Numerical CDM table covers arco_sul_tasto only; pp/mf/ff come from "
        "assumption-based extrapolation workbooks (not Zenodo-measured CDM).",
        "Other registry supported_techniques are organological capabilities without "
        "technique-specific table rows.",
    ),
    aliases=("cello_sul_tasto", "Cello_sul_tasto", "cello sul tasto", "violoncelo sul tasto", "violoncelo_sul_tasto", "sul tasto cello", "sul_tasto_cello"),
)


REGISTRY["violoncelo_sul_ponticello"] = _profile(
    "violoncelo_sul_ponticello",
    "Cello sul ponticello",
    "strings",
    sounding=(36, 84),
    comfortable=(40, 65),
    brightness="bright",
    sustain="sustained",
    attack="hard",
    status="literature_derived",
    uncertainty="high",
    module_name="cello_sul_ponticello",
    supported=("arco", "sul_ponticello"),
    unsupported=("pizzicato", "mute", "sul_tasto"),
    source_notes=(
        "Sparse GPR table in instrumentos/cello_sul_ponticello.py from Strings Techniques "
        "Extrapolation Cello_pp.xlsx / Cello_mf.xlsx / Cello_ff.xlsx "
        "(assumption-based EWSD; pp/mf/ff from estimate_mean)."
    ),
    warnings=(
        "String density uses externally sourced sparse CDM tables interpolated by GPR.",
        "Numerical CDM table covers arco_sul_ponticello only; pp/mf/ff come from "
        "assumption-based extrapolation workbooks (not Zenodo-measured CDM).",
        "Other registry supported_techniques are organological capabilities without "
        "technique-specific table rows.",
    ),
    aliases=("cello_sul_ponticello", "Cello_sul_ponticello", "cello sul pont", "cello_sul_pont", "cello sul ponticello", "violoncelo sul ponticello", "violoncelo_sul_ponticello", "sul ponticello cello", "sul_ponticello_cello"),
)


REGISTRY["contrabaixo_sordina"] = _profile(
    "contrabaixo_sordina",
    "Double bass sordina",
    "strings",
    sounding=(28, 72),
    comfortable=(31, 55),
    brightness="neutral",
    sustain="sustained",
    attack="soft",
    status="literature_derived",
    uncertainty="high",
    module_name="double_bass_sordina",
    supported=("arco", "mute"),
    unsupported=("pizzicato", "sul_ponticello", "sul_tasto"),
    source_notes=(
        "Sparse GPR table in instrumentos/double_bass_sordina.py from Strings Techniques "
        "Extrapolation Contrabass-pp.xlsx / Contrabass_mf.xlsx / Contrabass_ff.xlsx "
        "(assumption-based EWSD; pp/mf/ff from estimate_mean)."
    ),
    warnings=(
        "String density uses externally sourced sparse CDM tables interpolated by GPR.",
        "Numerical CDM table covers arco_sordina only; pp/mf/ff come from "
        "assumption-based extrapolation workbooks (not Zenodo-measured CDM).",
        "Other registry supported_techniques are organological capabilities without "
        "technique-specific table rows.",
    ),
    aliases=("double_bass_sordina", "Double_bass_sordina", "double bass sordina", "contrabass sordina", "contrabass_sordina", "contrabaixo sordina", "contrabaixo_sordina", "bass sordina", "muted double bass", "muted contrabass"),
)


REGISTRY["contrabaixo_sul_tasto"] = _profile(
    "contrabaixo_sul_tasto",
    "Double bass sul tasto",
    "strings",
    sounding=(28, 72),
    comfortable=(31, 55),
    brightness="dark",
    sustain="sustained",
    attack="soft",
    status="literature_derived",
    uncertainty="high",
    module_name="double_bass_sul_tasto",
    supported=("arco", "sul_tasto"),
    unsupported=("pizzicato", "mute", "sul_ponticello"),
    source_notes=(
        "Sparse GPR table in instrumentos/double_bass_sul_tasto.py from Strings Techniques "
        "Extrapolation Contrabass-pp.xlsx / Contrabass_mf.xlsx / Contrabass_ff.xlsx "
        "(assumption-based EWSD; pp/mf/ff from estimate_mean)."
    ),
    warnings=(
        "String density uses externally sourced sparse CDM tables interpolated by GPR.",
        "Numerical CDM table covers arco_sul_tasto only; pp/mf/ff come from "
        "assumption-based extrapolation workbooks (not Zenodo-measured CDM).",
        "Other registry supported_techniques are organological capabilities without "
        "technique-specific table rows.",
    ),
    aliases=("double_bass_sul_tasto", "Double_bass_sul_tasto", "double bass sul tasto", "contrabass sul tasto", "contrabass_sul_tasto", "contrabaixo sul tasto", "contrabaixo_sul_tasto", "sul tasto double bass", "sul_tasto_double_bass"),
)


REGISTRY["contrabaixo_sul_ponticello"] = _profile(
    "contrabaixo_sul_ponticello",
    "Double bass sul ponticello",
    "strings",
    sounding=(28, 72),
    comfortable=(31, 55),
    brightness="bright",
    sustain="sustained",
    attack="hard",
    status="literature_derived",
    uncertainty="high",
    module_name="double_bass_sul_ponticello",
    supported=("arco", "sul_ponticello"),
    unsupported=("pizzicato", "mute", "sul_tasto"),
    source_notes=(
        "Sparse GPR table in instrumentos/double_bass_sul_ponticello.py from Strings Techniques "
        "Extrapolation Contrabass-pp.xlsx / Contrabass_mf.xlsx / Contrabass_ff.xlsx "
        "(assumption-based EWSD; pp/mf/ff from estimate_mean)."
    ),
    warnings=(
        "String density uses externally sourced sparse CDM tables interpolated by GPR.",
        "Numerical CDM table covers arco_sul_ponticello only; pp/mf/ff come from "
        "assumption-based extrapolation workbooks (not Zenodo-measured CDM).",
        "Other registry supported_techniques are organological capabilities without "
        "technique-specific table rows.",
    ),
    aliases=("double_bass_sul_ponticello", "Double_bass_sul_ponticello", "double bass sul ponticello", "contrabass sul ponticello", "contrabass_sul_ponticello", "contrabaixo sul ponticello", "contrabaixo_sul_ponticello", "sul ponticello double bass", "sul_ponticello_double_bass"),
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
    source_notes=(
        "Coarse brass profile without committed acoustic CDM table. "
        "sounding_range (MIDI 28–58) is a provisional validation placeholder — not source-table validated."
    ),
    warnings=(
        "Tuba spectral density uses coarse register/dynamic proxy only; range metadata requires organological review.",
    ),
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
