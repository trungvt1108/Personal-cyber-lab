"""Opt-in evidence checks after manually generating the documented lab markers."""

import pytest

from cyberlab.config import load_config
from cyberlab.validation import marker_matches, validate_monitor

pytestmark = pytest.mark.lab


def test_fresh_ids_marker(monitor_evidence):
    records = monitor_evidence["eve"].records
    assert any(marker_matches(record, load_config(), "ids") for record in records)


def test_central_auth_marker(monitor_evidence):
    assert any(
        marker_matches(record, load_config(), "auth") for record in monitor_evidence["auth"].records
    )


def test_end_to_end_ingestion(monitor_evidence):
    checks = validate_monitor(load_config(), confirmed=True)
    assert not any(check["status"] == "FAIL" for check in checks)
