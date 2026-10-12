"""Default-deny lab networking, direct routes and bounded diagnostics."""

from __future__ import annotations

import http.client
import json
import platform
import socket
import subprocess
from dataclasses import dataclass
from pathlib import Path

from cyberlab.config import ConfigError, LabConfig


class SafetyError(ConfigError):
    """An operation cannot establish the configured lab-only safety boundary."""


def _local_command(arguments: list[str]) -> str:
    try:
        result = subprocess.run(arguments, check=True, capture_output=True, text=True, timeout=4)
    except (OSError, subprocess.SubprocessError) as exc:
        raise SafetyError(
            "Required local isolation check failed; verify guest tools and routes"
        ) from exc
    return result.stdout.strip()


def check_guest(config: LabConfig, source_role: str = "kali") -> dict[str, object]:
    """Verify the VMware guest and lab address; allow NAT during installation."""
    if source_role not in config.hosts:
        raise SafetyError("Unknown source role")
    if platform.system() != "Linux":
        raise SafetyError("This operation requires a Linux VMware lab guest")
    if _local_command(["systemd-detect-virt", "--vm"]) != "vmware":
        raise SafetyError("This operation requires detected VMware virtualization")
    source = config.hosts[source_role]
    try:
        addresses = json.loads(
            _local_command(["ip", "-j", "address", "show", "dev", source.interface])
        )
        assigned = {
            (entry.get("local"), entry.get("prefixlen"))
            for link in addresses
            for entry in link.get("addr_info", [])
            if entry.get("family") == "inet"
        }
        if (source.ip, config.subnet.prefixlen) not in assigned:
            raise SafetyError(
                "Configured source IP/prefix is not assigned to the private interface"
            )
    except SafetyError:
        raise
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        raise SafetyError("Malformed local addressing state; aborting") from exc
    return {
        "status": "PASS",
        "source_ip": source.ip,
        "interface": source.interface,
        "virtualization": "vmware",
    }


def check_isolation(
    config: LabConfig, source_role: str = "kali", target: str | None = None
) -> dict[str, object]:
    """Require a verified VMware guest, no default route and a direct lab route."""
    if target is not None:
        target = config.validate_target(target)
    state = check_guest(config, source_role)
    source = config.hosts[source_role]
    try:
        for family in ("-4", "-6"):
            defaults = json.loads(_local_command(["ip", family, "-j", "route", "show", "default"]))
            if defaults:
                raise SafetyError(
                    "Default route exists; disconnect NAT and clear stale routes before testing"
                )
        if target is not None:
            routes = json.loads(
                _local_command(["ip", "-j", "route", "get", target, "from", source.ip])
            )
            if len(routes) != 1:
                raise SafetyError("Destination does not have a single verifiable lab route")
            route = routes[0]
            if (
                route.get("dev") != source.interface
                or route.get("gateway")
                or route.get("type", "unicast") != "unicast"
            ):
                raise SafetyError(
                    "Destination must use a direct private-interface route without a gateway"
                )
    except SafetyError:
        raise
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        raise SafetyError("Malformed local networking state; aborting") from exc
    return {**state, "default_routes": 0}


@dataclass
class LabNetwork:
    config: LabConfig
    confirmed: bool = False
    source_role: str = "kali"

    def __post_init__(self) -> None:
        if not self.confirmed:
            raise SafetyError(
                "Live operation requires --confirm-isolated after manual topology review"
            )
        check_isolation(self.config, self.source_role)

    @property
    def source_ip(self) -> str:
        return self.config.hosts[self.source_role].ip

    def _destination(self, target: str, port: int | None = None) -> str:
        target = self.config.validate_target(target)
        if port is not None and (
            type(port) is not int
            or port not in set(self.config.services.values()) | set(self.config.discovery_ports)
        ):
            raise SafetyError("Port is not in the bounded configured allowlist")
        # Recheck immediately before every operation so route changes fail closed.
        check_isolation(self.config, self.source_role, target)
        return target

    def ping(self, target: str, count: int = 1) -> bool:
        if type(count) is not int or not 1 <= count <= min(5, self.config.max_count):
            raise SafetyError("ICMP count exceeds its small demonstration bound")
        target = self._destination(target)
        arguments = [
            "ping",
            "-n",
            "-I",
            self.source_ip,
            "-c",
            str(count),
            "-i",
            str(self.config.interval),
            "-W",
            "2",
            target,
        ]
        try:
            result = subprocess.run(
                arguments, capture_output=True, text=True, timeout=count * 3 + 3, check=False
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise SafetyError("ICMP diagnostic could not complete") from exc
        return result.returncode == 0

    def tcp(self, target: str, port: int) -> bool:
        """Attempt one normal TCP connection using the configured lab source."""
        target = self._destination(target, port)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connection:
                connection.settimeout(2)
                connection.bind((self.source_ip, 0))
                return connection.connect_ex((target, port)) == 0
        except OSError:
            return False

    def http(self, target: str, port: int, path: str) -> tuple[int, bytes]:
        """Make one literal-IP request; ignore proxy environment and reject redirects."""
        allowed_paths = {
            "/",
            "/health",
            "/api/status",
            "/api/health",
            "/login-demo",
            "/admin-test",
            "/security-test",
            "/scanner-test",
        }
        if path not in allowed_paths or port not in (
            self.config.services["http"],
            self.config.services["grafana"],
        ):
            raise SafetyError("HTTP endpoint is outside the lab demo allowlist")
        target = self._destination(target, port)
        connection = http.client.HTTPConnection(
            target, port, timeout=3, source_address=(self.source_ip, 0)
        )
        try:
            connection.request(
                "GET",
                path,
                headers={"User-Agent": "CyberLab educational telemetry", "Connection": "close"},
            )
            response = connection.getresponse()
            if 300 <= response.status < 400:
                raise SafetyError("HTTP redirects are refused; no redirected request was sent")
            return response.status, response.read(65_536)
        except (OSError, http.client.HTTPException) as exc:
            raise SafetyError("HTTP request did not complete") from exc
        finally:
            connection.close()

    def ssh_rejection(self, target: str) -> bool:
        """Request no authentication method for a reserved invalid user; send no secret."""
        target = self._destination(target, self.config.services["ssh"])
        known_hosts = Path("~/.ssh/known_hosts").expanduser()
        if not known_hosts.is_file():
            raise SafetyError("Enroll and verify the target SSH host key before this demonstration")
        arguments = [
            "ssh",
            "-F",
            "/dev/null",
            "-b",
            self.source_ip,
            "-p",
            str(self.config.services["ssh"]),
            "-o",
            "BatchMode=yes",
            "-o",
            "StrictHostKeyChecking=yes",
            "-o",
            f"UserKnownHostsFile={known_hosts}",
            "-o",
            "GlobalKnownHostsFile=/dev/null",
            "-o",
            "PreferredAuthentications=none",
            "-o",
            "PubkeyAuthentication=no",
            "-o",
            "PasswordAuthentication=no",
            "-o",
            "KbdInteractiveAuthentication=no",
            "-o",
            "ProxyCommand=none",
            "-o",
            "ProxyJump=none",
            "-o",
            "PermitLocalCommand=no",
            "-o",
            "ConnectionAttempts=1",
            "-o",
            "ConnectTimeout=3",
            f"cyberlab-invalid@{target}",
            "true",
        ]
        try:
            result = subprocess.run(
                arguments, capture_output=True, text=True, timeout=6, check=False
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise SafetyError("SSH diagnostic could not complete") from exc
        if (
            "Host key verification failed" in result.stderr
            or "REMOTE HOST IDENTIFICATION HAS CHANGED" in result.stderr
        ):
            raise SafetyError("SSH host key verification failed; investigate at the guest console")
        return result.returncode == 255 and "Permission denied" in result.stderr
