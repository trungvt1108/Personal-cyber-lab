#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
if [[ $# -eq 0 ]]; then
  printf 'Usage: run.sh ping|tcp|discover|http|ssh|urls [--dry-run|--confirm-isolated]\n' >&2
  exit 2
fi
exec python3 "$repo_root/cyberlab.py" simulate "$@"
