"""Run inside the monitor after target logger and Kali URL marker exercises."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from cyberlab.config import ConfigError, load_config  # noqa: E402
from cyberlab.validation import validate_monitor  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirm-isolated", action="store_true")
    args = parser.parse_args()
    try:
        checks = validate_monitor(load_config(), confirmed=args.confirm_isolated)
    except ConfigError as exc:
        print(f"[ABORT] {exc}", file=sys.stderr)
        return 2
    for check in checks:
        print(f"[{check['status']}] {check['name']}")
    return int(any(check["status"] == "FAIL" for check in checks))


if __name__ == "__main__":
    raise SystemExit(main())
