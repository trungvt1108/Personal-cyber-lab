"""Timestamp freshness does not treat old fixture data as current evidence."""

import json
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest

from cyberlab.config import load_config
from cyberlab.monitoring import EventFile
from cyberlab.validation import MARKER, is_fresh, marker_matches, validate_monitor


def test_freshness_requires_valid_recent_timezone():
    assert is_fresh(datetime.now(UTC).isoformat())
    assert not is_fresh("2000-01-01T00:00:00+00:00")
    assert not is_fresh("not a timestamp")
    assert not is_fresh(datetime.now().replace(tzinfo=None).isoformat())
    assert not is_fresh((datetime.now(UTC) + timedelta(minutes=5)).isoformat())


@pytest.fixture
def actual_markers():
    now = datetime.now(UTC).isoformat()
    addresses = {"src_ip": "192.168.56.10", "dest_ip": "192.168.56.20"}
    return {
        "eve": EventFile(
            [
                {
                    "timestamp": now,
                    "event_type": "stats",
                    "stats": {"capture": {"kernel_packets": 3}},
                },
                {
                    "timestamp": now,
                    **addresses,
                    "event_type": "alert",
                    "dest_port": 80,
                    "alert": {"signature_id": 1000004},
                },
            ]
        ),
        "auth": EventFile([{"timestamp": now, "sender_ip": "192.168.56.20", "message": MARKER}]),
        "http": EventFile([{"timestamp": now, **addresses, "path": "/admin-test", "status": 200}]),
    }


@pytest.fixture
def mocked_monitor(monkeypatch, actual_markers):
    from cyberlab import validation

    monkeypatch.setattr(validation, "check_isolation", lambda *args: {"status": "PASS"})
    monkeypatch.setattr(
        validation.subprocess, "run", lambda *args, **kwargs: SimpleNamespace(returncode=0)
    )
    monkeypatch.setattr(validation, "_container_running", lambda *args: True)
    monkeypatch.setattr(validation, "_query_marker", lambda *args: True)

    def read(path, config):
        name = "eve" if "eve.json" in path else "auth" if "auth.jsonl" in path else "http"
        return actual_markers[name]

    monkeypatch.setattr(validation, "read_events", read)
    return actual_markers


def test_complete_pipeline_requires_all_three_loki_streams(monkeypatch, mocked_monitor):
    from cyberlab import validation

    queries = []
    monkeypatch.setattr(
        validation, "_query_marker", lambda config, query: queries.append(query) or True
    )
    checks = validate_monitor(load_config(), confirmed=True)
    assert all(check["status"] == "PASS" for check in checks)
    assert len(queries) == 3
    assert any('kind="nginx_access"' in query for query in queries)


@pytest.mark.parametrize("kind", ["eve", "auth", "http"])
def test_synthetic_markers_never_prove_live_pipeline(mocked_monitor, kind):
    for record in mocked_monitor[kind].records:
        record["synthetic"] = True
    checks = validate_monitor(load_config(), confirmed=True)
    assert any(check["status"] == "FAIL" for check in checks)


@pytest.mark.parametrize(
    "field,value",
    [
        ("src_ip", "192.168.56.30"),
        ("dest_ip", "192.168.56.30"),
        ("dest_port", 22),
        ("src_ip", None),
        ("alert", {}),
        ("timestamp", "2000-01-01T00:00:00+00:00"),
    ],
)
def test_ids_marker_requires_expected_addresses_port_sid_and_time(actual_markers, field, value):
    record = actual_markers["eve"].records[-1]
    record[field] = value
    assert not marker_matches(record, load_config(), "ids")


def test_http_failure_and_wrong_auth_sender_are_rejected(actual_markers):
    actual_markers["http"].records[0]["status"] = 500
    actual_markers["auth"].records[0]["sender_ip"] = "192.168.56.30"
    assert not marker_matches(actual_markers["http"].records[0], load_config(), "http")
    assert not marker_matches(actual_markers["auth"].records[0], load_config(), "auth")


def test_exited_alloy_fails_even_with_recent_evidence(monkeypatch, mocked_monitor):
    from cyberlab import validation

    monkeypatch.setattr(validation, "_container_running", lambda name: "alloy" not in name)
    checks = validate_monitor(load_config(), confirmed=True)
    assert {"name": "container alloy", "status": "FAIL"} in checks


def test_lightweight_does_not_require_dashboard_services(monkeypatch, mocked_monitor):
    from cyberlab import validation

    def forbidden(*args):
        raise AssertionError("dashboard operation in lightweight mode")

    monkeypatch.setattr(validation, "_container_running", forbidden)
    monkeypatch.setattr(validation, "_query_marker", forbidden)
    checks = validate_monitor(replace(load_config(), mode="lightweight"), confirmed=True)
    assert not any(check["status"] == "FAIL" for check in checks)
    assert {"name": "dashboard pipeline (lightweight mode)", "status": "SKIP"} in checks


@pytest.mark.parametrize(
    "state",
    [
        {"Running": True, "Restarting": False},
        {"Running": False, "Restarting": False},
        {"Running": True, "Restarting": True},
        {"Running": True, "Health": {"Status": "unhealthy"}},
    ],
)
def test_container_state_is_checked_without_compose(monkeypatch, state):
    from cyberlab import validation

    calls = []

    def run(arguments, **kwargs):
        calls.append(arguments)
        return SimpleNamespace(stdout=json.dumps(state))

    monkeypatch.setattr(validation.subprocess, "run", run)
    expected = (
        state.get("Running")
        and not state.get("Restarting")
        and state.get("Health", {}).get("Status", "healthy") == "healthy"
    )
    assert validation._container_running("cyberlab-monitoring-alloy-1") == expected
    assert calls[0][:2] == ["docker", "inspect"]
