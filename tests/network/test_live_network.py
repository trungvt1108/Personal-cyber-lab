"""Opt-in ICMP checks, using the same lab gate as every other network operation."""

import pytest

pytestmark = pytest.mark.lab


@pytest.mark.parametrize("role", ["target", "monitor"])
def test_guest_replies(kali_transport, role):
    assert kali_transport.ping(kali_transport.config.hosts[role].ip)
