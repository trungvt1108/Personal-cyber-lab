"""Live tests require two explicit switches and are always disabled in CI."""

import os

import pytest

from cyberlab.config import load_config
from cyberlab.monitoring import read_events
from cyberlab.network import LabNetwork, check_isolation


def pytest_addoption(parser):
    parser.addoption("--run-lab", action="store_true", default=False)
    parser.addoption("--confirm-isolated", action="store_true", default=False)
    parser.addoption("--lab-role", choices=("kali", "monitor"), default="kali")


def _require_lab(request, role):
    if os.environ.get("GITHUB_ACTIONS") or not request.config.getoption("--run-lab"):
        pytest.skip("SKIPPED - requires running cyber lab.")
    if not request.config.getoption("--confirm-isolated"):
        pytest.fail(
            "Live tests require --confirm-isolated after reviewing VMware Workstation Pro isolation"
        )
    if request.config.getoption("--lab-role") != role:
        pytest.skip(f"SKIPPED - requires running cyber lab in the {role} guest.")


@pytest.fixture
def kali_transport(request):
    _require_lab(request, "kali")
    return LabNetwork(load_config(), confirmed=True)


@pytest.fixture
def monitor_evidence(request):
    _require_lab(request, "monitor")
    config = load_config()
    check_isolation(config, "monitor")
    return {
        "eve": read_events("/var/log/suricata/eve.json", config),
        "auth": read_events("/var/log/cyberlab-target/auth.jsonl", config),
        "http": read_events("/var/log/cyberlab-target/nginx-access.jsonl", config),
    }
