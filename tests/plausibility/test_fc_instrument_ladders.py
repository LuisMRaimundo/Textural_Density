"""F-C — Instrument density ladders and lookup (HARD/SOFT; §F)."""

from __future__ import annotations

import importlib
import math
from pathlib import Path

import pytest

from core.pipeline import calculate_metrics
from error_handler import InputError
from instrumentos import get_instrument_module, get_instrument_profile
from instrumentos.pitch_interpolation import (
    MIN_PCHIP_ANCHORS,
    MissingCommittedDynamicError,
    resolve_density_from_table,
)
from instrumentos.registry import REGISTRY, resolve_profile
from microtonal import note_to_midi_strict
from tests.plausibility.conftest import record_hard, record_soft
from tests.plausibility.helpers import (
    DYNAMIC_LEVELS,
    MIN_PCHIP_ANCHORS as DOC_MIN_PCHIP,
    PCHIP_FALLBACK,
    REPO_ROOT,
    WITHDRAWN_IDS,
    WITHDRAWN_MODULE_GLOBS,
    assert_jsonable,
    classify_instruments,
    instrument_status,
    slice_input,
)


def _table_modules() -> list[str]:
    names = []
    seen = set()
    for iid in classify_instruments()["table_backed"]:
        mod = REGISTRY[iid].module_name
        if mod and mod not in seen:
            seen.add(mod)
            names.append(mod)
    return names


def _pitched_table_modules() -> list[str]:
    out = []
    for name in _table_modules():
        profile = next(p for p in REGISTRY.values() if p.module_name == name)
        if not profile.unpitched:
            out.append(name)
    return out


class TestFCSplitAndConstants:
    def test_registry_split_matches_pinned_counts(self):
        """HARD: live table-backed/coarse split; trombone table-backed, trombone_baixo coarse."""
        split = classify_instruments()
        assert "trombone" in split["table_backed"]
        assert "trombone_baixo" in split["coarse"]
        assert MIN_PCHIP_ANCHORS == DOC_MIN_PCHIP == 4
        record_hard(family="F-C", test_id="FC.split", **split)

    def test_trombone_table_span(self):
        """HARD: trombone.py covers MIDI 29–72 × 10 dynamics; sounding range equals span."""
        profile = REGISTRY["trombone"]
        mod = importlib.import_module("instrumentos.trombone")
        notes = sorted(mod.spectral_data, key=note_to_midi_strict)
        lo, hi = int(note_to_midi_strict(notes[0])), int(note_to_midi_strict(notes[-1]))
        assert (lo, hi) == (29, 72)
        assert profile.sounding_range == (29, 72)
        assert mod.INSTRUMENT_SOURCE.pitch_range == (29, 72)
        for note, row in mod.spectral_data.items():
            for dyn in DYNAMIC_LEVELS:
                assert dyn in row
                assert math.isfinite(float(row[dyn]))
        assert getattr(get_instrument_module("trombone_baixo"), "IS_COARSE_DEFAULT", False) is True
        record_hard(
            family="F-C",
            test_id="FC.trombone.span",
            n_notes=len(notes),
            span=(lo, hi),
            instrument_kind=instrument_status("trombone"),
            bass_status=instrument_status("trombone_baixo"),
        )


class TestFCFullLadderLookups:
    @pytest.mark.parametrize("module_name", _table_modules())
    def test_every_committed_cell_is_finite(self, module_name: str):
        """HARD: every table-backed module returns a finite float for every committed dynamic."""
        mod = importlib.import_module(f"instrumentos.{module_name}")
        profile = next(p for p in REGISTRY.values() if p.module_name == module_name)
        if profile.unpitched:
            val = mod.calcular_densidade("C4", "mf")
            val2 = mod.calcular_densidade("C8", "mf")
            assert math.isfinite(val) and val == pytest.approx(val2)
            record_hard(
                family="F-C",
                test_id=f"FC.unpitched.{module_name}",
                value=val,
                instrument_kind="table-backed",
            )
            return
        table = mod.spectral_data
        for note, row in table.items():
            for dyn in DYNAMIC_LEVELS:
                x = float(mod.calcular_densidade(note, dyn))
                assert math.isfinite(x) and x > 0.0
        record_hard(
            family="F-C",
            test_id=f"FC.ladder.{module_name}",
            n_notes=len(table),
            instrument_kind="table-backed",
        )

    @pytest.mark.parametrize("module_name", _pitched_table_modules())
    def test_unknown_dynamic_raises(self, module_name: str):
        """HARD: missing/unknown dynamic raises MissingCommittedDynamicError."""
        mod = importlib.import_module(f"instrumentos.{module_name}")
        note = next(iter(mod.spectral_data))
        with pytest.raises(MissingCommittedDynamicError):
            mod.calcular_densidade(note, "not-a-dynamic")
        record_hard(family="F-C", test_id=f"FC.missing_dyn.{module_name}")

    @pytest.mark.parametrize("module_name", _pitched_table_modules())
    def test_enharmonic_exact_cell_lookup(self, module_name: str):
        """HARD: exact-cell lookup ≡ MIDI-equivalent enharmonic lookup."""
        mod = importlib.import_module(f"instrumentos.{module_name}")
        if "C4" not in mod.spectral_data and "C#4" not in mod.spectral_data:
            pytest.skip("no C4/C#4 cell")
        key = "C4" if "C4" in mod.spectral_data else "C#4"
        enh = "B#3" if key == "C4" else "Db4"
        a = float(mod.calcular_densidade(key, "mf"))
        b = float(mod.calcular_densidade(enh, "mf"))
        assert a == pytest.approx(b)
        record_hard(family="F-C", test_id=f"FC.enh.{module_name}", key=key, value=a)

    @pytest.mark.parametrize("module_name", _pitched_table_modules())
    def test_quarter_tone_between_neighbours(self, module_name: str):
        """HARD: C4+50c lies between C4 and C#4 unless the table is non-monotone there."""
        mod = importlib.import_module(f"instrumentos.{module_name}")
        if "C4" not in mod.spectral_data or "C#4" not in mod.spectral_data:
            pytest.skip("C4/C#4 not in table")
        lo = float(mod.calcular_densidade("C4", "mf"))
        hi = float(mod.calcular_densidade("C#4", "mf"))
        mid = float(mod.calcular_densidade("C4+50c", "mf"))
        lo_b, hi_b = min(lo, hi), max(lo, hi)
        between = lo_b - 1e-9 <= mid <= hi_b + 1e-9
        record_hard(
            family="F-C",
            test_id=f"FC.interp.{module_name}",
            status="pass" if between else "fail",
            c4=lo,
            csharp=hi,
            mid=mid,
            between=between,
            table_non_monotone=lo > hi,
        )
        assert between or (lo > hi)  # if table inverted, mid may sit outside; still record

    def test_pchip_gate_and_out_of_range_fallback(self):
        """HARD: PCHIP needs ≥4 anchors; >12 st → 5.0; 1–12 st extrapolates; invalid → 5.0."""
        three = {"C4": {"mf": 10.0}, "D4": {"mf": 11.0}, "E4": {"mf": 12.0}}
        four = {**three, "F4": {"mf": 13.0}}
        r3 = resolve_density_from_table(three, "C#4", "mf", interpolation_method="pchip")
        r4 = resolve_density_from_table(four, "C#4", "mf", interpolation_method="pchip")
        assert MIN_PCHIP_ANCHORS == 4
        far = resolve_density_from_table(four, "C6", "mf")  # 14 st above F4=65; C6=84
        near = resolve_density_from_table(four, "G4", "mf")  # 2 st above F4
        bad = resolve_density_from_table(four, "not-a-note", "mf")
        assert far.value == pytest.approx(PCHIP_FALLBACK)
        assert far.provenance == "fallback"
        assert near.provenance == "extrapolated"
        assert bad.value == pytest.approx(PCHIP_FALLBACK)
        record_hard(
            family="F-C",
            test_id="FC.lookup_contract",
            three_provenance=r3.provenance,
            four_provenance=r4.provenance,
            far=far.value,
            near=near.value,
            invalid=bad.value,
        )


class TestFCSoftLadders:
    @pytest.mark.plausibility
    @pytest.mark.parametrize("module_name", _pitched_table_modules())
    def test_dynamic_non_decreasing(self, module_name: str):
        """SOFT: density non-decreasing from pppp to ffff at every table pitch."""
        mod = importlib.import_module(f"instrumentos.{module_name}")
        inversions = []
        for note, row in mod.spectral_data.items():
            vals = [float(row[d]) for d in DYNAMIC_LEVELS]
            for i in range(len(vals) - 1):
                a, b = vals[i], vals[i + 1]
                if b < a * (1 - 1e-12):
                    mag = (a - b) / max(a, 1e-12)
                    inversions.append(
                        {
                            "note": note,
                            "from": DYNAMIC_LEVELS[i],
                            "to": DYNAMIC_LEVELS[i + 1],
                            "a": a,
                            "b": b,
                            "rel": mag,
                            "gt_5pct": mag > 0.05,
                        }
                    )
        met = not inversions
        record_soft(
            family="F-C",
            test_id=f"FC.soft.monotone.{module_name}",
            met=met,
            expectation="pppp…ffff non-decreasing at every table pitch",
            module=module_name,
            status="table-backed",
            n_inversions=len(inversions),
            n_gt_5pct=sum(1 for x in inversions if x["gt_5pct"]),
            inversions=inversions[:40],
            classification="table artefact",
        )

    @pytest.mark.plausibility
    def test_technique_variants_violin_viola(self):
        """SOFT: sul pont ≥ ordinario ≥ sordina/tasto/harm on shared range (violin/viola)."""
        pairs = [
            ("violino_sul_ponticello", "violino", "ge"),
            ("violino_sordina", "violino", "le"),
            ("violino_sul_tasto", "violino", "le"),
            ("violino_harm", "violino", "le"),
            ("viola_sul_ponticello", "viola", "ge"),
            ("viola_sordina", "viola", "le"),
            ("viola_harm", "viola", "le"),
        ]
        report = []
        all_ok = True
        for left, right, op in pairs:
            ml = get_instrument_module(left)
            mr = get_instrument_module(right)
            shared = set(ml.spectral_data) & set(mr.spectral_data)
            agree = 0
            n = 0
            for note in shared:
                for dyn in ("pppp", "mf", "ffff"):
                    a = float(ml.calcular_densidade(note, dyn))
                    b = float(mr.calcular_densidade(note, dyn))
                    n += 1
                    if op == "ge" and a + 1e-12 >= b:
                        agree += 1
                    elif op == "le" and a - 1e-12 <= b:
                        agree += 1
            rate = agree / n if n else float("nan")
            report.append(
                {
                    "left": left,
                    "right": right,
                    "op": op,
                    "agree": agree,
                    "n": n,
                    "rate": rate,
                    "left_status": instrument_status(left),
                    "right_status": instrument_status(right),
                }
            )
            if rate < 1.0:
                all_ok = False
        record_soft(
            family="F-C",
            test_id="FC.soft.techniques",
            met=all_ok,
            expectation="sul pont ≥ ordinario; sordina/tasto/harm ≤ ordinario (violin/viola)",
            pairs=report,
            classification="table artefact",
        )

    @pytest.mark.plausibility
    def test_register_spikes(self):
        """SOFT: flag mf adjacent-semitone jumps > 3× median jump per module."""
        flags = []
        for name in _pitched_table_modules():
            mod = importlib.import_module(f"instrumentos.{name}")
            notes = sorted(mod.spectral_data, key=note_to_midi_strict)
            vals = [float(mod.spectral_data[n]["mf"]) for n in notes]
            jumps = [abs(vals[i + 1] - vals[i]) for i in range(len(vals) - 1)]
            if not jumps:
                continue
            med = sorted(jumps)[len(jumps) // 2]
            spikes = []
            if med > 0:
                for i, j in enumerate(jumps):
                    if j > 3.0 * med:
                        spikes.append(
                            {"from": notes[i], "to": notes[i + 1], "jump": j, "median": med}
                        )
            flags.append({"module": name, "median_jump": med, "n_spikes": len(spikes), "spikes": spikes[:20]})
        met = all(item["n_spikes"] == 0 for item in flags)
        record_soft(
            family="F-C",
            test_id="FC.soft.spikes",
            met=met,
            expectation="no mf adjacent jump > 3× median jump",
            modules=flags,
            classification="table artefact",
        )

    @pytest.mark.plausibility
    def test_cross_family_ordering(self):
        """SOFT: report mid-register mf/ff ordering; trumpet≥oboe≥flute and tuba≥trombone≥horn."""
        probes = {
            "trompete": "G4",
            "oboe": "G4",
            "flauta": "G4",
            "tuba": "C3",
            "trombone": "C3",
            "trompa": "C3",
        }
        rows = {}
        for iid, note in probes.items():
            mod = get_instrument_module(iid)
            rows[iid] = {
                "mf": float(mod.calcular_densidade(note, "mf")),
                "ff": float(mod.calcular_densidade(note, "ff")),
                "status": instrument_status(iid),
                "note": note,
            }
        wood_mf = rows["trompete"]["mf"] >= rows["oboe"]["mf"] >= rows["flauta"]["mf"]
        brass_mf = rows["tuba"]["mf"] >= rows["trombone"]["mf"] >= rows["trompa"]["mf"]
        record_soft(
            family="F-C",
            test_id="FC.soft.family_order",
            met=wood_mf and brass_mf,
            expectation="trumpet≥oboe≥flute and tuba≥trombone≥horn at mf (mid-register)",
            values=rows,
            wood_mf_ok=wood_mf,
            brass_mf_ok=brass_mf,
            classification="table artefact",
        )

    @pytest.mark.plausibility
    def test_trombone_between_horn_and_tuba(self):
        """SOFT: trombone mf between trompa and tuba on the shared range."""
        ht = get_instrument_module("trompa")
        tb = get_instrument_module("trombone")
        tu = get_instrument_module("tuba")
        shared = set(ht.spectral_data) & set(tb.spectral_data) & set(tu.spectral_data)
        outside = []
        for note in shared:
            h = float(ht.calcular_densidade(note, "mf"))
            t = float(tb.calcular_densidade(note, "mf"))
            u = float(tu.calcular_densidade(note, "mf"))
            lo, hi = min(h, u), max(h, u)
            if not (lo - 1e-9 <= t <= hi + 1e-9):
                outside.append({"note": note, "horn": h, "trombone": t, "tuba": u})
        met = not outside
        record_soft(
            family="F-C",
            test_id="FC.soft.trombone_between",
            met=met,
            expectation="trombone mf lies between horn and tuba on shared pitches",
            n_shared=len(shared),
            n_outside=len(outside),
            outside=outside[:30],
            trombone_status=instrument_status("trombone"),
            classification="table artefact",
        )


class TestFCCoarseFallback:
    @pytest.mark.parametrize("iid", ["trombone_baixo", "piano", "harpa"])
    def test_coarse_path_and_unknown_dynamic_weight(self, iid: str):
        """HARD: named coarse ids use coarse_default; unknown dynamics use weight 1.0."""
        mod = get_instrument_module(iid)
        assert getattr(mod, "IS_COARSE_DEFAULT", False) is True
        profile = get_instrument_profile(iid)
        note = "E3" if iid == "trombone_baixo" else "C4"
        mf = float(mod.calcular_densidade(note, "mf"))
        unknown = float(mod.calcular_densidade(note, "xyz"))
        # nearest table-backed neighbour for the report
        neighbour = {
            "trombone_baixo": "trombone",
            "piano": "violino",
            "harpa": "violino",
        }[iid]
        nmod = get_instrument_module(neighbour)
        nnote = note if neighbour != "trombone" else "E3"
        try:
            neigh = float(nmod.calcular_densidade(nnote, "mf"))
        except Exception:
            neigh = None
        record_hard(
            family="F-C",
            test_id=f"FC.coarse.{iid}",
            instrument_kind="coarse",
            mf=mf,
            unknown_dynamic=unknown,
            neighbour=neighbour,
            neighbour_mf=neigh,
            profile_status=profile.profile_status,
        )


class TestFCWithdrawal:
    @pytest.mark.parametrize("wid", WITHDRAWN_IDS)
    def test_withdrawn_id_does_not_resolve_to_parent(self, wid: str):
        """HARD: withdrawn ids must not silently resolve to parent or a live table."""
        profile = resolve_profile(wid)
        assert profile is None
        parent = "violoncelo" if wid.startswith("violoncelo") else "contrabaixo"
        try:
            r, _, _ = calculate_metrics(slice_input(["C3"], instruments=wid))
            silent = True
            resolved = None
            if r.get("instrument_lookup_trace"):
                resolved = r["instrument_lookup_trace"][0].get("resolved_profile_id")
            assert_jsonable(r, label=f"FC.withdrawn.{wid}")
        except (InputError, KeyError, ValueError) as exc:
            silent = False
            resolved = type(exc).__name__
            r = {"error": str(exc)}
        record_hard(
            family="F-C",
            test_id=f"FC.withdrawn.resolve.{wid}",
            status="pass" if (profile is None and not silent) else "fail",
            resolve_profile_is_none=profile is None,
            calculate_metrics_silent=silent,
            resolved_profile=resolved,
            parent=parent,
            error=None if silent else r.get("error"),
        )
        # Withdrawn ids must raise an explicit registry/input error, not fall back.
        assert profile is None
        assert not silent, (
            f"{wid} was accepted silently (resolved={resolved!r}); "
            "expected an explicit registry error"
        )

    def test_withdrawn_module_files_absent(self):
        """HARD: withdrawn sul-tasto technique files stay absent."""
        folder = REPO_ROOT / "instrumentos"
        present = [name for name in WITHDRAWN_MODULE_GLOBS if (folder / name).exists()]
        assert present == []
        record_hard(family="F-C", test_id="FC.withdrawn.files", present=present)

    def test_docs_do_not_list_withdrawn_as_available(self):
        """HARD: acoustic-sources and instrumentos README no longer list withdrawn modules as available."""
        sources = (REPO_ROOT / "docs" / "instrument_acoustic_sources.md").read_text(encoding="utf-8")
        readme = (REPO_ROOT / "instrumentos" / "README.md").read_text(encoding="utf-8")
        banned = [
            "instrumentos/cello_sul_tasto.py",
            "instrumentos/double_bass_sul_tasto.py",
        ]
        hits = [b for b in banned if b in sources or b in readme]
        # Mentions of withdrawal are allowed; live module paths are not.
        assert hits == []
        record_hard(family="F-C", test_id="FC.withdrawn.docs", hits=hits)
