# Licensed benchmark corpus (project-authored excerpts)

Five representative MusicXML excerpts for replication. **Owned by project author**
— safe for CI and frozen-output comparison.

| ID | File | Description |
|----|------|-------------|
| excerpt_001 | `corpus/excerpt_001.musicxml` | C major triad, single flute |
| excerpt_002 | `corpus/excerpt_002.musicxml` | Four-note vertical, flute + clarinet |
| excerpt_003 | `corpus/excerpt_003.musicxml` | Bb clarinet `<transpose>` with flute (single measure) |
| excerpt_004 | `corpus/excerpt_004.musicxml` | Bb clarinet transpose **persists into measure 2** |
| excerpt_005 | `corpus/excerpt_005.musicxml` | Flute + oboe + violin with pp/mf/ff dynamics |

```bash
python benchmarks/scripts/run_benchmarks.py
python benchmarks/scripts/freeze_outputs.py
```

After orchestration or Qty-scaling changes, re-freeze and verify Qty semantics
(`docs/qa_checklist.md`).

See `corpus/manifest.yml` for metadata and license fields.
