"""
Scenario families A–E for the density stress battery.

Each scenario is a dict:
  id, family, summary, notes, dynamics, instruments, qtys
  expect_error (optional bool) — empty / invalid entry should raise
"""

from __future__ import annotations

from typing import Any

WEIGHT = 0.5

SliceSpec = dict[str, Any]


def _s(
    sid: str,
    family: str,
    summary: str,
    notes: tuple[str, ...],
    dynamics: tuple[str, ...],
    instruments: tuple[str, ...],
    qtys: tuple[int, ...] | None = None,
    *,
    expect_error: bool = False,
) -> SliceSpec:
    n = len(notes)
    return {
        "id": sid,
        "family": family,
        "summary": summary,
        "notes": notes,
        "dynamics": dynamics,
        "instruments": instruments,
        "qtys": qtys if qtys is not None else tuple(1 for _ in range(n)),
        "weight_factor": WEIGHT,
        "expect_error": expect_error,
    }


def build_scenarios() -> list[SliceSpec]:
    out: list[SliceSpec] = []

    # --- A. Pitched-only baselines -------------------------------------------------
    for inst, note in (
        ("Violin", "C4"),
        ("Flute", "C4"),
        ("Double bass", "C2"),
        ("Piano", "C4"),
    ):
        out.append(
            _s(
                f"A1_{inst.replace(' ', '_').lower()}_{note}",
                "A",
                f"Solo {inst} {note} mf",
                (note,),
                ("mf",),
                (inst,),
            )
        )

    for q in (1, 2, 4, 8, 16):
        out.append(
            _s(
                f"A2_violin_C4_qty{q}",
                "A",
                f"Violin C4 unison Qty={q}",
                ("C4",),
                ("mf",),
                ("Violin",),
                (q,),
            )
        )

    chord_steps = [
        ("C4",),
        ("C4", "E4"),
        ("C4", "E4", "G4"),
        ("C4", "E4", "G4", "Bb4"),
        ("C4", "E4", "G4", "Bb4", "D5"),
        ("C4", "E4", "G4", "Bb4", "D5", "F#5"),
    ]
    for notes in chord_steps:
        tag = "+".join(notes)
        out.append(
            _s(
                f"A3_chord_{len(notes)}",
                "A",
                f"Violin chord growth n={len(notes)} ({tag})",
                notes,
                tuple("mf" for _ in notes),
                tuple("Violin" for _ in notes),
            )
        )

    out.append(
        _s(
            "A4_close_triad",
            "A",
            "Close triad C4 E4 G4 (Piano)",
            ("C4", "E4", "G4"),
            ("mf", "mf", "mf"),
            ("Piano", "Piano", "Piano"),
        )
    )
    out.append(
        _s(
            "A4_open_triad",
            "A",
            "Open triad C2 E4 G6 (Piano) — same pitch classes, wider span",
            ("C2", "E4", "G6"),
            ("mf", "mf", "mf"),
            ("Piano", "Piano", "Piano"),
        )
    )

    # A5 full-orchestra pitched tutti (12 pitches, realistic string Qty)
    a5_notes = (
        "C2",
        "G2",
        "C3",
        "G3",
        "C4",
        "E4",
        "G4",
        "C5",
        "E5",
        "G5",
        "C4",
        "G4",
    )
    a5_insts = (
        "Double bass",
        "Cello",
        "Cello",
        "Viola",
        "Violin",
        "Violin",
        "Violin",
        "Flute",
        "Oboe",
        "Clarinet",
        "Horn",
        "Trumpet",
    )
    a5_qtys = (8, 10, 10, 12, 16, 14, 12, 2, 2, 2, 4, 3)
    out.append(
        _s(
            "A5_pitched_tutti",
            "A",
            "12-pitch pitched tutti ff with realistic Qty",
            a5_notes,
            tuple("ff" for _ in a5_notes),
            a5_insts,
            a5_qtys,
        )
    )

    # --- B. Percussion-only --------------------------------------------------------
    perc = ("Bass drum", "Cymbals", "Tam-tam", "Gong")
    # Canonical lookup keys (placeholders; pipeline injects for unpitched)
    perc_notes = {
        "Bass drum": "D2",
        "Cymbals": "C5",
        "Tam-tam": "C2",
        "Gong": "C3",
    }
    for inst in perc:
        for dyn in ("mf", "ff"):
            out.append(
                _s(
                    f"B1_{inst.replace('-', '_').replace(' ', '_').lower()}_{dyn}",
                    "B",
                    f"{inst} alone {dyn}",
                    (perc_notes[inst],),
                    (dyn,),
                    (inst,),
                )
            )

    out.append(
        _s(
            "B2_pair_bd_cym",
            "B",
            "Bass drum + Cymbals ff",
            (perc_notes["Bass drum"], perc_notes["Cymbals"]),
            ("ff", "ff"),
            ("Bass drum", "Cymbals"),
        )
    )
    out.append(
        _s(
            "B2_pair_tt_gong",
            "B",
            "Tam-tam + Gong ff",
            (perc_notes["Tam-tam"], perc_notes["Gong"]),
            ("ff", "ff"),
            ("Tam-tam", "Gong"),
        )
    )
    out.append(
        _s(
            "B2_full_battery",
            "B",
            "All four percussion ff",
            tuple(perc_notes[i] for i in perc),
            ("ff",) * 4,
            perc,
        )
    )

    for dyn in ("pp", "mf", "ff", "ffff"):
        out.append(
            _s(
                f"B3_tamtam_{dyn}",
                "B",
                f"Tam-tam dynamics ladder {dyn}",
                (perc_notes["Tam-tam"],),
                (dyn,),
                ("Tam-tam",),
            )
        )

    # --- C. Mixed aggregates -------------------------------------------------------
    quartet_notes = ("C4", "E4", "G4", "C3")
    quartet_insts = ("Violin", "Violin", "Viola", "Cello")
    quartet_dyns = ("ff", "ff", "ff", "ff")
    out.append(
        _s(
            "C1_quartet_alone",
            "C",
            "String quartet alone ff",
            quartet_notes,
            quartet_dyns,
            quartet_insts,
        )
    )
    for inst in perc:
        out.append(
            _s(
                f"C1_quartet_plus_{inst.replace('-', '_').replace(' ', '_').lower()}",
                "C",
                f"Quartet + {inst} ff",
                quartet_notes + (perc_notes[inst],),
                quartet_dyns + ("ff",),
                quartet_insts + (inst,),
            )
        )

    out.append(
        _s(
            "C2_quartet_plus_tamtam_ffff",
            "C",
            "Compression probe: quartet + Tam-tam ffff",
            quartet_notes + (perc_notes["Tam-tam"],),
            quartet_dyns + ("ffff",),
            quartet_insts + ("Tam-tam",),
        )
    )
    out.append(
        _s(
            "C2_quintet_fifth_string",
            "C",
            "Compression probe: quintet (add Double bass C2) instead of percussion",
            quartet_notes + ("C2",),
            quartet_dyns + ("ff",),
            quartet_insts + ("Double bass",),
        )
    )

    # C3: 8-player total, percussion share 0..4
    # pitched players fill the rest as Violin C4 Qty
    for n_perc in range(0, 5):
        n_pitched = 8 - n_perc
        notes: list[str] = []
        dyns: list[str] = []
        insts: list[str] = []
        qtys: list[int] = []
        if n_pitched > 0:
            notes.append("C4")
            dyns.append("ff")
            insts.append("Violin")
            qtys.append(n_pitched)
        for j in range(n_perc):
            inst = perc[j % len(perc)]
            notes.append(perc_notes[inst])
            dyns.append("ff")
            insts.append(inst)
            qtys.append(1)
        out.append(
            _s(
                f"C3_perc_share_{n_perc}_of_8",
                "C",
                f"8-player mix; unpitched events={n_perc}, pitched Qty={n_pitched}",
                tuple(notes),
                tuple(dyns),
                tuple(insts),
                tuple(qtys),
            )
        )

    # C4 order invariance — same mixed content, 6 permutations
    c4_base = {
        "notes": ("C4", "E4", "G3", "D2", "C5"),
        "dynamics": ("ff", "ff", "ff", "ff", "ff"),
        "instruments": ("Violin", "Viola", "Cello", "Bass drum", "Cymbals"),
        "qtys": (1, 1, 1, 1, 1),
    }
    orders = [
        (0, 1, 2, 3, 4),
        (4, 3, 2, 1, 0),
        (2, 0, 4, 1, 3),
        (3, 1, 4, 0, 2),
        (1, 3, 0, 4, 2),
        (4, 0, 3, 2, 1),
    ]
    for i, order in enumerate(orders):
        out.append(
            _s(
                f"C4_perm_{i}",
                "C",
                f"Order-invariance perm {i}",
                tuple(c4_base["notes"][j] for j in order),
                tuple(c4_base["dynamics"][j] for j in order),
                tuple(c4_base["instruments"][j] for j in order),
                tuple(c4_base["qtys"][j] for j in order),
            )
        )

    out.append(
        _s(
            "C5_tutti_no_perc",
            "C",
            "A5 pitched tutti without percussion",
            a5_notes,
            tuple("ff" for _ in a5_notes),
            a5_insts,
            a5_qtys,
        )
    )
    out.append(
        _s(
            "C5_tutti_with_perc",
            "C",
            "A5 pitched tutti + full percussion battery ff",
            a5_notes + tuple(perc_notes[i] for i in perc),
            tuple("ff" for _ in a5_notes) + ("ff",) * 4,
            a5_insts + perc,
            a5_qtys + (1, 1, 1, 1),
        )
    )

    # --- D. Degenerate / adversarial ----------------------------------------------
    out.append(
        _s(
            "D1_empty",
            "D",
            "Empty slice (no rows)",
            (),
            (),
            (),
            (),
            expect_error=True,
        )
    )
    out.append(
        _s(
            "D2_min_unpitched_pp",
            "D",
            "Single Tam-tam pp Qty=1",
            (perc_notes["Tam-tam"],),
            ("pp",),
            ("Tam-tam",),
        )
    )
    out.append(
        _s(
            "D3_violin_qty500",
            "D",
            "Violin C4 Qty=500",
            ("C4",),
            ("mf",),
            ("Violin",),
            (500,),
        )
    )
    # 24 distinct pitches: chromatic C4–B5 with +33c on odd indices (microtonal bins)
    chroma = [
        "C4",
        "C#4",
        "D4",
        "D#4",
        "E4",
        "F4",
        "F#4",
        "G4",
        "G#4",
        "A4",
        "A#4",
        "B4",
        "C5",
        "C#5",
        "D5",
        "D#5",
        "E5",
        "F5",
        "F#5",
        "G5",
        "G#5",
        "A5",
        "A#5",
        "B5",
    ]
    micro_notes = tuple(
        base if (i % 2 == 0) else f"{base}+33c" for i, base in enumerate(chroma)
    )
    out.append(
        _s(
            "D4_microtonal_24",
            "D",
            "24 distinct pitches with cent offsets (Violin)",
            micro_notes,
            tuple("mf" for _ in micro_notes),
            tuple("Violin" for _ in micro_notes),
        )
    )
    out.append(
        _s(
            "D5_violin_flute_unison",
            "D",
            "Violin C4 + Flute C4 (same pitch, two instruments)",
            ("C4", "C4"),
            ("mf", "mf"),
            ("Violin", "Flute"),
        )
    )
    out.append(
        _s(
            "D6_all_pp",
            "D",
            "Quartet all pp",
            quartet_notes,
            ("pp",) * 4,
            quartet_insts,
        )
    )
    out.append(
        _s(
            "D6_all_ffff",
            "D",
            "Quartet all ffff",
            quartet_notes,
            ("ffff",) * 4,
            quartet_insts,
        )
    )
    out.append(
        _s(
            "D7_tamtam_qty50",
            "D",
            "Tam-tam ffff Qty=50 (musically unreal)",
            (perc_notes["Tam-tam"],),
            ("ffff",),
            ("Tam-tam",),
            (50,),
        )
    )

    return out


def all_instrument_names(scenarios: list[SliceSpec]) -> list[str]:
    names: list[str] = []
    for s in scenarios:
        names.extend(s["instruments"])
    return sorted(set(names))
