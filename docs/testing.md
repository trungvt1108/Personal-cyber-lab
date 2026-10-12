# Testing and evidence boundaries

Offline unit tests validate the safety controls, parser, report escaping, demo
responses, CLI dry-runs, template scope and dashboard structure. They mock all
network operations and never start a service. Static validation cannot establish
that a VM exists, packets reach Suricata or Loki receives logs.

## Local checks

From the repository root after installing `.[dev]`:

```bash
python -m pytest
python -m ruff check .
python -m ruff format --check .
python -m yamllint .
python scripts/check_repository.py
shellcheck scripts/linux/*.sh scripts/simulations/*.sh scripts/monitoring/*.sh scripts/*.sh
python scripts/lint_markdown.py
```

ShellCheck and PyMarkdown are development tools, not guest runtime dependencies.
On Windows, PowerShell can syntax-parse `.ps1` files without running them; use
the Git Bash `-n` flag only for Bash syntax validation. `bash -n` does not perform
ShellCheck's semantic analysis. Review the measured results in
[validation-results.md](validation-results.md).

## Explicit VM tests

Create the lab, disconnect NAT and disable Shared Folders, clipboard and
drag-and-drop on every VM first. Complete file transfer before testing. Run the
diagnostic wrapper from Kali:

```bash
bash scripts/validate-lab.sh --confirm-isolated
python3 -m pytest tests/network tests/services/test_live_services.py \
  --run-lab --confirm-isolated --lab-role kali
```

Then generate a target logger marker and Kali URL marker as documented in the
detection guide. On monitor, within ten minutes of those exercises:

```bash
sudo python3 scripts/monitoring/validate-local.py --confirm-isolated
sudo python3 -m pytest tests/detection/test_live_monitor.py \
  --run-lab --confirm-isolated --lab-role monitor
```

Install pytest in a guest venv if needed and use the venv's interpreter rather
than installing into Ubuntu's managed system Python. `sudo` is used only when
the evidence/secret permissions require it; a limited local read account may
run the evidence checks instead. Do not loosen secrets to make tests pass.

Six live test cases are skipped by default with
`SKIPPED - requires running cyber lab.` There are two ICMP cases, one guest service
case and three monitor evidence/ingestion cases. `GITHUB_ACTIONS` always disables
live fixtures even if someone adds live switches to CI accidentally.

Before guest service startup, Ansible also runs `sshd -t`, `rsyslogd -N1` and
`suricata -T` on the installed configuration. Run `sudo nginx -t` for both sites
and inspect firewall rules/container publications. Operator-observed guest results
and checks that remain pending are recorded in [validation-results.md](validation-results.md).
