"""Public-API execution, metric flattening, formula self-check, property trials."""

from __future__ import annotations

import hashlib
import math
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from core import AnalysisRequest, calculate_metrics, format_output_string
from error_handler import InputError
from tests.stress.registry_check import require_instruments
from tests.stress.scenarios import WEIGHT, SliceSpec, all_instrument_names, build_scenarios

ROOT = Path(__file__).resolve().parents[2]


@dataclass
class AssertionResult:
    family: str
    name: str
    passed: bool
    detail: str
    severity: str = "blocker"  # blocker | caveat | cosmetic
    slice_id: str = ""


@dataclass
class SliceResult:
    spec: SliceSpec
    ok: bool
    error: str | None = None
    resultados: dict[str, Any] | None = None
    display: str | None = None
    flat: dict[str, Any] = field(default_factory=dict)


def git_hash() -> str:
    """Return short HEAD hash; never silently invent values when git works."""
    attempts = (
        ["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
        ["git", "rev-parse", "--short", "HEAD"],
    )
    for cmd in attempts:
        try:
            out = subprocess.check_output(
                cmd,
                cwd=str(ROOT),
                stderr=subprocess.DEVNULL,
                text=True,
            ).strip()
            if out:
                return out
        except Exception:
            continue
    # Last resort: read .git/HEAD / ref files without spawning git.
    try:
        head = (ROOT / ".git" / "HEAD").read_text(encoding="utf-8").strip()
        if head.startswith("ref:"):
            ref = head.split(" ", 1)[1].strip()
            sha = (ROOT / ".git" / ref).read_text(encoding="utf-8").strip()
        else:
            sha = head
        return sha[:7] if sha else "unknown"
    except Exception:
        return "unknown"


def flatten_metrics(obj: Any, prefix: str = "") -> dict[str, Any]:
    """Wide-format flatten of nested result dicts (lists → indexed / joined)."""
    out: dict[str, Any] = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            key = f"{prefix}.{k}" if prefix else str(k)
            out.update(flatten_metrics(v, key))
    elif isinstance(obj, (list, tuple)):
        if not obj:
            out[prefix] = ""
        elif all(isinstance(x, (int, float, str, bool)) or x is None for x in obj):
            out[prefix] = "|".join("" if x is None else str(x) for x in obj)
        else:
            for i, v in enumerate(obj):
                out.update(flatten_metrics(v, f"{prefix}[{i}]"))
    elif isinstance(obj, (np.floating, np.integer)):
        out[prefix] = float(obj) if isinstance(obj, np.floating) else int(obj)
    elif isinstance(obj, (int, float, str, bool)) or obj is None:
        out[prefix] = obj
    else:
        out[prefix] = str(obj)
    return out


def run_slice(spec: SliceSpec) -> SliceResult:
    if spec.get("expect_error"):
        try:
            if not spec["notes"]:
                raise InputError("Notes are required.")
            calculate_metrics(
                AnalysisRequest(
                    notes=tuple(spec["notes"]),
                    dynamics=tuple(spec["dynamics"]),
                    instruments=tuple(spec["instruments"]),
                    num_instruments=tuple(spec["qtys"]),
                    weight_factor=float(spec.get("weight_factor", WEIGHT)),
                )
            )
            return SliceResult(
                spec=spec,
                ok=False,
                error="Expected InputError for empty/invalid slice, but call succeeded",
            )
        except InputError as e:
            return SliceResult(spec=spec, ok=True, error=str(e), flat={"error": str(e)})
        except Exception as e:
            return SliceResult(
                spec=spec,
                ok=False,
                error=f"Unexpected {type(e).__name__}: {e}",
            )

    try:
        req = AnalysisRequest(
            notes=tuple(spec["notes"]),
            dynamics=tuple(spec["dynamics"]),
            instruments=tuple(spec["instruments"]),
            num_instruments=tuple(spec["qtys"]),
            weight_factor=float(spec.get("weight_factor", WEIGHT)),
        )
        resultados, _dens, _pitches = calculate_metrics(req)
        display = format_output_string(resultados)
        flat = flatten_metrics(resultados)
        flat["slice_id"] = spec["id"]
        flat["family"] = spec["family"]
        flat["summary"] = spec["summary"]
        flat["weight_factor"] = float(spec.get("weight_factor", WEIGHT))
        return SliceResult(
            spec=spec,
            ok=True,
            resultados=resultados,
            display=display,
            flat=flat,
        )
    except Exception as e:
        return SliceResult(spec=spec, ok=False, error=f"{type(e).__name__}: {e}")


def _get(r: SliceResult, *keys: str, default: Any = None) -> Any:
    if not r.resultados:
        return default
    cur: Any = r.resultados
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def header_formula_self_check(r: SliceResult) -> tuple[bool, str]:
    if not r.resultados or not r.display:
        return False, "no results"
    header = next((ln for ln in r.display.splitlines() if ln.startswith("Composite:")), None)
    if not header:
        return False, "no Composite header line"
    m = re.search(
        r"w=(?P<w>[0-9.]+), REF=(?P<ref>[0-9.]+), "
        r"D_blend=(?P<d_blend>[0-9.]+), M=(?P<M>[0-9.]+)",
        header,
    )
    if not m:
        return False, f"unparseable header: {header}"
    w = float(m.group("w"))
    ref = float(m.group("ref"))
    sonic_mass = float(m.group("M"))
    di = float(_get(r, "density", "instrument", default=0.0))
    dv = float(_get(r, "density", "interval", default=0.0))
    blend_def = re.search(r"\(D_blend = (.+)\)$", header)
    if not blend_def:
        return False, "no blend definition in header"
    d_blend = float(
        eval(blend_def.group(1), {"__builtins__": {}}, {"w": w, "DI": di, "DV": dv})
    )
    outer = re.match(r"Composite: (.+) with w=", header)
    if not outer:
        return False, "no outer expression"
    outer_val = float(
        eval(
            outer.group(1),
            {"__builtins__": {}, "log10": math.log10, "sqrt": math.sqrt},
            {"D_blend": d_blend, "M": sonic_mass, "REF": ref},
        )
    )
    reported = float(_get(r, "density", "total", default=float("nan")))
    ok = abs(outer_val - reported) <= 1e-6
    return ok, f"header_eval={outer_val:.12g} reported={reported:.12g}"


def by_id(results: list[SliceResult]) -> dict[str, SliceResult]:
    return {r.spec["id"]: r for r in results}


def evaluate_assertions(
    results: list[SliceResult],
    *,
    e1_trials: int,
    e1_slices: int,
    seed: int,
) -> list[AssertionResult]:
    asserts: list[AssertionResult] = []
    idx = by_id(results)

    def add(
        family: str,
        name: str,
        passed: bool,
        detail: str,
        severity: str = "blocker",
        slice_id: str = "",
    ) -> None:
        asserts.append(
            AssertionResult(family, name, passed, detail, severity, slice_id)
        )

    # Scenario execution
    for r in results:
        if r.spec.get("expect_error"):
            add(
                r.spec["family"],
                f"{r.spec['id']}_graceful_error",
                r.ok and bool(r.error),
                r.error or "missing error message",
                slice_id=r.spec["id"],
            )
        else:
            add(
                r.spec["family"],
                f"{r.spec['id']}_runs",
                r.ok,
                r.error or "ok",
                slice_id=r.spec["id"],
            )

    # A2: pitch metrics invariant under Qty; composite non-decreasing
    a2_ids = [f"A2_violin_C4_qty{q}" for q in (1, 2, 4, 8, 16)]
    if all(i in idx and idx[i].ok for i in a2_ids):
        pitch_keys = ("interval", "pitch_structure")
        base = idx[a2_ids[0]]
        pitch_ok = all(
            all(
                abs(
                    float(_get(idx[i], "density", k, default=0))
                    - float(_get(base, "density", k, default=0))
                )
                < 1e-12
                for k in pitch_keys
            )
            for i in a2_ids[1:]
        )
        totals = [float(_get(idx[i], "density", "total")) for i in a2_ids]
        mono = all(totals[j] + 1e-12 >= totals[j - 1] for j in range(1, len(totals)))
        add("A", "A2_pitch_invariant_under_qty", pitch_ok, f"totals={totals}")
        add("A", "A2_composite_nondecreasing_qty", mono, f"totals={totals}")

    # A3 chord growth strict increase
    a3_ids = [f"A3_chord_{n}" for n in range(1, 7)]
    if all(i in idx and idx[i].ok for i in a3_ids):
        totals = [float(_get(idx[i], "density", "total")) for i in a3_ids]
        ps = [float(_get(idx[i], "density", "pitch_structure")) for i in a3_ids]
        add(
            "A",
            "A3_composite_strictly_increasing",
            all(totals[j] > totals[j - 1] for j in range(1, len(totals))),
            f"totals={totals}",
        )
        add(
            "A",
            "A3_pitch_structure_strictly_increasing",
            all(ps[j] > ps[j - 1] for j in range(1, len(ps))),
            f"pitch_structure={ps}",
        )

    # A4 register spread
    _c, _o = idx.get("A4_close_triad"), idx.get("A4_open_triad")
    if _c and _c.ok and _o and _o.ok:
        c, o = _c, _o
        span_c = float(
            _get(c, "density_subindices", "registral", "raw", "pitch_span_semitones", default=-1)
        )
        span_o = float(
            _get(o, "density_subindices", "registral", "raw", "pitch_span_semitones", default=-1)
        )
        dist_c = int(_get(c, "pitch_aggregation", "distinct_pitch_count", default=-1))
        dist_o = int(_get(o, "pitch_aggregation", "distinct_pitch_count", default=-1))
        add(
            "A",
            "A4_registral_span_differs",
            span_o > span_c + 1e-9,
            f"close_span={span_c} open_span={span_o}",
        )
        add(
            "A",
            "A4_distinct_pitch_count_equal",
            dist_c == dist_o == 3,
            f"close={dist_c} open={dist_o}",
        )

    # B1 unpitched alone
    b1 = [r for r in results if r.spec["id"].startswith("B1_") and r.ok]
    for r in b1:
        dist = int(_get(r, "pitch_aggregation", "distinct_pitch_count", default=-1))
        interval = float(_get(r, "density", "interval", default=-1))
        ps = float(_get(r, "density", "pitch_structure", default=-1))
        text = r.display or ""
        blend = float(_get(r, "density", "weighted", default=0))
        wo = float(_get(r, "density", "weighted_orchestral", default=0))
        add(
            "B",
            f"{r.spec['id']}_pitch_zero",
            dist == 0 and interval == 0.0 and ps == 0.0,
            f"dist={dist} interval={interval} ps={ps}",
            slice_id=r.spec["id"],
        )
        add(
            "B",
            f"{r.spec['id']}_spectral_na",
            "n/a — no pitched content" in text,
            "spectral block",
            slice_id=r.spec["id"],
        )
        # Post-8c: blend equals weighted orchestral (DV=0); composite is log path
        add(
            "B",
            f"{r.spec['id']}_blend_equals_weighted_orch",
            abs(blend - wo) < 1e-12,
            f"blend={blend} wo={wo}",
            slice_id=r.spec["id"],
        )

    # B1 ff ordering vs CDM (instrument density / one-player)
    b1_ff = [r for r in b1 if r.spec["id"].endswith("_ff")]
    if len(b1_ff) == 4:
        by_cdm = sorted(
            b1_ff, key=lambda r: float(_get(r, "density", "instrument", default=0))
        )
        by_comp = sorted(
            b1_ff, key=lambda r: float(_get(r, "density", "total", default=0))
        )
        order_cdm = [r.spec["id"] for r in by_cdm]
        order_comp = [r.spec["id"] for r in by_comp]
        add(
            "B",
            "B1_ff_composite_order_matches_CDM",
            order_cdm == order_comp,
            f"CDM={order_cdm} composite={order_comp}",
            severity="caveat" if order_cdm != order_comp else "blocker",
        )

    # B2 monotone growth
    chain = ["B1_bass_drum_ff", "B2_pair_bd_cym", "B2_full_battery"]
    if all(i in idx and idx[i].ok for i in chain):
        totals = [float(_get(idx[i], "density", "total")) for i in chain]
        add(
            "B",
            "B2_monotone_growth",
            all(totals[j] + 1e-12 >= totals[j - 1] for j in range(1, len(totals))),
            f"totals={totals}",
        )

    # B3 dynamics ladder
    b3 = [f"B3_tamtam_{d}" for d in ("pp", "mf", "ff", "ffff")]
    if all(i in idx and idx[i].ok for i in b3):
        totals = [float(_get(idx[i], "density", "total")) for i in b3]
        add(
            "B",
            "B3_dynamics_nondecreasing",
            all(totals[j] + 1e-12 >= totals[j - 1] for j in range(1, len(totals))),
            f"pp→mf→ff→ffff totals={totals}",
        )
        jump = totals[2] - totals[1]
        add(
            "B",
            "B3_mf_to_ff_jump_recorded",
            True,
            f"mf→ff Δcomposite={jump:.6g} (documented cascade discontinuity flag)",
            severity="caveat",
        )

    # C1 percussion additions raise composite; rank vs CDM
    if idx.get("C1_quartet_alone") and idx["C1_quartet_alone"].ok:
        base_t = float(_get(idx["C1_quartet_alone"], "density", "total"))
        incs = []
        for inst, sid in (
            ("Bass drum", "C1_quartet_plus_bass_drum"),
            ("Cymbals", "C1_quartet_plus_cymbals"),
            ("Tam-tam", "C1_quartet_plus_tam_tam"),
            ("Gong", "C1_quartet_plus_gong"),
        ):
            if sid in idx and idx[sid].ok:
                t = float(_get(idx[sid], "density", "total"))
                cdm = float(_get(idx[sid], "density", "instrument")) - float(
                    _get(idx["C1_quartet_alone"], "density", "instrument")
                )
                incs.append((inst, t - base_t, cdm, t))
                add(
                    "C",
                    f"{sid}_raises_composite",
                    t > base_t + 1e-12,
                    f"base={base_t:.6g} mixed={t:.6g}",
                    slice_id=sid,
                )
        if len(incs) == 4:
            rank_inc = [x[0] for x in sorted(incs, key=lambda z: z[1])]
            rank_cdm = [x[0] for x in sorted(incs, key=lambda z: z[2])]
            add(
                "C",
                "C1_increment_rank_matches_CDM_rank",
                rank_inc == rank_cdm,
                f"Δcomposite_rank={rank_inc} ΔCDM_rank={rank_cdm}",
                severity="caveat" if rank_inc != rank_cdm else "blocker",
            )

    # C2 compression probe — documentary (always pass; record values)
    _tt, _q5 = idx.get("C2_quartet_plus_tamtam_ff"), idx.get("C2_quintet_fifth_string")
    if _tt and _tt.ok and _q5 and _q5.ok:
        t_tt = float(_get(_tt, "density", "total"))
        t_q5 = float(_get(_q5, "density", "total"))
        add(
            "C",
            "C2_compression_probe_documented",
            True,
            f"quartet+tam-tam_ff={t_tt:.6g}; quintet={t_q5:.6g}; diff={t_tt - t_q5:.6g}",
            severity="caveat",
        )

    # C3 player count always 8
    for n in range(0, 5):
        sid = f"C3_perc_share_{n}_of_8"
        if sid in idx and idx[sid].ok:
            pc = int(_get(idx[sid], "pitch_aggregation", "player_count", default=-1))
            add("C", f"{sid}_player_count_8", pc == 8, f"player_count={pc}", slice_id=sid)

    # C4 order-invariant equality across perms (float ulps + bin order ignored)
    c4 = [f"C4_perm_{i}" for i in range(6)]
    if all(i in idx and idx[i].ok for i in c4):
        numeric_keys = (
            "density.interval",
            "density.instrument",
            "density.weighted",
            "density.sonic_mass",
            "density.total",
            "density.pitch_structure",
            "pitch_aggregation.event_count",
            "pitch_aggregation.player_count",
            "pitch_aggregation.distinct_pitch_count",
            "texture.average_texture_density",
            "timbre.density_variance",
        )
        ref = idx[c4[0]]
        same = True
        detail_bits = []
        for sid in c4[1:]:
            other = idx[sid]
            for k in numeric_keys:
                a, b = ref.flat.get(k), other.flat.get(k)
                try:
                    fa, fb = float(a), float(b)
                    if not math.isclose(fa, fb, rel_tol=0.0, abs_tol=1e-9):
                        same = False
                        detail_bits.append(f"{sid}:{k} ({fa} vs {fb})")
                except (TypeError, ValueError):
                    if a != b:
                        same = False
                        detail_bits.append(f"{sid}:{k}")
            bins_a = sorted(
                float(b.get("midi", 0))
                for b in (_get(ref, "pitch_aggregation", "pitch_bins") or [])
            )
            bins_b = sorted(
                float(b.get("midi", 0))
                for b in (_get(other, "pitch_aggregation", "pitch_bins") or [])
            )
            if bins_a != bins_b:
                same = False
                detail_bits.append(f"{sid}:pitch_bins_multiset")
        add(
            "C",
            "C4_permutation_invariance",
            same,
            "order-invariant numeric match" if same else f"mismatches={detail_bits[:8]}",
        )

    # C5 tutti with perc >= without
    _c5a, _c5b = idx.get("C5_tutti_no_perc"), idx.get("C5_tutti_with_perc")
    if _c5a and _c5a.ok and _c5b and _c5b.ok:
        t0 = float(_get(_c5a, "density", "total"))
        t1 = float(_get(_c5b, "density", "total"))
        add(
            "C",
            "C5_tutti_with_perc_raises_composite",
            t1 > t0 + 1e-12,
            f"no_perc={t0:.6g} with_perc={t1:.6g}",
        )

    # D2–D7 specifics
    if idx.get("D2_min_unpitched_pp") and idx["D2_min_unpitched_pp"].ok:
        t = float(_get(idx["D2_min_unpitched_pp"], "density", "total"))
        add("D", "D2_minimum_nonzero", t > 0, f"total={t}")
    if idx.get("D3_violin_qty500") and idx["D3_violin_qty500"].ok:
        r = idx["D3_violin_qty500"]
        t = float(_get(r, "density", "total"))
        m = float(_get(r, "density", "sonic_mass"))
        add(
            "D",
            "D3_no_nan_overflow",
            math.isfinite(t) and math.isfinite(m),
            f"total={t} mass={m}",
        )
    if idx.get("D4_microtonal_24") and idx["D4_microtonal_24"].ok:
        dist = int(
            _get(idx["D4_microtonal_24"], "pitch_aggregation", "distinct_pitch_count")
        )
        add("D", "D4_distinct_count_24", dist == 24, f"distinct_pitch_count={dist}")
    if idx.get("D5_violin_flute_unison") and idx["D5_violin_flute_unison"].ok:
        r = idx["D5_violin_flute_unison"]
        dist = int(_get(r, "pitch_aggregation", "distinct_pitch_count"))
        events = int(_get(r, "pitch_aggregation", "event_count"))
        add(
            "D",
            "D5_unison_two_instruments",
            dist == 1 and events == 2,
            f"distinct={dist} events={events}",
        )
    _pp, _ffff = idx.get("D6_all_pp"), idx.get("D6_all_ffff")
    if _pp and _pp.ok and _ffff and _ffff.ok:
        t_pp = float(_get(_pp, "density", "total"))
        t_ff = float(_get(_ffff, "density", "total"))
        # Expected musical ordering: all-ffff > all-pp. When this fails (e.g. loud-tail
        # / table non-monotone at extremes), record as caveat finding — not a crash.
        ordered = t_ff > t_pp + 1e-12
        add(
            "D",
            "D6_ffff_gt_pp",
            ordered,
            f"pp={t_pp:.6g} ffff={t_ff:.6g} ratio={t_ff / t_pp if t_pp else float('inf'):.4g}",
            severity="caveat" if not ordered else "blocker",
        )
    if idx.get("D7_tamtam_qty50") and idx["D7_tamtam_qty50"].ok:
        t = float(_get(idx["D7_tamtam_qty50"], "density", "total"))
        add(
            "D",
            "D7_absurd_qty_finite",
            math.isfinite(t) and t > 0,
            f"total={t} (musically unreal; numerically sane)",
            severity="caveat",
        )

    # E4 formula self-check on all successful slices
    for r in results:
        if not r.ok or r.spec.get("expect_error"):
            continue
        ok, detail = header_formula_self_check(r)
        add("E", f"E4_header_{r.spec['id']}", ok, detail, slice_id=r.spec["id"])

    # E1–E3 property trials
    asserts.extend(
        _property_trials(seed=seed, e1_trials=e1_trials, e1_slices=e1_slices)
    )

    return asserts


def _property_trials(
    *, seed: int, e1_trials: int, e1_slices: int
) -> list[AssertionResult]:
    rng = np.random.default_rng(seed)
    asserts: list[AssertionResult] = []
    pitched_pool = [
        ("Violin", "C4"),
        ("Violin", "E4"),
        ("Violin", "G4"),
        ("Viola", "C4"),
        ("Cello", "C3"),
        ("Cello", "G2"),
        ("Flute", "C5"),
        ("Oboe", "C4"),
        ("Double bass", "C2"),
        ("Piano", "C4"),
    ]
    unpitched_pool = [
        ("Bass drum", "D2"),
        ("Cymbals", "C5"),
        ("Tam-tam", "C2"),
        ("Gong", "C3"),
    ]
    dyn_pool = ("pp", "mf", "ff", "ffff")

    def random_slice(n_events: int) -> SliceSpec:
        notes, dyns, insts, qtys = [], [], [], []
        for _ in range(n_events):
            if rng.random() < 0.7:
                inst, note = pitched_pool[int(rng.integers(0, len(pitched_pool)))]
            else:
                inst, note = unpitched_pool[int(rng.integers(0, len(unpitched_pool)))]
            notes.append(note)
            dyns.append(dyn_pool[int(rng.integers(0, len(dyn_pool)))])
            insts.append(inst)
            qtys.append(int(rng.integers(1, 4)))
        return {
            "id": "rand",
            "family": "E",
            "summary": "random",
            "notes": tuple(notes),
            "dynamics": tuple(dyns),
            "instruments": tuple(insts),
            "qtys": tuple(qtys),
            "weight_factor": WEIGHT,
            "expect_error": False,
        }

    # E1 monotonicity
    fails = 0
    for trial in range(e1_trials):
        base = random_slice(int(rng.integers(1, 5)))
        add_pitched = rng.random() < 0.5
        if add_pitched:
            inst, note = pitched_pool[int(rng.integers(0, len(pitched_pool)))]
        else:
            inst, note = unpitched_pool[int(rng.integers(0, len(unpitched_pool)))]
        nxt = {
            **base,
            "notes": base["notes"] + (note,),
            "dynamics": base["dynamics"] + (dyn_pool[int(rng.integers(0, len(dyn_pool)))],),
            "instruments": base["instruments"] + (inst,),
            "qtys": base["qtys"] + (int(rng.integers(1, 3)),),
        }
        rb, ra = run_slice(base), run_slice(nxt)
        if not rb.ok or not ra.ok:
            fails += 1
            continue
        tb = float(_get(rb, "density", "total"))
        ta = float(_get(ra, "density", "total"))
        if ta + 1e-12 < tb:
            fails += 1
    asserts.append(
        AssertionResult(
            "E",
            "E1_monotonicity_random_additions",
            fails == 0,
            f"trials={e1_trials} failures={fails} seed={seed}",
        )
    )

    # E2 pitch-space invariance under unpitched deletion
    e2_fail = 0
    for _ in range(e1_slices):
        # ensure at least one pitched and one unpitched
        notes = ["C4", "E4", "D2"]
        dyns = ["mf", "mf", "ff"]
        insts = ["Violin", "Viola", "Bass drum"]
        qtys = [1, 1, 1]
        for _j in range(int(rng.integers(0, 3))):
            inst, note = pitched_pool[int(rng.integers(0, len(pitched_pool)))]
            notes.append(note)
            dyns.append("mf")
            insts.append(inst)
            qtys.append(1)
        for _j in range(int(rng.integers(1, 3))):
            inst, note = unpitched_pool[int(rng.integers(0, len(unpitched_pool)))]
            notes.append(note)
            dyns.append("ff")
            insts.append(inst)
            qtys.append(1)
        mixed = {
            "id": "e2",
            "family": "E",
            "summary": "e2",
            "notes": tuple(notes),
            "dynamics": tuple(dyns),
            "instruments": tuple(insts),
            "qtys": tuple(qtys),
            "weight_factor": WEIGHT,
            "expect_error": False,
        }
        pitched_only = {
            **mixed,
            "notes": tuple(
                n
                for n, i in zip(notes, insts)
                if i not in {u[0] for u in unpitched_pool}
            ),
            "dynamics": tuple(
                d
                for d, i in zip(dyns, insts)
                if i not in {u[0] for u in unpitched_pool}
            ),
            "instruments": tuple(i for i in insts if i not in {u[0] for u in unpitched_pool}),
            "qtys": tuple(
                q
                for q, i in zip(qtys, insts)
                if i not in {u[0] for u in unpitched_pool}
            ),
        }
        rm, rp = run_slice(mixed), run_slice(pitched_only)
        if not rm.ok or not rp.ok:
            e2_fail += 1
            continue
        for key in ("interval", "pitch_structure"):
            if abs(
                float(_get(rm, "density", key)) - float(_get(rp, "density", key))
            ) > 1e-12:
                e2_fail += 1
                break
        else:
            # spectral entropy if pitched content exists
            se_m = _get(rm, "spectral_moments", "spectral_entropy")
            se_p = _get(rp, "spectral_moments", "spectral_entropy")
            if se_m is not None and se_p is not None and se_m != se_p:
                e2_fail += 1
    asserts.append(
        AssertionResult(
            "E",
            "E2_pitch_metrics_invariant_deleting_unpitched",
            e2_fail == 0,
            f"slices={e1_slices} failures={e2_fail}",
        )
    )

    # E3 Qty scaling
    e3_fail = 0
    for _ in range(min(10, e1_slices)):
        base = {
            "id": "e3",
            "family": "E",
            "summary": "e3",
            "notes": ("C4", "E4", "G4"),
            "dynamics": ("mf", "mf", "mf"),
            "instruments": ("Violin", "Viola", "Cello"),
            "qtys": (1, 2, 1),
            "weight_factor": WEIGHT,
            "expect_error": False,
        }
        k = int(rng.integers(2, 5))
        scaled = {**base, "qtys": tuple(q * k for q in base["qtys"])}
        rb, rs = run_slice(base), run_slice(scaled)
        if not rb.ok or not rs.ok:
            e3_fail += 1
            continue
        for key in ("interval", "pitch_structure"):
            if abs(float(_get(rb, "density", key)) - float(_get(rs, "density", key))) > 1e-12:
                e3_fail += 1
                break
        mb = float(_get(rb, "density", "sonic_mass"))
        ms = float(_get(rs, "density", "sonic_mass"))
        if abs(ms - mb * k) > 1e-6 * max(1.0, abs(mb * k)):
            e3_fail += 1
    asserts.append(
        AssertionResult(
            "E",
            "E3_qty_scale_pitch_invariant_mass_linear",
            e3_fail == 0,
            f"failures={e3_fail}",
        )
    )

    return asserts


def csv_sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def prepare_and_validate_registry() -> list[SliceSpec]:
    scenarios = build_scenarios()
    require_instruments(all_instrument_names(scenarios))
    return scenarios
