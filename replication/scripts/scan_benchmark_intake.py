#!/usr/bin/env python3
"""Scan benchmark intake folders and report candidate files for manifest registration."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

INTAKE_DIRS = [
    ROOT / "replication" / "corpus" / "intake",
    ROOT / "replication" / "corpus" / "musicxml",
    ROOT / "replication" / "corpus" / "mxl",
    ROOT / "replication" / "corpus" / "xml",
    ROOT / "replication" / "corpus" / "midi",
]

EXTENSIONS = {
    ".musicxml": "musicxml",
    ".mxl": "mxl",
    ".xml": "xml",
    ".mid": "midi",
    ".midi": "midi",
    ".json": "json_input",
}

OFFICIAL_LICENSES = frozenset(
    {
        "owned_by_project_author",
        "public_domain_verified",
        "openly_licensed",
    }
)


def _scan_files() -> list[dict[str, str]]:
    found: list[dict[str, str]] = []
    for directory in INTAKE_DIRS:
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob("*")):
            if not path.is_file() or path.name.startswith("."):
                continue
            ext = path.suffix.lower()
            if ext not in EXTENSIONS:
                continue
            rel = path.relative_to(ROOT).as_posix()
            found.append(
                {
                    "file_path": rel,
                    "format": EXTENSIONS[ext],
                    "corpus_status": "pending_license_review",
                    "license_status": "missing",
                    "license_note": "Complete license metadata before setting include_in_official_benchmark.",
                    "include_in_official_benchmark": "false",
                }
            )
    return found


def main() -> int:
    manifest_path = ROOT / "replication" / "benchmark_manifest.json"
    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)

    registered = {e["file_path"] for e in manifest.get("entries", [])}
    candidates = _scan_files()
    new_files = [c for c in candidates if c["file_path"] not in registered]

    print(f"Manifest version: {manifest.get('manifest_version')}")
    print(f"Corpus maturity: {manifest.get('corpus_maturity')}")
    print(f"Registered entries: {len(manifest.get('entries', []))}")
    official = [
        e
        for e in manifest.get("entries", [])
        if e.get("include_in_official_benchmark")
        and e.get("license_status") in OFFICIAL_LICENSES
    ]
    print(f"Official representative benchmarks: {len(official)}")

    if not candidates:
        print("\nNo score files in intake folders.")
        print("Add files to replication/corpus/intake/ and re-run.")
        return 0

    print(f"\nIntake scan found {len(candidates)} file(s):")
    for c in candidates:
        flag = "NEW" if c["file_path"] in {n["file_path"] for n in new_files} else "registered"
        print(f"  [{flag}] {c['file_path']} ({c['format']})")

    if new_files:
        print("\nAdd manifest entries manually with composer, work_title, license_note.")
        print("Only owned_by_project_author, public_domain_verified, or openly_licensed")
        print("may set include_in_official_benchmark: true.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
