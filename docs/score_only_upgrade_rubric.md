# Textural Density — Score-Only Upgrade Rubric Toward 90+

This rubric evaluates **Textural Density** as a **formal score-based symbolic descriptor** — a systematic score-analysis tool. It does **not** evaluate psychoacoustic realism, audio analysis, perceptual hearing-model validity, or prediction of human ratings.

## Principle

> Textural Density is evaluated as a formal score-based symbolic descriptor. Its methodological strength depends on **explicit construct definitions**, **reproducible score-derived outputs**, **internal consistency**, **canonical test cases**, **corpus benchmarks**, **transparent assumptions**, and **auditable architecture**.

> **External human-rating studies** may be useful if the project later claims to predict expert or listener judgments. **They are not required** for the core score-only systematic research line.

**Not required for 90+:** psychoacoustic tests · listening tests · external human ratings · expert density annotations · inter-rater reliability · correlation with raters.

**Still required:** testing · verification · reproducibility · **formal score-based validation** (systematic construct verification).

Machine-readable definition: [`score_only_upgrade_rubric.json`](score_only_upgrade_rubric.json) (version **2.0.0**)

---

## Validation terminology

| Term | Use |
|------|-----|
| **Formal score-based validation** | Primary label for construct verification via definitions, axioms, and tests |
| **Systematic construct verification** | Alternate label |

**Status labels (systematic line):**

| Label | Meaning |
|-------|---------|
| `formally_defined` | Construct documented with expected behaviours |
| `verified_by_tests` | Regression/property tests confirm axioms |
| `benchmark_replicated` | Frozen outputs match on benchmark inputs |
| `corpus_replicated` | Full representative corpus replicated |
| `externally_compared_optional` | Optional human-rating comparison (not required) |
| `legacy_proxy` | Opt-in out-of-scope branch |
| `out_of_scope` | Not part of score-only line |
| `not_yet_verified` | Defined but not yet covered by tests/benchmark |

**Legacy mapping (compatibility):** `verified_only` → `verified_by_tests` · `score_validated` → `externally_compared_optional` · `unvalidated` → `not_yet_verified`

Lack of external ratings does **not** mean the tool is methodologically invalid on the systematic score-only line.

---

## Dimensions (100 points)

| # | Dimension | Weight |
|---|-----------|--------|
| 1 | Score-only scientific scope and construct clarity | **10** |
| 2 | Formal construct definition and axioms | **15** |
| 3 | Construct separation | **15** |
| 4 | Benchmark corpus and replication package | **15** |
| 5 | Core-native auditable architecture | **15** |
| 6 | Symbolic orchestration metadata honesty | **10** |
| 7 | Testing, regression, and quality gates | **10** |
| 8 | Reporting and epistemic transparency | **10** |
| | **Total** | **100** |

---

## 1. Score-only scope (10)

Symbolic, notation-based, score-derived identity — no psychoacoustic or audio-analysis claims.

| Band | Points |
|------|--------|
| Absent | 0 |
| Minimal | 1–3 |
| Incomplete | 4–6 |
| Strong | 7–8 |
| Research-grade | 9–10 |

---

## 2. Formal construct definition and axioms (15)

Explicit definitions and **expected formal behaviours**, e.g.:

- Adding active score events **increases** event density  
- Adding player count **increases** orchestration mass, **not** interval compactness  
- Widening pitch span **decreases** registral compactness/cohesion (where applicable)  
- Tighter pitch spacing **increases** interval compactness  
- Written dynamics affect **symbolic orchestration mass**, not pitch-only constructs  
- Enabling legacy/proxy branches **does not silently alter** score-only results  

| Band | Points |
|------|--------|
| Absent | 0 |
| Informal only | 1–4 |
| Partial axioms + some tests | 5–9 |
| Most constructs covered | 10–12 |
| Full formal + systematic verification | 13–15 |

---

## 3. Construct separation (15)

Separate computation, documentation, and interpretation for:

event density · interval compactness · registral density · orchestration mass · timbral/orchestration complexity · temporal vertical density · composite symbolic vertical density

| Band | Points |
|------|--------|
| Absent | 0 |
| Minimal | 1–4 |
| Incomplete | 5–9 |
| Strong | 10–12 |
| Research-grade | 13–15 |

---

## 4. Benchmark and replication (15)

Fixed symbolic inputs · frozen JSON/CSV · checksums/config hashes · reproduce/compare scripts · table generation.

Synthetic fixtures = **scaffold credit only**. Higher scores need representative score excerpts — **not** human ratings.

| Band | Points |
|------|--------|
| Absent | 0 |
| Scaffold only | 1–4 |
| Synthetic frozen outputs | 5–9 |
| Representative excerpts | 10–12 |
| Mature corpus + CI | 13–15 |

---

## 5. Core-native architecture (15)

Auditable path in `core/`:

`score input → vertical slices → score-derived subindices → composite symbolic density → report`

| Band | Points |
|------|--------|
| Absent | 0 |
| Hidden legacy | 1–4 |
| Hybrid documented | 5–9 |
| Mostly core-native | 10–12 |
| Full core-native | 13–15 |

---

## 6. Orchestration metadata honesty (10)

Symbolic metadata — not acoustic measurements or SPL.

| Band | Points |
|------|--------|
| Absent | 0–3 |
| Incomplete | 4–6 |
| Strong | 7–8 |
| Research-grade | 9–10 |

---

## 7. Testing and quality gates (10)

Unit · regression · **property/axiom tests** · frozen-output · no NaN/inf · coverage/CI.

| Band | Points |
|------|--------|
| Absent | 0–3 |
| Incomplete | 4–6 |
| Strong | 7–8 |
| Research-grade | 9–10 |

---

## 8. Reporting transparency (10)

`score_only_mode` · config/input hash · metric schema version · `source_type` · validation status · assumptions · warnings · legacy/proxy state.

| Band | Points |
|------|--------|
| Absent | 0–3 |
| Incomplete | 4–6 |
| Strong | 7–8 |
| Research-grade | 9–10 |

---

## Interpretation bands (total)

| Total | Label |
|-------|--------|
| 0–59 | Prototype / incomplete formalization |
| 60–74 | Functional score-based tool; formalization, benchmark, or architecture gaps |
| 75–84 | Strong systematic score-analysis software |
| 85–89 | Near-publication-grade score-based research infrastructure |
| 90–94 | Publication-grade systematic score-analysis method |
| 95–100 | Reference implementation |

**90+ does not require expert ratings or psychoacoustic validation.**

---

## Optional empirical extensions

Listed for **optional** future work if the research question shifts toward perception or expert-judgment **prediction**:

- Expert score annotations  
- Inter-rater reliability  
- Correlation with human ratings  
- Listening tests  
- Psychoacoustic calibration  

---

## Scoring

Human-assigned dimension scores only:

```bash
python validation/scripts/score_upgrade_rubric.py docs/examples/score_only_rubric_scores_example.json
```

Checklist: [`score_only_90_readiness_checklist.md`](score_only_90_readiness_checklist.md)
