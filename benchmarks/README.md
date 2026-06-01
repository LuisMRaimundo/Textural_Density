# Licensed benchmark corpus (project-authored excerpts)

Three representative MusicXML excerpts for replication. **Owned by project author**
— safe for CI and frozen-output comparison.

| ID | File | Description |
|----|------|-------------|
| excerpt_001 | `corpus/excerpt_001.musicxml` | C major triad, single flute |
| excerpt_002 | `corpus/excerpt_002.musicxml` | Four-note vertical, flute + clarinet |
| excerpt_003 | `corpus/excerpt_003.musicxml` | Bb clarinet `<transpose>` concert-pitch regression |

```bash
python benchmarks/scripts/run_benchmarks.py
python benchmarks/scripts/freeze_outputs.py
```

After orchestration or Qty-scaling changes, re-freeze and verify Qty semantics
(`docs/qa_checklist.md`).

See `corpus/manifest.yml` for metadata and license fields.
