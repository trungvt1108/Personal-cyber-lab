#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
if [[ $# -ne 1 || ! "$1" =~ ^(kali|target|monitor)$ ]]; then
  printf 'Usage: bash scripts/linux/configure-network.sh kali|target|monitor\n' >&2
  exit 2
fi
cd -- "$repo_root"
python3 cyberlab.py render-network "$1"
printf 'Review the generated file and interface names at the guest console.\n'
printf 'Ubuntu: manually install it with mode 600, then use sudo netplan try.\n'
printf 'Kali: use the NetworkManager commands in docs/installation.md.\n'
