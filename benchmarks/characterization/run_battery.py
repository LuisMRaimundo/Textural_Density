"""Characterization battery runner (value dump, not pass/fail).

Resolves instrument roles against the live registry, materializes the DATA case
list, runs every case through ``core.calculate_metrics`` (twice, for a
determinism probe), collects curated columns + the full result dict, runs a set
of reported probes (which never abort the run), and writes the deliverables to
``results/characterization/``.

Read-only characterization: does not modify config, core, or metric logic.
"""

from __future__ import annotations

import csv
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:  # ensure non-ASCII report content prints cleanly on Windows consoles
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from config import DYNAMIC_LEVELS  # noqa: E402
from core import calculate_metrics  # noqa: E402
from core.defaults import METRIC_SCHEMA_VERSION  # noqa: E402
from instrumentos.registry import list_instrument_ids, resolve_profile  # noqa: E402
from microtonal import InvalidPitchNotation, note_to_midi  # noqa: E402

import battery_cases as BC  # noqa: E402

OUT_DIR = ROOT / "results" / "characterization"

CURATED_COLUMNS = [
    "id", "category", "description", "notes", "dynamics", "instruments", "assigned", "qty", "w",
    "n_events", "n_distinct", "player_count", "span_semitones",
    "interval_raw", "interval_reported", "pitch_structure_density",
    "sonic_mass", "instrument_rss", "composite_total", "composite_total_pre_log",
    "spectral_entropy", "harmonic_ratio", "weighted_orchestral", "weighted_pitch",
    "warnings", "nonfinite_flag",
]

NUMERIC_FIELDS = [
    "span_semitones", "interval_raw", "interval_reported", "pitch_structure_density",
    "sonic_mass", "instrument_rss", "composite_total", "composite_total_pre_log",
    "spectral_entropy", "harmonic_ratio", "weighted_orchestral", "weighted_pitch",
]

TOL = 1e-9


def get_pkg_version() -> str:
    try:
        import importlib.metadata as md

        return md.version("densidade-vertical")
    except Exception:
        pass
    try:
        txt = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        m = re.search(r'^version\s*=\s*"([^"]+)"', txt, re.M)
        if m:
            return m.group(1)
    except Exception:
        pass
    return "unknown"


class CaseSetupError(Exception):
    """Raised when no module-backed instrument covers a required pitch."""


def _module_backed(key: str):
    """Return the resolved profile only if it has a dedicated script (module_name)."""
    p = resolve_profile(key)
    if p is not None and getattr(p, "module_name", None):
        return p
    return None


def in_range(prof, midi: float) -> bool:
    """True when ``midi`` lies within the profile's registry sounding range."""
    lo, hi = prof.sounding_range
    return lo <= midi <= hi


def band_preferred(midi: float) -> list[str]:
    """Register-band preferred order of module-backed registry ids (not hardcoded ranges)."""
    if midi < 40:
        return ["contrabaixo", "fagote"]
    if midi <= 54:
        return ["fagote", "violoncelo", "clarinete"]
    if midi <= 70:
        return ["clarinete", "violino", "trompete"]
    if midi <= 98:
        return ["flauta", "violino"]
    return ["violino"]


def assign(pitch: str, preferred_order: list[str]) -> str:
    """First module-backed instrument whose registry range covers the sounding MIDI."""
    m = note_to_midi(pitch, strict=True)
    for key in preferred_order:
        prof = resolve_profile(key)
        if prof is not None and getattr(prof, "module_name", None) and in_range(prof, m):
            return key
    raise CaseSetupError(f"no module-backed instrument covers {pitch} (MIDI {m:.6g})")


def auto_assign_instruments(notes: list[str]) -> tuple[list[str], list[tuple[str, str]]]:
    """Assign each note a register-appropriate module-backed instrument.

    Returns ``(instruments, mapping)`` where ``mapping`` is the pitch->instrument
    log. Raises ``CaseSetupError`` on the first uncoverable note.
    """
    instruments: list[str] = []
    mapping: list[tuple[str, str]] = []
    for p in notes:
        m = note_to_midi(p, strict=True)
        inst = assign(p, band_preferred(m))
        instruments.append(inst)
        mapping.append((p, inst))
    return instruments, mapping


def resolve_roles(pool: list[str], substitutions: list) -> dict[str, str]:
    """Resolve each role to a preferred key that has a dedicated script.

    Only module-backed instruments (``profile.module_name`` set) are eligible;
    coarse-only profiles (e.g. Piccolo/``flautim``) are skipped. Falls back to the
    first module-backed id in POOL order and logs the substitution.
    """
    module_pool = [i for i in pool if _module_backed(i) is not None]
    roles: dict[str, str] = {}
    for role, preferred in BC.ROLE_PREFERENCES.items():
        chosen = None
        for key in preferred:
            if _module_backed(key) is not None:
                chosen = key
                break
        if chosen is None:
            chosen = module_pool[0] if module_pool else pool[0]
            substitutions.append({"role": role, "preferred": preferred, "substituted": chosen})
        roles[role] = chosen
    return roles


def extract_curated(res: dict) -> dict:
    d = res["density"]
    agg = res["pitch_aggregation"]
    mm = res.get("metric_metadata", {})
    metrics = mm.get("metrics", {})
    sm = res.get("spectral_moments", {})
    am = res.get("additional_metrics", {})
    ct_inputs = res.get("composite_trace", {}).get("inputs", {})
    warns = sorted(set(mm.get("warnings", []) or []))
    return {
        "n_events": agg.get("event_count"),
        "n_distinct": agg.get("distinct_pitch_count"),
        "player_count": agg.get("player_count"),
        "span_semitones": ct_inputs.get("registral_span"),
        "interval_raw": metrics.get("density.interval", {}).get("raw_value"),
        "interval_reported": d.get("interval"),
        "pitch_structure_density": d.get("pitch_structure"),
        "sonic_mass": d.get("sonic_mass"),
        "instrument_rss": d.get("instrument"),
        "composite_total": d.get("total"),
        "composite_total_pre_log": metrics.get("density.total", {}).get("raw_value"),
        "spectral_entropy": sm.get("spectral_entropy"),
        "harmonic_ratio": am.get("harmonic_ratio"),
        "weighted_orchestral": d.get("weighted_orchestral"),
        "weighted_pitch": d.get("weighted_pitch"),
        "warnings": warns,
    }


def numeric_signature(curated: dict) -> tuple:
    sig = []
    for f in NUMERIC_FIELDS:
        v = curated.get(f)
        sig.append(round(v, 12) if isinstance(v, (int, float)) and math.isfinite(v) else v)
    return tuple(sig)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pool = list_instrument_ids()
    substitutions: list = []
    roles = resolve_roles(pool, substitutions)
    cases = BC.build_cases(roles)

    rows: list[dict] = []
    full_records: list[dict] = []
    errors: list[dict] = []
    nondeterminism: list[dict] = []
    nonfinite: list[dict] = []
    density_schema: list[str] = []
    result_schema: list[str] = []

    for case in cases:
        n = len(case.notes)
        dynamics = case.dynamics if case.dynamics is not None else ["mf"] * n
        qty = case.num_instruments if case.num_instruments is not None else [1] * n

        # Strict pitch validation on EVERY literal pitch (never silent C4).
        try:
            for p in case.notes:
                note_to_midi(p, strict=True)
        except InvalidPitchNotation as exc:
            errors.append({"id": case.id, "stage": "pitch_validation", "message": str(exc),
                           "notes": case.notes})
            continue

        # Register-aware auto-assignment (logged); uncoverable notes -> ERRORS.
        assigned_map: list[tuple[str, str]] | None = None
        if case.auto:
            try:
                instruments, assigned_map = auto_assign_instruments(case.notes)
            except CaseSetupError as exc:
                errors.append({"id": case.id, "stage": "instrument_assignment",
                               "message": f"CaseSetupError: {exc}", "notes": case.notes})
                continue
        else:
            instruments = case.instruments

        data = {
            "notes": case.notes,
            "dynamics": dynamics,
            "instruments": instruments,
            "num_instruments": qty,
            "weight_factor": case.weight_factor,
        }

        try:
            res1, _, _ = calculate_metrics(dict(data))
            res2, _, _ = calculate_metrics(dict(data))
        except Exception as exc:  # never abort the run
            errors.append({"id": case.id, "stage": "calculate_metrics",
                           "message": f"{type(exc).__name__}: {exc}", "notes": case.notes})
            continue

        if not density_schema:
            density_schema = sorted(res1["density"].keys())
            result_schema = sorted(res1.keys())

        cur1 = extract_curated(res1)
        cur2 = extract_curated(res2)
        if numeric_signature(cur1) != numeric_signature(cur2):
            nondeterminism.append({"id": case.id, "run1": numeric_signature(cur1),
                                   "run2": numeric_signature(cur2)})

        nf_fields = [f for f in NUMERIC_FIELDS
                     if isinstance(cur1.get(f), (int, float)) and not math.isfinite(cur1[f])]
        nonfinite_flag = bool(nf_fields)
        if nonfinite_flag:
            nonfinite.append({"id": case.id, "fields": nf_fields})

        assigned_str = (" ".join(f"{p}:{i}" for p, i in assigned_map)
                        if assigned_map is not None else "")
        row = {
            "id": case.id,
            "category": case.category,
            "description": case.description,
            "notes": " ".join(case.notes),
            "dynamics": " ".join(dynamics),
            "instruments": " ".join(instruments),
            "qty": " ".join(str(q) for q in qty),
            "w": case.weight_factor,
            **{k: cur1[k] for k in (
                "n_events", "n_distinct", "player_count", "span_semitones",
                "interval_raw", "interval_reported", "pitch_structure_density",
                "sonic_mass", "instrument_rss", "composite_total", "composite_total_pre_log",
                "spectral_entropy", "harmonic_ratio", "weighted_orchestral", "weighted_pitch")},
            "warnings": cur1["warnings"],
            "nonfinite_flag": nonfinite_flag,
            "assigned": assigned_str,
            "auto": bool(case.auto),
            "_probe": case.probe,
        }
        rows.append(row)
        full_records.append({
            "id": case.id, "category": case.category, "description": case.description,
            "input": data, "auto_assigned": case.auto,
            "assignment_map": assigned_map, "curated": {k: cur1[k] for k in cur1},
            "nonfinite_flag": nonfinite_flag, "resultados": res1,
        })

    probes = run_probes(rows)

    header = {
        "tool": "benchmarks/characterization/run_battery.py",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "metric_schema_version": METRIC_SCHEMA_VERSION,
        "package_version": get_pkg_version(),
        "dynamic_levels": list(DYNAMIC_LEVELS),
        "resolved_instrument_map": roles,
        "substitutions": substitutions,
        "pool_size": len(pool),
        "result_schema": result_schema,
        "density_schema": density_schema,
        "n_cases_total": len(cases),
        "n_cases_valued": len(rows),
        "n_errors": len(errors),
    }

    write_json(full_records, header)
    write_csv(rows)
    md = build_markdown(header, rows, probes, errors, nondeterminism, nonfinite)
    (OUT_DIR / "characterization_battery.md").write_text(md, encoding="utf-8")
    write_readme(header)

    print(md)
    return 0


def run_probes(rows: list[dict]) -> list[dict]:
    by_id = {r["id"]: r for r in rows}
    probes: list[dict] = []

    def grp(name: str) -> list[dict]:
        g = [r for r in rows if r.get("_probe") and r["_probe"].get("group") == name]
        return sorted(g, key=lambda r: r["_probe"].get("order", 0))

    for gname in ("card_compact", "card_wide", "card_farbass"):
        series = grp(gname)
        if not series:
            continue
        seq = [(r["id"], r["composite_total"]) for r in series]
        ok = all(seq[i][1] >= seq[i - 1][1] - 1e-9 for i in range(1, len(seq)))
        probes.append({"name": f"monotonic composite_total [{gname}]",
                       "status": "OK" if ok else "VIOLATED",
                       "detail": " -> ".join(f"{i}:{v:.6g}" for i, v in seq)})

    single = by_id.get("QTY.rowsplit_single")
    split = by_id.get("QTY.rowsplit_split")
    if single and split:
        checks = {f: (single[f], split[f]) for f in ("sonic_mass", "instrument_rss", "pitch_structure_density")}
        ok = all(abs((a or 0) - (b or 0)) <= 1e-6 for a, b in checks.values())
        probes.append({"name": "QTY row-split equivalence (mass/RSS/pitch_structure)",
                       "status": "OK" if ok else "VIOLATED",
                       "detail": "; ".join(f"{k}: single={a:.6g} split={b:.6g}" for k, (a, b) in checks.items())})

    uni = next((r for r in rows if r.get("_probe") and r["_probe"].get("kind") == "unison_zero"), None)
    if uni:
        ok = abs(uni["pitch_structure_density"] or 0) <= 1e-9
        probes.append({"name": "QTY unison pitch_structure_density == 0",
                       "status": "OK" if ok else "VIOLATED",
                       "detail": f"pitch_structure_density={uni['pitch_structure_density']:.6g}; "
                                 f"sonic_mass={uni['sonic_mass']:.6g}; instrument_rss={uni['instrument_rss']:.6g}; "
                                 f"players={uni['player_count']}"})

    wsweep = grp("weight_sweep")
    if wsweep:
        comps = [r["composite_total"] for r in wsweep]
        ok = max(comps) - min(comps) <= 1e-9
        probes.append({"name": "WEIGHT invariance of composite_total",
                       "status": "OK (invariant)" if ok else "VARIES",
                       "detail": "; ".join(f"w={r['w']}: comp={r['composite_total']:.6g} "
                                           f"(w_orch={r['weighted_orchestral']:.6g}, w_pitch={r['weighted_pitch']:.6g})"
                                           for r in wsweep)})

    iso = grp("timbre_iso")
    if len(iso) == 2:
        a, b = iso
        ok = abs((a["pitch_structure_density"] or 0) - (b["pitch_structure_density"] or 0)) <= 1e-9 and \
            abs((a["interval_reported"] or 0) - (b["interval_reported"] or 0)) <= 1e-9
        probes.append({"name": "INST timbre-isolation: identical pitch structure, differing timbre",
                       "status": "OK" if ok else "DIFFERS",
                       "detail": f"PSD {a['id']}={a['pitch_structure_density']:.6g} vs {b['id']}={b['pitch_structure_density']:.6g}; "
                                 f"composite {a['composite_total']:.6g} vs {b['composite_total']:.6g}"})

    def _mono(role_name: str, pair: str):
        return next((r for r in rows if r.get("_probe")
                     and r["_probe"].get("mono") == pair
                     and r["_probe"].get("role") == role_name), None)

    for pair in ("octave", "twelfth", "farbass"):
        base, add = _mono("base", pair), _mono("add", pair)
        if not base or not add:
            continue

        def _d(field):
            return (add[field] or 0.0) - (base[field] or 0.0)

        dS, dcomp = _d("interval_raw"), _d("composite_total")
        decreased = dcomp < -1e-12
        probes.append({
            "name": f"MONO adversarial addition [{pair}] (composite non-decrease)",
            "status": "DECREASED" if decreased else "OK",
            "detail": (f"dS={dS:+.6g}; dharm={_d('harmonic_ratio'):+.6g}; "
                       f"dentropy={_d('spectral_entropy'):+.6g}; dmass={_d('sonic_mass'):+.6g}; "
                       f"dPSD={_d('pitch_structure_density'):+.6g}; dcomposite={dcomp:+.6g} "
                       f"({base['id']}->{add['id']}: S {base['interval_raw']:.6g}->{add['interval_raw']:.6g}, "
                       f"comp {base['composite_total']:.6g}->{add['composite_total']:.6g})"),
        })

    def pget(field: str, value):
        return next((r for r in rows if r.get("_probe") and r["_probe"].get(field) == value), None)

    # REG-1: register-invariance of S for identical shapes (instruments vary by register).
    reg_rows = [r for r in rows if r.get("_probe") and r["_probe"].get("group") == "reg"]
    for shape in ("cluster3", "triad"):
        g = sorted([r for r in reg_rows if r["_probe"].get("shape") == shape],
                   key=lambda r: r["_probe"].get("reg", ""))
        if not g:
            continue
        s_vals = [r["interval_raw"] for r in g]
        ok = (max(s_vals) - min(s_vals)) <= 1e-6
        detail = "; ".join(f"{r['_probe']['reg']}[{r['instruments']}]: S={r['interval_raw']:.6g}, "
                           f"mass={r['sonic_mass']:.6g}, RSS={r['instrument_rss']:.6g}, "
                           f"comp={r['composite_total']:.6g}" for r in g)
        probes.append({"name": f"REG-1 register-invariance of S [{shape}]",
                       "status": "OK (S identical)" if ok else "FINDING",
                       "detail": detail})

    # BI-1: bimodal strata — union vs parts; S additive (cross-strata pairs ~0), int diluted.
    low, high, comb = pget("bi", "low"), pget("bi", "high"), pget("bi", "combined")
    if low and high and comb:
        s_sum = (low["interval_raw"] or 0) + (high["interval_raw"] or 0)
        c_sum = (low["composite_total"] or 0) + (high["composite_total"] or 0)
        union_more = comb["composite_total"] > max(low["composite_total"], high["composite_total"])
        s_additive = abs((comb["interval_raw"] or 0) - s_sum) <= 1e-2
        ok = union_more and s_additive
        probes.append({"name": "BI-1 bimodal strata union vs parts", "status": "OK" if ok else "FINDING",
                       "detail": (f"S: low={low['interval_raw']:.6g} + high={high['interval_raw']:.6g} = {s_sum:.6g} "
                                  f"vs combined={comb['interval_raw']:.6g} (cross-strata {comb['interval_raw'] - s_sum:+.3g}); "
                                  f"int(compactness): low={low['interval_reported']:.6g}, high={high['interval_reported']:.6g}, "
                                  f"combined={comb['interval_reported']:.6g} (span dilutes); "
                                  f"composite: low={low['composite_total']:.6g}, high={high['composite_total']:.6g}, "
                                  f"parts-sum={c_sum:.6g}, combined={comb['composite_total']:.6g}")})

    # DS-1: density/mass opposition 2x2 — which axis orders the composite.
    ds = {k: pget("ds", k) for k in ("dense_soft", "sparse_loud", "dense_loud", "sparse_soft")}
    if all(ds.values()):
        dense_psd = min(ds["dense_soft"]["pitch_structure_density"], ds["dense_loud"]["pitch_structure_density"])
        sparse_psd = max(ds["sparse_loud"]["pitch_structure_density"], ds["sparse_soft"]["pitch_structure_density"])
        ok = dense_psd > sparse_psd
        detail = "; ".join(f"{k}: S={r['interval_raw']:.6g}, mass={r['sonic_mass']:.6g}, RSS={r['instrument_rss']:.6g}, "
                           f"PSD={r['pitch_structure_density']:.6g}, comp={r['composite_total']:.6g}"
                           for k, r in ds.items())
        probes.append({"name": "DS-1 density/mass opposition (2x2)",
                       "status": "OK (pitch-structure orders dense>sparse)" if ok else "FINDING",
                       "detail": detail})

    # DG-1: opposed dynamics at fixed pitch structure — S identical for a-d.
    dg = {k: pget("dg", k) for k in ("uniform", "wedge", "inv_wedge", "extremes")}
    if all(dg.values()):
        s_vals = [r["interval_raw"] for r in dg.values()]
        ok = (max(s_vals) - min(s_vals)) <= 1e-9
        detail = "; ".join(f"{k}: S={r['interval_raw']:.6g}, mass={r['sonic_mass']:.6g}, RSS={r['instrument_rss']:.6g}, "
                           f"entropy={r['spectral_entropy']:.6g}, harm={r['harmonic_ratio']:.6g}, "
                           f"PSD={r['pitch_structure_density']:.6g}, comp={r['composite_total']:.6g}"
                           for k, r in dg.items())
        probes.append({"name": "DG-1 opposed dynamics at fixed pitch structure",
                       "status": "OK (S identical a-d)" if ok else "FINDING",
                       "detail": detail})

    # FU-1: fusion vs inharmonicity — 15% harmonic damping separation at matched cardinality.
    harmonic, inharm = pget("fu", "harmonic"), pget("fu", "inharmonic")
    pillar, qtone = pget("fu", "octave_pillar"), pget("fu", "qtone_cluster")
    parts, ok_ab, ok_cd = [], True, True
    if harmonic and inharm:
        ok_ab = harmonic["harmonic_ratio"] > inharm["harmonic_ratio"]
        parts.append(f"a-vs-b: harmonic(harm={harmonic['harmonic_ratio']:.6g}, PSD={harmonic['pitch_structure_density']:.6g}, "
                     f"comp={harmonic['composite_total']:.6g}) vs inharmonic(harm={inharm['harmonic_ratio']:.6g}, "
                     f"PSD={inharm['pitch_structure_density']:.6g}, comp={inharm['composite_total']:.6g})")
    if pillar and qtone:
        ok_cd = pillar["harmonic_ratio"] > qtone["harmonic_ratio"]
        parts.append(f"c-vs-d: octave_pillar(harm={pillar['harmonic_ratio']:.6g}, PSD={pillar['pitch_structure_density']:.6g}, "
                     f"comp={pillar['composite_total']:.6g}) vs qtone(harm={qtone['harmonic_ratio']:.6g}, "
                     f"PSD={qtone['pitch_structure_density']:.6g}, comp={qtone['composite_total']:.6g})")
    if parts:
        probes.append({"name": "FU-1 fusion vs inharmonicity (harmonic damping)",
                       "status": "OK" if (ok_ab and ok_cd) else "FINDING", "detail": " || ".join(parts)})

    # MA-1: Qty asymmetry at fixed pitch structure — S identical, composite is pure orchestral weighting.
    ma = {k: pget("ma", k) for k in ("massed_bass", "massed_treble", "balanced")}
    if all(ma.values()):
        s_vals = [r["interval_raw"] for r in ma.values()]
        ok = (max(s_vals) - min(s_vals)) <= 1e-9
        detail = "; ".join(f"{k}: S={r['interval_raw']:.6g}, mass={r['sonic_mass']:.6g}, RSS={r['instrument_rss']:.6g}, "
                           f"comp={r['composite_total']:.6g}" for k, r in ma.items())
        probes.append({"name": "MA-1 Qty asymmetry at fixed pitch structure",
                       "status": "OK (S identical)" if ok else "FINDING", "detail": detail})

    # GLOBAL-1: top-5 / bottom-5 by composite, PSD, RSS across all valued cases (face validity).
    def _topbot(field: str, label: str) -> str:
        valid = [r for r in rows if isinstance(r.get(field), (int, float)) and math.isfinite(r[field])]
        s = sorted(valid, key=lambda r: r[field])
        top = ", ".join(f"{r['id']}={r[field]:.6g}" for r in reversed(s[-5:]))
        bot = ", ".join(f"{r['id']}={r[field]:.6g}" for r in s[:5])
        return f"{label} TOP5: {top} || BOTTOM5: {bot}"

    probes.append({"name": "GLOBAL-1 face-validity rankings (all valued cases)", "status": "OK",
                   "detail": (_topbot("composite_total", "composite") + "  ;;  "
                              + _topbot("pitch_structure_density", "PSD") + "  ;;  "
                              + _topbot("instrument_rss", "RSS"))})
    return probes


def fnum(v) -> str:
    if v is None:
        return ""
    if isinstance(v, bool):
        return "T" if v else "F"
    if isinstance(v, float):
        if not math.isfinite(v):
            return "NONFINITE"
        return f"{v:.6g}"
    return str(v)


MD_COLUMNS = [
    ("id", "id"), ("description", "desc"), ("notes", "notes"), ("instruments", "instr"),
    ("auto", "asg"), ("dynamics", "dyn"), ("qty", "qty"), ("w", "w"),
    ("n_events", "ev"), ("n_distinct", "dist"), ("player_count", "plr"),
    ("span_semitones", "span"), ("interval_raw", "S(raw)"), ("interval_reported", "int"),
    ("pitch_structure_density", "PSD"), ("sonic_mass", "mass"), ("instrument_rss", "RSS"),
    ("composite_total", "comp"), ("composite_total_pre_log", "comp_pre"),
    ("spectral_entropy", "entropy"), ("harmonic_ratio", "harm"),
    ("weighted_orchestral", "w_orch"), ("weighted_pitch", "w_pitch"),
    ("warnings", "warn#"), ("nonfinite_flag", "nf"),
]


def _cell(row: dict, key: str) -> str:
    if key == "warnings":
        return str(len(row["warnings"]))
    if key == "auto":
        return "auto" if row.get("auto") else ""
    v = row.get(key)
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return fnum(v)
    return fnum(v) if isinstance(v, bool) else str(v)


def build_markdown(header, rows, probes, errors, nondeterminism, nonfinite) -> str:
    L: list[str] = []
    L.append("# Textural Density — Characterization Battery (value dump)")
    L.append("")
    L.append(f"- **Tool:** `{header['tool']}`")
    L.append(f"- **Generated:** {header['generated_at']}")
    L.append(f"- **METRIC_SCHEMA_VERSION:** `{header['metric_schema_version']}`")
    L.append(f"- **Package version (pyproject):** `{header['package_version']}`")
    L.append(f"- **Cases:** {header['n_cases_valued']} valued / {header['n_cases_total']} total; "
             f"errors: {header['n_errors']}")
    L.append(f"- **DYNAMIC_LEVELS:** {', '.join(header['dynamic_levels'])}")
    L.append(f"- **Registry POOL size:** {header['pool_size']}")
    L.append("- **Resolved instrument map:**")
    for role, inst in header["resolved_instrument_map"].items():
        L.append(f"  - `{role}` -> `{inst}`")
    if header["substitutions"]:
        L.append("- **Substitutions (preferred key unresolved -> POOL fallback):**")
        for s in header["substitutions"]:
            L.append(f"  - `{s['role']}` {s['preferred']} -> `{s['substituted']}`")
    else:
        L.append("- **Substitutions:** none (all preferred role keys resolved)")
    L.append(f"- **`sorted(resultados.keys())`:** {header['result_schema']}")
    L.append(f"- **`sorted(resultados['density'].keys())`:** {header['density_schema']}")
    L.append("")
    L.append("**Column legend:** `S(raw)`=raw pairwise interval sum "
             "(`metric_metadata.metrics['density.interval'].raw_value`); "
             "`int`=`density.interval` (reported compactness); `PSD`=`density.pitch_structure`; "
             "`mass`=`density.sonic_mass`; `RSS`=`density.instrument` (pressure-equiv); "
             "`comp`=`density.total`; `comp_pre`=composite pre-log "
             "(`metrics['density.total'].raw_value`); `entropy`=`spectral_moments.spectral_entropy`; "
             "`harm`=`additional_metrics.harmonic_ratio`; `span`=`composite_trace.inputs.registral_span`; "
             "`asg`=`auto` when instruments were register-auto-assigned (full pitch->instrument map in the "
             "*Per-case assignment map* appendix and the CSV `assigned` column); "
             "`warn#`=count of distinct `metric_metadata.warnings`; `nf`=non-finite flag. "
             "Full warning text per case is in the JSON and the *Per-case warnings* appendix.")
    L.append("")

    cats: list[str] = []
    for r in rows:
        if r["category"] not in cats:
            cats.append(r["category"])

    head = "| " + " | ".join(lbl for _, lbl in MD_COLUMNS) + " |"
    sep = "|" + "|".join("---" for _ in MD_COLUMNS) + "|"
    for cat in cats:
        L.append(f"## {cat}")
        L.append("")
        L.append(head)
        L.append(sep)
        for r in rows:
            if r["category"] != cat:
                continue
            L.append("| " + " | ".join(_cell(r, key) for key, _ in MD_COLUMNS) + " |")
        L.append("")

    L.append("## PROBES (reported only; never abort)")
    L.append("")
    if probes:
        for p in probes:
            L.append(f"- **[{p['status']}]** {p['name']} — {p['detail']}")
    else:
        L.append("- (none)")
    L.append("")

    L.append("## ERRORS (excluded from value table)")
    L.append("")
    if errors:
        for e in errors:
            L.append(f"- `{e['id']}` [{e['stage']}]: {e['message']} — notes={e['notes']}")
    else:
        L.append("- (none)")
    L.append("")

    L.append("## NONDETERMINISM (curated outputs differ across two runs)")
    L.append("")
    if nondeterminism:
        for nd in nondeterminism:
            L.append(f"- `{nd['id']}`: run1={nd['run1']} run2={nd['run2']}")
    else:
        L.append("- (none — all cases deterministic across two runs)")
    L.append("")

    L.append("## NON-FINITE (any reported scalar not finite)")
    L.append("")
    if nonfinite:
        for nf in nonfinite:
            L.append(f"- `{nf['id']}`: fields={nf['fields']}")
    else:
        L.append("- (none — all reported scalars finite)")
    L.append("")

    L.append("## Per-case assignment map (auto-assigned cases)")
    L.append("")
    any_a = False
    for r in rows:
        if r.get("auto") and r.get("assigned"):
            any_a = True
            L.append(f"- `{r['id']}`: {r['assigned']}")
    if not any_a:
        L.append("- (none)")
    L.append("")

    L.append("## Per-case warnings (full text)")
    L.append("")
    any_w = False
    for r in rows:
        if r["warnings"]:
            any_w = True
            L.append(f"- `{r['id']}`: " + " | ".join(r["warnings"]))
    if not any_w:
        L.append("- (none)")
    L.append("")
    return "\n".join(L)


def write_csv(rows: list[dict]) -> None:
    path = OUT_DIR / "characterization_battery.csv"
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CURATED_COLUMNS)
        writer.writeheader()
        for r in rows:
            out = {k: r.get(k) for k in CURATED_COLUMNS}
            out["warnings"] = " | ".join(r["warnings"])
            writer.writerow(out)


def write_json(full_records: list[dict], header: dict) -> None:
    path = OUT_DIR / "characterization_battery_full.json"
    path.write_text(json.dumps({"header": header, "cases": full_records}, indent=2, default=str),
                    encoding="utf-8")


def write_readme(header: dict) -> None:
    lines = [
        "# Characterization battery — provenance",
        "",
        f"- Generated: {header['generated_at']}",
        f"- Tool: `{header['tool']}`",
        f"- METRIC_SCHEMA_VERSION: `{header['metric_schema_version']}`",
        f"- Package version (pyproject): `{header['package_version']}`",
        f"- Cases: {header['n_cases_valued']} valued / {header['n_cases_total']} total; "
        f"errors: {header['n_errors']}",
        "",
        "## Resolved instrument map",
        "",
    ]
    for role, inst in header["resolved_instrument_map"].items():
        lines.append(f"- `{role}` -> `{inst}`")
    lines.append("")
    lines.append("## Substitutions")
    lines.append("")
    if header["substitutions"]:
        for s in header["substitutions"]:
            lines.append(f"- `{s['role']}` {s['preferred']} -> `{s['substituted']}`")
    else:
        lines.append("- none (all preferred role keys resolved)")
    lines.append("")
    lines.append("## Outputs")
    lines.append("")
    lines.append("- `characterization_battery.md` — grouped human-readable tables + header + diagnostics")
    lines.append("- `characterization_battery.csv` — flat union of all valued rows (curated columns)")
    lines.append("- `characterization_battery_full.json` — per case: input + full `resultados` + curated + flags")
    lines.append("")
    lines.append("Read-only characterization of the current build; config/core/metric logic untouched.")
    (OUT_DIR / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
