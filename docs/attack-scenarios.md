# Safe educational event scenarios

All commands below run only in the isolated Kali VM after setup. Always review
the dry-run first. Source/destination must match shared config, VMware Workstation Pro must
be detected, NAT/default routes must be absent, and egress must use the direct
private interface. There is no override for public addresses, domains, unlimited
rates or arbitrary port ranges. A maximum of 20 events is enforced globally;
scenario-specific limits can be smaller.

```bash
python3 cyberlab.py simulate ping --dry-run
python3 cyberlab.py simulate ping --confirm-isolated
```

| Scenario | Bounded action | Host/network evidence | Expected detection |
| --- | --- | --- | --- |
| `ping` | Three echo requests by default, at most five | ICMP packets/replies and EVE | SID 1000001 for target echo requests |
| `tcp` | Up to five normal connections, alternating SSH/HTTP | TCP state, EVE flow, possible SSH preauth notices | Connection rules depend on counts/timing |
| `discover` | One normal connect per configured port, max eight ports | Open/blocked/closed observations and SYN packets | Possible SID 1000002; counts retransmissions, not distinct ports |
| `http` | Eight `/health` GETs by default, max config count, no faster than two/second | Nginx access, EVE HTTP and rate metadata | SID 1000007 after threshold is exceeded |
| `ssh` | At most three rejected attempts; no keys/passwords/auth method offered | Invalid-user/preauth auth log, encrypted SSH flow | Host auth rejection; SID 1000003 only sees repeated connections |
| `urls` | Three harmless marker paths by default, at most nine | Nginx URI and EVE HTTP | SIDs 1000004, 1000005, 1000006 |

Choose one scenario and substitute its name:

```bash
python3 cyberlab.py simulate discover --dry-run
python3 cyberlab.py simulate discover --confirm-isolated
python3 cyberlab.py simulate http --confirm-isolated --count 8
python3 cyberlab.py simulate ssh --confirm-isolated --count 3
python3 cyberlab.py simulate urls --confirm-isolated
```

Closed/blocked discovery ports are expected on the hardened target. Discovery
does not identify software, exploit services or retry a broad range. HTTP
requests use a literal IP and fixed path, ignore proxy environment settings and
refuse redirects. No cookies, credentials, real login data or payloads are sent.

SSH requires a previously verified host key and the reserved absent user
`cyberlab-invalid`. It bypasses local SSH proxy/config/agent authentication and
uses `PreferredAuthentications=none`; it cannot guess a password. Ansible verifies
the user is absent. A host key error aborts, while a network timeout is not
reported as a confirmed rejection. Investigate target logs to verify the event.

Do not repeatedly run the scenarios to inflate alert statistics. Record the UTC
window, expected SID, actual observations and failures, then wait for counters
to clear before a separate exercise. See [detection-guide.md](detection-guide.md).
