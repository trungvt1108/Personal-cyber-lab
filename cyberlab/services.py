"""Source-bound reachability and service checks with explicit pending states."""

from __future__ import annotations

import json
import time

from cyberlab.config import LabConfig
from cyberlab.network import LabNetwork, SafetyError


def check_network(network: LabNetwork) -> list[dict[str, object]]:
    """Report local assignment separately from actual remote ICMP replies."""
    results = []
    for role, host in network.config.hosts.items():
        if role == network.source_role:
            results.append(
                {
                    "host": role,
                    "ip": host.ip,
                    "status": "PASS",
                    "detail": "assigned locally; not a remote ping",
                }
            )
            continue
        time.sleep(network.config.interval)
        received = network.ping(host.ip)
        results.append(
            {
                "host": role,
                "ip": host.ip,
                "status": "PASS" if received else "FAIL",
                "detail": "ICMP reply" if received else "no verified ICMP reply",
            }
        )
    return results


def check_services(network: LabNetwork) -> list[dict[str, object]]:
    """Check TCP SSH and HTTP application health; never assert IDS/log ingestion."""
    config: LabConfig = network.config
    results = []
    for role, service, path in (
        ("target", "ssh", None),
        ("target", "http", "/health"),
        ("monitor", "ssh", None),
        ("monitor", "grafana", "/api/health"),
    ):
        port = config.services[service]
        if role == network.source_role:
            results.append(
                {
                    "host": role,
                    "service": service,
                    "port": port,
                    "status": "SKIP",
                    "detail": "use the guest-local service validator",
                }
            )
            continue
        if service == "grafana" and config.mode == "lightweight":
            results.append(
                {
                    "host": role,
                    "service": service,
                    "port": port,
                    "status": "SKIP",
                    "detail": "lightweight mode",
                }
            )
            continue
        time.sleep(config.interval)
        try:
            if path:
                status, payload = network.http(config.hosts[role].ip, port, path)
                data = json.loads(payload)
                healthy = (
                    status == 200
                    and isinstance(data, dict)
                    and (
                        data.get("status") == "ok"
                        if service == "http"
                        else data.get("database") == "ok"
                    )
                )
            else:
                healthy = network.tcp(config.hosts[role].ip, port)
        except (SafetyError, ValueError, UnicodeError):
            healthy = False
        results.append(
            {
                "host": role,
                "service": service,
                "port": port,
                "status": "PASS" if healthy else "FAIL",
                "detail": "application health"
                if path
                else "TCP connection only; not authentication",
            }
        )
    return results
