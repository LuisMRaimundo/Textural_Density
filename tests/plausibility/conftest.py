"""Session collector for HARD / SOFT findings."""

from __future__ import annotations

import json
import threading
from typing import Any

import pytest

from tests.plausibility.helpers import RESULTS_PATH

_LOCK = threading.Lock()
_RECORDS: list[dict[str, Any]] = []


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "plausibility: musicological/acoustic SOFT expectation (not a production defect)",
    )


def record(
    *,
    family: str,
    test_id: str,
    kind: str,
    status: str,
    **payload: Any,
) -> dict[str, Any]:
    entry = {
        "family": family,
        "test_id": test_id,
        "kind": kind,
        "status": status,
        **payload,
    }
    with _LOCK:
        _RECORDS.append(entry)
    return entry


def record_soft(
    *,
    family: str,
    test_id: str,
    met: bool,
    expectation: str,
    **payload: Any,
) -> None:
    payload.pop("status", None)
    record(
        family=family,
        test_id=test_id,
        kind="SOFT",
        status="met" if met else "not_met",
        expectation=expectation,
        **payload,
    )
    if not met:
        pytest.xfail(f"SOFT {test_id}: {expectation}")


def record_hard(
    *,
    family: str,
    test_id: str,
    status: str = "pass",
    **payload: Any,
) -> None:
    record(family=family, test_id=test_id, kind="HARD", status=status, **payload)


@pytest.fixture(scope="session", autouse=True)
def _dump_plausibility_records():
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    yield
    with _LOCK:
        payload = {"n": len(_RECORDS), "records": list(_RECORDS)}
    def _clean(o):
        if isinstance(o, float) and (o != o or o in (float("inf"), float("-inf"))):
            return None
        if isinstance(o, dict):
            return {k: _clean(v) for k, v in o.items()}
        if isinstance(o, list):
            return [_clean(v) for v in o]
        return o

    RESULTS_PATH.write_text(
        json.dumps(_clean(payload), indent=2, allow_nan=False),
        encoding="utf-8",
    )
