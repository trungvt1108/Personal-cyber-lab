#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ "${1:-}" != --confirm-isolated ]]; then
  printf 'SKIPPED - requires running cyber lab. Run inside Kali with --confirm-isolated.\n'
  exit 3
fi
cd -- "$repo_root"
python3 cyberlab.py preflight --confirm-isolated
result=0
python3 cyberlab.py check-network --confirm-isolated || result=1
python3 cyberlab.py check-services --confirm-isolated || result=1
printf '[PENDING] Packet/log/dashboard verification: run the monitor-local validator after marker exercises.\n'
printf 'See docs/detection-guide.md; service reachability alone does not prove ingestion.\n'
exit "$result"
