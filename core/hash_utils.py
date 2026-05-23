"""
Deterministic hashes for replication and report metadata.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from core.defaults import METRIC_SCHEMA_VERSION, RESEARCH_ANALYSIS_DEFAULTS


def _canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)


def sha256_hex(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def config_hash(config: dict[str, Any] | Any) -> str:
    """Hash analysis configuration relevant to metric outputs."""
    if hasattr(config, "weight_factor"):
        payload = {
            "weight_factor": float(config.weight_factor),
            "metric_schema_version": METRIC_SCHEMA_VERSION,
        }
    else:
        merged = {**RESEARCH_ANALYSIS_DEFAULTS, **dict(config)}
        payload = {
            "weight_factor": float(merged.get("weight_factor", 0.5)),
            "metric_schema_version": METRIC_SCHEMA_VERSION,
        }
    return sha256_hex(_canonical_json(payload))


def input_hash_from_dict(input_data: dict[str, Any]) -> str:
    """Hash symbolic score input fields (notes, dynamics, instruments, counts)."""
    payload = {
        "notes": list(input_data.get("notes", [])),
        "dynamics": list(input_data.get("dynamics", [])),
        "instruments": list(input_data.get("instruments", [])),
        "num_instruments": list(input_data.get("num_instruments", [])),
    }
    return sha256_hex(_canonical_json(payload))
