# xml_loader.py
"""
Carrega dados de análise de densidade a partir de um ficheiro XML.
O formato é compatível com a estrutura esperada por get_input_data() da GUI.
"""

import logging
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.converters import make_instrument_event
from microtonal import midi_to_note_name, note_to_midi
from core.defaults import RESEARCH_ANALYSIS_DEFAULTS, apply_research_defaults
from core.input_validation import strip_removed_gui_preference_keys
from core.models import InstrumentEvent
from utils.notes import extract_cents, normalize_note_string

logger = logging.getLogger(__name__)

# Mapeamento de nota base (ASCII) para o símbolo usado na GUI (Unicode ♯)
_NOTE_BASE_TO_GUI = {
    "C": "C",
    "C#": "C♯",
    "D": "D",
    "D#": "D♯",
    "E": "E",
    "F": "F",
    "F#": "F♯",
    "G": "G",
    "G#": "G♯",
    "A": "A",
    "A#": "A♯",
    "B": "B",
}


def _parse_note_to_gui_parts(note_str: str):
    """
    Converte uma string de nota (ex: C4, C#4, C4+25c) em partes para a GUI:
    (note_base_gui, octave_str, cents_str).
    """
    if not note_str or not note_str.strip():
        return "C", "4", "0"
    note_str = normalize_note_string(note_str.strip())
    base_note, cents = extract_cents(note_str)
    # base_note é ex: "C4", "C#4"
    m = re.match(r"^([A-G]#?)(\d+)$", base_note)
    if not m:
        return "C", "4", "0"
    base, octave = m.groups()
    gui_base = _NOTE_BASE_TO_GUI.get(base, base)
    cents_str = str(cents) if cents != 0 else "0"
    if cents > 0:
        cents_str = f"+{cents}"
    elif cents < 0:
        cents_str = str(cents)
    return gui_base, octave, cents_str


def _text(el, default=""):
    if el is None:
        return default
    return (el.text or "").strip() or default


def _float_attr(el, default=0.0):
    try:
        return float(_text(el, str(default)))
    except ValueError:
        return default


def _bool_attr(el, default=True):
    t = _text(el).lower()
    if t in ("1", "true", "yes", "on"):
        return True
    if t in ("0", "false", "no", "off"):
        return False
    return default


# Mapeamento MusicXML dynamics -> nosso formato
_MUSICXML_DYNAMICS = {
    "pppp": "pppp",
    "ppp": "ppp",
    "pp": "pp",
    "p": "p",
    "mf": "mf",
    "mp": "mf",
    "f": "f",
    "ff": "ff",
    "fff": "fff",
    "ffff": "ffff",
}


def _musicxml_pitch_to_note(pitch_el, accidental_el=None):
    """Converte elemento <pitch> (step, alter, octave) + opcional accidental em string C4, C#4, etc."""
    if pitch_el is None:
        return "C4"
    step_el = pitch_el.find("step")
    octave_el = pitch_el.find("octave")
    alter_el = pitch_el.find("alter")
    step = _text(step_el, "C").upper()
    octave = _text(octave_el, "4")
    alter = 0
    if alter_el is not None and _text(alter_el):
        try:
            alter = int(float(_text(alter_el)))
        except ValueError:
            pass
    # Microtonal a partir de accidental (MusicXML)
    cents = 0
    if accidental_el is not None:
        acc = _text(accidental_el).lower()
        if "quarter-flat" in acc or acc == "flat-down":
            cents = -25
        elif "quarter-sharp" in acc or acc == "sharp-up":
            cents = 25
        elif "three-quarters-sharp" in acc:
            cents = 75
        elif "three-quarters-flat" in acc:
            cents = -75
    if cents != 0:
        base = step
        if alter == 1:
            base = step + "#"
        elif alter == -1:
            base = step + "b"
        note = f"{base}{octave}"
        sign = "+" if cents > 0 else ""
        return f"{note}{sign}{cents}c"
    if alter == 1:
        step = step + "#"
    elif alter == -1:
        step = step + "b"
    elif alter == 2:
        step = step + "##"
    elif alter == -2:
        step = step + "bb"
    return f"{step}{octave}"


@dataclass
class _ExtractedMusicXmlNote:
    """One MusicXML note: script (written) pitch is the analytical pitch."""

    written_note: str
    sounding_note: str
    dynamic: str
    part_id: str
    part_name: str
    transpose_semitones: int


# MusicXML may declare <transpose> for concert-pitch export; this project analyses
# the pitches as notated on each part (script pitch), so offsets are not applied.
_APPLY_MUSICXML_TRANSPOSE = False


def _transpose_semitones_from_attributes(attributes_el) -> int | None:
    """
    Concert-pitch offset from MusicXML ``<attributes><transpose>``.

    sounding_midi = written_midi + chromatic + 12 * octave_change
    """
    if attributes_el is None:
        return None
    transpose_el = attributes_el.find("transpose")
    if transpose_el is None:
        return None
    chromatic = 0
    chrom_el = transpose_el.find("chromatic")
    if chrom_el is not None and _text(chrom_el):
        try:
            chromatic = int(float(_text(chrom_el)))
        except ValueError:
            pass
    octave_change = 0
    oct_el = transpose_el.find("octave-change")
    if oct_el is not None and _text(oct_el):
        try:
            octave_change = int(float(_text(oct_el)))
        except ValueError:
            pass
    return chromatic + 12 * octave_change


def _apply_semitone_transpose(note_str: str, semitones: int) -> str:
    """Map a written note string to concert/sounding pitch."""
    if semitones == 0:
        return note_str
    shifted = note_to_midi(note_str) + semitones
    _, cents = extract_cents(normalize_note_string(note_str))
    if abs(cents) > 0 or abs(shifted - round(shifted)) > 1e-6:
        return midi_to_note_name(shifted, include_cents=True)
    return midi_to_note_name(shifted)


def _extract_musicxml_notes(root) -> list[_ExtractedMusicXmlNote]:
    """
    Parse score-partwise / score-timewise MusicXML into note records.

    Notes are taken **as written on the part** (script pitch). Declared ``<transpose>``
    elements are recorded in metadata but not applied unless ``_APPLY_MUSICXML_TRANSPOSE``
    is enabled.
    """
    part_list = root.find("part-list")
    part_names: dict[str, str] = {}
    if part_list is not None:
        for sp in part_list.findall("score-part"):
            pid = sp.get("id")
            if pid:
                part_names[pid] = _text(sp.find("part-name"), "Part")

    extracted: list[_ExtractedMusicXmlNote] = []

    def collect_notes_from_measure(
        measure,
        part_id: str,
        part_name: str,
        part_state: dict[str, Any],
    ) -> None:
        cur_dyn = part_state["dynamic"]
        for el in measure:
            if el.tag == "attributes":
                offset = _transpose_semitones_from_attributes(el)
                if offset is not None:
                    part_state["transpose"] = offset
            elif el.tag == "direction":
                for dtype in el.findall("direction-type"):
                    dyn_el = dtype.find("dynamics")
                    if dyn_el is not None:
                        for d in ("pppp", "ppp", "pp", "p", "mp", "mf", "f", "ff", "fff", "ffff"):
                            if dyn_el.find(d) is not None:
                                cur_dyn = _MUSICXML_DYNAMICS.get(d, d)
                                break
                part_state["dynamic"] = cur_dyn
            elif el.tag == "note":
                if el.find("rest") is not None:
                    continue
                pitch = el.find("pitch")
                if pitch is None:
                    continue
                acc_el = el.find("accidental")
                written = _musicxml_pitch_to_note(pitch, acc_el)
                transpose = int(part_state["transpose"])
                if _APPLY_MUSICXML_TRANSPOSE:
                    sounding = _apply_semitone_transpose(written, transpose)
                else:
                    sounding = written
                extracted.append(
                    _ExtractedMusicXmlNote(
                        written_note=written,
                        sounding_note=sounding,
                        dynamic=cur_dyn,
                        part_id=part_id or "",
                        part_name=part_name,
                        transpose_semitones=transpose,
                    )
                )

    parts = root.findall("part")
    if parts:
        for part in parts:
            part_id = part.get("id") or ""
            part_name = part_names.get(part_id, "Flute")
            part_state = {"dynamic": "mf", "transpose": 0}
            for measure in part.findall("measure"):
                collect_notes_from_measure(measure, part_id, part_name, part_state)
    else:
        for measure in root.findall("measure"):
            for part in measure.findall("part"):
                part_id = part.get("id") or ""
                part_name = part_names.get(part_id, "Flute")
                part_state = {"dynamic": "mf", "transpose": 0}
                collect_notes_from_measure(part, part_id, part_name, part_state)

    return extracted


def _parse_musicxml(root) -> dict:
    """
    Interpreta MusicXML (score-partwise): part-list, part/measure/note, dynamics em direction.
    Retorna o mesmo dict que parse_xml (notes, dynamics, instruments, num_instruments, etc.).
    """
    extracted = _extract_musicxml_notes(root)
    if not extracted:
        notes = []
    else:
        notes = [n.sounding_note for n in extracted]
        if any(n.transpose_semitones != 0 for n in extracted):
            if _APPLY_MUSICXML_TRANSPOSE:
                logger.info(
                    "MusicXML transpose applied for concert pitch (%d note(s) with non-zero offset).",
                    sum(1 for n in extracted if n.transpose_semitones != 0),
                )
            else:
                logger.info(
                    "MusicXML <transpose> declared on %d note(s); using script pitch (not transposed).",
                    sum(1 for n in extracted if n.transpose_semitones != 0),
                )

    dynamics = [n.dynamic for n in extracted] if extracted else []
    instruments = [n.part_name for n in extracted] if extracted else []
    num_instruments = [1] * len(extracted) if extracted else []

    if not notes:
        raise ValueError("MusicXML não contém notas (apenas rests ou part-list vazio).")

    return apply_research_defaults(
        {
            "notes": notes,
            "dynamics": dynamics,
            "instruments": instruments,
            "num_instruments": num_instruments,
            "weight_factor": 0.5,
            "save_results": False,
            "show_graphs": True,
        }
    )


def parse_xml(filepath: str) -> dict:
    """
    Lê um ficheiro XML e devolve um dicionário no mesmo formato que get_input_data().

    Estrutura XML esperada:
        <densidade_analysis>
          <settings>
            <weight_factor>0.5</weight_factor>
            <lambda>0.05</lambda>
            <!-- opcional: tuning A4 em Hz -->
            <tuning_a4>440</tuning_a4>
          </settings>
          <voices>
            <voice>
              <note>C4</note>
              <dynamics>mf</dynamics>
              <instrument>Flute</instrument>
              <num_instruments>1</num_instruments>
            </voice>
            ...
          </voices>
        </densidade_analysis>

    Returns:
        dict com keys: notes, dynamics, instruments, num_instruments, weight_factor,
        weight_factor, save_results, show_graphs; opcional: lambda, tuning_a4.
        Legacy removed options (use_stevens, alpha, beta, use_psychoacoustic,
        use_perceptual_weighting) are stripped with a migration warning if present.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Ficheiro não encontrado: {filepath}")

    tree = ET.parse(path)
    root = tree.getroot()
    if root is None:
        raise ValueError("Ficheiro XML vazio ou inválido.")

    # Remover namespaces para que find("voices") etc. funcionem
    for el in root.iter():
        if el.tag and "}" in el.tag:
            el.tag = el.tag.split("}", 1)[1]

    # MusicXML (Sibelius, Finale, etc.): score-partwise ou score-timewise
    if root.tag in ("score-partwise", "score-timewise"):
        return _parse_musicxml(root)

    if root.tag != "densidade_analysis":
        candidate = root.find("densidade_analysis")
        if candidate is not None:
            root = candidate
        elif root.find("voices") is None and root.find("settings") is None:
            raise ValueError(
                "XML deve ser MusicXML (score-partwise) ou ter elemento raiz <densidade_analysis> com <voices> ou <settings>."
            )
    settings = root.find("settings")
    voices_el = root.find("voices")

    notes = []
    dynamics = []
    instruments = []
    num_instruments = []

    if voices_el is not None:
        for voice in voices_el.findall("voice"):
            note_el = voice.find("note") or voice.find("pitch")
            dyn_el = voice.find("dynamics") or voice.find("dynamic")
            inst_el = voice.find("instrument") or voice.find("instrumento")
            num_el = (
                voice.find("num_instruments")
                or voice.find("num_instruments")
                or voice.find("quantity")
            )

            n = _text(note_el, "C4")
            d = _text(dyn_el, "mf")
            i = _text(inst_el, "Flute")
            num = _text(num_el, "1")
            try:
                num = max(1, min(20, int(num)))
            except ValueError:
                num = 1

            notes.append(n)
            dynamics.append(d)
            instruments.append(i)
            num_instruments.append(num)

    if not notes:
        raise ValueError("XML deve conter pelo menos um <voice> com <note> em <voices>.")

    options = _settings_to_options(settings)
    out = {
        "notes": notes,
        "dynamics": dynamics,
        "instruments": instruments,
        "num_instruments": num_instruments,
        **{k: v for k, v in options.items() if k not in ("lambda", "tuning_a4")},
    }
    if "lambda" in options:
        out["lambda"] = options["lambda"]
    if "tuning_a4" in options:
        out["tuning_a4"] = options["tuning_a4"]

    logger.info(f"XML loaded: {path.name}, {len(notes)} voice(s).")
    return out


def _finalize_loader_options(raw: dict[str, Any]) -> dict[str, Any]:
    """Strip removed legacy keys and apply research defaults."""
    cleaned, stripped = strip_removed_gui_preference_keys(raw)
    if stripped:
        logger.warning(
            "Legacy XML settings contained removed options (stripped, not passed to analysis): %s",
            ", ".join(sorted(stripped)),
        )
    return apply_research_defaults(cleaned)


def _settings_to_options(settings) -> dict[str, Any]:
    """Extract analysis options from <settings> element."""
    weight_factor = RESEARCH_ANALYSIS_DEFAULTS["weight_factor"]
    save_results = RESEARCH_ANALYSIS_DEFAULTS["save_results"]
    show_graphs = True
    raw_legacy: dict[str, Any] = {}

    if settings is not None:
        weight_factor = _float_attr(settings.find("weight_factor"), weight_factor)
        weight_factor = max(0.0, min(1.0, weight_factor))
        save_results = _bool_attr(settings.find("save_results"), save_results)
        show_graphs = _bool_attr(settings.find("show_graphs"), show_graphs)
        for tag in (
            "use_stevens",
            "alpha",
            "beta",
            "use_psychoacoustic",
            "use_perceptual_weighting",
            "calculate_combination_tones",
            "combination_tones",
            "resultant_tones",
            "include_resultants",
            "include_combination_tones",
            "virtual_tones",
            "generated_tones",
        ):
            el = settings.find(tag)
            if el is not None and _text(el):
                if tag in (
                    "use_stevens",
                    "use_psychoacoustic",
                    "use_perceptual_weighting",
                    "calculate_combination_tones",
                    "include_resultants",
                    "include_combination_tones",
                ):
                    raw_legacy[tag] = _bool_attr(el, False)
                elif tag in ("combination_tones", "resultant_tones", "virtual_tones", "generated_tones"):
                    raw_legacy[tag] = _text(el)
                else:
                    raw_legacy[tag] = _float_attr(el, 0.0)

    options = {
        "weight_factor": weight_factor,
        "save_results": save_results,
        "show_graphs": show_graphs,
        **raw_legacy,
    }
    if settings is not None:
        lamb_el = settings.find("lambda")
        if lamb_el is not None and _text(lamb_el):
            try:
                options["lambda"] = _float_attr(lamb_el, 0.05)
            except ValueError:
                pass
        tuning_el = settings.find("tuning_a4") or settings.find("tuning")
        if tuning_el is not None and _text(tuning_el):
            try:
                options["tuning_a4"] = _float_attr(tuning_el, 440.0)
            except ValueError:
                pass
    return _finalize_loader_options(options)


def _optional_float(el) -> float | None:
    if el is None or not _text(el):
        return None
    try:
        return float(_text(el))
    except ValueError:
        return None


def parse_xml_to_events(filepath: str) -> tuple[list[InstrumentEvent], dict[str, Any], list[str]]:
    """
    Parse custom densidade XML (and untimed MusicXML) into InstrumentEvent list.

    Custom ``<voice>`` elements may include optional ``<onset>``, ``<duration>``,
    or ``<offset>`` (seconds). MusicXML without explicit timing yields untimed events.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Ficheiro não encontrado: {filepath}")

    tree = ET.parse(path)
    root = tree.getroot()
    if root is None:
        raise ValueError("Ficheiro XML vazio ou inválido.")

    for el in root.iter():
        if el.tag and "}" in el.tag:
            el.tag = el.tag.split("}", 1)[1]

    warnings: list[str] = []

    if root.tag in ("score-partwise", "score-timewise"):
        extracted = _extract_musicxml_notes(root)
        if not extracted:
            raise ValueError("MusicXML não contém notas (apenas rests ou part-list vazio).")
        warnings.append(
            "MusicXML loaded without measure timing; treated as a single vertical slice."
        )
        if any(n.transpose_semitones != 0 for n in extracted):
            if _APPLY_MUSICXML_TRANSPOSE:
                warnings.append(
                    "Concert pitch derived from MusicXML <transpose> (chromatic + octave-change)."
                )
            else:
                warnings.append(
                    "MusicXML <transpose> declared but not applied; notes use script pitch "
                    "as written on the part."
                )
        events = [
            make_instrument_event(
                idx=idx,
                note=n.sounding_note,
                written_note=n.written_note if n.written_note != n.sounding_note else None,
                dynamic=n.dynamic,
                instrument_name=n.part_name,
                player_count=1,
                part_id=n.part_id or None,
                metadata={
                    "source": "musicxml",
                    "transpose_semitones": n.transpose_semitones,
                },
            )
            for idx, n in enumerate(extracted)
        ]
        options = apply_research_defaults(
            {
                "weight_factor": 0.5,
                "save_results": False,
                "show_graphs": True,
            }
        )
        return events, options, warnings

    if root.tag != "densidade_analysis":
        candidate = root.find("densidade_analysis")
        if candidate is not None:
            root = candidate
        elif root.find("voices") is None and root.find("settings") is None:
            raise ValueError(
                "XML must be MusicXML (score-partwise) or have root <densidade_analysis>."
            )

    settings = root.find("settings")
    options = _settings_to_options(settings)
    voices_el = root.find("voices")
    events: list[InstrumentEvent] = []

    if voices_el is not None:
        for idx, voice in enumerate(voices_el.findall("voice")):
            note_el = voice.find("note") or voice.find("pitch")
            dyn_el = voice.find("dynamics") or voice.find("dynamic")
            inst_el = voice.find("instrument") or voice.find("instrumento")
            num_el = voice.find("num_instruments") or voice.find("quantity")
            onset_el = voice.find("onset")
            duration_el = voice.find("duration")
            offset_el = voice.find("offset")

            n = _text(note_el, "C4")
            d = _text(dyn_el, "mf")
            i = _text(inst_el, "Flute")
            num = _text(num_el, "1")
            try:
                num_i = max(1, min(20, int(num)))
            except ValueError:
                num_i = 1

            events.append(
                make_instrument_event(
                    idx=idx,
                    note=n,
                    dynamic=d,
                    instrument_name=i,
                    player_count=num_i,
                    onset=_optional_float(onset_el),
                    offset=_optional_float(offset_el),
                    duration=_optional_float(duration_el),
                    metadata={"source": "custom_xml"},
                )
            )

    if not events:
        raise ValueError("XML must contain at least one <voice> with <note>.")

    if not any(ev.onset is not None for ev in events):
        warnings.append(
            "No <onset> metadata in XML voices; score will be analysed as one slice."
        )

    logger.info("XML loaded (events): %s, %d event(s).", path.name, len(events))
    return events, options, warnings


def note_string_to_gui_parts(note_str: str) -> tuple:
    """
    Convert a note string (e.g. C4, C#4+25c) to (note_base_gui, octave, cents_str)
    for filling GUI fields.
    """
    return _parse_note_to_gui_parts(note_str)
