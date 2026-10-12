#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
if [[ "$(uname -s)" != Linux || "${1:-}" != --confirm-lab-guest || $# -gt 2 ]]; then
  printf 'Usage inside VMware monitor: start-stack.sh --confirm-lab-guest [up|ps|logs|validate]\n' >&2
  exit 2
fi
cd -- "$repo_root"
if [[ -n "${CYBERLAB_CONFIG:-}" ]]; then
  printf 'Deployment uses config/lab.yml; edit that file on every VM and unset CYBERLAB_CONFIG.\n' >&2
  exit 2
fi
action="${2:-up}"
if [[ ! "$action" =~ ^(up|ps|logs|validate)$ ]]; then
  printf 'Unknown stack action.\n' >&2
  exit 2
fi
python3 cyberlab.py validate-config
python3 cyberlab.py verify-guest --source-role monitor --confirm-lab-guest
lab_mode="$(python3 -c 'from cyberlab.config import load_config; print(load_config().mode)')"
if [[ "$lab_mode" == lightweight ]]; then
  printf 'Lightweight mode: use central files and CLI reports; dashboard stack omitted.\n'
  exit 0
fi
if [[ "$action" == up ]]; then
  sudo python3 scripts/monitoring/initialize-runtime.py --confirm-lab-guest
fi
log_gid="$(getent group cyberlab-logs | cut -d: -f3)"
if [[ ! "$log_gid" =~ ^[0-9]+$ ]]; then
  printf 'Missing cyberlab-logs group; deploy the monitor role first.\n' >&2
  exit 1
fi
grafana_root_url="$(python3 -c 'from cyberlab.config import load_config; c=load_config(); print("http://{}:{}/".format(c.hosts["monitor"].ip,c.services["grafana"]))')"
compose() {
  sudo env "CYBERLAB_LOG_GID=$log_gid" "CYBERLAB_GRAFANA_ROOT_URL=$grafana_root_url" \
    docker compose -f docker/monitoring/compose.yml "$@"
}
compose config --quiet
case "$action" in
  ps) compose ps --all ;;
  logs) compose logs --tail 100 ;;
  validate) compose run --rm --no-deps alloy validate /etc/alloy/config.alloy ;;
  up)
    compose run --rm --no-deps alloy validate /etc/alloy/config.alloy
    compose up -d
    compose ps --all
    printf 'Containers launched. Validate fresh markers and Grafana before claiming success.\n'
    ;;
esac
