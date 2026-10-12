"""Bounded parsing of local EVE and central JSON logs; untrusted text stays data."""

from __future__ import annotations

import json
import os
import re
import stat
from collections import Counter, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cyberlab.config import ConfigError, LabConfig

MAX_BYTES = 32 * 1024 * 1024
MAX_LINE = 65_536
REJECTION = re.compile(
    r"Invalid user|Failed (?:password|publickey)|Connection closed by invalid user"
)


class MonitoringError(ValueError):
    """A selected evidence file cannot be safely read or interpreted."""


@dataclass
class EventFile:
    records: list[dict[str, Any]]
    malformed: int = 0
    out_of_scope: int = 0
    omitted: int = 0
    missing: bool = False


def read_events(
    path: Path | str, config: LabConfig, *, limit: int = 5000, missing_ok: bool = False
) -> EventFile:
    """Read only a bounded regular UTF-8 log; retain recent scoped records."""
    if type(limit) is not int or not 1 <= limit <= 10_000:
        raise MonitoringError("Evidence record limit must be 1 through 10000")
    selected = Path(path)
    if selected.is_symlink():
        raise MonitoringError("Evidence symlinks are refused")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    try:
        fd = os.open(selected, flags)
    except FileNotFoundError as exc:
        if missing_ok:
            return EventFile([], missing=True)
        raise MonitoringError("Selected evidence file is missing") from exc
    except OSError as exc:
        raise MonitoringError("Cannot read evidence; check guest permissions") from exc
    with os.fdopen(fd, "rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_BYTES:
            raise MonitoringError("Evidence must be a regular file no larger than 32 MiB")
        content = stream.read(MAX_BYTES + 1)
    if len(content) > MAX_BYTES:
        raise MonitoringError("Evidence grew beyond the 32 MiB limit")
    records: deque[dict[str, Any]] = deque(maxlen=limit)
    malformed = out_of_scope = valid = 0
    for line in content.splitlines():
        if not line.strip():
            continue
        if len(line) > MAX_LINE:
            malformed += 1
            continue
        try:
            record = json.loads(line)
            if not isinstance(record, dict) or not isinstance(record.get("timestamp"), str):
                raise ValueError("missing event timestamp")
            if "alert" in record and not isinstance(record["alert"], dict):
                raise ValueError("malformed alert")
            for key in ("src_ip", "dest_ip", "sender_ip"):
                if key in record:
                    config.validate_target(record[key])
            for key in ("http", "stats"):
                if key in record and not isinstance(record[key], dict):
                    raise ValueError("malformed metadata")
        except ConfigError:
            out_of_scope += 1
            continue
        except (ValueError, TypeError, RecursionError):
            malformed += 1
            continue
        records.append(record)
        valid += 1
    return EventFile(list(records), malformed, out_of_scope, max(0, valid - limit))


def alert_view(record: dict[str, Any]) -> dict[str, str]:
    """Select only report fields; raw headers, bodies and credentials are omitted."""
    alert = record.get("alert", {})
    return {
        "timestamp": str(record.get("timestamp", "unknown"))[:40],
        "src_ip": str(record.get("src_ip", "unknown"))[:40],
        "dest_ip": str(record.get("dest_ip", "unknown"))[:40],
        "dest_port": str(record.get("dest_port", "-"))[:8],
        "protocol": str(record.get("proto", "unknown"))[:12],
        "sid": str(alert.get("signature_id", "unknown"))[:12],
        "severity": str(alert.get("severity", "unknown"))[:8],
        "signature": str(alert.get("signature", "unnamed"))[:256],
    }


def summarize_events(eve: EventFile, auth: EventFile, http: EventFile) -> dict[str, Any]:
    """Summarize only loaded records and preserve parser warnings and uncertainty."""
    alerts = [record for record in eve.records if record.get("event_type") == "alert"]
    messages = [str(record.get("message", "")) for record in auth.records]
    stats = [
        record.get("stats", {}) for record in eve.records if record.get("event_type") == "stats"
    ]
    capture = stats[-1].get("capture", {}) if stats else {}
    if not isinstance(capture, dict):
        capture = {}
    return {
        "event_counts": dict(
            Counter(str(record.get("event_type", "unknown")) for record in eve.records)
        ),
        "ids_alert_count": len(alerts),
        "recent_alerts": [alert_view(record) for record in alerts[-20:]][::-1],
        "ssh_rejection_lines": sum(bool(REJECTION.search(message)) for message in messages),
        "ssh_accepted_lines": sum("Accepted " in message for message in messages),
        "recent_auth": [
            {
                "timestamp": str(record.get("timestamp", "unknown"))[:40],
                "message": str(record.get("message", ""))[:512],
            }
            for record in auth.records[-10:]
        ][::-1],
        "http_request_count": len(http.records),
        "top_http_paths": dict(
            Counter(
                str(record.get("path", "unknown")).split("?", 1)[0][:256] for record in http.records
            ).most_common(8)
        ),
        "ids_packets_observed": capture.get("kernel_packets", "UNVERIFIED"),
        "ids_packet_drops": capture.get("kernel_drops", "UNVERIFIED"),
        "malformed_records": eve.malformed + auth.malformed + http.malformed,
        "out_of_scope_records": eve.out_of_scope + auth.out_of_scope + http.out_of_scope,
        "omitted_records": eve.omitted + auth.omitted + http.omitted,
        "missing_sources": [
            name
            for name, source in (("EVE", eve), ("auth", auth), ("HTTP", http))
            if source.missing
        ],
    }
