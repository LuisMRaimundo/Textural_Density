# GPR determinism audit

- Repository SHA: `05299aafaae8d57ed4db0db033db75a17bb0de44`
- Classification: **PASS**
- `GPR_RANDOM_STATE`: `0`
- Instruments tested: 7
- Dynamic predictions tested: 1470
- Max repeated-call variation (violin G4 mp): 0.0
- Max global-seed variation (mp): 0.0
- Order permutation exact match: True
- Global RNG preserved: True
- Benchmark order max variation: 0.0
- Frozen output changes: False

## Inventory

- `instrumentos\gpr_dynamic_interpolation.py` `create_dynamic_gpr` random_state=0 class=production
- `instrumentos/violin.py` `predict_intermediate_dynamics` random_state=0 class=production
- `instrumentos/viola.py` `predict_intermediate_dynamics` random_state=0 class=production
- `instrumentos/cello.py` `predict_intermediate_dynamics` random_state=0 class=production
- `instrumentos/double_bass.py` `predict_intermediate_dynamics` random_state=0 class=production
- `instrumentos/flute.py` `predict_intermediate_dynamics` random_state=0 class=production
- `instrumentos/clarinet.py` `predict_intermediate_dynamics` random_state=0 class=production
- `instrumentos/oboe.py` `predict_intermediate_dynamics` random_state=0 class=production
- `tools/audit_mp_dynamic_interpolation.py` `_gpr_std_at_mp` random_state=0 class=tool

## Frozen output differences


## Notes

- Determinism means repeatability of the numerical procedure.
- Determinism does not establish acoustic or perceptual validity.
- Production GPR owns `random_state`; global `np.random.seed` is not required.
