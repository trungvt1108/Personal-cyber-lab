"""Argparse entry point: offline-first diagnostics, bounded exercises and reports."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

from cyberlab.config import ROOT, ConfigError, load_config
from cyberlab.monitoring import MonitoringError, alert_view, read_events, summarize_events
from cyberlab.network import LabNetwork, check_guest, check_isolation
from cyberlab.reporting import render_report, write_report
from cyberlab.services import check_network, check_services
from cyberlab.simulations import SCENARIOS, plan_simulation, run_simulation

SKIPPED = "SKIPPED - requires running cyber lab."


def _live_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--confirm-isolated",
        action="store_true",
        help="confirm you manually reviewed the isolated VMware LAN Segment topology",
    )


def _evidence_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--sample", action="store_true", help="use explicitly synthetic repository fixtures"
    )
    parser.add_argument("--eve", type=Path, default=Path("/var/log/suricata/eve.json"))
    parser.add_argument("--auth", type=Path, default=Path("/var/log/cyberlab-target/auth.jsonl"))
    parser.add_argument(
        "--http", type=Path, default=Path("/var/log/cyberlab-target/nginx-access.jsonl")
    )


def parser_for_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cyberlab-cli",
        description="Local defensive lab diagnostics; live traffic requires isolation checks.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(os.environ.get("CYBERLAB_CONFIG", ROOT / "config/lab.yml")),
    )
    parser.add_argument("--version", action="version", version="cyberlab-cli 1.0.0")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("validate-config", help="offline config safety validation")
    commands.add_parser("hosts", help="show configured lab hosts, without discovery")
    guest = commands.add_parser("verify-guest", help="verify VMware guest/address for installation")
    guest.add_argument("--source-role", choices=("kali", "target", "monitor"), default="kali")
    guest.add_argument("--confirm-lab-guest", action="store_true")
    status = commands.add_parser(
        "status", help="offline status; opt in to live service observations"
    )
    status.add_argument("--live", action="store_true")
    _live_options(status)
    preflight = commands.add_parser(
        "preflight", help="verify guest addressing, virtualization and routes"
    )
    preflight.add_argument("--source-role", choices=("kali", "target", "monitor"), default="kali")
    _live_options(preflight)
    for name in ("check-network", "check-services"):
        _live_options(commands.add_parser(name))
    simulate = commands.add_parser("simulate", help="bounded educational event generation")
    simulate.add_argument("scenario", choices=SCENARIOS)
    simulate.add_argument("--target")
    simulate.add_argument("--count", type=int)
    exclusive = simulate.add_mutually_exclusive_group()
    exclusive.add_argument("--dry-run", action="store_true")
    exclusive.add_argument("--confirm-isolated", action="store_true")
    alerts = commands.add_parser("alerts", help="read local EVE alerts or synthetic examples")
    alerts.add_argument("--limit", type=int, default=20)
    _evidence_options(alerts)
    report = commands.add_parser(
        "report", help="write a private or synthetic standalone HTML report"
    )
    report.add_argument("--output", type=Path)
    report.add_argument("--live", action="store_true")
    _live_options(report)
    _evidence_options(report)
    render = commands.add_parser(
        "render-network", help="generate a guest network file without applying it"
    )
    render.add_argument("role", choices=("kali", "target", "monitor"))
    return parser


def _print_json(value: Any) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False))


def _print_checks(checks: list[dict[str, Any]]) -> int:
    for check in checks:
        name = f"{check['host']} {check.get('service', 'network')}"
        print(f"[{check['status']}] {name}: {check['detail']}")
    return int(any(check["status"] == "FAIL" for check in checks))


def _render_network(config: Any, role: str) -> None:
    import yaml

    host = config.hosts[role]
    if role == "kali":
        print(
            "Kali uses NetworkManager. Apply the reviewed nmcli commands in docs/installation.md."
        )
        return
    document = {
        "network": {
            "version": 2,
            "renderer": "networkd",
            "ethernets": {
                host.nat_interface: {"dhcp4": True, "optional": True},
                host.interface: {
                    "dhcp4": False,
                    "dhcp6": False,
                    "accept-ra": False,
                    "addresses": [f"{host.ip}/{config.subnet.prefixlen}"],
                },
            },
        }
    }
    destination = ROOT / ".generated" / f"50-cyberlab-{role}.yaml"
    if destination.parent.is_symlink() or destination.is_symlink():
        raise ConfigError("Generated network output must not be a symlink")
    destination.parent.mkdir(exist_ok=True)
    destination.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    destination.chmod(0o600)
    print(
        f"[GENERATED] .generated/{destination.name}; review at the guest console before netplan try"
    )


def main(argv: list[str] | None = None) -> int:
    args = parser_for_cli().parse_args(argv)
    try:
        config = load_config(args.config)
        if args.command == "validate-config":
            print(f"[PASS] Configuration validated: {config.subnet}, {config.mode} mode")
        elif args.command == "hosts":
            for role, host in config.hosts.items():
                print(f"{role:8} {host.hostname:16} {host.ip:16} {host.interface}")
        elif args.command == "verify-guest":
            if not args.confirm_lab_guest:
                raise ConfigError("Guest installation check requires --confirm-lab-guest")
            _print_json(check_guest(config, args.source_role))
        elif args.command == "render-network":
            _render_network(config, args.role)
        elif args.command == "preflight":
            if not args.confirm_isolated:
                raise ConfigError(
                    "Preflight requires --confirm-isolated after manual topology review"
                )
            _print_json(check_isolation(config, args.source_role))
        elif args.command in ("check-network", "check-services"):
            if not args.confirm_isolated:
                print(SKIPPED + " Use --confirm-isolated inside Kali.")
                return 3
            network = LabNetwork(config, confirmed=True)
            return _print_checks(
                check_network(network)
                if args.command == "check-network"
                else check_services(network)
            )
        elif args.command == "status":
            if args.live:
                network = LabNetwork(config, confirmed=args.confirm_isolated)
                return _print_checks(check_network(network) + check_services(network))
            _print_json(
                {
                    "configuration": "valid",
                    "lab_status": "UNVERIFIED",
                    "mode": config.mode,
                    "hosts": {
                        role: {"hostname": host.hostname, "ip": host.ip}
                        for role, host in config.hosts.items()
                    },
                    "services": dict(config.services),
                    "system_health": "UNVERIFIED",
                    "notice": SKIPPED,
                }
            )
        elif args.command == "simulate":
            plan = plan_simulation(config, args.scenario, args.target, args.count)
            _print_json({"event": "simulation_plan", **asdict(plan)})
            result = run_simulation(
                config, plan, dry_run=args.dry_run, confirmed=args.confirm_isolated
            )
            _print_json(result)
            if not args.dry_run:
                if "replies_received" in result and not result["replies_received"]:
                    return 1
                for outcome in result.get("outcomes", []):
                    if (
                        outcome.get("expected_ssh_rejection") is False
                        or outcome.get("http_status", 200) != 200
                    ):
                        return 1
        else:
            if args.sample:
                if args.command == "report" and args.live:
                    raise ConfigError("Synthetic reports cannot be combined with live observations")
                eve_path, auth_path, http_path = (
                    ROOT / "detection/test-events" / f"{name}.ndjson"
                    for name in ("eve", "auth", "http")
                )
            else:
                eve_path, auth_path, http_path = args.eve, args.auth, args.http
            eve = read_events(eve_path, config, missing_ok=not args.sample)
            if args.command == "alerts":
                if type(args.limit) is not int or not 1 <= args.limit <= 1000:
                    raise ConfigError("Alert limit must be 1 through 1000")
                if eve.missing:
                    print(SKIPPED + " Select an EVE file or use --sample.")
                    return 3
                _print_json(
                    {
                        "synthetic": args.sample,
                        "alerts": [
                            alert_view(record)
                            for record in eve.records
                            if record.get("event_type") == "alert"
                        ][-args.limit :],
                        "malformed": eve.malformed,
                        "out_of_scope": eve.out_of_scope,
                        "omitted": eve.omitted,
                    }
                )
            else:
                auth = read_events(auth_path, config, missing_ok=not args.sample)
                http = read_events(http_path, config, missing_ok=not args.sample)
                summary = summarize_events(eve, auth, http)
                checks = (
                    check_services(LabNetwork(config, confirmed=args.confirm_isolated))
                    if args.live
                    else None
                )
                output = write_report(
                    render_report(config, summary, synthetic=args.sample, checks=checks),
                    args.output,
                    synthetic=args.sample,
                )
                print(
                    f"[REPORT] {output.relative_to(ROOT).as_posix()}; {'SYNTHETIC EXAMPLE' if args.sample else 'PRIVATE, not for Git'}"
                )
                if summary["missing_sources"]:
                    print(SKIPPED + " Report marks missing evidence and services as unverified.")
                    return 3
                if checks and any(check["status"] == "FAIL" for check in checks):
                    return 1
    except (ConfigError, MonitoringError, OSError) as exc:
        print(f"[ABORT] {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
