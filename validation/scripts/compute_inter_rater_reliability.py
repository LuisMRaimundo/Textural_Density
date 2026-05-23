#!/usr/bin/env python3
"""Compute inter-rater reliability for score annotations (when multi-rater data exist)."""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from validation.metrics import krippendorff_alpha_placeholder
from validation.score_schemas import load_score_annotations


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("annotation_file", help="Path to annotation JSON list")
    args = parser.parse_args()

    annotations = load_score_annotations(args.annotation_file)
    real = [a for a in annotations if not a.is_fixture]
    if not real:
        print("No non-fixture score annotations available. IRR status: verification only.")
        return 0

    by_slice_dim: dict[tuple[str, str], dict[str, float]] = defaultdict(dict)
    for ann in real:
        key = (ann.slice_id, ann.rating_dimension)
        by_slice_dim[key][ann.rater_id] = ann.rating_value

    multi = {k: v for k, v in by_slice_dim.items() if len(v) >= 2}
    if not multi:
        print(f"Annotations loaded: {len(real)}; multi-rater slices: 0")
        return 0

    rater_ids = sorted({rid for ratings in multi.values() for rid in ratings})
    slice_keys = sorted(multi.keys())
    matrix = np.full((len(rater_ids), len(slice_keys)), np.nan)
    for j, sk in enumerate(slice_keys):
        for i, rid in enumerate(rater_ids):
            if rid in multi[sk]:
                matrix[i, j] = multi[sk][rid]

    alpha = krippendorff_alpha_placeholder(matrix)
    print(f"Multi-rater slice-dimensions: {len(slice_keys)}")
    print(f"Raters: {len(rater_ids)}")
    print(f"Krippendorff alpha (placeholder): {alpha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
