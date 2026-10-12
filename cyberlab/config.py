"""Load the shared configuration and reject unsafe or ambiguous addressing."""

from __future__ import annotations

import ipaddress
import os
import re
import stat
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
RFC1918 = tuple(
    ipaddress.IPv4Network(value) for value in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16")
)
ROLES = ("kali", "target", "monitor")


class ConfigError(ValueError):
    """Configuration does not satisfy the lab safety boundary."""


class UniqueLoader(yaml.SafeLoader):
    """Reject duplicate YAML keys instead of silently overwriting them."""


def _unique_mapping(loader: UniqueLoader, node: yaml.MappingNode) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=True)
        if not isinstance(key, str) or key in result:
            raise ConfigError("YAML mapping keys must be unique strings")
        result[key] = loader.construct_object(value_node, deep=True)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _unique_mapping)


@dataclass(frozen=True)
class Host:
    hostname: str
    ip: str
    interface: str
    nat_interface: str


@dataclass(frozen=True)
class LabConfig:
    name: str
    subnet: ipaddress.IPv4Network
    network_name: str
    mode: str
    hosts: Mapping[str, Host]
    services: Mapping[str, int]
    max_count: int
    interval: float
    discovery_ports: tuple[int, ...]

    def validate_target(self, value: str) -> str:
        """Allow only literal IPv4 addresses of configured, usable lab hosts."""
        if not isinstance(value, str):
            raise ConfigError("Target must be a literal IPv4 string")
        try:
            address = ipaddress.IPv4Address(value)
        except (ipaddress.AddressValueError, TypeError) as exc:
            raise ConfigError(
                "Target must be a literal lab IPv4 address; domains are refused"
            ) from exc
        if address not in self.subnet or str(address) not in {h.ip for h in self.hosts.values()}:
            raise ConfigError("Target is outside the configured host allowlist")
        return str(address)


def _mapping(value: Any, expected: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != expected:
        raise ConfigError(f"{label} must contain exactly: {', '.join(sorted(expected))}")
    return value


def _text(value: Any, pattern: str, label: str) -> str:
    if not isinstance(value, str) or re.fullmatch(pattern, value) is None:
        raise ConfigError(f"Invalid {label}")
    return value


def _integer(value: Any, low: int, high: int, label: str) -> int:
    if type(value) is not int or not low <= value <= high:
        raise ConfigError(f"{label} must be an integer between {low} and {high}")
    return value


def load_config(path: Path | str = ROOT / "config/lab.yml") -> LabConfig:
    """Validate a small RFC1918 subnet, explicit hosts and bounded simulations."""
    try:
        config_path = Path(path)
        if config_path.is_symlink():
            raise ConfigError("Configuration symlinks are refused")
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
        fd = os.open(config_path, flags)
        with os.fdopen(fd, "rb") as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode):
                raise ConfigError("Configuration must be an ordinary file")
            content_bytes = stream.read(65_537)
        if len(content_bytes) > 65_536:
            raise ConfigError("Configuration exceeds the 64 KiB size limit")
        content = content_bytes.decode("utf-8")
        if any(isinstance(event, yaml.AliasEvent) for event in yaml.parse(content)):
            raise ConfigError("YAML aliases are not allowed in lab configuration")
        data = yaml.load(content, Loader=UniqueLoader)  # noqa: S506 — extends SafeLoader
    except (OSError, UnicodeError, yaml.YAMLError, RecursionError) as exc:
        raise ConfigError("Cannot read a valid UTF-8 YAML configuration") from exc
    top = _mapping(data, {"lab", "hosts", "services", "simulation"}, "configuration")
    lab = _mapping(top["lab"], {"name", "subnet", "network_name", "mode"}, "lab")
    try:
        subnet = ipaddress.IPv4Network(lab["subnet"], strict=True)
    except (ValueError, TypeError) as exc:
        raise ConfigError("Lab subnet must be a canonical IPv4 network") from exc
    if not 24 <= subnet.prefixlen <= 28 or not any(subnet.subnet_of(net) for net in RFC1918):
        raise ConfigError("Lab subnet must be RFC1918 with a /24 through /28 prefix")
    name = _text(lab["name"], r"[A-Za-z0-9][A-Za-z0-9 ._-]{2,63}", "lab name")
    network_name = _text(lab["network_name"], r"[A-Za-z][A-Za-z0-9_-]{2,39}", "network name")
    if lab["mode"] not in ("standard", "lightweight"):
        raise ConfigError("Mode must be standard or lightweight")
    raw_hosts = _mapping(top["hosts"], set(ROLES), "hosts")
    hosts: dict[str, Host] = {}
    for role in ROLES:
        raw = _mapping(raw_hosts[role], {"hostname", "ip", "interface", "nat_interface"}, role)
        hostname = _text(raw["hostname"], r"LAB-[A-Z0-9-]{1,30}", "lab hostname")
        interface = _text(raw["interface"], r"[A-Za-z][A-Za-z0-9_.-]{0,14}", "lab interface")
        nat = _text(raw["nat_interface"], r"[A-Za-z][A-Za-z0-9_.-]{0,14}", "NAT interface")
        if interface == nat:
            raise ConfigError("NAT and lab interfaces must differ")
        if not isinstance(raw["ip"], str):
            raise ConfigError("Host IP must be a literal IPv4 string")
        try:
            address = ipaddress.IPv4Address(raw["ip"])
        except (ValueError, TypeError) as exc:
            raise ConfigError("Each host must have a literal IPv4 address") from exc
        if address not in subnet or address in (subnet.network_address, subnet.broadcast_address):
            raise ConfigError("Host is not a usable address in the lab subnet")
        hosts[role] = Host(hostname, str(address), interface, nat)
    if len({h.ip for h in hosts.values()}) != len(hosts):
        raise ConfigError("Host addresses must be unique")
    if len({h.hostname for h in hosts.values()}) != len(hosts):
        raise ConfigError("Hostnames must be unique")
    raw_services = _mapping(top["services"], {"ssh", "http", "grafana", "syslog"}, "services")
    services = {
        key: _integer(value, 1, 65535, "service port") for key, value in raw_services.items()
    }
    if len(set(services.values())) != len(services):
        raise ConfigError("Service ports must be distinct")
    simulation = _mapping(
        top["simulation"], {"max_count", "interval_seconds", "discovery_ports"}, "simulation"
    )
    max_count = _integer(simulation["max_count"], 1, 20, "max_count")
    interval = simulation["interval_seconds"]
    if type(interval) not in (int, float) or not 0.5 <= interval <= 5:
        raise ConfigError("Simulation interval must be between 0.5 and 5 seconds")
    ports = simulation["discovery_ports"]
    if not isinstance(ports, list) or not 1 <= len(ports) <= 8:
        raise ConfigError("Discovery must contain 1 through 8 ports")
    ports = tuple(_integer(port, 1, 65535, "discovery port") for port in ports)
    if len(set(ports)) != len(ports):
        raise ConfigError("Discovery ports must be unique")
    if max_count < len(ports):
        raise ConfigError("max_count must accommodate the small discovery port list")
    return LabConfig(
        name,
        subnet,
        network_name,
        lab["mode"],
        MappingProxyType(hosts),
        MappingProxyType(services),
        max_count,
        float(interval),
        ports,
    )
