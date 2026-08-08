# instrumentos/tamtam.py
"""
Tam-tam instrument density module.

Pitch-independent Combined Density Metric (CDM) proxy from **NonTunPerc**
MC Analysis exports
(``replication/percussion_nontunperc/Analysis/density_profiles_mc.csv``).

Phase = shimmer of the tam-tam template (post-bloom sustained regime). The CDM proxy feeds sustained-texture analysis; the strike window under-represents plates and, combined with the excitation filter, artificially collapses pp/mf.

- **ff:** MC p50 ``composite_index`` for phase ``shimmer``
  (p05=2.634758, p50=12.324004, p95=75.077651; seed=20260803)
- **pp/mf:** ``generate_profile(stroke='yarn_mallet', dynamic=…)``
  shimmer indices, scaled so ff matches MC p50 exactly
- **mf→ff jump:** ff/mf ≈ 3.008 (physical cascade / ff plate bypass
  retained; interior/tail levels committed from the former offline
  piecewise log-linear CDM + adaptive-tail ladder — no runtime fill-in)
- **NonTunPerc:** v0.3.5 commit ``4a110dbbaab3af831c0987e99a4b7019b008bbd6``

Unpitched: GUI/MusicXML/MIDI do not associate sounding pitch. ``nota`` is
ignored; density is dynamics-only. ``spectral_data`` keeps a single canonical
placeholder key (``C2``) for lookup-compat only.
"""

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="model_derived",
    citation=('theoretical model output (NonTunPerc v0.3.5, MC median), anchored in Rossing 2000 / Fletcher & Rossing 1998 / Sivian et al. 1931; validated against Iowa EMS recordings for mallet-excited plates and mf tam-tams; NOT validated for striking-position-specific strokes. Specimen tamtam_80cm_bronze phase=shimmer MC p50 composite_index=12.324004 (p05=2.634758, p95=75.077651; seed=20260803).'),
    source_url_or_identifier=(
        "replication/percussion_nontunperc/Analysis/density_profiles_mc.csv"
    ),
    extraction_method=("density_profiles_mc.csv shimmer p50 band weights → composite_index (ff); generate_profile(stroke='yarn_mallet', dynamic=pp|mf|ff) shimmer indices scaled so ff=MC p50; pitch-independent DYNAMIC_CDM; committed 10-level ladder via offline piecewise log-linear CDM + adaptive tails (former internal_default; not runtime GPR). Cross-family ratio caveat: NonTunPerc calibration bridge reports NO CALIBRATION ACHIEVED; CDM comparisons between these four instruments and empirically derived pitched-instrument tables are rank-order indicative only, not ratio-valid."),
    dynamic_levels=('pppp', 'ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', 'ffff'),
    pitch_range=(24, 48),
    uncertainty="high",
    version="2026-08-03+nontunperc-0.3.5+mc20260803+committed-ladder",
    source_technique="struck_plate",
    table_supported_techniques=("struck_plate",),
    unpitched=True,
)

import logging

from instrumentos.pitch_interpolation import MissingCommittedDynamicError

logger = logging.getLogger("tamtam")

# MC composite_index CI for the chosen phase (scale reference; seed=20260803).
SPECTRAL_PHASE_CI = {
    "phase": "shimmer",
    "p05": 2.634758,
    "p50": 12.324004,
    "p95": 75.077651,
    "mc_seed": 20260803,
    "nontunperc_commit": "4a110dbbaab3af831c0987e99a4b7019b008bbd6",
    "nontunperc_version": "0.3.5",
}

spectral_data_ci = {
    "p05": 2.634758,
    "p50": 12.324004,
    "p95": 75.077651,
}

# Pitch-independent committed 10-dynamic CDM ladder (pp/mf/ff = NonTunPerc
# anchors; other levels = former internal_default log-linear + adaptive tails).
DYNAMIC_CDM = {'pppp': 2.832909, 'ppp': 2.903432, 'pp': 3.049788, 'p': 3.534628, 'mp': 3.805229, 'mf': 4.096546, 'f': 7.105339, 'ff': 12.324004, 'fff': 16.230628, 'ffff': 18.626321}

# Single canonical placeholder for MIDI-space table shape (lookup convention only).
LOOKUP_NOTE = 'C2'
spectral_data = {LOOKUP_NOTE: DYNAMIC_CDM}


def calcular_densidade(nota, dinamica):
    """Unpitched density: dynamics only; ``nota`` is ignored."""
    dyn = (dinamica or "mf").strip().lower()
    if dyn not in DYNAMIC_CDM:
        raise MissingCommittedDynamicError(
            f"Dynamic {dyn!r} not committed in tamtam DYNAMIC_CDM "
            f"(have {sorted(DYNAMIC_CDM)})."
        )
    return float(DYNAMIC_CDM[dyn])
