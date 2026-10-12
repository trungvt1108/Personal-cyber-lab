"""Create monitor-only private runtime directories and secrets; never print values."""

from __future__ import annotations

import argparse
import getpass
import os
import platform
import secrets
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from cyberlab.config import ROOT, load_config  # noqa: E402
from cyberlab.network import check_guest  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirm-lab-guest", action="store_true")
    args = parser.parse_args()
    if not args.confirm_lab_guest or platform.system() != "Linux" or os.geteuid() != 0:
        parser.error("run with sudo inside the monitor VM and --confirm-lab-guest")
    config = load_config()
    check_guest(config, "monitor")
    base = ROOT / "local"
    for relative in (".", "runtime", "runtime/grafana", "runtime/loki", "runtime/alloy"):
        directory = base / relative
        if directory.is_symlink() or (directory.exists() and not directory.is_dir()):
            parser.error("runtime paths must be ordinary directories, not links")
        directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    for name, uid in (("grafana", 472), ("loki", 10001), ("alloy", 10002)):
        directory = base / "runtime" / name
        os.chown(directory, uid, uid)
        directory.chmod(0o750)
    for name in ("grafana-admin-password", "grafana-security-key"):
        destination = base / name
        if destination.is_symlink():
            parser.error("secret paths must not be links")
        if destination.exists():
            if not destination.is_file() or destination.stat().st_size < 16:
                parser.error("existing secret must be a valid ordinary file")
            os.chown(destination, 472, 472)
            destination.chmod(0o600)
            continue
        if name == "grafana-admin-password":
            if not sys.stdin.isatty():
                parser.error("an interactive terminal is required to create the password")
            value = getpass.getpass("Unique lab Grafana password (16+ characters): ")
            if not 16 <= len(value) <= 128 or value in ("CHANGE_ME", "PLACEHOLDER"):
                parser.error("choose a unique password with 16 through 128 characters")
            if getpass.getpass("Repeat the entry: ") != value:
                parser.error("passwords do not match")
        else:
            value = secrets.token_urlsafe(48)
        fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as secret_file:
            secret_file.write(value)
        os.chown(destination, 472, 472)
    print("Private monitor runtime prepared. No credential values displayed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
