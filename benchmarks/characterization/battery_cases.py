"""Characterization battery — pure DATA layer.

Defines the parametrized case list (ids, descriptions, inputs) exercised by
``run_battery.py``. This module contains **no** config mutation, no thresholds,
and no calls to ``calculate_metrics``. Instrument roles are injected by the
runner as a resolved ``roles`` map (role token -> concrete registry id), so this
file stays independent of registry resolution and substitution policy.

Pitch construction helpers use strict microtonal parsing with round-trip
assertions, so any EDO/cents pitch emitted here is guaranteed valid. Literal
pitch strings are stored verbatim and are strict-validated by the runner (so a
malformed literal is recorded under ERRORS rather than aborting the build).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from microtonal import (
    format_cents_suffix,
    midi_to_note_name,
    note_to_midi,
    note_to_midi_strict,
)

# Role token -> preferred registry keys (attempted in order, else POOL fallback).
ROLE_PREFERENCES: dict[str, list[str]] = {
    "WW_HI": ["flautim", "flauta"],
    "WW_MID": ["clarinete", "Oboe"],
    "WW_LO": ["fagote", "contrafagote"],
    "BRASS": ["trompete", "trombone"],
    "STR_HI": ["violino"],
    "STR_LO": ["double_bass", "contrabaixo", "violoncelo"],
}


def P(s: str) -> str:
    """Validate a literal pitch; raise loudly on malformed input (never silent C4)."""
    note_to_midi(s, strict=True)
    return s


def edo_pitch(root_midi: float, n_edo: int, k: int) -> str:
    """k-th degree of n-EDO from ``root_midi``, anchored to nearest semitone + cents."""
    target = root_midi + k * (1200.0 / n_edo) / 100.0
    nearest = round(target)
    residual_cents = (target - nearest) * 100.0
    s = midi_to_note_name(nearest) + format_cents_suffix(residual_cents)
    assert abs(note_to_midi(s, strict=True) - target) < 1e-6, (s, target)
    return s


def edo_scale(root: str, n_edo: int, degrees: list[int]) -> list[str]:
    rm = note_to_midi(P(root), strict=True)
    return [edo_pitch(rm, n_edo, k) for k in degrees]


def cents_pitch(root_midi: float, cents: float) -> str:
    """Pitch at ``cents`` above ``root_midi`` (anchored to nearest semitone + residual)."""
    target = root_midi + cents / 100.0
    nearest = round(target)
    residual_cents = (target - nearest) * 100.0
    s = midi_to_note_name(nearest) + format_cents_suffix(residual_cents)
    assert abs(note_to_midi_strict(s) - target) < 1e-6, (s, target)
    return s


@dataclass
class Case:
    """One characterization case. dynamics/num_instruments default at run time.

    When ``auto`` is true, ``instruments`` is ignored and the runner assigns a
    register-appropriate module-backed instrument to each note (logging the full
    pitch->instrument map). A note that no module-backed instrument can cover
    raises ``CaseSetupError`` in the runner and is recorded under ERRORS.
    """

    id: str
    category: str
    description: str
    notes: list[str]
    instruments: list[str]
    dynamics: list[str] | None = None
    num_instruments: list[int] | None = None
    weight_factor: float = 0.5
    probe: dict[str, Any] | None = None
    auto: bool = False


def build_cases(roles: dict[str, str]) -> list[Case]:
    """Materialize the full battery given a resolved role->instrument map."""

    def rep(role: str, n: int) -> list[str]:
        return [roles[role]] * n

    C4 = note_to_midi_strict("C4")
    C2 = note_to_midi_strict("C2")
    cases: list[Case] = []

    # ---------------------------------------------------------------- MORPH
    cat = "MORPH"
    cases.append(Case("MORPH.single", cat, "single pitch", ["C4"], rep("WW_HI", 1)))
    dyads = [
        ("min2", "C#4"), ("maj2", "D4"), ("M3", "E4"), ("tritone", "F#4"),
        ("P5", "G4"), ("8ve", "C5"), ("2x8ve", "C6"), ("3x8ve", "C7"),
    ]
    for name, top in dyads:
        cases.append(Case(f"MORPH.dyad_{name}", cat, f"dyad C4-{top} ({name})",
                          ["C4", top], rep("WW_HI", 2)))
    clusters = {3: ["C4", "C#4", "D4"],
                5: ["C4", "C#4", "D4", "D#4", "E4"],
                7: ["C4", "C#4", "D4", "D#4", "E4", "F4", "F#4"],
                12: ["C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", "B4"]}
    for size, notes in clusters.items():
        cases.append(Case(f"MORPH.cluster_{size}", cat, f"{size}-semitone chromatic cluster from C4",
                          notes, rep("WW_HI", len(notes))))
    triads = {"major": ["C4", "E4", "G4"], "minor": ["C4", "D#4", "G4"],
              "dim": ["C4", "D#4", "F#4"], "aug": ["C4", "E4", "G#4"]}
    for name, notes in triads.items():
        cases.append(Case(f"MORPH.triad_{name}", cat, f"{name} triad on C4", notes, rep("WW_HI", 3)))
    cases.append(Case("MORPH.dom7", cat, "dominant 7th", ["C4", "E4", "G4", "A#4"], rep("WW_HI", 4)))
    cases.append(Case("MORPH.maj9", cat, "major 9th", ["C4", "E4", "G4", "B4", "D5"], rep("WW_HI", 5)))
    cases.append(Case("MORPH.quartal", cat, "quartal stack", ["C4", "F4", "A#4", "D#5"], rep("WW_HI", 4)))
    cases.append(Case("MORPH.wide_triad", cat, "wide-spaced triad", ["C4", "E5", "G6"], rep("WW_HI", 3)))
    cases.append(Case("MORPH.very_spacious", cat, "very spacious voicing", ["C2", "G3", "D5", "A6"], rep("WW_HI", 4)))
    cases.append(Case("MORPH.extreme_span", cat, "extreme span dyad", ["C0", "C8"], rep("WW_HI", 2)))
    cases.append(Case("MORPH.low_cluster", cat, "low-register cluster", ["C1", "C#1", "D1"], rep("WW_HI", 3)))
    cases.append(Case("MORPH.high_cluster", cat, "high-register cluster", ["C7", "C#7", "D7"], rep("WW_HI", 3)))
    cases.append(Case("MORPH.full_range", cat, "full-range octaves", ["C1", "C3", "C5", "C7"], rep("WW_HI", 4)))

    # ---------------------------------------------------------------- CARD
    cat = "CARD"
    compact_seq = ["C4", "C#4", "D4", "D#4", "E4", "F4", "F#4"]
    for k in range(1, 8):
        notes = compact_seq[:k]
        cases.append(Case(f"CARD.compact_n{k}", cat, f"compact growth n={k}", notes,
                          rep("WW_HI", k), probe={"group": "card_compact", "order": k}))
    wide_base = ["C4", "C5"]
    wide_appends = ["E6", "G3", "B7", "D2"]
    for i in range(len(wide_appends) + 1):
        notes = wide_base + wide_appends[:i]
        n = len(notes)
        cases.append(Case(f"CARD.wide_n{n}", cat, f"wide growth n={n}", notes,
                          rep("WW_HI", n), probe={"group": "card_wide", "order": n}))
    fb_base = ["C4", "D4", "E4", "F4", "A#4"]
    cases.append(Case("CARD.farbass_0", cat, "far-bass base (5 WW)", fb_base, rep("WW_HI", 5),
                      probe={"group": "card_farbass", "order": 1}))
    cases.append(Case("CARD.farbass_E1", cat, "far-bass +E1 (STR_LO)", fb_base + ["E1"],
                      rep("WW_HI", 5) + rep("STR_LO", 1), probe={"group": "card_farbass", "order": 2}))
    cases.append(Case("CARD.farbass_E0", cat, "far-bass +E1+E0 (STR_LO)", fb_base + ["E1", "E0"],
                      rep("WW_HI", 5) + rep("STR_LO", 2), probe={"group": "card_farbass", "order": 3}))

    # ---------------------------------------------------------------- INST
    cat = "INST"
    cases.append(Case("INST.homogeneous", cat, "3x WW_HI triad", ["C4", "E4", "G4"], rep("WW_HI", 3)))
    cases.append(Case("INST.contrasting", cat, "WW_HI + STR_LO extremes", ["C6", "C2"],
                      [roles["WW_HI"], roles["STR_LO"]]))
    cases.append(Case("INST.mixed_ww", cat, "WW hi/mid/lo", ["C6", "C4", "C2"],
                      [roles["WW_HI"], roles["WW_MID"], roles["WW_LO"]]))
    cases.append(Case("INST.full_ensemble", cat, "6-role full ensemble",
                      ["C7", "C5", "C4", "C3", "C2", "C1"],
                      [roles["WW_HI"], roles["WW_MID"], roles["WW_LO"], roles["BRASS"],
                       roles["STR_HI"], roles["STR_LO"]]))
    cases.append(Case("INST.timbre_iso_ww", cat, "triad as 3x WW_HI (timbre iso A)",
                      ["C4", "E4", "G4"], rep("WW_HI", 3), probe={"group": "timbre_iso", "order": 1}))
    cases.append(Case("INST.timbre_iso_mixed", cat, "triad as WW_HI/STR_HI/WW_LO (timbre iso B)",
                      ["C4", "E4", "G4"], [roles["WW_HI"], roles["STR_HI"], roles["WW_LO"]],
                      probe={"group": "timbre_iso", "order": 2}))
    cases.append(Case("INST.string_choir", cat, "string choir hi/hi/lo", ["C5", "G4", "C2"],
                      [roles["STR_HI"], roles["STR_HI"], roles["STR_LO"]]))
    cases.append(Case("INST.brass_triad", cat, "triad as 3x BRASS", ["C4", "E4", "G4"], rep("BRASS", 3),
                      probe={"group": "brass_vs_ww", "order": 1}))
    cases.append(Case("INST.ww_triad_ref", cat, "triad as 3x WW_HI (brass ref)", ["C4", "E4", "G4"],
                      rep("WW_HI", 3), probe={"group": "brass_vs_ww", "order": 2}))

    # ---------------------------------------------------------------- QTY
    cat = "QTY"
    triad = ["C4", "E4", "G4"]
    for q in (1, 2, 4, 8):
        cases.append(Case(f"QTY.q{q}", cat, f"triad Qty={q} each", triad, rep("WW_HI", 3),
                          num_instruments=[q, q, q]))
    cases.append(Case("QTY.rowsplit_single", cat, "one event Qty=3 (unison)", ["C4"], rep("WW_HI", 1),
                      num_instruments=[3], probe={"group": "qty_rowsplit", "role": "single"}))
    cases.append(Case("QTY.rowsplit_split", cat, "three events Qty=1 (unison)", ["C4", "C4", "C4"],
                      rep("WW_HI", 3), num_instruments=[1, 1, 1],
                      probe={"group": "qty_rowsplit", "role": "split"}))
    cases.append(Case("QTY.unison_multi_timbre", cat, "unison C4 across 3 timbres Qty1",
                      ["C4", "C4", "C4"], [roles["WW_HI"], roles["WW_MID"], roles["STR_HI"]],
                      num_instruments=[1, 1, 1], probe={"group": "qty_unison", "kind": "unison_zero"}))

    # ---------------------------------------------------------------- DYN
    cat = "DYN"
    for dyn in ("pppp", "pp", "mp", "mf", "ff", "ffff"):
        cases.append(Case(f"DYN.uniform_{dyn}", cat, f"triad uniform {dyn}", triad, rep("WW_HI", 3),
                          dynamics=[dyn, dyn, dyn]))
    cases.append(Case("DYN.mixed", cat, "triad [pp,mf,ff]", triad, rep("WW_HI", 3),
                      dynamics=["pp", "mf", "ff"]))
    cases.append(Case("DYN.contrast", cat, "triad [ffff,pppp,ffff]", triad, rep("WW_HI", 3),
                      dynamics=["ffff", "pppp", "ffff"]))

    # ---------------------------------------------------------------- EDO
    cat = "EDO"
    for n in (12, 19, 24, 31, 53, 72):
        frag = edo_scale("C4", n, [0, 1, 2, 3])
        cases.append(Case(f"EDO.{n}_scale", cat, f"{n}-EDO scale fragment [0,1,2,3]", frag,
                          rep("WW_HI", len(frag))))
        clus = edo_scale("C4", n, [0, 1, 2])
        cases.append(Case(f"EDO.{n}_cluster", cat, f"{n}-EDO cluster [0,1,2]", clus,
                          rep("WW_HI", len(clus))))
    cases.append(Case("EDO.12_spread", cat, "12-EDO spread reference", ["C4", "E5", "G6"], rep("WW_HI", 3)))
    detune = [("0c", "C4"), ("10c", cents_pitch(C4, 10.0)), ("25c", cents_pitch(C4, 25.0)),
              ("50c", cents_pitch(C4, 50.0)), ("100c", "C#4")]
    for name, top in detune:
        cases.append(Case(f"EDO.detune_{name}", cat, f"detune sweep C4 vs +{name}", ["C4", top],
                          rep("WW_HI", 2)))
    cases.append(Case("EDO.near_unison_0p5c", cat, "near-unison C4 vs +0.5c",
                      ["C4", cents_pitch(C4, 0.5)], rep("WW_HI", 2)))
    partials = [cents_pitch(C2, c) for c in (0, 1200, 1902, 2400, 2786, 3102)]
    cases.append(Case("EDO.spectral_c2", cat, "partials 1-6 of C2 (cents)", partials,
                      rep("WW_HI", len(partials))))

    # ---------------------------------------------------------------- WEIGHT
    cat = "WEIGHT"
    for w in (0.0, 0.25, 0.5, 0.75, 1.0):
        cases.append(Case(f"WEIGHT.w{w}", cat, f"weight sweep w={w}", ["C6", "C4", "C2"],
                          [roles["WW_HI"], roles["STR_HI"], roles["STR_LO"]], weight_factor=w,
                          probe={"group": "weight_sweep", "order": w}))

    # ---------------------------------------------------------------- EDGE
    cat = "EDGE"
    cases.append(Case("EDGE.two_note_min", cat, "two-note minimum", ["C4", "C#4"], rep("WW_HI", 2)))
    cases.append(Case("EDGE.all_unison", cat, "all-unison stack", ["G3", "G3", "G3", "G3"], rep("WW_HI", 4)))
    cases.append(Case("EDGE.single", cat, "single pitch", ["C4"], rep("WW_HI", 1)))
    cases.append(Case("EDGE.bimodal", cat, "bimodal low+high clusters",
                      ["C1", "C#1", "D1", "C7", "C#7", "D7"], rep("WW_HI", 6)))
    cases.append(Case("EDGE.micro_macro", cat, "micro + macro span",
                      ["C0", cents_pitch(note_to_midi_strict("C0"), 33.0), "C8"], rep("WW_HI", 3)))

    # ---------------------------------------------------------------- MONO
    # Adversarial quasi-monotonicity probes (see docs/MATHEMATICAL_MANUAL.md §H).
    # Each pair is base -> add; the runner reports OK/DECREASED for composite_total
    # together with the S/harm/entropy/mass/PSD/composite deltas. Never aborts.
    cat = "MONO"
    cluster7 = ["C4", "C#4", "D4", "D#4", "E4", "F4", "F#4"]  # mid-register, in flauta range
    # (a) octave-related addition at pppp: minimal added mass, maximal octave fusion
    #     (C6 is an octave multiple of the C4 root -> raises harmonic ratio).
    cases.append(Case("MONO.octave_base", cat, "7-note cluster (mf) — octave-probe base",
                      cluster7, rep("WW_HI", 7), dynamics=["mf"] * 7,
                      probe={"mono": "octave", "role": "base"}))
    cases.append(Case("MONO.octave_add", cat, "cluster + octave C6 at pppp (min mass, max fusion)",
                      cluster7 + ["C6"], rep("WW_HI", 8), dynamics=["mf"] * 7 + ["pppp"],
                      probe={"mono": "octave", "role": "add"}))
    # (b) perfect-twelfth addition at pppp: strong harmonic but NOT an octave multiple
    #     (G5 is 19 semitones above C4; mod 12 = 7), a contrast to the octave case.
    cases.append(Case("MONO.twelfth_base", cat, "7-note cluster (mf) — twelfth-probe base",
                      cluster7, rep("WW_HI", 7), dynamics=["mf"] * 7,
                      probe={"mono": "twelfth", "role": "base"}))
    cases.append(Case("MONO.twelfth_add", cat, "cluster + perfect twelfth G5 at pppp",
                      cluster7 + ["G5"], rep("WW_HI", 8), dynamics=["mf"] * 7 + ["pppp"],
                      probe={"mono": "twelfth", "role": "add"}))
    # (c) far-bass regression: a mass-bearing addition must not decrease composite.
    fb5 = ["C4", "D4", "E4", "F4", "A#4"]
    cases.append(Case("MONO.farbass_base", cat, "5 WW (mf) — far-bass regression base",
                      fb5, rep("WW_HI", 5), dynamics=["mf"] * 5,
                      probe={"mono": "farbass", "role": "base"}))
    cases.append(Case("MONO.farbass_add", cat, "far-bass +E1 (STR_LO, mf) — mass-bearing add",
                      fb5 + ["E1"], rep("WW_HI", 5) + rep("STR_LO", 1), dynamics=["mf"] * 6,
                      probe={"mono": "farbass", "role": "add"}))

    # ================================================================ CONTRAST
    # All CONTRAST cases use register-aware auto-assignment (auto=True): the
    # runner picks the first module-backed instrument whose registry range covers
    # each note's sounding MIDI, and logs the full pitch->instrument map. Notes
    # below/above every module-backed range go to ERRORS (a coverage finding).

    def chrom_cluster(root_note: str, size: int) -> list[str]:
        rm = round(note_to_midi_strict(root_note))
        return [midi_to_note_name(rm + i) for i in range(size)]

    def open_triad(root_note: str) -> list[str]:
        rm = round(note_to_midi_strict(root_note))
        return [midi_to_note_name(rm), midi_to_note_name(rm + 16), midi_to_note_name(rm + 31)]

    def auto(id_, cat_, desc, notes, **kw):
        n = len(notes)
        return Case(id_, cat_, desc, notes, [""] * n, auto=True, **kw)

    # ---------------------------------------------------------------- REG
    cat = "REG"
    for reg in ("C1", "C2", "C3", "C4", "C7"):
        cases.append(auto(f"REG.cluster3_{reg}", cat,
                          f"3-note chromatic cluster shape rooted at {reg}",
                          chrom_cluster(reg, 3), probe={"group": "reg", "shape": "cluster3", "reg": reg}))
    for reg in ("C1", "C3", "C5"):
        cases.append(auto(f"REG.triad_{reg}", cat,
                          f"open triad shape (root,+16,+31) rooted at {reg}",
                          open_triad(reg), probe={"group": "reg", "shape": "triad", "reg": reg}))

    # ---------------------------------------------------------------- BIMODAL
    cat = "BIMODAL"
    low_stratum = ["C2", "C#2", "D2"]
    high_stratum = ["C7", "C#7", "D7"]
    cases.append(auto("BIMODAL.low", cat, "low cluster stratum alone", low_stratum,
                      probe={"bi": "low"}))
    cases.append(auto("BIMODAL.high", cat, "high cluster stratum alone", high_stratum,
                      probe={"bi": "high"}))
    cases.append(auto("BIMODAL.combined", cat, "low + high strata (6 notes)",
                      low_stratum + high_stratum, probe={"bi": "combined"}))
    cases.append(auto("BIMODAL.combined_bridge", cat, "low + high strata + mid bridge G4",
                      low_stratum + high_stratum + ["G4"], probe={"bi": "bridge"}))

    # ---------------------------------------------------------------- DENSPARSE
    cat = "DENSPARSE"
    dense_cluster = chrom_cluster("C5", 7)  # C5..F#5, within flauta range
    sparse_trio = ["C2", "E4", "C7"]
    cases.append(auto("DENSPARSE.dense_soft", cat, "7-note cluster from C5, all pppp",
                      dense_cluster, dynamics=["pppp"] * 7, probe={"ds": "dense_soft"}))
    cases.append(auto("DENSPARSE.sparse_loud", cat, "wide trio [C2,E4,C7], all ffff",
                      sparse_trio, dynamics=["ffff"] * 3, probe={"ds": "sparse_loud"}))
    cases.append(auto("DENSPARSE.dense_loud", cat, "7-note cluster from C5, all ffff",
                      dense_cluster, dynamics=["ffff"] * 7, probe={"ds": "dense_loud"}))
    cases.append(auto("DENSPARSE.sparse_soft", cat, "wide trio [C2,E4,C7], all pppp",
                      sparse_trio, dynamics=["pppp"] * 3, probe={"ds": "sparse_soft"}))

    # ---------------------------------------------------------------- DYNGRAD
    cat = "DYNGRAD"
    dg_cluster = chrom_cluster("C4", 6)  # C4..F4
    cases.append(auto("DYNGRAD.uniform", cat, "6-note cluster C4, uniform mf",
                      dg_cluster, dynamics=["mf"] * 6, probe={"dg": "uniform"}))
    cases.append(auto("DYNGRAD.wedge", cat, "6-note cluster C4, wedge pppp..ffff (low->high)",
                      dg_cluster, dynamics=["pppp", "pp", "mp", "f", "ff", "ffff"],
                      probe={"dg": "wedge"}))
    cases.append(auto("DYNGRAD.inv_wedge", cat, "6-note cluster C4, inverted wedge ffff..pppp",
                      dg_cluster, dynamics=["ffff", "ff", "f", "mp", "pp", "pppp"],
                      probe={"dg": "inv_wedge"}))
    cases.append(auto("DYNGRAD.extremes", cat, "6-note cluster C4, extremes-only ffff/pppp",
                      dg_cluster, dynamics=["ffff", "pppp", "pppp", "pppp", "pppp", "ffff"],
                      probe={"dg": "extremes"}))
    cases.append(auto("DYNGRAD.bass_heavy", cat, "bass ffff + soft treble triad (C2,C5,C#5,D5)",
                      ["C2", "C5", "C#5", "D5"], dynamics=["ffff", "pppp", "pppp", "pppp"],
                      probe={"dg": "bass_heavy"}))

    # ---------------------------------------------------------------- FUSION
    cat = "FUSION"
    harmonic_series = [cents_pitch(C2, c) for c in (0, 1200, 1902, 2400, 2786, 3102)]
    inharmonic = ["C2", "C#3", "F#3+50c", "B3", "D#4+50c", "A4"]
    octave_pillar = ["C2", "C3", "C4", "C5", "C6"]
    qtone_cluster = ["C4", "C4+50c", "C#4", "C#4+50c", "D4"]
    cases.append(auto("FUSION.harmonic", cat, "partials 1-6 on C2 (harmonic series)",
                      harmonic_series, probe={"fu": "harmonic"}))
    cases.append(auto("FUSION.inharmonic", cat, "equal-cardinality inharmonic stack (6)",
                      inharmonic, probe={"fu": "inharmonic"}))
    cases.append(auto("FUSION.octave_pillar", cat, "5-octave pillar C2..C6",
                      octave_pillar, probe={"fu": "octave_pillar"}))
    cases.append(auto("FUSION.qtone_cluster", cat, "5-note quarter-tone cluster from C4",
                      qtone_cluster, probe={"fu": "qtone_cluster"}))

    # ---------------------------------------------------------------- MICROMIX
    cat = "MICROMIX"
    cases.append(auto("MICROMIX.near_unison", cat, "near-unison triple C5/+8c/-8c",
                      ["C5", "C5+8c", "C5-8c"]))
    cases.append(auto("MICROMIX.micro_frame", cat, "micro-knot in wide frame [C4,C5,+8c,-8c,C7]",
                      ["C4", "C5", "C5+8c", "C5-8c", "C7"]))
    cases.append(auto("MICROMIX.edo24_pedal", cat, "24-EDO 5-cluster from C5 over C2 pedal",
                      ["C2", "C5", "C5+50c", "C#5", "C#5+50c", "D5"]))
    cases.append(auto("MICROMIX.mixed_system", cat, "JI-flavoured tetrad [C4,E4-14c,G4+2c,B4-31c]",
                      ["C4", "E4-14c", "G4+2c", "B4-31c"]))

    # ---------------------------------------------------------------- MASSASYM
    cat = "MASSASYM"
    cases.append(Case("MASSASYM.massed_bass", cat, "massed bass Qty8 (contrabaixo) + solo treble (flauta)",
                      ["C2", "C6"], ["contrabaixo", "flauta"], num_instruments=[8, 1],
                      probe={"ma": "massed_bass"}))
    cases.append(Case("MASSASYM.massed_treble", cat, "solo bass (contrabaixo) + massed treble Qty8 (violino)",
                      ["C2", "C6"], ["contrabaixo", "violino"], num_instruments=[1, 8],
                      probe={"ma": "massed_treble"}))
    cases.append(Case("MASSASYM.balanced", cat, "balanced Qty4/4 (contrabaixo/flauta)",
                      ["C2", "C6"], ["contrabaixo", "flauta"], num_instruments=[4, 4],
                      probe={"ma": "balanced"}))

    # ---------------------------------------------------------------- XTREME
    # Recovered extreme shapes with register-appropriate auto-assignment.
    # Substitutions/drops are baked into the DATA and logged in the description.
    cat = "XTREME"
    cases.append(auto("XTREME.very_spacious", cat, "very spacious [C2,G3,D5,A6]",
                      ["C2", "G3", "D5", "A6"]))
    cases.append(auto("XTREME.full_range", cat, "full-range octaves [C1,C3,C5,C7] (C1 likely uncoverable)",
                      ["C1", "C3", "C5", "C7"]))
    cases.append(auto("XTREME.low_cluster_sub", cat,
                      "low cluster substituted C1->E1 (MIDI 24 below contrabaixo 28): [E1,F1,F#1]",
                      ["E1", "F1", "F#1"]))
    cases.append(auto("XTREME.micro_macro", cat, "micro+macro [C1,C1+33c,C7] (C1 likely uncoverable)",
                      ["C1", "C1+33c", "C7"]))
    cases.append(auto("XTREME.wide_n4", cat, "wide growth n=4 [C4,C5,E6,G3]",
                      ["C4", "C5", "E6", "G3"]))
    cases.append(auto("XTREME.wide_n5", cat, "wide growth n=5 [C4,C5,E6,G3,B7] (B7 likely uncoverable)",
                      ["C4", "C5", "E6", "G3", "B7"]))
    cases.append(auto("XTREME.wide_n6", cat, "wide growth n=6 [C4,C5,E6,G3,B7,D2] (B7 likely uncoverable)",
                      ["C4", "C5", "E6", "G3", "B7", "D2"]))
    cases.append(auto("XTREME.farbass_E0_sub", cat,
                      "far-bass E0->E1 (MIDI 12 below all ranges; lowest coverable E1); doubles existing E1",
                      ["C4", "D4", "E4", "F4", "A#4", "E1", "E1"]))
    cases.append(auto("XTREME.extreme_span", cat,
                      "extreme span: lowest coverable E1 (MIDI 28) to highest coverable G7 (MIDI 103)",
                      ["E1", "G7"]))

    return cases
