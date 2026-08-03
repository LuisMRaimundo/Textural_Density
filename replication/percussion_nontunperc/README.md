# NonTunPerc percussion metrical extracts

Committed copies of Percussion Tool / NonTunPerc **Analysis** exports used to
build Textural Density percussion GPR modules (`bass_drum`, `cymbals`,
`tamtam`, `gong`).

| File | Role |
|------|------|
| `Analysis/density_profiles.csv` | Per-ERB-band energy weights; strike-phase `composite_index` → **ff** CDM proxy |
| `Analysis/size_sweep_mc.csv` | Cymbal diameter Monte Carlo summary (documentation / uncertainty context) |
| `Analysis/calibration_report.md` | Scale-bridge status vs pitched fixtures (not yet a conversion factor) |

**Upstream path (authoritative regenerate):**  
`C:\Users\lmr20\Desktop\Percussion Tool\Analysis\`

**Regenerate instrument modules:**

```bash
python tools/generate_percussion_modules_from_nontunperc.py
```

Requires the Percussion Tool checkout on this machine for pp/mf excitation
shape; ff is always taken from the committed Analysis CSV.
