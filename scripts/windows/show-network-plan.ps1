[CmdletBinding()]
param()

Write-Output @'
Manual VMware Workstation Pro plan (power off VMs before editing):
  Network Adapter 1: NAT for updates; uncheck Connected and Connect at power on
  on every guest before exercises. No NAT port forwarding.
  Network Adapter 2: LAN Segment named cyberlab-internal on all three VMs.
  Assign static IPs without a gateway or DNS on this segment; no DHCP server.
  No Bridged adapter, NAT port forwards, shared clipboard or shared folders.

Identify Linux NICs by matching guest interfaces to VMware adapter MACs locally;
Ubuntu ens33 (NAT) / ens37 (LAN) are examples, not guaranteed names.
Update config/lab.yml on all three guest copies before deployment.

Suricata requests promiscuous capture inside the monitor. Verify a fresh
Kali-to-target URL alert: broadcast/syslog counts do not prove unicast visibility.
Use docs/network-design.md and docs/detection-guide.md to check capture.
This script prints instructions only and never changes host or VM settings.
'@
