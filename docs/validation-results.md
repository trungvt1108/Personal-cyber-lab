# Measured validation results

This log distinguishes executed offline checks from guest-dependent work.
Session began 2026-10-05; VMware review continued 2026-10-10. No VM was created or
service launched on the host. All recorded sample activity is synthetic.

| Phase | Executed checkpoint | Measured result |
| --- | --- | --- |
| 1 | TOML, JSON and shared YAML parsing | PASS |
| 2 | Private subnet, allowlist, limits, duplicate/alias config cases | 25 tests PASS |
| 3 | PowerShell parser and Git Bash `-n` | PASS after sandbox permission retry |
| 4 | Pure demo endpoint tests; Compose/YAML/Jinja syntax | 10 tests PASS; config checks PASS |
| 5 | Monitor Compose/YAML/template syntax | PASS; no container started |
| 6 | Rule scope/unique SID and private capture config | 2 tests PASS; engine validation pending |
| 7 | Sender/receiver template and collector scope checks | 2 tests PASS; service validation pending |
| 8 | Dashboard JSON/datasource references | 1 test PASS; actual LogQL execution pending |
| 9 | Mocked network gates, redirect refusal, bounded plans, dry-runs | 27 tests PASS |
| 10 | CLI offline, evidence parsing, escaped/private HTML | 17 tests PASS |
| 11 | Combined offline tests at first complete checkpoint | 85 PASS / 6 SKIPPED; Ruff/YAML/ShellCheck PASS |
| 12 | Gitleaks, pattern/path scan, dependency advisories | No secret leak; prompt finding inspected/fixed; no known package vulnerability |
| 13 | Bilingual guides and internal links | Final measured results recorded below |
| 14 | CI/publication manifest and final consistency checks | Final measured results recorded below |

## Failures corrected during implementation

- Windows sandbox blocked ensurepip/pip/pytest temporary directories and Git Bash
  signal pipes. Required commands were rerun after explicit tool permission.
- The initial pytest temp path lacked its parent directory; it was created.
- The initial Git ignore diagnostic used CRLF text stdin. Git treated `\r` as
  part of filenames on Windows. NUL-delimited binary stdin fixed the false report.
- Ruff found configuration-template autoescape warnings and style issues;
  template checks were explicitly scoped to non-HTML and code was formatted.
- yamllint found one long Compose healthcheck string; it was folded safely.
- The custom publication scan flagged an interactive prompt phrase. The exact
  source was inspected, revised and rescanned. It was not a stored credential.
- Dependency release review replaced older Python/Loki/Alloy image pins and
  restricted newly created Nginx error logs to mode 640.
- A new IPv6 default-route test exposed exception wrapping that hid the explicit
  refusal reason. SafetyError now passes through unchanged; the suite was rerun.
- Grafana root URL now comes from shared config. Ubuntu's SSH socket activation
  is handled explicitly so the configured private listener takes effect; the
  guest activation transition still requires live verification.

## Original local checkpoint

Executed on 2026-10-06 using the isolated development environment on Windows:

| Check | Measured result / boundary |
| --- | --- |
| pytest | **93 passed, 6 skipped**; all live cases opt-in, no packets sent |
| Ruff check and format check | PASS; 33 Python source files formatted |
| yamllint | PASS |
| PyMarkdown | PASS; 31 public Markdown files |
| ShellCheck 0.11.0 | PASS for all 5 Bash scripts |
| PowerShell parser | PASS for 2 scripts; no host setup script executed |
| Guest template rendering | PASS; 8 strict render checks including both SSH roles; service engines untested |
| Docker Compose config | PASS for target and monitor; no build/pull/start |
| Dashboard reproducibility | Generated JSON identical byte for byte; no Grafana query executed |
| Repository consistency | PASS; 124 public candidates, source parsing, relative links and privacy exclusions |
| Candidate path/text scan | PASS; zero findings, zero tracked files, no commits |
| Gitleaks 8.30.1 working tree | No leaks found; redacted scan, private/development exclusions documented |
| pip-audit 2.10.0 | No known vulnerabilities in the unchanged pinned 48-package snapshot |

Commands and limitations: [testing.md](testing.md),
[dependencies.md](dependencies.md) and [PUBLICATION_AUDIT.md](../PUBLICATION_AUDIT.md).
The workflow has full SHA pins for both official Actions. Publication remains
**NOT READY** pending the owner review and guest/deployment checks.

## VMware review on 2026-10-10

The complete 129-file public source candidate set was reviewed, including CLI,
Ansible, networking, service templates, containers, dashboard generator, fixtures,
tests, CI, documentation and publication controls. Private development/runtime
artifacts were excluded from the source review and archive.

Corrections: VMware detection and LAN Segment guidance, actual NIC examples,
guarded guest installation checks, Ansible prechecks before connections even with
`--limit`, identical controller/guest configs, non-root Suricata validation and
preserved EVE ownership, launcher diagnostics/Alloy validation, stricter fresh
EVE/auth/HTTP evidence, stopped-container detection, HTTP Loki queries, lightweight
service checks, report exit codes, bounded config reads, malformed demo URLs,
private VMware state exclusions, narrow Docker build context and scanned export.

| Check | Measured result / boundary |
| --- | --- |
| pytest | **129 passed, 6 skipped**; no live guest traffic |
| Ruff check and format | PASS; 36 public Python files |
| yamllint and PyMarkdown | PASS; 32 public Markdown files |
| ShellCheck and PowerShell syntax | PASS; 5 Bash / 2 PowerShell scripts |
| Compose syntax / strict Jinja rendering | PASS; both stacks / 8 render checks; no engines started |
| Dashboard generator | PASS; JSON reproduced byte for byte |
| Repository and publication scan | PASS; 129 candidates, current manifest, no path/text findings |
| Gitleaks working-tree scan | PASS; no leaks reported, redacted output |
| pip-audit on 48 pinned packages | No known vulnerabilities reported on review date |
| Source ZIP | Exported scanned candidate source; VMware/private state excluded |
| Prior-platform references | None in the public source candidate set |

Pytest initially hit Windows sandbox temporary-directory permissions and was
rerun with tool approval. Two new report tests initially patched their config
root unintentionally; fixtures were corrected and the full suite rerun. These
were offline test setup failures. The tests for new safety checks exercise mocked
network/container state; Ansible guard tests inspect task ordering, not execution.

At that checkpoint, VMware guest NICs, peer packet visibility, service startup/idempotence and
the event-to-dashboard path remain unverified for this updated source. Instructions
for applying it to existing VMs are in [vmware.vi.md](vmware.vi.md).

## VM/service checks pending at the 2026-10-10 checkpoint

**SKIPPED - requires running cyber lab.**

- Private adapter/IP reachability and live guest service health.
- Ansible execution/idempotence and installed `sshd -t`, `nginx -t`, `rsyslogd -N1`.
- Installed Suricata `-T`, capture privileges, packet visibility and real rule matches.
- Syslog transport, fresh central markers, Alloy file permissions/offsets and log rotation.
- Container build/start/readiness, Grafana secret readability and actual LogQL queries.
- Full marker → EVE/host log → Loki → dashboard → incident-report workflow.

CI source has been reviewed locally; no hosted GitHub workflow has been executed.
Image tags were reviewed, but deployment digests, image advisories and guest
package state remain unverified. Do not convert pending entries into PASS without
running the corresponding check and preserving evidence privately.

## Source closure on 2026-10-13

Windows checks were repeated after the runtime fixes, handler corrections and
IPv4 capture filter were included in source. This source revision has not yet
been synchronized to all guests. No host service was started for these checks.

| Check | Measured result / boundary |
| --- | --- |
| pytest | **129 passed, 6 skipped**; six guest tests remain opt-in |
| Ruff check and format | PASS; 36 public Python files |
| yamllint and PyMarkdown | PASS; 34 public Markdown files |
| ShellCheck and PowerShell parser | PASS; 5 Bash / 2 PowerShell scripts |
| Compose configuration | PASS; target and monitoring, no build/pull/start |
| Strict template rendering | PASS; 9 guest render checks, no engine started |
| Dashboard reproduction | PASS; generated JSON identical byte for byte |
| Repository / candidate publication scan | PASS; 132 files, zero findings |
| Python advisory scan | No known vulnerabilities reported for the pinned lock |
| Source ZIP | 132 entries matched the current source byte for byte |
| Gitleaks on exported source | No leaks found; all public files scanned without directory exclusions |

The final pytest rerun first encountered a Windows sandbox temporary-directory
permission error. It was repeated with tool approval and completed with the
result above; the failure was environmental. The dependency lock still has
version pins without hashes, so advisory scanning does not establish integrity.

The operator supplied guest screenshots separately: Kali baseline checks passed,
the monitor syslog listener was present after reboot, and Suricata accepted the
installed configuration. After applying the IPv4 filter and preserving the old
EVE file, the monitor validator reported all 15 checks PASS, including fresh
central markers and Loki ingestion. Discover/HTTP exercises had corresponding
Explore evidence. These are operator-observed checks of the existing deployment;
their logs, screenshots and hashes stay private.

Full Ansible execution/idempotence for this final source, another complete reboot
after the capture-filter change, image/guest advisory review and hosted GitHub CI
have not been established by those screenshots. The six live pytest cases were
not run by the Windows test suite. Follow [finalize.vi.md](finalize.vi.md) to sync
source, validate the guests and save a local Git version.
