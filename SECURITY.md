# Security policy and assumptions

This project is an educational defensive lab for systems you own. Use only the
configured private VMware LAN Segment. Live commands require a VMware Linux guest,
explicit isolation confirmation, the configured source IP and interface, a
direct route to the destination, and no IPv4 or IPv6 default route.

The default LAN Segment has no Windows host attachment. NAT is enabled only
for installation and updates, then disconnected before exercises. Never use
Bridged networking, port forwarding, shared folders, clipboard sharing or guest
packet forwarding during exercises. A private IP alone does not prove isolation;
verify the VMware topology manually.

The CLI accepts literal IPv4 addresses of configured hosts, limits the subnet to
a small RFC1918 network, binds traffic to the source lab address, refuses DNS
targets, proxies and HTTP redirects, and bounds timeouts, counts and ports.
Simulations contain no exploitation, password guessing or executable payloads.

SSH is key based with verified host keys. Grafana has no default password;
generate one locally in an ignored file. Docker applications drop capabilities,
use non-root users, and expose only loopback ports. Nginx exposes the intended
guest lab ports with source restrictions. The Docker group grants effective root
access; automation does not add the learner to it.

Public files must contain only source, safe templates, documentation and labelled
synthetic examples. Keep keys, logs, captures, screenshots and live reports out
of Git. `.gitignore` does not remove already tracked data. Review the exact file
list and Git history with [PUBLICATION_CHECKLIST.md](PUBLICATION_CHECKLIST.md).

## Reporting a concern

Do not paste secrets or personal logs into public issues. Describe a reproducible
problem using synthetic data. For an exposed credential, revoke or rotate it,
remove it from all history, then scan again before publication. This repository
contains no personal contact information; use a private advisory channel in your
own GitHub repository after creating it.

## Residual risks

Lab syslog and HTTP are plaintext so Suricata can inspect them. Grafana sessions
also use HTTP inside the isolated segment: use only a unique lab password. The
monitor observes lab traffic and stores private logs. VMs and containers are not
a substitute for host patching. IDS signatures indicate telemetry, not proof of
compromise. Recheck dependency advisories and container digests before use.
