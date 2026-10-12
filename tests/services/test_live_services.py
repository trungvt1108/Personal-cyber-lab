"""Opt-in guest service checks; never run on public CI infrastructure."""

import pytest

from cyberlab.services import check_services

pytestmark = pytest.mark.lab


def test_required_guest_services(kali_transport):
    assert not any(check["status"] == "FAIL" for check in check_services(kali_transport))
