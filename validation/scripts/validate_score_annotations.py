#!/usr/bin/env python3
"""Validate score annotation JSON files against the score-only schema."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from validation.score_schemas import validate_annotation_file


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate score annotation files.")
    parser.add_argument("paths", nargs="+", help="Annotation JSON file(s)")
    args = parser.parse_args()
    exit_code = 0
    for p in args.paths:
        annotations, errors = validate_annotation_file(p)
        if errors:
            print(f"FAIL {p}: {errors[0]}")
            exit_code = 1
        else:
            n_fixture = sum(1 for a in annotations if a.is_fixture)
            print(f"OK {p}: {len(annotations)} annotation(s), {n_fixture} fixture(s)")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
