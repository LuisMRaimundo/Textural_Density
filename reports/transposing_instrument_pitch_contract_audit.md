# Transposing instrument pitch contract audit

- Instruments audited: 28
- Transposing watchlist: 8
- Failures: 0
- Review required: 3

## Pitch contract

- **manual_legacy_input:** notes[] are sounding/concert pitch; registry transposition is not applied
- **musicxml:** written <pitch> converted via <transpose> once before validation and lookup
- **density_lookup:** sounding_pitch (concert pitch after MusicXML transpose when applicable)
- **range_validation:** sounding/concert pitch vs registry.sounding_range
- **registry_transposition_field:** metadata_only_not_applied_at_runtime
- **spectral_data_tables:** sounding/concert pitch keys only

## REVIEW REQUIRED

- contrabaixo: transposition metadata is 0 (octave notation only)
- contrafagote: transposition metadata is 0 (octave notation only)
- flautim: transposition metadata is 0 (octave notation only)
