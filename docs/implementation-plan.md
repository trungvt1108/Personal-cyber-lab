# Implementation plan and phase checkpoints

The starting workspace was empty. No VM, Git history, personal settings or real
logs were imported. Configuration is centralized in `config/lab.yml`; Ansible
templates consume it. The default is a LAN Segment with Kali acting as the
administration workstation. The monitor captures its lab NIC; peer visibility requires measured evidence.

| Phase | Deliverables | Relevant check |
| --- | --- | --- |
| 1 | Foundation, privacy exclusions, Python packaging | TOML and YAML parsing |
| 2 | Architecture, network comparison, boundaries | Config safety validation |
| 3 | Manual VM setup, read-only host prerequisites | PowerShell syntax parsing |
| 4 | Target role, Nginx, SSH, demo container | App tests, Compose validation |
| 5 | Monitor role, restricted service bindings | Template and Compose validation |
| 6 | Suricata service, documented custom rules | Rule/config static checks; guest `suricata -T` pending |
| 7 | rsyslog forwarding/receiver, Alloy, log rotation | Template checks; guest `rsyslogd -N1` pending |
| 8 | Provisioned SOC dashboard and LogQL queries | JSON/provisioning consistency |
| 9 | Bounded ICMP/TCP/HTTP/SSH simulations | Safety regression tests and dry-run |
| 10 | Modular CLI, diagnostics, HTML reports | CLI tests, parser robustness, escaping |
| 11 | Unit/static/live checks and validation wrapper | pytest, Ruff, YAML/shell/Markdown lint |
| 12 | Security and dependency review | Secret/pattern/path scans, dependency audit |
| 13 | Bilingual workflow, detection and investigation guides | Internal links and documentation lint |
| 14 | Safe CI, publication gate, exact file manifest | Final local checks and publication audit |

Each phase is checked before the next phase; the measured outcome is recorded in
`docs/validation-results.md`. A static check never establishes guest service
health or packet visibility. All VM-dependent checks are recorded as
`SKIPPED - requires running cyber lab.` until explicitly executed in the lab.

## Software and manual work

Host: Windows 11, VMware Workstation Pro, Git, VS Code, PowerShell and Python 3.12+ for offline
checks. Guests: Kali and Ubuntu Server 24.04 LTS; Python/PyYAML, Ansible on Kali;
OpenSSH, UFW, Nginx, rsyslog, Docker/Compose and Suricata on the relevant guests.
Optional checks use Ruff, pytest, yamllint, shellcheck, markdownlint and Gitleaks.

You create VMs, confirm LAN Segment attachment, configure static interfaces
from the consoles, enroll SSH host keys, install a public SSH key, temporarily
enable updates, then disconnect NAT and take clean snapshots. Automation never
changes Windows networking or creates VMware Workstation Pro networks automatically.
