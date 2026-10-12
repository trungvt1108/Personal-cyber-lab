# Dependencies, provenance and review

Runtime Python dependency: PyYAML 6.0.3 for safely loading the shared configuration.
Network, HTTP, logging, reporting and argparse use the standard library. No web
framework, external telemetry SDK or password-guessing library is needed.

Development tools are optional `.[dev]`: pytest, Ruff, yamllint, Jinja2 (template
checks), pip-audit and PyMarkdown. `requirements-dev.lock` records the measured
development environment as names/versions only; it contains no editable local
paths. It is a version snapshot, not a hash-verified supply-chain attestation.
PyMarkdown's parser dependencies are development-only; do not install them in
the target demo container. See [PyPI](https://pypi.org/) for release metadata.

## Image pins reviewed against upstream releases

| Component | Pin | Upstream reference |
| --- | --- | --- |
| Target Python base | 3.12.15-slim-bookworm | [Python security release](https://www.python.org/downloads/release/python-31215/) / [official image tags](https://github.com/docker-library/official-images/blob/master/library/python) |
| Grafana | 13.2.3 | [Official release](https://github.com/grafana/grafana/releases/tag/v13.2.3) |
| Loki | 3.7.8 | [Official release](https://github.com/grafana/loki/releases/tag/v3.7.8) |
| Alloy | v1.20.1 | [Official releases](https://github.com/grafana/alloy/releases) |

Release metadata was reviewed on 2026-10-06. Newer Python/Loki/Alloy security
patches replaced initial older pins during review. Tags can be rebuilt/moved;
pull, inspect exact digests, review advisories and validate configuration inside
the guest before considering the deployed images verified. No container was
built or run on the Windows host for this project.

The four pinned upstream release pages were checked again on 2026-10-10; pins
were retained. The 48-package Python snapshot was reaudited with pip-audit and
reported no known vulnerabilities. Image digests and guest runtime compatibility
still require deployment checks. The stack launcher runs
[Alloy validate](https://grafana.com/docs/alloy/latest/reference/cli/validate/)
inside the monitor before starting the services.

GitHub Actions checkout and setup-python are pinned to full commit SHAs resolved
from the official [checkout v6 reference](https://api.github.com/repos/actions/checkout/git/ref/tags/v6)
and [setup-python v6 reference](https://api.github.com/repos/actions/setup-python/git/ref/tags/v6).
Dependabot may propose changes; review each update before merging.

Suricata, OpenSSH, Nginx, Docker, rsyslog and Ansible come from the guest distro
repositories during controlled update windows. Record installed package versions
privately and apply distro security updates; distro patch backports cannot be
assessed using an upstream version number alone. Keep setup tooling current.

## Review commands and limitations

```bash
python -m pip_audit -r requirements-dev.lock --disable-pip --no-deps
gitleaks dir . --config .gitleaks.toml --redact --no-banner
gitleaks git . --config .gitleaks.toml --redact --no-banner
```

The dependency audit contacts a public advisory service with package names and
versions, not lab logs/credentials. It is separate from the runtime CLI, which
has no external integration. Findings are limited to known published advisories;
no result certifies all packages or images safe. Reaudit after any version change.

Windows offline checks used the already installed Python 3.12.10 interpreter.
It was not upgraded by this project. Prefer a current supported Windows Python
release for further use; Ubuntu guests receive distro patches, and the target
container uses the reviewed 3.12.15 pin. Package audit results do not audit CPython
itself, guest kernels, Docker engine or the operating system.

Gitleaks 8.30.1 and ShellCheck 0.11.0 portable Windows tools were fetched from
their official GitHub releases and SHA256 checked against release asset digests.
They stay in ignored `.generated/tools/`, never in the public source tree.
Promtail is not used: [it reached EOL on 2026-03-02](https://grafana.com/docs/loki/latest/send-data/promtail/).
