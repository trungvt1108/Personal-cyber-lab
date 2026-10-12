# Central logs and local collection

Target rsyslog keeps `/var/log/auth.log` and `/var/log/syslog` locally, reads the
structured Nginx access and error files with `imfile`, then sends RFC5424 over TCP
to the configured monitor port. A bounded disk queue handles temporary outages;
TCP alone does not guarantee every message survives a crash. This is plaintext
inside an isolated lab, with source-IP restrictions rather than mutual TLS.

The monitor binds its receiver only to the private IP and discards senders whose
socket source is not the target IP. Auth, HTTP, error and system streams are
separate. `sender_ip` identifies the forwarding target, not the original SSH
client; extract the client from the SSH message. Nginx `src_ip` is the connecting
Kali address because Nginx ignores untrusted forwarded headers.

Alloy reads only these central files and EVE. It extracts event timestamps and
adds bounded `job`, `kind` and `event_type` labels; source/destination IP and URLs
remain query fields to avoid high-cardinality indexes. Reader offsets persist in
the local runtime directory. Missing timestamps fall back to ingestion time;
invalid JSON may appear as unparsed lines and should be investigated.

## Verify one hop at a time

1. Target: `sudo rsyslogd -N1` checks the complete installed configuration.
2. Target: `logger -p authpriv.notice -t cyberlab 'CYBERLAB synthetic pipeline marker'`
   creates a harmless lab-only authentication-facility event.
3. Target: verify the marker in `auth.log`; monitor: verify it in
   `/var/log/cyberlab-target/auth.jsonl` without copying the real file into Git.
4. Monitor: inspect collector container status/errors, directory mode and group
   membership. Use `sudo docker logs --tail 30 cyberlab-monitoring-alloy-1`
   locally only. See [troubleshooting.md](troubleshooting.md) for container state
   checks and the launcher's required Compose variables.

   The launcher now supports `bash scripts/monitoring/start-stack.sh
   --confirm-lab-guest ps` and the `logs`/`validate` actions. It derives the required
   variables for each command. Startup runs Alloy's configuration validator first.
5. Grafana Explore: `{job="target",kind="auth"} |= "CYBERLAB synthetic pipeline marker"`.
6. Exercise an HTTP marker and verify Nginx, EVE, Loki and dashboard independently.

Allow up to 30 seconds for forwarding, collection and dashboard refresh. Keep VM
clocks synchronized during the update window and check their UTC time before
disconnecting NAT. A snapshot may restore an old clock; out-of-window logs are
easy to miss, and Loki rejects samples older than the configured window.

Log rotation is time/size based with limited archives and private group access.
Only current files are ingested; a stopped collector can miss events after
rotation. Monitor disk space and queue size. Do not solve permissions by using
world-readable files or running Alloy as root.

All real logs, including URLs, login names and timestamps, are private. The
repository's `detection/test-events/` files are explicitly synthetic fixtures.
Suricata can retain URL query metadata, and Nginx errors can contain request
details. Send no real passwords, tokens, cookies or personal traffic in this lab.

Sources: [rsyslog omfwd](https://www.rsyslog.com/doc/configuration/modules/omfwd.html),
[JSON templates](https://www.rsyslog.com/doc/configuration/templates.html),
[Alloy file source](https://grafana.com/docs/alloy/latest/reference/components/loki/loki.source.file/).
