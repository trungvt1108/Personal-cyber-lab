"""Offline repository consistency checks using the exact Git candidate file list."""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cyberlab.config import load_config  # noqa: E402


def candidate_files() -> list[Path]:
    """List tracked and untracked nonignored files; never stage anything."""
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    return sorted({ROOT / name.decode("utf-8") for name in result.stdout.split(b"\0") if name})


def check_links(path: Path) -> list[str]:
    failures = []
    for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
        target = link.split("#", 1)[0].strip("<>")
        if not target or re.match(r"[a-zA-Z]+:", target):
            continue
        if not (path.parent / target).exists():
            failures.append(f"{path.relative_to(ROOT).as_posix()}: missing link {target}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-links", action="store_true", help="intermediate phases only")
    parser.add_argument(
        "--manifest", action="store_true", help="write the exact candidate manifest"
    )
    args = parser.parse_args()
    failures = []
    load_config()
    files = candidate_files()
    for path in files:
        relative = path.relative_to(ROOT).as_posix()
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(ROOT):
            failures.append(f"{relative}: not a regular file")
            continue
        try:
            if path.suffix == ".py":
                ast.parse(path.read_text(encoding="utf-8"))
            elif path.suffix in (".yml", ".yaml"):
                yaml.safe_load(path.read_text(encoding="utf-8"))
            elif path.suffix == ".json":
                json.loads(path.read_text(encoding="utf-8"))
            elif path.suffix == ".toml":
                tomllib.loads(path.read_text(encoding="utf-8"))
            elif path.suffix == ".ndjson":
                for line in path.read_text(encoding="utf-8").splitlines():
                    record = json.loads(line)
                    if record.get("synthetic") is not True:
                        failures.append(f"{relative}: example record lacks synthetic label")
            elif path.suffix == ".md" and not args.skip_links:
                failures.extend(check_links(path))
        except (ValueError, SyntaxError, UnicodeError, yaml.YAMLError) as exc:
            failures.append(f"{relative}: syntax/parsing error ({type(exc).__name__})")
    for line in (ROOT / ".env.example").read_text(encoding="utf-8").splitlines():
        if (
            line
            and not line.startswith("#")
            and line.partition("=")[2] not in {"CHANGE_ME", "PLACEHOLDER", "example", "dummy"}
        ):
            failures.append(".env.example: only explicit placeholder values are allowed")
    protected = [
        ".env",
        ".env.production",
        "id_ed25519",
        "id_ed25519.pub",
        "local/secret",
        "logs/auth.log",
        "captures/lab.pcap",
        "reports/private/report.html",
        "known_hosts",
        "dump.sqlite3",
        "docs/screenshots/private.png",
        "LAB-MONITOR.vmx",
        "LAB-MONITOR.nvram",
        "LAB-MONITOR.vmem",
        ".aws/settings.json",
        ".codex/settings.json",
    ]
    result = subprocess.run(
        ["git", "check-ignore", "--stdin", "-z"],
        input=("\0".join(protected) + "\0").encode("utf-8"),
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    ignored = {name.decode("utf-8") for name in result.stdout.split(b"\0") if name}
    failures.extend(
        f"privacy exclusion missing: {path}" for path in protected if path not in ignored
    )
    names = {path.relative_to(ROOT).as_posix() for path in files}
    names.add("PUBLICATION_FILES.txt")
    manifest = ROOT / "PUBLICATION_FILES.txt"
    if args.manifest:
        manifest.write_text("\n".join(sorted(names)) + "\n", encoding="utf-8")
    elif not manifest.is_file() or manifest.read_text(encoding="utf-8").splitlines() != sorted(
        names
    ):
        failures.append("PUBLICATION_FILES.txt: stale manifest; run check_repository.py --manifest")
    for failure in failures:
        print(f"[FAIL] {failure}")
    if failures:
        return 1
    print(
        f"[PASS] {len(files)} Git candidate files checked; configuration, syntax and privacy exclusions valid"
    )
    if args.skip_links:
        print("[PENDING] Markdown links excluded for this intermediate phase")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
