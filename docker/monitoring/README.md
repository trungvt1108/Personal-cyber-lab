# Local monitoring stack

Use `scripts/monitoring/start-stack.sh` inside the monitor VM after deploying its
role. Images are pinned to upstream release tags; tag pinning is not digest
verification. Resolve and review the official digests during the update window
before publication/use. Sources and review commands are in `docs/dependencies.md`.

Loki and Alloy are accessible only on an internal Docker network. Grafana's
loopback publication is reached through host Nginx, which allows Kali only.
Alloy reads only Suricata and central target-log directories; it receives the
numeric cyberlab-logs GID as a supplementary group. It has no Docker socket.

Grafana uses locally generated/entered secrets with UID 472 ownership and mode
600. Runtime data belongs to the service UID; do not recursively loosen file
permissions to solve an ingestion error. Analytics and update checks are disabled.
Use the Grafana browser on Kali. Never expose Loki directly; it has no auth layer.

The launcher supports `--confirm-lab-guest ps`, `logs` and `validate`. Each action
checks VMware/address identity and supplies the log GID and Grafana URL. Startup
validates Alloy using the pinned image before launching the stack. Container
launch is not proof of ingestion; follow the fresh-marker validator afterward.

The stack is intentionally omitted when `lab.mode` is `lightweight`. Changing
mode does not destroy existing data or automatically stop already-running
containers; stop them manually if switching an existing deployment.
