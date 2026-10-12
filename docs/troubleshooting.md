# Troubleshooting by observation

| Symptom | Likely cause | Check / correction |
| --- | --- | --- |
| CLI refuses live networking on Windows | Safety boundary requires a Linux VMware Workstation Pro guest | Use offline commands on Windows; run live exercises from Kali |
| Preflight reports default route | NAT still connected or DHCP route remains | Disconnect NAT on every VM; inspect IPv4/IPv6 routes and restart the NAT connection/guest |
| Wrong source/interface | Example NIC name differs from your guest | Identify adapter 2 locally, update shared config and static connection |
| Target unreachable | Different LAN Segment name, cable disabled, IP error or firewall | Inspect VM settings and console addresses before touching firewall |
| SSH hardening would lock you out | Authorized key absent, wrong account or unverified host key | Enroll/verify key at console first; retain console and clean snapshot |
| SSH demo lacks confirmed rejection | Host key missing/mismatched, timeout or real account collision | Inspect fingerprints/auth logs; reserved invalid user must remain absent |
| HTTP 502 | Demo container not built/running, internal bind mismatch | Check target container status and loopback health from the target guest |
| Suricata sees only monitor traffic | Wrong capture NIC/segment or peer unicast unavailable | Inspect VMware LAN Segment attachment and capture NIC; require a fresh Kali-to-target URL SID, not just counters |
| TCP flows but no HTTP markers | Rules not loaded, wrong port, checksum/offload artifact | Run `suricata -T`, confirm rendered ports, inspect EVE decoder/stream stats |
| Central files absent | rsyslog syntax, TCP 514 rule or sender address mismatch | `rsyslogd -N1` on both guests; create a target logger marker and follow each hop |
| rsyslog active but TCP 514 absent, with `Cannot assign requested address` | Receiver started before its private IPv4 address was ready | Deploy the monitor rsyslog network wait override, restart rsyslog, then verify `ss -lntp 'sport = :514'` |
| Alloy cannot read logs | Directory/group permissions or wrong supplementary GID | Review cyberlab-logs ownership, 750 directories, 640 files and the launch script |
| Compose `ps`/`logs` reports missing CYBERLAB variables | The launcher passes log GID/root URL only to its own Compose process | Use launcher `ps`/`logs` actions or direct Docker commands below |
| Grafana fails startup | Secret file inaccessible to UID 472 or data ownership wrong | Rerun guest runtime initializer; keep mode 600, not world-readable |
| Empty panels with healthy containers | No matching data, time window/clock skew, collector delay, query error | Explore one marker, compare event timestamps and check collector errors |
| EVE scope fails on IPv6 or IPv4 multicast flows | Capture includes background traffic outside the IPv4 exercise scope | Inspect rejected records, apply the documented IPv4 capture filter, archive old EVE before starting a new window, then verify fresh markers; old records remain outside scope |
| IDS restarts or guest swaps | Memory allocation/budget insufficient | Use lightweight mode, lower guest load and inspect measured memory usage |
| Repeated kernel soft lockups/systemd watchdog timeouts | Guest scheduling, host load, clock interruptions or virtualization problems require investigation | Check guest memory/load and VMware Workstation Pro runtime/logs; do not infer an OOM from a soft lockup |
| Public scanner flags a file | Sensitive path/data or suspicious literal | Review it privately; stop publication until explained/fixed, then rescan |

Virtual NIC offloading can produce apparent bad checksums at a passive capture
point. Confirm this with counters first. If necessary, from a **lab guest console**
use `ethtool -k <LAB_INTERFACE>` to inspect settings and manually disable the
relevant offload features only on the private NIC. Do not globally disable
checksum validation to conceal dropped packets; record the change and verify a
single HTTP marker afterward. Install ethtool during an update window if needed.

## Inspect existing monitoring containers

`start-stack.sh` derives `CYBERLAB_LOG_GID` and `CYBERLAB_GRAFANA_ROOT_URL` from the
guest group and shared config, then passes them to Compose with `sudo env`.
They are not persisted in your shell. A later bare Compose command still parses
the file and fails unless both variables are supplied. This error does not
establish whether an existing container is healthy.

These local read-only commands inspect the existing deployment without Compose
interpolation or exposing environment/secret files:

```bash
bash scripts/monitoring/start-stack.sh --confirm-lab-guest ps
bash scripts/monitoring/start-stack.sh --confirm-lab-guest logs
sudo docker ps -a --filter label=com.docker.compose.project=cyberlab-monitoring
sudo docker inspect cyberlab-monitoring-alloy-1 \
  --format 'status={{.State.Status}} exit={{.State.ExitCode}} oom={{.State.OOMKilled}}'
sudo docker logs --tail 60 cyberlab-monitoring-alloy-1
```

Look for exited/restarting state and the exact collector error before changing
its memory limit, permissions or configuration. `OOMKilled=true` identifies an
observed container OOM; a guest kernel soft lockup does not establish an OOM.
Keep actual logs private and share only the diagnostic lines needed for review.

For repeated guest soft lockups, inspect `uptime`, `free -h`, `nproc` and
`sudo journalctl -k -b --no-pager | tail -n 80`. Review host CPU/memory pressure,
VMware vCPU allocation and the private `vmware.log` beside the VM configuration.
An isolated watchdog message does not identify the cause. Reduce simultaneous
guest workload, install current guest updates during an update window, then
repeat one marker. Record whether the issue recurs. Do not hide it by disabling
kernel watchdogs or Windows security features.

If a snapshot restores an old clock, correct time during a controlled update
window, disconnect NAT again and repeat preflight. Do not loosen Loki's age
limits merely to make old synthetic fixtures appear as fresh observations.

Package/image downloads require temporary guest Internet access. Stop exercises
before enabling NAT; keep the lab private adapter unchanged, update, disconnect
NAT, then revalidate. No troubleshooting step requires Windows ICS, bridged
networking, disabling host security software or exposing Loki to the host/LAN.
