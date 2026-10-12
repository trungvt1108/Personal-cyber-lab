# Screenshots for a reviewed portfolio

No real screenshots are added automatically. `docs/screenshots/` is ignored
except its empty placeholder. Capture only after actual VM checks; a dashboard
image must represent observed lab events. Do not fabricate activity or metrics.

Recommended captures:

1. VMware Workstation Pro adapter settings: shared LAN Segment name and disconnected NAT adapters,
   with real MACs, storage paths and host/user details cropped out.
2. Architecture Mermaid diagram rendered from source documentation.
3. Kali preflight/dry-run/diagnostics with only generic lab identifiers visible.
4. An observed harmless URL marker, EVE SID and source/destination within the lab.
5. Grafana SOC overview with a narrow event window and expanded alert evidence.
6. SSH/HTTP correlation timeline or a rewritten synthetic incident summary.
7. Offline tests/static checks, clearly labelled separately from live results.

Before sharing, inspect every pixel for real usernames, email, filesystem paths,
public IPs, hostnames, MACs, Wi-Fi names, keys/tokens, terminal history, browser
tabs/bookmarks, notifications, account IDs or serial numbers. Close personal apps,
use generic lab accounts and crop the view before taking a screenshot. Redact
carefully and review again; metadata can also disclose information.

After your manual review, explicitly stage only the approved image files and
update the publication checklist/audit. An ignored image is not permission to
force-add it blindly. This project provides dashboard code so images are optional.
