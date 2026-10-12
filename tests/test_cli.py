"""Offline CLI commands cannot silently perform live operations."""

import pytest

from cyberlab.cli import main


@pytest.mark.parametrize(
    "arguments",
    [
        ["status"],
        ["hosts"],
        ["validate-config"],
        ["alerts", "--sample"],
        ["simulate", "urls", "--dry-run"],
    ],
)
def test_offline_cli_has_no_network(monkeypatch, arguments):
    from cyberlab import cli, simulations

    def forbidden(*args, **kwargs):
        raise AssertionError("unexpected live operation")

    monkeypatch.setattr(cli, "LabNetwork", forbidden)
    monkeypatch.setattr(simulations, "LabNetwork", forbidden)
    assert main(arguments) == 0


def test_live_checks_without_confirmation_are_skipped(capsys):
    assert main(["check-network"]) == 3
    assert "SKIPPED - requires running cyber lab." in capsys.readouterr().out


def test_bad_target_and_count_fail_before_network():
    assert main(["simulate", "http", "--target", "example.invalid", "--dry-run"]) == 2
    assert main(["simulate", "ssh", "--count", "4", "--dry-run"]) == 2


def test_synthetic_report_cannot_include_live_observations():
    assert main(["report", "--sample", "--live", "--confirm-isolated"]) == 2


def test_missing_report_evidence_returns_skip_without_fake_data(monkeypatch, tmp_path):
    from cyberlab import cli
    from cyberlab.config import load_config

    config = load_config()
    monkeypatch.setattr(cli, "load_config", lambda *args: config)
    monkeypatch.setattr(cli, "ROOT", tmp_path)
    monkeypatch.setattr(cli, "write_report", lambda *args, **kwargs: tmp_path / "private.html")
    missing = str(tmp_path / "missing.ndjson")
    assert main(["report", "--eve", missing, "--auth", missing, "--http", missing]) == 3


def test_failed_live_report_returns_nonzero_after_writing(monkeypatch, tmp_path):
    from cyberlab import cli
    from cyberlab.config import load_config
    from cyberlab.monitoring import EventFile

    config = load_config()
    monkeypatch.setattr(cli, "load_config", lambda *args: config)
    monkeypatch.setattr(cli, "ROOT", tmp_path)
    monkeypatch.setattr(cli, "read_events", lambda *args, **kwargs: EventFile([]))
    monkeypatch.setattr(cli, "LabNetwork", lambda *args, **kwargs: object())
    monkeypatch.setattr(
        cli,
        "check_services",
        lambda *args: [
            {
                "host": "target",
                "service": "http",
                "status": "FAIL",
                "detail": "fixture failure",
            }
        ],
    )
    written = []

    def write(document, *args, **kwargs):
        written.append(document)
        return tmp_path / "private.html"

    monkeypatch.setattr(cli, "write_report", write)
    assert main(["report", "--live", "--confirm-isolated"]) == 1
    assert len(written) == 1
