# Public repository tree

The tree below lists public source candidates only. Private development tools,
runtime secrets, real logs and captures are excluded. The exact file manifest is
[PUBLICATION_FILES.txt](../PUBLICATION_FILES.txt).

```text
personal-cyber-lab/
├── .github/
│   ├── workflows/
│   │   └── ci.yml
│   └── dependabot.yml
├── ansible/
│   ├── inventory/
│   │   ├── group_vars/
│   │   │   └── all.yml
│   │   └── hosts.yml
│   ├── playbooks/
│   │   └── site.yml
│   ├── roles/
│   │   ├── common/
│   │   │   ├── handlers/
│   │   │   │   └── main.yml
│   │   │   └── tasks/
│   │   │       └── main.yml
│   │   ├── kali/
│   │   │   └── tasks/
│   │   │       └── main.yml
│   │   ├── monitor/
│   │   │   ├── handlers/
│   │   │   │   └── main.yml
│   │   │   └── tasks/
│   │   │       ├── logging.yml
│   │   │       ├── main.yml
│   │   │       └── suricata.yml
│   │   └── target/
│   │       ├── handlers/
│   │       │   └── main.yml
│   │       └── tasks/
│   │           ├── logging.yml
│   │           └── main.yml
│   ├── tasks/
│   │   └── controller-preflight.yml
│   └── ansible.cfg
├── config/
│   └── lab.yml
├── configs/
│   ├── firewall/
│   │   └── README.md
│   ├── kali/
│   │   └── README.md
│   ├── monitor/
│   │   ├── logrotate.conf
│   │   ├── nginx.conf.j2
│   │   ├── rsyslog-network.conf.j2
│   │   └── rsyslog-receive.conf.j2
│   ├── ssh/
│   │   └── 00-cyberlab.conf.j2
│   └── target/
│       ├── logrotate.conf
│       ├── nginx.conf.j2
│       └── rsyslog-forward.conf.j2
├── cyberlab/
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── demo.py
│   ├── monitoring.py
│   ├── network.py
│   ├── reporting.py
│   ├── services.py
│   ├── simulations.py
│   └── validation.py
├── dashboards/
│   └── grafana/
│       ├── provisioning/
│       │   ├── dashboards/
│       │   │   └── lab.yml
│       │   └── datasources/
│       │       └── loki.yml
│       ├── README.md
│       └── cyberlab.json
├── detection/
│   ├── rules/
│   │   ├── README.md
│   │   └── local.rules.j2
│   ├── suricata/
│   │   ├── cyberlab-suricata.service
│   │   └── suricata.yaml.j2
│   └── test-events/
│       ├── README.md
│       ├── auth.ndjson
│       ├── eve.ndjson
│       └── http.ndjson
├── docker/
│   ├── monitoring/
│   │   ├── README.md
│   │   ├── compose.yml
│   │   ├── config.alloy
│   │   └── loki.yml
│   └── target/
│       ├── Dockerfile
│       └── compose.yml
├── docs/
│   ├── screenshots/
│   │   └── .gitkeep
│   ├── architecture.md
│   ├── attack-scenarios.md
│   ├── cli.md
│   ├── demo.vi.md
│   ├── dependencies.md
│   ├── detection-guide.md
│   ├── finalize.vi.md
│   ├── handoff.vi.md
│   ├── implementation-plan.md
│   ├── incident-response.md
│   ├── installation.md
│   ├── logging.md
│   ├── network-design.md
│   ├── repository-tree.md
│   ├── screenshots.md
│   ├── testing.md
│   ├── threat-model.md
│   ├── troubleshooting.md
│   ├── validation-results.md
│   └── vmware.vi.md
├── reports/
│   ├── examples/
│   │   └── synthetic-report.html
│   └── templates/
│       └── incident-report.md
├── scripts/
│   ├── linux/
│   │   ├── bootstrap-kali.sh
│   │   └── configure-network.sh
│   ├── monitoring/
│   │   ├── initialize-runtime.py
│   │   ├── start-stack.sh
│   │   └── validate-local.py
│   ├── simulations/
│   │   └── run.sh
│   ├── windows/
│   │   ├── check-prerequisites.ps1
│   │   └── show-network-plan.ps1
│   ├── build-dashboard.py
│   ├── check_repository.py
│   ├── export-source.py
│   ├── lint_markdown.py
│   ├── publication_audit.py
│   └── validate-lab.sh
├── tests/
│   ├── detection/
│   │   ├── test_dashboard.py
│   │   ├── test_live_monitor.py
│   │   ├── test_monitoring.py
│   │   ├── test_pipeline_config.py
│   │   └── test_rules.py
│   ├── network/
│   │   └── test_live_network.py
│   ├── security/
│   │   ├── test_ci_and_containers.py
│   │   ├── test_config.py
│   │   ├── test_deployment.py
│   │   ├── test_network_safety.py
│   │   ├── test_publication.py
│   │   ├── test_reporting.py
│   │   ├── test_simulations.py
│   │   └── test_validation.py
│   ├── services/
│   │   ├── test_demo.py
│   │   └── test_live_services.py
│   ├── conftest.py
│   └── test_cli.py
├── .dockerignore
├── .editorconfig
├── .env.example
├── .gitattributes
├── .gitignore
├── .gitleaks.toml
├── .markdownlint.json
├── .pymarkdown.json
├── .yamllint.yml
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── PUBLICATION_AUDIT.md
├── PUBLICATION_CHECKLIST.md
├── PUBLICATION_FILES.txt
├── README.md
├── README.vi.md
├── SECURITY.md
├── cyberlab.py
├── pyproject.toml
└── requirements-dev.lock
```
