# NonTunPerc percussion metrical extracts

Committed copies of Percussion Tool / NonTunPerc **Analysis** exports used to
build Textural Density percussion GPR/log-CDM modules (`bass_drum`, `cymbals`,
`tamtam`, `gong`).

| File | Role |
|------|------|
| `Analysis/density_profiles_mc.csv` | **Primary citation** — MC p50/p05/p95 band weights → phase `composite_index` |
| `Analysis/density_profiles_mc.meta.json` | MC seed, draw counts, amplitude-layer flags |
| `Analysis/density_profiles.csv` | Deterministic export (deprecated for citation; kept for comparison) |
| `Analysis/size_sweep_mc.csv` | Cymbal diameter MC summary (uncertainty context) |
| `Analysis/calibration_report.md` | Scale-bridge status (**NO CALIBRATION ACHIEVED**) |

**Upstream path:** `C:\Users\lmr20\Desktop\Percussion Tool\Analysis\`  
**NonTunPerc:** v0.3.5 / commit `4a110dbbaab3af831c0987e99a4b7019b008bbd6`

**Phase policy:** bass drum → strike; cymbals / tam-tam / gong → shimmer.

**Regenerate modules:**

```bash
python tools/generate_percussion_modules_from_nontunperc.py
```

Requires the Percussion Tool checkout for pp/mf excitation shape; ff is always
taken from the committed MC CSV p50.
