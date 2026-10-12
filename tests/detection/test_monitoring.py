"""Malformed, out-of-scope and bounded evidence parsing regressions."""

import json

import pytest

from cyberlab.config import load_config
from cyberlab.monitoring import MonitoringError, read_events, summarize_events


def test_partial_evidence_is_reported(tmp_path):
    path = tmp_path / "synthetic.ndjson"
    records = [
        "not JSON",
        json.dumps({"timestamp": "2000-01-01", "src_ip": "203.0.113.1"}),
        json.dumps({"timestamp": "2000-01-01", "event_type": "alert", "alert": []}),
        json.dumps(
            {
                "synthetic": True,
                "timestamp": "2000-01-01",
                "event_type": "flow",
                "src_ip": "192.168.56.10",
            }
        ),
    ]
    path.write_text("\n".join(records), encoding="utf-8")
    evidence = read_events(path, load_config())
    assert evidence.malformed == 2
    assert evidence.out_of_scope == 1
    assert len(evidence.records) == 1


def test_only_recent_records_retained(tmp_path):
    path = tmp_path / "synthetic.ndjson"
    path.write_text(
        "\n".join(
            json.dumps(
                {"synthetic": True, "timestamp": f"2000-01-01T00:00:0{i}", "event_type": "flow"}
            )
            for i in range(4)
        ),
        encoding="utf-8",
    )
    evidence = read_events(path, load_config(), limit=2)
    assert len(evidence.records) == 2
    assert evidence.omitted == 2
    assert evidence.records[-1]["timestamp"].endswith("03")


def test_missing_and_invalid_limits(tmp_path):
    path = tmp_path / "missing.ndjson"
    assert read_events(path, load_config(), missing_ok=True).missing
    with pytest.raises(MonitoringError):
        read_events(path, load_config())
    with pytest.raises(MonitoringError):
        read_events(path, load_config(), limit=0)


def test_synthetic_statistics_are_not_unique_incidents():
    from cyberlab.config import ROOT

    sources = [
        read_events(ROOT / "detection/test-events" / f"{name}.ndjson", load_config())
        for name in ("eve", "auth", "http")
    ]
    summary = summarize_events(*sources)
    assert summary["ids_alert_count"] == 4
    assert summary["ssh_rejection_lines"] == 2
    assert summary["ssh_accepted_lines"] == 0
    assert summary["http_request_count"] == 3
    assert summary["missing_sources"] == []
