"""Verify isolation before any network access; mock every OS/network interaction."""

import json
from types import SimpleNamespace

import pytest

from cyberlab.config import load_config
from cyberlab.network import LabNetwork, SafetyError, check_guest, check_isolation


@pytest.fixture
def isolated(monkeypatch):
    from cyberlab import network

    monkeypatch.setattr(network.platform, "system", lambda: "Linux")
    state = {
        "virtualization": "vmware",
        "default": [],
        "device": "eth1",
        "gateway": None,
        "assigned": "192.168.56.10",
        "prefixlen": 24,
    }

    def command(arguments):
        if arguments[0] == "systemd-detect-virt":
            return state["virtualization"]
        if "address" in arguments:
            return json.dumps(
                [
                    {
                        "addr_info": [
                            {
                                "local": state["assigned"],
                                "family": "inet",
                                "prefixlen": state["prefixlen"],
                            }
                        ]
                    }
                ]
            )
        if "default" in arguments:
            return json.dumps(state["default"])
        return json.dumps([{"dev": state["device"], "gateway": state["gateway"]}])

    monkeypatch.setattr(network, "_local_command", command)
    return state


@pytest.mark.parametrize(
    "field,value",
    [
        ("virtualization", "none"),
        ("virtualization", "kvm"),
        ("prefixlen", 16),
        ("assigned", "192.168.56.11"),
        ("default", [{"dev": "eth0"}]),
        ("device", "eth0"),
        ("gateway", "192.168.56.1"),
    ],
)
def test_egress_denied_before_socket(monkeypatch, isolated, field, value):
    from cyberlab import network

    isolated[field] = value
    calls = []
    monkeypatch.setattr(network.socket, "socket", lambda *_: calls.append(True))
    with pytest.raises(SafetyError):
        LabNetwork(load_config(), confirmed=True).tcp("192.168.56.20", 22)
    assert calls == []


def test_confirmation_is_required(isolated):
    with pytest.raises(SafetyError):
        LabNetwork(load_config())


def test_vmware_guest_is_accepted_and_installation_allows_nat(isolated):
    isolated["default"] = [{"dev": "eth0"}]
    assert check_guest(load_config())["virtualization"] == "vmware"
    with pytest.raises(SafetyError, match="Default route"):
        check_isolation(load_config())


def test_ipv6_default_route_also_blocks_live_checks(monkeypatch, isolated):
    from cyberlab import network

    original = network._local_command

    def command(arguments):
        if "-6" in arguments and "default" in arguments:
            return json.dumps([{"dev": "eth0"}])
        return original(arguments)

    monkeypatch.setattr(network, "_local_command", command)
    with pytest.raises(SafetyError, match="Default route"):
        check_isolation(load_config())


def test_tcp_socket_binds_the_configured_source(monkeypatch, isolated):
    from cyberlab import network

    calls = {}

    class FakeSocket:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def settimeout(self, value):
            calls["timeout"] = value

        def bind(self, address):
            calls["source"] = address

        def connect_ex(self, address):
            calls["target"] = address
            return 0

    monkeypatch.setattr(network.socket, "socket", lambda *_: FakeSocket())
    assert LabNetwork(load_config(), confirmed=True).tcp("192.168.56.20", 22)
    assert calls == {"timeout": 2, "source": ("192.168.56.10", 0), "target": ("192.168.56.20", 22)}


def test_ssh_demo_sends_no_password_or_key(monkeypatch, isolated):
    from cyberlab import network

    class KnownHostsFixture:
        def expanduser(self):
            return self

        def is_file(self):
            return True

        def __str__(self):
            return "known_hosts_fixture"

    calls = []

    def run(arguments, **kwargs):
        calls.extend(arguments)
        return SimpleNamespace(returncode=255, stdout="", stderr="Permission denied (publickey).")

    monkeypatch.setattr(network, "Path", lambda *_: KnownHostsFixture())
    monkeypatch.setattr(network.subprocess, "run", run)
    assert LabNetwork(load_config(), confirmed=True).ssh_rejection("192.168.56.20")
    assert "PreferredAuthentications=none" in calls
    assert "PasswordAuthentication=no" in calls
    assert "PubkeyAuthentication=no" in calls
    assert "StrictHostKeyChecking=yes" in calls
    assert "ProxyCommand=none" in calls
    assert "-i" not in calls


def test_non_linux_is_refused(monkeypatch):
    from cyberlab import network

    monkeypatch.setattr(network.platform, "system", lambda: "Windows")
    with pytest.raises(SafetyError):
        check_isolation(load_config())


def test_route_rechecked_when_state_changes(isolated):
    net = LabNetwork(load_config(), confirmed=True)
    isolated["default"] = [{"dev": "eth0"}]
    with pytest.raises(SafetyError):
        net.tcp("192.168.56.20", 22)


def test_http_redirect_is_not_followed(monkeypatch, isolated):
    from cyberlab import network

    calls = []

    class FakeHTTP:
        def __init__(self, host, port, **kwargs):
            assert host == "192.168.56.20"
            assert kwargs["source_address"] == ("192.168.56.10", 0)

        def request(self, method, path, **kwargs):
            calls.append((method, path))

        def getresponse(self):
            return SimpleNamespace(status=302)

        def close(self):
            pass

    monkeypatch.setenv("HTTP_PROXY", "http://proxy.invalid:8080")
    monkeypatch.setattr(network.http.client, "HTTPConnection", FakeHTTP)
    with pytest.raises(SafetyError, match="redirect"):
        LabNetwork(load_config(), confirmed=True).http("192.168.56.20", 80, "/health")
    assert calls == [("GET", "/health")]


def test_port_and_path_allowlist(isolated):
    net = LabNetwork(load_config(), confirmed=True)
    with pytest.raises(SafetyError):
        net.tcp("192.168.56.20", 9999)
    with pytest.raises(SafetyError):
        net.http("192.168.56.20", 80, "http://example.invalid/")
