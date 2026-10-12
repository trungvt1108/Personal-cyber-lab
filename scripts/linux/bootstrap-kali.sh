#!/usr/bin/env bash
set -euo pipefail
if [[ "$(uname -s)" != Linux ]]; then
  printf 'ABORT: run only inside the Kali lab guest.\n' >&2
  exit 1
fi
if [[ "${1:-}" != --confirm-lab-guest ]]; then
  printf 'This installs guest packages during a temporary NAT update window.\n'
  printf 'Run from the Kali VM console with --confirm-lab-guest.\n' >&2
  exit 2
fi
if [[ "$(systemd-detect-virt --vm)" != vmware ]]; then
  printf 'ABORT: VMware virtualization was not detected.\n' >&2
  exit 1
fi
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-yaml ansible openssh-client iproute2 iputils-ping
printf 'Packages installed. Enroll SSH keys, deploy guests, then disconnect NAT.\n'
