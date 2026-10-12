# Publication audit

Publication status: **NOT READY**

Review date: 2026-10-13. This repository contains source/templates/synthetic data;
the owner must complete manual staging, deployment and dependency reviews below.
Unverified items are **REQUIRES MANUAL REVIEW**, not automatically treated as safe.
No commit, push, remote repository creation or publication was performed.

## Secret scan

Gitleaks 8.30.1 ran against the working source tree with `.gitleaks.toml` and
`--redact`; it reported no leaks. The first sandbox run could not read two
generated pytest cache directories; the scan was repeated with access and no
skipped-directory warning. Private/development directories are excluded by
configuration and are not candidates for public staging. A separate candidate
path audit rejects protected files even if Git already tracks them.

On 2026-10-13, Gitleaks also scanned all 132 files extracted from the exported
source ZIP with default rules and no private-directory allowlist. It reported
no leaks and no skipped-directory warnings. The extraction needed a Windows
sandbox permission retry. This source-only scan excludes private data by using
the audited export, rather than relying on directory exclusions during scanning.

The custom pattern scan reported a phrase in an interactive password-repeat
prompt. The exact line was manually inspected: it contained UI prompt text, not
a credential assignment. The prompt was revised to remove the ambiguous pattern,
then the source scan was repeated. Real/suspected credential values would require
owner notification and revocation before publication; none was found here.

## Personal information scan

Candidate text was checked for personal emails, home-directory paths, MACs and
suspicious literal credentials. Public config uses generic lab hostnames/accounts.
No real identity, host settings, personal SSH material or host logs were imported.
**REQUIRES MANUAL REVIEW:** owner review of exact staged files and future commit
author metadata. Pattern scanning cannot recognize every possible identifying text.

## Network information scan

Configured addresses belong to the example `192.168.56.0/24` lab. Loopback
container/control-plane bindings and `0.0.0.0` inside the demo container are
intentional; its host publication is loopback only. Non-lab targets occur in
negative unit tests, including RFC5737 documentation addresses and a shared-space
subnet rejection case. They are never contacted. No real external host/router IP,
SSID, ISP, VPN endpoint or physical MAC is present.

## File and Git history audit

See [PUBLICATION_FILES.txt](PUBLICATION_FILES.txt) for the exact public candidate
list. It includes source, documentation, safe templates and labelled synthetic
fixtures/report only. It excludes `.venv`, `.generated`, local runtime, keys,
logs, captures, databases, unreviewed screenshots and live reports.
The final candidate manifest contains **132 files**; the path/text scan has zero
findings. Markdown links, parseable source and privacy exclusions passed the
repository consistency check. Exact measured results are in
[validation-results.md](docs/validation-results.md).

Git was initialized locally on `main`; there are **zero tracked files and no
commits** in this snapshot. Therefore history scanning is currently not applicable.
Candidate review is not staged-file review. **REQUIRES MANUAL REVIEW:** explicitly
stage reviewed files, inspect their diff, configure nonidentifying commit metadata,
then run Gitleaks history scanning after the first commit. No `git add .` was used.

## Dependency audit

pip-audit 2.10.0 queried the pinned 48-package development environment and reported
no known vulnerabilities; the pinned lock was rescanned on 2026-10-13 with the
same result. The audit is limited to published Python package
advisories, not CPython/OS/image vulnerabilities. The lock records versions without
hashes; advisory output recommends hash-based locks for stronger integrity.

Upstream releases were checked and initial image pins updated to Python 3.12.15,
Loki 3.7.8, Alloy v1.20.1 and Grafana 13.2.3. The Python image tag appears in the
official image manifest. **REQUIRES MANUAL REVIEW:** actual image digests/security
scan, guest package updates, configuration compatibility and deployment.
The existing Windows Python interpreter was used for offline tests only and not
upgraded. Details and sources: [dependencies.md](docs/dependencies.md).

## Simulation safety audit

Live operations require detected VMware Workstation Pro/Linux, explicit confirmation, assigned
source IP, a direct private-interface route, no IPv4/IPv6 default route and an
explicit configured guest/port allowlist. Simulations target only the target VM,
refuse domains, redirects and proxy environment behavior, and bound counts,
intervals and timeouts. SSH offers no password/key/authentication method and
uses strict pre-enrolled host key verification for an absent generic user.
The VMware review additionally requires the configured prefix, validates the
controller before guest fact gathering even with `--limit`, and rejects differing
configuration copies. Monitor acceptance requires fresh actual evidence from
the expected addresses, all three Loki streams and running stack containers.
Source ZIP export rejects protected candidate paths including VMware state;
the target build context allows only its Dockerfile and demo Python module.
Ubuntu SSH socket activation is disabled in the guest role and its distribution
migration overrides removed; the ordinary SSH service binds the validated lab
address and waits for network-online. Operator screenshots now show the monitor
syslog listener after reboot and a passing marker/ingestion validator after the
capture-filter fix. Final source sync and full Ansible execution/idempotence
remain separate checks.

Regression tests cover the safety gates, malformed input, no-network dry-runs,
HTTP redirect refusal, parser scope and report escaping/path restrictions. No
live simulation was run on Windows or GitHub infrastructure. **REQUIRES MANUAL
REVIEW:** VMware Workstation Pro adapters, guest routes, source identity and live evidence.

## GitHub Actions audit

The workflow uses read-only repository permissions, disables persisted checkout
credentials, avoids `pull_request_target`, creates no services, executes no live
exercise, prints no environment/credential dump and uploads no artifacts. Tests
always skip live fixtures when `GITHUB_ACTIONS` is set. Gitleaks uses redacted
output. Dashboard/Compose checks only validate source/configuration.

Checkout and setup-python use full commit SHAs resolved from their official v6
references on the review date. Dependabot proposes updates for review.
**REQUIRES MANUAL REVIEW:** owner review of the workflow and future action updates.
Hosted CI has not actually run; its status is pending.

## Remaining risks and release decision

Private plaintext HTTP/syslog, educational thresholds, possible capture/rotation
gaps, small VM resource budgets and dependency supply-chain uncertainty remain
documented in [SECURITY.md](SECURITY.md) and the threat model. Operator-observed
guest results and their limits are recorded in
[validation-results.md](docs/validation-results.md); raw evidence remains private.
Source checks do not prove network isolation.

Complete [PUBLICATION_CHECKLIST.md](PUBLICATION_CHECKLIST.md), record measured live
results and review the staged snapshot. Keep status NOT READY until unresolved
checks are explained and approved; push is a separate manual owner action.
