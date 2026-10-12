"""Small lab-only demonstrations using a single validated network implementation."""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass

from cyberlab.config import ConfigError, LabConfig
from cyberlab.network import LabNetwork

SCENARIOS = ("ping", "tcp", "discover", "http", "ssh", "urls")
MARKERS = ("/admin-test", "/security-test", "/scanner-test")


@dataclass(frozen=True)
class SimulationPlan:
    scenario: str
    target: str
    count: int
    interval_seconds: float
    source_ip: str
    ports: tuple[int, ...]
    paths: tuple[str, ...]


def plan_simulation(
    config: LabConfig, scenario: str, target: str | None = None, count: int | None = None
) -> SimulationPlan:
    """Validate all user input before even a dry-run; discover visits each port once."""
    if scenario not in SCENARIOS:
        raise ConfigError("Unknown educational scenario")
    destination = config.validate_target(target or config.hosts["target"].ip)
    if destination != config.hosts["target"].ip:
        raise ConfigError("Simulations may target only the configured target guest")
    defaults = {
        "ping": 3,
        "tcp": 3,
        "discover": len(config.discovery_ports),
        "http": 8,
        "ssh": 3,
        "urls": 3,
    }
    limits = {
        "ping": 5,
        "tcp": 5,
        "discover": len(config.discovery_ports),
        "http": 20,
        "ssh": 3,
        "urls": 9,
    }
    effective = min(defaults[scenario], config.max_count) if count is None else count
    if type(effective) is not int or not 1 <= effective <= min(limits[scenario], config.max_count):
        raise ConfigError("Simulation count exceeds the configured or scenario limit")
    if scenario == "discover" and effective != len(config.discovery_ports):
        raise ConfigError("Discovery visits exactly the configured small port list once")
    ports = (
        config.discovery_ports
        if scenario == "discover"
        else (config.services["ssh"], config.services["http"])
    )
    return SimulationPlan(
        scenario,
        destination,
        effective,
        config.interval,
        config.hosts["kali"].ip,
        ports,
        MARKERS if scenario == "urls" else ("/health",),
    )


def run_simulation(
    config: LabConfig, plan: SimulationPlan, *, dry_run: bool = False, confirmed: bool = False
) -> dict[str, object]:
    """Perform only the reviewed bounded plan, or return it without network access."""
    reviewed = plan_simulation(config, plan.scenario, plan.target, plan.count)
    if plan != reviewed:
        raise ConfigError("Simulation plan differs from the validated shared configuration")
    if dry_run:
        return {"dry_run": True, "plan": asdict(plan), "network_operations": 0}
    network = LabNetwork(config, confirmed=confirmed)
    if plan.scenario == "ping":
        return {
            "scenario": "ping",
            "count": plan.count,
            "replies_received": network.ping(plan.target, plan.count),
        }
    outcomes: list[dict[str, object]] = []
    for index in range(plan.count):
        if index:
            time.sleep(plan.interval_seconds)
        if plan.scenario in ("tcp", "discover"):
            port = plan.ports[index % len(plan.ports)]
            outcomes.append({"port": port, "connected": network.tcp(plan.target, port)})
        elif plan.scenario in ("http", "urls"):
            path = plan.paths[index % len(plan.paths)]
            status, _body = network.http(plan.target, config.services["http"], path)
            outcomes.append({"path": path, "http_status": status})
        else:
            outcomes.append({"expected_ssh_rejection": network.ssh_rejection(plan.target)})
    return {
        "scenario": plan.scenario,
        "target": plan.target,
        "outcomes": outcomes,
        "note": "Traffic generation does not establish log capture or detection",
    }
