"""Safety regression cases; all configuration data is synthetic."""

from pathlib import Path

import pytest
import yaml

from cyberlab.config import ROOT, ConfigError, load_config


@pytest.fixture
def raw_config():
    return yaml.safe_load((ROOT / "config/lab.yml").read_text(encoding="utf-8"))


def write_config(tmp_path, data):
    path = tmp_path / "lab.yml"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


@pytest.mark.parametrize(
    "target",
    [
        "example.com",
        "203.0.113.1",
        "127.0.0.1",
        "192.168.56.1",
        "192.168.57.20",
        "::1",
        "192.168.56.0",
        "192.168.56.255",
        "192.168.056.20",
        "192.168.56.20;id",
    ],
)
def test_target_denied(target):
    with pytest.raises(ConfigError):
        load_config().validate_target(target)


def test_configured_host_allowed():
    assert load_config().validate_target("192.168.56.20") == "192.168.56.20"


def test_integer_encoded_address_is_not_a_literal_target():
    with pytest.raises(ConfigError):
        load_config().validate_target(3232251924)


@pytest.mark.parametrize(
    "subnet",
    [
        "0.0.0.0/0",
        "127.0.0.0/24",
        "169.254.1.0/24",
        "100.64.0.0/24",
        "203.0.113.0/24",
        "192.168.0.0/16",
        "192.168.56.2/24",
    ],
)
def test_unsafe_subnet_rejected(tmp_path, raw_config, subnet):
    raw_config["lab"]["subnet"] = subnet
    with pytest.raises(ConfigError):
        load_config(write_config(tmp_path, raw_config))


@pytest.mark.parametrize(
    "key,value",
    [
        ("max_count", 999),
        ("max_count", True),
        ("interval_seconds", 0.01),
        ("discovery_ports", list(range(1, 100))),
    ],
)
def test_rate_and_scope_limits(tmp_path, raw_config, key, value):
    raw_config["simulation"][key] = value
    with pytest.raises(ConfigError):
        load_config(write_config(tmp_path, raw_config))


def test_duplicate_hosts_rejected(tmp_path, raw_config):
    raw_config["hosts"]["kali"]["ip"] = raw_config["hosts"]["target"]["ip"]
    with pytest.raises(ConfigError):
        load_config(write_config(tmp_path, raw_config))


def test_alias_and_duplicate_yaml_rejected(tmp_path):
    for content in ("lab: 1\nlab: 2\n", "lab: &x [1]\nhosts: *x\n"):
        path = Path(tmp_path) / "bad.yml"
        path.write_text(content, encoding="utf-8")
        with pytest.raises(ConfigError):
            load_config(path)


def test_interface_cannot_be_a_command(tmp_path, raw_config):
    raw_config["hosts"]["kali"]["interface"] = "eth1; touch bad"
    with pytest.raises(ConfigError):
        load_config(write_config(tmp_path, raw_config))


def test_configuration_size_and_depth_are_bounded(tmp_path):
    path = tmp_path / "bad.yml"
    for content in (" " * 65_537, "lab: " + "[" * 2000 + "]" * 2000):
        path.write_text(content, encoding="utf-8")
        with pytest.raises(ConfigError):
            load_config(path)
