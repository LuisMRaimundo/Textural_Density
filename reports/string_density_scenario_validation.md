# String density scenario validation report

**Date (UTC):** 2026-06-25 09:33:24
**Repository SHA:** `3e083ceb273edd827e8def29eae27a52348f3c86`

## Scope

- Strings only: violin, viola, cello, double bass
- Sounding/concert pitch only (double bass uses sounding notes, e.g. E1 not written octave)
- Score-grounded symbolic density model
- **Not** perceptual validation

## API

`core.pipeline.calculate_metrics` with legacy dict input (`notes`, `dynamics`, `instruments`, `num_instruments`, `weight_factor`).

## Summary

| Metric | Value |
|--------|-------|
| repository_sha | 3e083ceb273edd827e8def29eae27a52348f3c86 |
| seed | 20260625 |
| scenarios_generated | 347 |
| scenarios_executed | 347 |
| positive_scenarios | 327 |
| negative_scenarios | 20 |
| scenarios_passed | 347 |
| scenarios_failed | 0 |
| invariant_checks | 34 |
| invariant_failures | 0 |
| warnings_count | 280 |
| instruments_covered | ['violin', 'viola', 'cello', 'double_bass'] |
| dynamics_covered | ['pp', 'p', 'mp', 'mf', 'f', 'ff'] |
| register_bands_covered | ['low', 'low_mid', 'middle', 'upper_mid', 'high', 'near_lower_boundary', 'near_upper_boundary'] |
| aggregate_types_covered | ['cluster_plus_octave', 'compact_chromatic_cluster', 'compact_dyad', 'compact_trichord', 'cross_dynamic_comparison', 'diatonic_aggregate', 'event_order_invariance', 'exact_unison', 'heterogeneous_string', 'high_register_mass', 'instrument_substitution', 'low_register_mass', 'mixed_dynamics', 'negative_out_of_range', 'octave_doubling', 'quantity_scaling', 'quartet_voicing', 'register_shift_comparison', 'registrally_stratified', 'same_instrument_unison_qty', 'sectional_string', 'single_note', 'sparse_aggregate', 'very_dense_chromatic', 'very_sparse_aggregate'] |
| campaign_conclusion | PASS |

## Instrument ranges (registry sounding_range)

- **violin:** MIDI 55–103
- **viola:** MIDI 48–96
- **cello:** MIDI 36–84
- **double_bass:** MIDI 28–72

## Dynamics

pp, p, mp, mf, f, ff
 (source anchors: ff, mf, pp)

## Aggregate types

single_note, exact_unison, same_instrument_unison_qty, octave_doubling, compact_dyad, compact_trichord, compact_chromatic_cluster, very_dense_chromatic, diatonic_aggregate, sparse_aggregate, very_sparse_aggregate, registrally_stratified, homogeneous_instrument, heterogeneous_string, sectional_string, quartet_voicing, cluster_plus_octave, low_register_mass, high_register_mass, mixed_dynamics, cross_dynamic_comparison, instrument_substitution, quantity_scaling, event_order_invariance, pitch_collection_invariance, register_shift_comparison, boundary_safe, negative_out_of_range

## Positive scenario summary

- Total: 327
- Passed: 327
- Failed: 0

## Negative scenario summary

- Total: 20
- Passed (clean failure): 20
- Failed: 0

## Density statistics (instrument density, positive scenarios)

- min: 3.062043
- max: 190.019095
- mean: 37.357104
- median: 30.868050
- stdev: 26.786091

## Invariant checks

- **event_order_invariance** (event_order_trio): PASS — pitch_structure and interval matched
- **quantity_row_splitting** (qty_split_STRINGS_QTY_SPLIT_MID_FF_VLN_0191): PASS — sonic_mass matched
- **quantity_row_splitting** (qty_split_STRINGS_QTY_SPLIT_MID_MF_VLN_0189): PASS — sonic_mass matched
- **quantity_row_splitting** (qty_split_STRINGS_QTY_SPLIT_MID_PP_VLN_0187): PASS — sonic_mass matched
- **unison_distinct_pitch** (STRINGS_UNISON_MID_P_N3_0173): PASS — distinct_pitch_count=1
- **unison_distinct_pitch** (STRINGS_UNISON_MID_F_N3_0182): PASS — distinct_pitch_count=1
- **unison_distinct_pitch** (STRINGS_UNISON_MID_F_N4_0183): PASS — distinct_pitch_count=1
- **unison_distinct_pitch** (STRINGS_UNISON_MID_MP_N2_0175): PASS — distinct_pitch_count=1
- **unison_distinct_pitch** (STRINGS_UNISON_MID_FF_N2_0184): PASS — distinct_pitch_count=1
- **unison_distinct_pitch** (STRINGS_UNISON_MID_P_N4_0174): PASS — distinct_pitch_count=1
- **unison_distinct_pitch** (STRINGS_UNISON_MID_MP_N3_0176): PASS — distinct_pitch_count=1
- **unison_distinct_pitch** (STRINGS_UNISON_MID_FF_N3_0185): PASS — distinct_pitch_count=1
- **unison_distinct_pitch** (STRINGS_UNISON_MID_P_N2_0172): PASS — distinct_pitch_count=1
- **unison_distinct_pitch** (STRINGS_UNISON_MID_PP_N3_0170): PASS — distinct_pitch_count=1
- **unison_distinct_pitch** (STRINGS_UNISON_MID_F_N2_0181): PASS — distinct_pitch_count=1
- **unison_distinct_pitch** (STRINGS_UNISON_MID_MF_N3_0179): PASS — distinct_pitch_count=1
- **unison_distinct_pitch** (STRINGS_UNISON_MID_FF_N4_0186): PASS — distinct_pitch_count=1
- **unison_distinct_pitch** (STRINGS_UNISON_MID_PP_N4_0171): PASS — distinct_pitch_count=1
- **unison_distinct_pitch** (STRINGS_UNISON_MID_PP_N2_0169): PASS — distinct_pitch_count=1
- **unison_distinct_pitch** (STRINGS_UNISON_MID_MF_N4_0180): PASS — distinct_pitch_count=1
- **unison_distinct_pitch** (STRINGS_UNISON_MID_MF_N2_0178): PASS — distinct_pitch_count=1
- **unison_distinct_pitch** (STRINGS_UNISON_MID_MP_N4_0177): PASS — distinct_pitch_count=1
- **octave_distinct_pitch** (STRINGS_OCTAVE_LOWMID_MP_VIOLA_0196): PASS — distinct_pitch_count=2
- **octave_distinct_pitch** (STRINGS_OCTAVE_LOWMID_F_CELLO_0201): PASS — distinct_pitch_count=2
- **octave_distinct_pitch** (STRINGS_OCTAVE_LOWMID_MF_DOUBLE_BASS_0203): PASS — distinct_pitch_count=2
- **octave_distinct_pitch** (STRINGS_OCTAVE_LOWMID_MF_CELLO_0200): PASS — distinct_pitch_count=2
- **octave_distinct_pitch** (STRINGS_OCTAVE_LOWMID_MP_VIOLIN_0193): PASS — distinct_pitch_count=2
- **octave_distinct_pitch** (STRINGS_OCTAVE_LOWMID_F_DOUBLE_BASS_0204): PASS — distinct_pitch_count=2
- **octave_distinct_pitch** (STRINGS_OCTAVE_LOWMID_MF_VIOLA_0197): PASS — distinct_pitch_count=2
- **octave_distinct_pitch** (STRINGS_OCTAVE_LOWMID_MF_VIOLIN_0194): PASS — distinct_pitch_count=2
- **octave_distinct_pitch** (STRINGS_OCTAVE_LOWMID_MP_DOUBLE_BASS_0202): PASS — distinct_pitch_count=2
- **octave_distinct_pitch** (STRINGS_OCTAVE_LOWMID_F_VIOLIN_0195): PASS — distinct_pitch_count=2
- **octave_distinct_pitch** (STRINGS_OCTAVE_LOWMID_MP_CELLO_0199): PASS — distinct_pitch_count=2
- **octave_distinct_pitch** (STRINGS_OCTAVE_LOWMID_F_VIOLA_0198): PASS — distinct_pitch_count=2

## Anomalies

- `STRINGS_SINGLE_MIDDLE_MP_DOUBLE_BASS_0141`: PASS status=success warnings=2
- `STRINGS_SINGLE_NEAR_UPPER_BOUNDARY_MP_VIOLIN_0039`: PASS status=success warnings=2
- `STRINGS_SINGLE_LOW_MID_MP_DOUBLE_BASS_0135`: PASS status=success warnings=2
- `STRINGS_SINGLE_MIDDLE_FF_VIOLIN_0018`: PASS status=success warnings=1
- `STRINGS_SINGLE_HIGH_FF_VIOLIN_0030`: PASS status=success warnings=1
- `STRINGS_SINGLE_MIDDLE_F_VIOLA_0059`: PASS status=success warnings=1
- `STRINGS_CLUSTER_MID_MP_VIOLA_0231`: PASS status=success warnings=5
- `STRINGS_SINGLE_MIDDLE_P_VIOLA_0056`: PASS status=success warnings=1
- `STRINGS_PAIR_MID_MP_VIO_DOU_0312`: PASS status=success warnings=2
- `STRINGS_SINGLE_LOW_F_DOUBLE_BASS_0131`: PASS status=success warnings=1
- `STRINGS_SINGLE_NEAR_UPPER_BOUNDARY_P_CELLO_0122`: PASS status=success warnings=1
- `STRINGS_TRICHORD_MID_MP_VIOLIN_0212`: PASS status=success warnings=3
- `STRINGS_ALIAS_MID_MF_VIOLIN_0324`: PASS status=success warnings=1
- `STRINGS_OCTAVE_LOWMID_MP_VIOLA_0196`: PASS status=success warnings=2
- `STRINGS_SINGLE_NEAR_LOWER_BOUNDARY_MF_VIOLA_0076`: PASS status=success warnings=1
- `STRINGS_QTYSCALE_MID_MF_Q4_0300`: PASS status=success warnings=1
- `STRINGS_TRICHORD_MID_MP_VIOLA_0230`: PASS status=success warnings=3
- `STRINGS_SINGLE_NEAR_UPPER_BOUNDARY_MF_CELLO_0124`: PASS status=success warnings=1
- `STRINGS_SINGLE_NEAR_UPPER_BOUNDARY_MP_VIOLA_0081`: PASS status=success warnings=2
- `STRINGS_ALIAS_MID_MF_CELLO_0326`: PASS status=success warnings=1
- `STRINGS_SINGLE_MIDDLE_MF_VIOLA_0058`: PASS status=success warnings=1
- `STRINGS_SINGLE_LOW_MP_VIOLA_0045`: PASS status=success warnings=2
- `STRINGS_SINGLE_LOW_MP_DOUBLE_BASS_0129`: PASS status=success warnings=2
- `STRINGS_SINGLE_UPPER_MID_P_DOUBLE_BASS_0146`: PASS status=success warnings=1
- `STRINGS_SINGLE_NEAR_LOWER_BOUNDARY_F_VIOLIN_0035`: PASS status=success warnings=1
- `STRINGS_SINGLE_NEAR_LOWER_BOUNDARY_PP_CELLO_0115`: PASS status=success warnings=1
- `STRINGS_SINGLE_LOW_MID_P_VIOLA_0050`: PASS status=success warnings=1
- `STRINGS_SINGLE_UPPER_MID_F_VIOLIN_0023`: PASS status=success warnings=1
- `STRINGS_SINGLE_NEAR_LOWER_BOUNDARY_F_DOUBLE_BASS_0161`: PASS status=success warnings=1
- `STRINGS_SINGLE_LOW_MID_MF_DOUBLE_BASS_0136`: PASS status=success warnings=1

## Interpretation

Results demonstrate internal consistency of the string density pipeline under controlled
symbolic scenarios. They do not validate perceptual density or empirical listening outcomes.

## Files

- `reports/string_density_scenario_validation.json`
- `reports/string_density_scenario_validation.csv`
- `reports/string_density_scenario_validation_summary.json`

## Conclusion: **PASS**
