# Changelog

## Source closure — 2026-10-13

- Corrected Alloy storage to `/var/lib/alloy` and added proxy bridge networks
  without masquerading so loopback publications work alongside internal stacks.
- Added a monitor rsyslog network-online override with AF_NETLINK support.
- Enabled validation handlers to notify the required reload/restart after changes.
- Scoped Suricata capture to IPv4 without IPv4 multicast and documented the
  excluded traffic; retained parser checks for unexpected IPv4 hosts.
- Added source synchronization and Vietnamese demo guides, handler/filter
  regression assertions and explicit private-report secret scan exclusions.

## VMware review — 2026-10-10

- Migrated guest detection, host prerequisite checks, NIC examples and all guides
  to VMware Workstation Pro with a private LAN Segment.
- Added guarded installation checks, controller/guest configuration consistency,
  fatal Ansible prechecks and non-root Suricata configuration validation.
- Added monitoring launcher ps/logs/validate actions and Alloy validation before startup.
- Required actual fresh scoped EVE/auth/HTTP evidence and running collector containers;
  added HTTP-marker Loki validation and excluded dashboard services in lightweight mode.
- Corrected report exit codes, bounded config reads and rejected malformed demo URLs.
- Excluded VMware state/private candidate paths and added a scanned source ZIP exporter.
- Added regression tests and Vietnamese instructions for updating existing VMware guests.

## 1.0.0 — 2026-10-05

- Initial source and configuration implementation for a three-VM defensive lab.
- Shared configuration, bounded simulations, local CLI and private HTML reports.
- Suricata, centralized logs and a provisioned Grafana dashboard.
- English/Vietnamese guides, static CI and publication review procedures.
- Guest deployment and end-to-end detection remain pending until VMs are created.
