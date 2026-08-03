# instrumentos/gong.py
"""
Gong instrument density module.

Pitch-independent Combined Density Metric (CDM) proxy from **NonTunPerc**
MC Analysis exports
(``replication/percussion_nontunperc/Analysis/density_profiles_mc.csv``).

Phase = shimmer (tam-tam-template sustained regime for plate gongs; wind-gong subtypes share the same post-bloom emphasis). The CDM proxy feeds sustained-texture analysis; the strike window under-represents plates and, combined with the excitation filter, artificially collapses pp/mf.

- **ff:** MC p50 ``composite_index`` for phase ``shimmer``
  (p05=1.639183, p50=17.148679, p95=112.884854; seed=20260803)
- **pp/mf:** ``generate_profile(stroke='yarn_mallet', dynamic=…)``
  shimmer indices, scaled so ff matches MC p50 exactly
- **mf→ff jump:** ff/mf ≈ 8.135 (physical cascade / ff plate bypass
  retained; interior/tail levels committed from the former offline
  piecewise log-linear CDM + adaptive-tail ladder — no runtime fill-in)
- **NonTunPerc:** v0.3.5 commit ``4a110dbbaab3af831c0987e99a4b7019b008bbd6``

Unpitched: GUI/MusicXML/MIDI do not associate sounding pitch. ``nota`` is
ignored; density is dynamics-only. ``spectral_data`` keeps a single canonical
placeholder key (``C3``) for lookup-compat only.
"""

from instrumentos.provenance import InstrumentSource

INSTRUMENT_SOURCE = InstrumentSource(
    source_type="model_derived",
    citation=('theoretical model output (NonTunPerc v0.3.5, MC median), anchored in Rossing 2000 / Fletcher & Rossing 1998 / Sivian et al. 1931; validated against Iowa EMS recordings for mallet-excited plates and mf tam-tams; NOT validated for striking-position-specific strokes. Specimen gong_50cm_bronze phase=shimmer MC p50 composite_index=17.148679 (p05=1.639183, p95=112.884854; seed=20260803).'),
    source_url_or_identifier=(
        "replication/percussion_nontunperc/Analysis/density_profiles_mc.csv"
    ),
    extraction_method=("density_profiles_mc.csv shimmer p50 band weights → composite_index (ff); generate_profile(stroke='yarn_mallet', dynamic=pp|mf|ff) shimmer indices scaled so ff=MC p50; pitch-independent DYNAMIC_CDM; committed 10-level ladder via offline piecewise log-linear CDM + adaptive tails (former internal_default; not runtime GPR). Cross-family ratio caveat: NonTunPerc calibration bridge reports NO CALIBRATION ACHIEVED; CDM comparisons between these four instruments and empirically derived pitched-instrument tables are rank-order indicative only, not ratio-valid."),
    dynamic_levels=('pppp', 'ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', 'ffff'),
    pitch_range=(36, 60),
    uncertainty="high",
    version="2026-08-03+nontunperc-0.3.5+mc20260803+committed-ladder",
    source_technique="struck_plate",
    table_supported_techniques=("struck_plate",),
    unpitched=True,
)

import logging

from instrumentos.pitch_interpolation import MissingCommittedDynamicError

logger = logging.getLogger("gong")

# MC composite_index CI for the chosen phase (scale reference; seed=20260803).
SPECTRAL_PHASE_CI = {
    "phase": "shimmer",
    "p05": 1.639183,
    "p50": 17.148679,
    "p95": 112.884854,
    "mc_seed": 20260803,
    "nontunperc_commit": "4a110dbbaab3af831c0987e99a4b7019b008bbd6",
    "nontunperc_version": "0.3.5",
}

spectral_data_ci = {
    "p05": 1.639183,
    "p50": 17.148679,
    "p95": 112.884854,
}

# Pitch-independent committed 10-dynamic CDM ladder (pp/mf/ff = NonTunPerc
# anchors; other levels = former internal_default log-linear + adaptive tails).
DYNAMIC_CDM = {'pppp': 1.421062, 'ppp': 1.458913, 'pp': 1.537666, 'p': 1.800363, 'mp': 1.948091, 'mf': 2.10794, 'f': 6.012353, 'ff': 17.148679, 'fff': 28.961682, 'ffff': 37.637462}

# Single canonical placeholder for MIDI-space table shape (lookup convention only).
LOOKUP_NOTE = 'C3'
spectral_data = {LOOKUP_NOTE: DYNAMIC_CDM}


def calcular_densidade(nota, dinamica):
    """Unpitched density: dynamics only; ``nota`` is ignored."""
    dyn = (dinamica or "mf").strip().lower()
    if dyn not in DYNAMIC_CDM:
        raise MissingCommittedDynamicError(
            f"Dynamic {dyn!r} not committed in gong DYNAMIC_CDM "
            f"(have {sorted(DYNAMIC_CDM)})."
        )
    return float(DYNAMIC_CDM[dyn])
