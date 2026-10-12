# Publication checklist — owner review required

Review the **exact** candidate manifest and staged files before making the repo
public. Check marks below describe this source snapshot only; changing files,
adding screenshots, staging or committing requires the affected checks again.
The final approval belongs to the owner. Do not push automatically.

- [x] No real password in public source
- [x] No API key
- [x] No access/refresh/authentication token
- [x] No private key or personal SSH public key
- [x] No personal email
- [x] No personal username in source/config
- [x] No real hostname; configured names are LAB-KALI/TARGET/MONITOR
- [x] No real public IP; rejected documentation addresses appear only in tests
- [x] No real MAC address
- [x] No Wi-Fi information
- [x] No personal filesystem path
- [x] No real logs; fixtures are labelled synthetic
- [x] No PCAP/PCAPNG
- [x] No real screenshots included
- [x] No database dump or real database
- [x] No sensitive public report; example is explicitly synthetic
- [x] `.gitignore` reviewed and dummy protected paths checked
- [ ] Git tracked/staged files reviewed after explicit staging (currently none)
- [x] Public source secret scan completed; see audit for measured scope
- [x] Initial Git history reviewed: no commits, history scan not applicable yet
- [ ] Recheck first commit metadata/history with a redacted history secret scan
- [x] Simulation code limited to configured lab network and bounded operations
- [x] Python dependency package advisories reviewed for the recorded snapshot
- [ ] Container digests/advisories and installed guest packages reviewed locally
- [x] Source security review completed; residual risks documented
- [ ] Actual VM topology, firewall and SSH settings manually reviewed
- [ ] Guest service/configuration and end-to-end detection checks completed
- [ ] Any later screenshots/log-derived narrative sanitized and manually approved
- [ ] GitHub Actions reviewed by owner, including dependency/action pins
- [ ] Owner approves publication of the exact staged snapshot

`.gitignore` cannot protect already tracked files. Use `git ls-files` and
`git diff --cached --name-only` after staging explicit reviewed filenames. Scan
history after the first commit and every history rewrite. An exposed secret
requires revoke/rotate, history cleanup and rescanning before publication.

No screenshots are required for publishing source; if added later, review their
content/metadata separately. Keep logs, keys and runtime files ignored permanently.
