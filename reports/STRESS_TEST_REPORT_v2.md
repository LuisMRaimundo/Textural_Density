# Stress Test Report — Textural Density (v2, post D6 hotfix)

Post-fix archive (monotone pitched ladders; C2 Tam-tam ff + Double bass A1).
Companion pre-fix archive: `STRESS_TEST_REPORT_v1.md`.

## Header

- **Tool version:** 1.1.4
- **Git hash:** `ceb955c`
- **weight_factor (w):** 0.5
- **REF (`MAX_DENS_GLOBAL`):** 193
- **Date:** 2026-08-03 16:03 UTC
- **Battery seed:** 20260803
- **E1 trials:** 200
- **Slices run:** 61
- **Assertions:** 119 passed / 0 failed / 119 total
- **Wall time:** 3.8s
- **CSV:** `stress_results.csv`
- **E5 determinism (repeat CSV hash):** PASS

## A. Pitched-only baselines

| Slice id | Summary | DI (interval) | RSS | Mass | Composite | Events | Players | Distinct |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `A1_violin_C4` | Solo Violin C4 mf | 0.0000 | 27.3404 | 27.3404 | 0.0158 | 1 | 1 | 1 |
| `A1_flute_C4` | Solo Flute C4 mf | 0.0000 | 25.9548 | 25.9548 | 0.0146 | 1 | 1 | 1 |
| `A1_double_bass_C2` | Solo Double bass C2 mf | 0.0000 | 42.8691 | 42.8691 | 0.0305 | 1 | 1 | 1 |
| `A1_piano_C4` | Solo Piano C4 mf | 0.0000 | 8.4640 | 8.4640 | 0.0028 | 1 | 1 | 1 |
| `A2_violin_C4_qty1` | Violin C4 unison Qty=1 | 0.0000 | 27.3404 | 27.3404 | 0.0158 | 1 | 1 | 1 |
| `A2_violin_C4_qty2` | Violin C4 unison Qty=2 | 0.0000 | 38.6652 | 54.6808 | 0.0310 | 1 | 2 | 1 |
| `A2_violin_C4_qty4` | Violin C4 unison Qty=4 | 0.0000 | 54.6808 | 109.3616 | 0.0600 | 1 | 4 | 1 |
| `A2_violin_C4_qty8` | Violin C4 unison Qty=8 | 0.0000 | 77.3303 | 218.7232 | 0.1127 | 1 | 8 | 1 |
| `A2_violin_C4_qty16` | Violin C4 unison Qty=16 | 0.0000 | 109.3616 | 437.4463 | 0.2021 | 1 | 16 | 1 |
| `A3_chord_1` | Violin chord growth n=1 (C4) | 0.0000 | 27.3404 | 27.3404 | 0.0158 | 1 | 1 | 1 |
| `A3_chord_2` | Violin chord growth n=2 (C4+E4) | 0.2228 | 45.1915 | 63.3233 | 0.0405 | 2 | 2 | 2 |
| `A3_chord_3` | Violin chord growth n=3 (C4+E4+G4) | 0.2138 | 53.4719 | 91.9062 | 0.0562 | 3 | 3 | 3 |
| `A3_chord_4` | Violin chord growth n=4 (C4+E4+G4+Bb4) | 0.2025 | 58.0723 | 114.5588 | 0.0669 | 4 | 4 | 4 |
| `A3_chord_5` | Violin chord growth n=5 (C4+E4+G4+Bb4+D5) | 0.1860 | 60.8818 | 132.8401 | 0.0746 | 5 | 5 | 5 |
| `A3_chord_6` | Violin chord growth n=6 (C4+E4+G4+Bb4+D5+F#5) | 0.1705 | 63.2902 | 150.1334 | 0.0815 | 6 | 6 | 6 |
| `A4_close_triad` | Close triad C4 E4 G4 (Piano) | 0.2138 | 14.6601 | 25.3920 | 0.0094 | 3 | 3 | 3 |
| `A4_open_triad` | Open triad C2 E4 G6 (Piano) — same pitch classes, wider span | 0.0187 | 14.6601 | 25.3920 | 0.0083 | 3 | 3 | 3 |
| `A5_pitched_tutti` | 12-pitch pitched tutti ff with realistic Qty | 0.1060 | 418.9111 | 3778.9853 | 0.8858 | 12 | 95 | 10 |

| Assertion | Result | Detail |
|---|---|---|
| `A1_violin_C4_runs` | **PASS** | ok |
| `A1_flute_C4_runs` | **PASS** | ok |
| `A1_double_bass_C2_runs` | **PASS** | ok |
| `A1_piano_C4_runs` | **PASS** | ok |
| `A2_violin_C4_qty1_runs` | **PASS** | ok |
| `A2_violin_C4_qty2_runs` | **PASS** | ok |
| `A2_violin_C4_qty4_runs` | **PASS** | ok |
| `A2_violin_C4_qty8_runs` | **PASS** | ok |
| `A2_violin_C4_qty16_runs` | **PASS** | ok |
| `A3_chord_1_runs` | **PASS** | ok |
| `A3_chord_2_runs` | **PASS** | ok |
| `A3_chord_3_runs` | **PASS** | ok |
| `A3_chord_4_runs` | **PASS** | ok |
| `A3_chord_5_runs` | **PASS** | ok |
| `A3_chord_6_runs` | **PASS** | ok |
| `A4_close_triad_runs` | **PASS** | ok |
| `A4_open_triad_runs` | **PASS** | ok |
| `A5_pitched_tutti_runs` | **PASS** | ok |
| `A2_pitch_invariant_under_qty` | **PASS** | totals=[0.015793681850629765, 0.031033103441821076, 0.0599958149215154, 0.11270053404900258, 0.20209859303292127] |
| `A2_composite_nondecreasing_qty` | **PASS** | totals=[0.015793681850629765, 0.031033103441821076, 0.0599958149215154, 0.11270053404900258, 0.20209859303292127] |
| `A3_composite_strictly_increasing` | **PASS** | totals=[0.015793681850629765, 0.04050651576834099, 0.05618536132175903, 0.06693769664702792, 0.0745758593308562, 0.0814608502542562] |
| `A3_pitch_structure_strictly_increasing` | **PASS** | pitch_structure=[0.0, 1.0572074638794595, 3.5458175337619626, 7.191397693610363, 11.345315039721063, 15.876189931185882] |
| `A4_registral_span_differs` | **PASS** | close_span=7.0 open_span=55.0 |
| `A4_distinct_pitch_count_equal` | **PASS** | close=3 open=3 |

Family A isolates instrument CDM, unison Qty (mass without pitch growth), chordal cardinality, and registral span at fixed pitch-class cardinality. Together these establish the pitched baseline against which mixed and percussion-only regimes are compared.

![A2 doubling curve](stress_figures/A2_doubling_curve.png)

## B. Percussion-only

| Slice id | Summary | DI (interval) | RSS | Mass | Composite | Events | Players | Distinct |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `B1_bass_drum_mf` | Bass drum alone mf | 0.0000 | 12.8893 | 12.8893 | 0.0052 | 1 | 1 | 0 |
| `B1_bass_drum_ff` | Bass drum alone ff | 0.0000 | 22.8883 | 22.8883 | 0.0121 | 1 | 1 | 0 |
| `B1_cymbals_mf` | Cymbals alone mf | 0.0000 | 2.6658 | 2.6658 | 0.0005 | 1 | 1 | 0 |
| `B1_cymbals_ff` | Cymbals alone ff | 0.0000 | 20.7291 | 20.7291 | 0.0105 | 1 | 1 | 0 |
| `B1_tam_tam_mf` | Tam-tam alone mf | 0.0000 | 4.0965 | 4.0965 | 0.0009 | 1 | 1 | 0 |
| `B1_tam_tam_ff` | Tam-tam alone ff | 0.0000 | 12.3240 | 12.3240 | 0.0048 | 1 | 1 | 0 |
| `B1_gong_mf` | Gong alone mf | 0.0000 | 2.1079 | 2.1079 | 0.0003 | 1 | 1 | 0 |
| `B1_gong_ff` | Gong alone ff | 0.0000 | 17.1487 | 17.1487 | 0.0079 | 1 | 1 | 0 |
| `B2_pair_bd_cym` | Bass drum + Cymbals ff | 0.0000 | 30.8799 | 43.6174 | 0.0224 | 2 | 2 | 0 |
| `B2_pair_tt_gong` | Tam-tam + Gong ff | 0.0000 | 21.1177 | 29.4727 | 0.0127 | 2 | 2 | 0 |
| `B2_full_battery` | All four percussion ff | 0.0000 | 37.4103 | 73.0901 | 0.0346 | 4 | 4 | 0 |
| `B3_tamtam_pp` | Tam-tam dynamics ladder pp | 0.0000 | 3.0498 | 3.0498 | 0.0006 | 1 | 1 | 0 |
| `B3_tamtam_mf` | Tam-tam dynamics ladder mf | 0.0000 | 4.0965 | 4.0965 | 0.0009 | 1 | 1 | 0 |
| `B3_tamtam_ff` | Tam-tam dynamics ladder ff | 0.0000 | 12.3240 | 12.3240 | 0.0048 | 1 | 1 | 0 |
| `B3_tamtam_ffff` | Tam-tam dynamics ladder ffff | 0.0000 | 18.6263 | 18.6263 | 0.0090 | 1 | 1 | 0 |

| Assertion | Result | Detail |
|---|---|---|
| `B1_bass_drum_mf_runs` | **PASS** | ok |
| `B1_bass_drum_ff_runs` | **PASS** | ok |
| `B1_cymbals_mf_runs` | **PASS** | ok |
| `B1_cymbals_ff_runs` | **PASS** | ok |
| `B1_tam_tam_mf_runs` | **PASS** | ok |
| `B1_tam_tam_ff_runs` | **PASS** | ok |
| `B1_gong_mf_runs` | **PASS** | ok |
| `B1_gong_ff_runs` | **PASS** | ok |
| `B2_pair_bd_cym_runs` | **PASS** | ok |
| `B2_pair_tt_gong_runs` | **PASS** | ok |
| `B2_full_battery_runs` | **PASS** | ok |
| `B3_tamtam_pp_runs` | **PASS** | ok |
| `B3_tamtam_mf_runs` | **PASS** | ok |
| `B3_tamtam_ff_runs` | **PASS** | ok |
| `B3_tamtam_ffff_runs` | **PASS** | ok |
| `B1_bass_drum_mf_pitch_zero` | **PASS** | dist=0 interval=0.0 ps=0.0 |
| `B1_bass_drum_mf_spectral_na` | **PASS** | spectral block |
| `B1_bass_drum_mf_blend_equals_weighted_orch` | **PASS** | blend=0.6444629000000001 wo=0.6444629000000001 |
| `B1_bass_drum_ff_pitch_zero` | **PASS** | dist=0 interval=0.0 ps=0.0 |
| `B1_bass_drum_ff_spectral_na` | **PASS** | spectral block |
| `B1_bass_drum_ff_blend_equals_weighted_orch` | **PASS** | blend=1.14441655 wo=1.14441655 |
| `B1_cymbals_mf_pitch_zero` | **PASS** | dist=0 interval=0.0 ps=0.0 |
| `B1_cymbals_mf_spectral_na` | **PASS** | spectral block |
| `B1_cymbals_mf_blend_equals_weighted_orch` | **PASS** | blend=0.13329015 wo=0.13329015 |
| `B1_cymbals_ff_pitch_zero` | **PASS** | dist=0 interval=0.0 ps=0.0 |
| `B1_cymbals_ff_spectral_na` | **PASS** | spectral block |
| `B1_cymbals_ff_blend_equals_weighted_orch` | **PASS** | blend=1.03645355 wo=1.03645355 |
| `B1_tam_tam_mf_pitch_zero` | **PASS** | dist=0 interval=0.0 ps=0.0 |
| `B1_tam_tam_mf_spectral_na` | **PASS** | spectral block |
| `B1_tam_tam_mf_blend_equals_weighted_orch` | **PASS** | blend=0.20482730000000002 wo=0.20482730000000002 |
| `B1_tam_tam_ff_pitch_zero` | **PASS** | dist=0 interval=0.0 ps=0.0 |
| `B1_tam_tam_ff_spectral_na` | **PASS** | spectral block |
| `B1_tam_tam_ff_blend_equals_weighted_orch` | **PASS** | blend=0.6162002000000001 wo=0.6162002000000001 |
| `B1_gong_mf_pitch_zero` | **PASS** | dist=0 interval=0.0 ps=0.0 |
| `B1_gong_mf_spectral_na` | **PASS** | spectral block |
| `B1_gong_mf_blend_equals_weighted_orch` | **PASS** | blend=0.105397 wo=0.105397 |
| `B1_gong_ff_pitch_zero` | **PASS** | dist=0 interval=0.0 ps=0.0 |
| `B1_gong_ff_spectral_na` | **PASS** | spectral block |
| `B1_gong_ff_blend_equals_weighted_orch` | **PASS** | blend=0.85743395 wo=0.85743395 |
| `B1_ff_composite_order_matches_CDM` | **PASS** | CDM=['B1_tam_tam_ff', 'B1_gong_ff', 'B1_cymbals_ff', 'B1_bass_drum_ff'] composite=['B1_tam_tam_ff', 'B1_gong_ff', 'B1_cymbals_ff', 'B1_bass_drum_ff'] |
| `B2_monotone_growth` | **PASS** | totals=[0.012148696608843854, 0.022360172924569478, 0.03457138176966582] |
| `B3_dynamics_nondecreasing` | **PASS** | pp→mf→ff→ffff totals=[0.0005988279121509948, 0.0009318751690567455, 0.004840633341214936, 0.008951670912361253] |
| `B3_mf_to_ff_jump_recorded` | **PASS** | mf→ff Δcomposite=0.00390876 (documented cascade discontinuity flag) |

Family B verifies unpitched-only routing: pitch metrics stay at zero, spectral blocks report n/a, and the blend collapses to the weighted orchestral term (DV = 0) while composite follows the unified log path. The tam-tam dynamics ladder records the mf→ff cascade discontinuity.

![B3 dynamics ladder](stress_figures/B3_dynamics_ladder.png)

## C. Mixed aggregates

| Slice id | Summary | DI (interval) | RSS | Mass | Composite | Events | Players | Distinct |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `C1_quartet_alone` | String quartet alone ff | 0.1543 | 73.5767 | 138.8077 | 0.0897 | 4 | 4 | 4 |
| `C1_quartet_plus_bass_drum` | Quartet + Bass drum ff | 0.1543 | 77.0546 | 161.6961 | 0.1000 | 5 | 5 | 4 |
| `C1_quartet_plus_cymbals` | Quartet + Cymbals ff | 0.1543 | 76.4410 | 159.5368 | 0.0987 | 5 | 5 | 4 |
| `C1_quartet_plus_tam_tam` | Quartet + Tam-tam ff | 0.1543 | 74.6017 | 151.1318 | 0.0943 | 5 | 5 | 4 |
| `C1_quartet_plus_gong` | Quartet + Gong ff | 0.1543 | 75.5487 | 155.9564 | 0.0967 | 5 | 5 | 4 |
| `C2_quartet_plus_tamtam_ff` | Compression probe: quartet + Tam-tam ff | 0.1543 | 74.6017 | 151.1318 | 0.0943 | 5 | 5 | 4 |
| `C2_quintet_fifth_string` | Compression probe: quintet (add Double bass A1, in-range) instead of percussion | 0.1116 | 94.8134 | 198.6078 | 0.1304 | 5 | 5 | 5 |
| `C3_perc_share_0_of_8` | 8-player mix; unpitched events=0, pitched Qty=8 | 0.0000 | 78.6174 | 222.3637 | 0.1152 | 1 | 8 | 1 |
| `C3_perc_share_1_of_8` | 8-player mix; unpitched events=1, pitched Qty=7 | 0.0000 | 77.0194 | 217.4566 | 0.1120 | 2 | 8 | 1 |
| `C3_perc_share_2_of_8` | 8-player mix; unpitched events=2, pitched Qty=6 | 0.0000 | 74.7603 | 210.3902 | 0.1075 | 3 | 8 | 1 |
| `C3_perc_share_3_of_8` | 8-player mix; unpitched events=3, pitched Qty=5 | 0.0000 | 70.4868 | 194.9187 | 0.0986 | 4 | 8 | 1 |
| `C3_perc_share_4_of_8` | 8-player mix; unpitched events=4, pitched Qty=4 | 0.0000 | 67.0066 | 184.2719 | 0.0919 | 5 | 8 | 1 |
| `C4_perm_0` | Order-invariance perm 0 | 0.1934 | 58.9358 | 128.4628 | 0.0714 | 5 | 5 | 3 |
| `C4_perm_1` | Order-invariance perm 1 | 0.1934 | 58.9358 | 128.4628 | 0.0714 | 5 | 5 | 3 |
| `C4_perm_2` | Order-invariance perm 2 | 0.1934 | 58.9358 | 128.4628 | 0.0714 | 5 | 5 | 3 |
| `C4_perm_3` | Order-invariance perm 3 | 0.1934 | 58.9358 | 128.4628 | 0.0714 | 5 | 5 | 3 |
| `C4_perm_4` | Order-invariance perm 4 | 0.1934 | 58.9358 | 128.4628 | 0.0714 | 5 | 5 | 3 |
| `C4_perm_5` | Order-invariance perm 5 | 0.1934 | 58.9358 | 128.4628 | 0.0714 | 5 | 5 | 3 |
| `C5_tutti_no_perc` | A5 pitched tutti without percussion | 0.1060 | 418.9111 | 3778.9853 | 0.8858 | 12 | 95 | 10 |
| `C5_tutti_with_perc` | A5 pitched tutti + full percussion battery ff | 0.1060 | 420.5782 | 3852.0754 | 0.8910 | 16 | 99 | 10 |

| Assertion | Result | Detail |
|---|---|---|
| `C1_quartet_alone_runs` | **PASS** | ok |
| `C1_quartet_plus_bass_drum_runs` | **PASS** | ok |
| `C1_quartet_plus_cymbals_runs` | **PASS** | ok |
| `C1_quartet_plus_tam_tam_runs` | **PASS** | ok |
| `C1_quartet_plus_gong_runs` | **PASS** | ok |
| `C2_quartet_plus_tamtam_ff_runs` | **PASS** | ok |
| `C2_quintet_fifth_string_runs` | **PASS** | ok |
| `C3_perc_share_0_of_8_runs` | **PASS** | ok |
| `C3_perc_share_1_of_8_runs` | **PASS** | ok |
| `C3_perc_share_2_of_8_runs` | **PASS** | ok |
| `C3_perc_share_3_of_8_runs` | **PASS** | ok |
| `C3_perc_share_4_of_8_runs` | **PASS** | ok |
| `C4_perm_0_runs` | **PASS** | ok |
| `C4_perm_1_runs` | **PASS** | ok |
| `C4_perm_2_runs` | **PASS** | ok |
| `C4_perm_3_runs` | **PASS** | ok |
| `C4_perm_4_runs` | **PASS** | ok |
| `C4_perm_5_runs` | **PASS** | ok |
| `C5_tutti_no_perc_runs` | **PASS** | ok |
| `C5_tutti_with_perc_runs` | **PASS** | ok |
| `C1_quartet_plus_bass_drum_raises_composite` | **PASS** | base=0.0896526 mixed=0.0999998 |
| `C1_quartet_plus_cymbals_raises_composite` | **PASS** | base=0.0896526 mixed=0.0987069 |
| `C1_quartet_plus_tam_tam_raises_composite` | **PASS** | base=0.0896526 mixed=0.0943005 |
| `C1_quartet_plus_gong_raises_composite` | **PASS** | base=0.0896526 mixed=0.0967071 |
| `C1_increment_rank_matches_CDM_rank` | **PASS** | Δcomposite_rank=['Tam-tam', 'Gong', 'Cymbals', 'Bass drum'] ΔCDM_rank=['Tam-tam', 'Gong', 'Cymbals', 'Bass drum'] |
| `C2_compression_probe_documented` | **PASS** | quartet+tam-tam_ff=0.0943005; quintet=0.13041; diff=-0.0361093 |
| `C3_perc_share_0_of_8_player_count_8` | **PASS** | player_count=8 |
| `C3_perc_share_1_of_8_player_count_8` | **PASS** | player_count=8 |
| `C3_perc_share_2_of_8_player_count_8` | **PASS** | player_count=8 |
| `C3_perc_share_3_of_8_player_count_8` | **PASS** | player_count=8 |
| `C3_perc_share_4_of_8_player_count_8` | **PASS** | player_count=8 |
| `C4_permutation_invariance` | **PASS** | order-invariant numeric match |
| `C5_tutti_with_perc_raises_composite` | **PASS** | no_perc=0.885834 with_perc=0.890954 |

Family C is analytically central: percussion additions to a pitched core, the mass-vs-component-count compression probe (C2), a fixed-player unpitched-share sweep, permutation invariance, and a realistic tutti comparison with/without the percussion battery.

### C2 — Compression probe (prominent)

Quartet + Tam-tam ff composite = **0.094300**; quintet (fifth string A1 instead) composite = **0.130410**; difference (tam-tam − quintet) = **-0.036109**.

Under **mass semantics** these two aggregates may be near-equal (or the percussion side even larger) because a loud unpitched stroke contributes substantial CDM/mass. Under **component-count semantics** the tam-tam side is 'fatter' by one non-pitched event without adding pitch structure. The battery documents the size of this seam rather than judging which reading is correct.

![C3 percussion fraction sweep](stress_figures/C3_perc_fraction_sweep.png)

![C5 tutti comparison](stress_figures/C5_tutti_comparison.png)

## D. Degenerate and adversarial

| Slice id | Summary | DI (interval) | RSS | Mass | Composite | Events | Players | Distinct |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `D1_empty` | Empty slice (no rows) | — | — | — | — | error | — | — |
| `D2_min_unpitched_pp` | Single Tam-tam pp Qty=1 | 0.0000 | 3.0498 | 3.0498 | 0.0006 | 1 | 1 | 0 |
| `D3_violin_qty500` | Violin C4 Qty=500 | 0.0000 | 611.3498 | 13670.1969 | 1.2904 | 1 | 500 | 1 |
| `D4_microtonal_24` | 24 distinct pitches with cent offsets (Violin) | 0.1753 | 114.3350 | 536.9113 | 0.2296 | 24 | 24 | 24 |
| `D5_violin_flute_unison` | Violin C4 + Flute C4 (same pitch, two instruments) | 0.0000 | 37.6981 | 53.2952 | 0.0299 | 2 | 2 | 1 |
| `D6_all_pp` | Quartet all pp | 0.1543 | 68.9704 | 130.5886 | 0.0823 | 4 | 4 | 4 |
| `D6_all_ffff` | Quartet all ffff | 0.1543 | 73.6421 | 138.9803 | 0.0898 | 4 | 4 | 4 |
| `D7_tamtam_qty50` | Tam-tam ffff Qty=50 (musically unreal) | 0.0000 | 131.7080 | 931.3161 | 0.3099 | 1 | 50 | 0 |

| Assertion | Result | Detail |
|---|---|---|
| `D1_empty_graceful_error` | **PASS** | Notes are required. |
| `D2_min_unpitched_pp_runs` | **PASS** | ok |
| `D3_violin_qty500_runs` | **PASS** | ok |
| `D4_microtonal_24_runs` | **PASS** | ok |
| `D5_violin_flute_unison_runs` | **PASS** | ok |
| `D6_all_pp_runs` | **PASS** | ok |
| `D6_all_ffff_runs` | **PASS** | ok |
| `D7_tamtam_qty50_runs` | **PASS** | ok |
| `D2_minimum_nonzero` | **PASS** | total=0.0005988279121509948 |
| `D3_no_nan_overflow` | **PASS** | total=1.2904313011529658 mass=13670.19695 |
| `D4_distinct_count_24` | **PASS** | distinct_pitch_count=24 |
| `D5_unison_two_instruments` | **PASS** | distinct=1 events=2 |
| `D6_ffff_gt_pp` | **PASS** | pp=0.0823388 ffff=0.0897735 ratio=1.09 |
| `D7_absurd_qty_finite` | **PASS** | total=0.30990553785279035 (musically unreal; numerically sane) |

Family D stresses empty input, minimum nonzero unpitched, extreme Qty, microtonal cardinality, cross-instrument unison, dynamic extremes, and musically unreal percussion Qty — confirming graceful failure or numerical sanity rather than musical plausibility.

## E. Invariance and consistency properties

| Assertion | Result | Detail |
|---|---|---|
| `E1_monotonicity_random_additions` | **PASS** | trials=200 failures=0 seed=20260803 |
| `E2_pitch_metrics_invariant_deleting_unpitched` | **PASS** | slices=20 failures=0 |
| `E3_qty_scale_pitch_invariant_mass_linear` | **PASS** | failures=0 |
| `E5_determinism_csv_hash` | **PASS** | hash1=ad30f3dc0f31 hash2=ad30f3dc0f31 |
| `E4_header_formula_self_check_all_slices` | **PASS** | slices=60 failures=0 |

Family E encodes standing contracts as assertions: random-addition monotonicity, pitch-metric invariance when unpitched events are removed, Qty scaling (pitch fixed, mass linear), printed-header formula self-check, and whole-battery determinism via CSV hash.

## FINDINGS

No findings: all 119 assertions passed.

### Documented caveats (not failures)

- `B3_mf_to_ff_jump_recorded`: mf→ff Δcomposite=0.00390876 (documented cascade discontinuity flag)
- `C2_compression_probe_documented`: quartet+tam-tam_ff=0.0943005; quintet=0.13041; diff=-0.0361093
- `D7_absurd_qty_finite`: total=0.30990553785279035 (musically unreal; numerically sane)

## SCOPE NOTES

The battery deliberately does **not** adjudicate the following standing caveats (restated for methods-chapter readers):

- (i) Mass-vs-component-count semantics of percussion aggregation: composite may treat a loud unpitched addition as comparable in mass terms to adding another pitched voice; C2 documents the size of this seam rather than adjudicating which semantics is 'correct'.
- (ii) Cross-family ratio validity pending calibration: absolute ratios of composites across pitched-only, unpitched-only, and mixed regimes are reported for inspection but are not treated as calibrated perceptual equivalences.
- (iii) Per-player means may legitimately move opposite to totals: `average_texture_density` is a Qty-weighted mean CDM and may fall when low-CDM instruments are added or rise under Qty expansion toward high-CDM instruments; monotone quantities are Sonic Mass, RSS, and Composite.

## Reproduction

```bash
python run_stress_battery.py
```

Optional: `python run_stress_battery.py --e1-trials 50 --seed 42` (adjusts E1 trial count / RNG seed). Regenerates `STRESS_TEST_REPORT.md`, `stress_results.csv`, and `stress_figures/`.
