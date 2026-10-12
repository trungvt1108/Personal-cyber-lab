"""Scan public candidate paths/text without printing possible secret values."""

from __future__ import annotations

import fnmatch
import ipaddress
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.check_repository import candidate_files  # noqa: E402

DOCUMENTATION_NETS = tuple(
    ipaddress.ip_network(value) for value in ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24")
)
PROTECTED_PARTS = {
    "local",
    "logs",
    "captures",
    "secrets",
    "credentials",
    ".venv",
    ".aws",
    ".ssh",
    ".generated",
    ".git",
    ".agents",
    ".codex",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
}
PROTECTED_NAMES = (
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
    "*.pub",
    "*.p12",
    "*.pfx",
    "id_rsa*",
    "id_ed25519*",
    "known_hosts*",
    "authorized_keys*",
    "*.pcap",
    "*.pcapng",
    "*.log",
    "*.jsonl",
    "*.db",
    "*.sqlite*",
    "*.dump",
    "*.sql",
    "*.png",
    "*.jpg",
    "*.jpeg",
    "*.vmx",
    "*.vmxf",
    "*.vmdk",
    "*.nvram",
    "*.vmsd",
    "*.vmsn",
    "*.vmem",
    "*.vmss",
    "*.vmtm",
    "*.vmpl",
    "*.ova",
    "*.iso",
)


def scan_file(path: Path) -> list[dict[str, object]]:
    """Classify suspicious patterns; require review rather than guessing safety."""
    relative = path.relative_to(ROOT).as_posix()
    findings = []
    if path.is_symlink() or not path.resolve().is_relative_to(ROOT):
        return [{"file": relative, "line": 0, "category": "unsafe public link"}]
    parts = set(path.relative_to(ROOT).parts)
    if (
        parts & PROTECTED_PARTS
        or (relative.startswith("reports/private/"))
        or (
            path.name != ".env.example"
            and any(fnmatch.fnmatch(path.name, pattern) for pattern in PROTECTED_NAMES)
        )
    ):
        findings.append({"file": relative, "line": 0, "category": "sensitive public path"})
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return findings + [
            {"file": relative, "line": 0, "category": "requires manual binary/file review"}
        ]
    if (
        relative.startswith("reports/examples/")
        and path.suffix == ".html"
        and "SYNTHETIC EXAMPLE" not in text
    ):
        findings.append({"file": relative, "line": 0, "category": "unlabelled public report"})
    patterns = (
        ("private key material", r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"),
        ("personal email", r"\b[A-Za-z0-9_.+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
        ("MAC address", r"\b(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\b"),
        ("personal Windows path", r"[A-Za-z]:\\Users\\(?!student(?:\\|\b)|<)[^\\\s<]+"),
        (
            "personal Unix path",
            r"/(?:home|Users)/(?!labuser(?:/|\b)|student(?:/|\b)|<)[A-Za-z0-9_.-]+",
        ),
    )
    for number, line in enumerate(text.splitlines(), start=1):
        for category, expression in patterns:
            if re.search(expression, line):
                findings.append({"file": relative, "line": number, "category": category})
        for match in re.finditer(
            r"\b(?:password|passwd|secret|token|api_key|apikey)\s*[:=]\s*['\"]([^'\"\r\n]+)",
            line,
            re.IGNORECASE,
        ):
            value = match.group(1)
            if value not in {"CHANGE_ME", "PLACEHOLDER", "example", "dummy"}:
                findings.append(
                    {
                        "file": relative,
                        "line": number,
                        "category": "possible literal credential; review required",
                    }
                )
        for match in re.finditer(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])", line):
            try:
                address = ipaddress.ip_address(match.group())
            except ValueError:
                continue
            approved = (
                address.is_private
                or address.is_loopback
                or address.is_unspecified
                or any(address in net for net in DOCUMENTATION_NETS)
            )
            if not approved and relative != "tests/security/test_config.py":
                findings.append(
                    {"file": relative, "line": number, "category": "non-example network address"}
                )
    return findings


def main() -> int:
    files = candidate_files()
    findings = [finding for path in files for finding in scan_file(path)]
    tracked = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True)
    history = subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD"], cwd=ROOT, capture_output=True, check=False
    )
    result = {
        "source_scan": "PASS" if not findings else "REQUIRES MANUAL REVIEW",
        "candidate_count": len(files),
        "tracked_count": len([name for name in tracked.stdout.split(b"\0") if name]),
        "history": "EXISTS: run gitleaks git"
        if history.returncode == 0
        else "NO COMMITS: history scan not applicable",
        "findings": findings,
        "publication_status": "NOT READY until the publication checklist is reviewed",
    }
    output = ROOT / ".generated/publication-scan.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return int(bool(findings))


if __name__ == "__main__":
    raise SystemExit(main())
