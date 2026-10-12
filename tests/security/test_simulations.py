"""Dry-runs and validation must never construct a live transport."""

import pytest

from cyberlab.config import ConfigError, load_config
from cyberlab.simulations import SCENARIOS, plan_simulation, run_simulation


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_dry_run_has_no_network(monkeypatch, scenario):
    from cyberlab import simulations

    def forbidden(*args, **kwargs):
        raise AssertionError("dry-run tried to construct network transport")

    monkeypatch.setattr(simulations, "LabNetwork", forbidden)
    config = load_config()
    result = run_simulation(config, plan_simulation(config, scenario), dry_run=True)
    assert result["network_operations"] == 0


@pytest.mark.parametrize(
    "target", ["example.invalid", "203.0.113.1", "192.168.56.30", "192.168.56.21"]
)
def test_only_target_guest_allowed(target):
    with pytest.raises(ConfigError):
        plan_simulation(load_config(), "http", target)


@pytest.mark.parametrize(
    "scenario,count",
    [("ssh", 4), ("ping", 6), ("http", 9999), ("discover", 100), ("http", -1), ("http", True)],
)
def test_bounded_counts(scenario, count):
    with pytest.raises(ConfigError):
        plan_simulation(load_config(), scenario, count=count)


def test_live_requires_manual_confirmation(monkeypatch):
    from cyberlab import network

    monkeypatch.setattr(network.platform, "system", lambda: "Windows")
    config = load_config()
    with pytest.raises(ConfigError):
        run_simulation(config, plan_simulation(config, "http"))
