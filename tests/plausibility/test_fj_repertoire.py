"""F-J — Repertoire plausibility (SOFT, report-only)."""

from __future__ import annotations

import pytest
from microtonal import midi_to_note_name

from core.pipeline import calculate_metrics
from tests.plausibility.conftest import record_soft
from tests.plausibility.helpers import assert_jsonable, instrument_status, slice_input


def _row(resultados: dict) -> dict:
    dens = resultados["density"]
    add = resultados.get("additional_metrics") or {}
    sub = resultados.get("density_subindices") or {}
    return {
        "total": dens.get("total"),
        "weighted_orchestral": dens.get("weighted_orchestral"),
        "weighted_pitch": dens.get("weighted_pitch"),
        "pitch_structure": dens.get("pitch_structure") or dens.get("refined"),
        "interval": dens.get("interval"),
        "instrument": dens.get("instrument"),
        "M_sonic": dens.get("sonic_mass"),
        "entropy": add.get("complexity"),
        "harmonic_ratio": add.get("harmonic_ratio"),
        "register_occupancy": sub.get("register_occupancy") or sub.get("registral"),
        "subindices": {k: sub[k] for k in list(sub)[:8]} if isinstance(sub, dict) else sub,
    }


def _run(notes, instruments, dynamics, nums=None):
    if isinstance(instruments, str):
        instruments = [instruments] * len(notes)
    if isinstance(dynamics, str):
        dynamics = [dynamics] * len(notes)
    payload = slice_input(notes, instruments=instruments, dynamics=dynamics, num_instruments=nums or 1)
    r, _, _ = calculate_metrics(payload)
    assert_jsonable(r, label="FJ")
    return r


class TestFJRepertoire:
    @pytest.mark.plausibility
    def test_repertoire_battery(self):
        """SOFT: encode seven repertoire slices and compare the expected qualitative ordering."""
        cases = {}

        # 1. Tristan — F2, B2, D#4, G#4; cello, bassoon, two oboes (cor anglais substituted).
        cases["tristan"] = {
            "result": _row(
                _run(
                    ["F2", "B2", "D#4", "G#4"],
                    ["violoncelo", "fagote", "oboe", "cor_anglais"],
                    "p",
                )
            ),
            "notes": "cor_anglais now table-backed (E_Horn)",
            "status": {
                "violoncelo": instrument_status("violoncelo"),
                "fagote": instrument_status("fagote"),
                "oboe": instrument_status("oboe"),
                "cor_anglais": instrument_status("cor_anglais"),
            },
        }

        # 2. Augurs — Fb-major over Eb7; strings + 8 horns; variant + 3 trb + tba.
        augurs_notes = ["Fb3", "Ab3", "Cb4", "Eb3", "G3", "Bb3", "Db4"]
        # Fb may parse as E; if Invalid, use E3.
        try:
            _ = [__import__("microtonal", fromlist=["note_to_midi_strict"]).note_to_midi_strict(n) for n in augurs_notes]
        except Exception:
            augurs_notes = ["E3", "Ab3", "B3", "Eb3", "G3", "Bb3", "Db4"]
        base = _run(
            augurs_notes,
            ["viola", "viola", "violino", "trombone", "trompa", "trompa", "trompa"],
            "ff",
            [4, 3, 4, 2, 3, 3, 2],
        )
        cases["rite"] = {"result": _row(base), "notes": "8 horns distributed; Fb spelled if parser allows"}
        variant = _run(
            augurs_notes + ["C3", "G2", "C2"],
            ["viola", "viola", "violino", "trombone", "trompa", "trompa", "trompa", "trombone", "trombone", "tuba"],
            "ff",
            [4, 3, 4, 2, 3, 3, 2, 2, 1, 1],
        )
        cases["rite_plus_trb_tba"] = {"result": _row(variant), "notes": "added 3 trombone + tuba"}

        # 3. Webern sparse three-note pp
        cases["webern"] = {
            "result": _row(_run(["G4", "Bb5", "C#4"], ["flauta", "clarinete", "violino"], "pp")),
        }

        # 4. Ligeti Atmosphères — chromatic 5 octaves, strings divisi, pppp
        ligeti = []
        ligeti_inst = []
        ligeti_n = []
        for midi in range(36, 97):  # C2–C7
            note = midi_to_note_name(float(midi))
            ligeti.append(note)
            if midi < 48:
                ligeti_inst.append("contrabaixo")
            elif midi < 60:
                ligeti_inst.append("violoncelo")
            elif midi < 72:
                ligeti_inst.append("viola")
            else:
                ligeti_inst.append("violino")
            ligeti_n.append(2)
        cases["ligeti"] = {"result": _row(_run(ligeti, ligeti_inst, "pppp", ligeti_n))}

        # 5. Penderecki Threnody — quarter-tone cluster high strings ff
        pend = []
        for midi in [i * 0.5 for i in range(148, 187)]:  # G5–Eb6-ish quarter tones
            pend.append(midi_to_note_name(float(midi), include_cents=True))
        cases["penderecki"] = {
            "result": _row(_run(pend, ["violino"] * len(pend), "ff", [1] * len(pend))),
        }

        # 6. Debussy La Mer — wide pentatonic, harp/strings mp; harp is coarse
        cases["debussy"] = {
            "result": _row(
                _run(
                    ["C3", "D4", "E4", "G4", "A5"],
                    ["harpa", "violino", "viola", "violoncelo", "violino"],
                    "mp",
                )
            ),
            "notes": "harpa is coarse",
            "status": {"harpa": instrument_status("harpa")},
        }

        # 7. Single flute + bare octave
        cases["flute_single"] = {"result": _row(_run(["A4"], "flauta", "mf"))}
        cases["flute_octave"] = {"result": _row(_run(["A4", "A5"], "flauta", "mf"))}

        totals = {k: cases[k]["result"]["total"] for k in cases}
        wp = {k: cases[k]["result"]["weighted_pitch"] for k in cases}
        mass = {k: cases[k]["result"]["M_sonic"] for k in cases}

        expected = {
            "highest_weighted_pitch": ["ligeti", "penderecki"],
            "highest_mass_and_total": ["rite", "rite_plus_trb_tba"],
            "lowest_total": ["webern", "flute_single"],
            "intermediate": ["tristan"],
        }
        # Qualitative checks (SOFT)
        high_wp = sorted(wp, key=lambda k: wp[k] or 0, reverse=True)[:2]
        high_tot = sorted(totals, key=lambda k: totals[k] or 0, reverse=True)[:2]
        low_tot = sorted(totals, key=lambda k: totals[k] or 0)[:2]
        met = (
            set(high_wp) <= {"ligeti", "penderecki", "rite", "rite_plus_trb_tba"}
            and "flute_single" in low_tot or "webern" in low_tot
        )
        record_soft(
            family="F-J",
            test_id="FJ.repertoire",
            met=bool(met),
            expectation=(
                "Ligeti/Penderecki highest weighted_pitch; Rite highest M_sonic/total; "
                "Webern and single flute lowest; Tristan intermediate with low harmonic ratio"
            ),
            cases=cases,
            observed_total_order=sorted(totals, key=lambda k: totals[k] or 0, reverse=True),
            observed_wp_order=sorted(wp, key=lambda k: wp[k] or 0, reverse=True),
            observed_mass_order=sorted(mass, key=lambda k: mass[k] or 0, reverse=True),
            expected=expected,
        )
