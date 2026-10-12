"""Escaped standalone HTML reports with private output boundaries."""

from __future__ import annotations

import html
import json
import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from cyberlab.config import ROOT, ConfigError, LabConfig


def _table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    heading = "".join(f"<th>{html.escape(column.replace('_', ' '))}</th>" for column in columns)
    body = "".join(
        "<tr>"
        + "".join(f"<td>{html.escape(str(row.get(column, '-')))}</td>" for column in columns)
        + "</tr>"
        for row in rows
    )
    return f"<div class='table'><table><thead><tr>{heading}</tr></thead><tbody>{body}</tbody></table></div>"


def render_report(
    config: LabConfig,
    summary: dict[str, Any],
    *,
    synthetic: bool = False,
    checks: list[dict[str, Any]] | None = None,
) -> str:
    """Render all evidence as escaped text with no scripts or external resources."""
    label = (
        "SYNTHETIC EXAMPLE — not live evidence"
        if synthetic
        else "PRIVATE LOCAL REPORT — review before sharing"
    )
    timestamp = "2000-01-01T00:30:00+00:00" if synthetic else datetime.now(UTC).isoformat()
    hosts = [
        {"role": role, "hostname": host.hostname, "ip": host.ip}
        for role, host in config.hosts.items()
    ]
    service_rows = checks or [
        {"host": role, "service": service, "port": config.services[service], "status": "UNVERIFIED"}
        for role, services in (("target", ("ssh", "http")), ("monitor", ("ssh", "grafana")))
        for service in services
    ]
    warnings = {
        key: summary.get(key)
        for key in (
            "missing_sources",
            "malformed_records",
            "out_of_scope_records",
            "omitted_records",
        )
    }
    metrics = (
        ("IDS alerts", summary["ids_alert_count"]),
        ("SSH rejection lines", summary["ssh_rejection_lines"]),
        ("Accepted SSH log lines", summary["ssh_accepted_lines"]),
        ("HTTP request records", summary["http_request_count"]),
    )
    cards = "".join(
        f"<div class='card'><strong>{html.escape(str(value))}</strong><span>{title}</span></div>"
        for title, value in metrics
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src 'none'; base-uri 'none'; form-action 'none'">
<title>Personal Cyber Lab report</title><style>
body{{font:15px system-ui,sans-serif;background:#0b1220;color:#dce6f2;margin:0;padding:32px}}main{{max-width:1150px;margin:auto}}
h1{{color:#5eead4}}h2{{margin-top:32px}}.notice{{border:1px solid #4b637b;padding:14px;border-radius:10px;background:#142235}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:14px;margin:24px 0}}.card{{background:#162436;padding:18px;border-radius:12px}}
.card strong{{display:block;font-size:32px;color:#5eead4}}.card span{{color:#abc0d6}}.table{{overflow:auto}}table{{border-collapse:collapse;width:100%;font-size:13px}}
th,td{{text-align:left;padding:10px;border-bottom:1px solid #293b50;vertical-align:top;overflow-wrap:anywhere}}th{{color:#93c5fd}}pre{{white-space:pre-wrap;overflow-wrap:anywhere}}
footer{{margin-top:32px;color:#93a8bf}}</style></head><body><main>
<h1>Personal Cyber Lab</h1><p>{html.escape(label)}</p><p>Timestamp (UTC): {timestamp}</p>
<div class="notice">Lab status: {"SYNTHETIC / illustrative only" if synthetic else "observed checks below; anything unmeasured is UNVERIFIED"}. System health: UNVERIFIED unless confirmed by guest-local diagnostics.
Counts refer to loaded log records, not unique incidents. An IDS alert is an investigation lead. Parser warnings can make evidence incomplete.</div>
<div class="cards">{cards}</div><h2>Configured hosts</h2>{_table(hosts, ["role", "hostname", "ip"])}
<h2>Available services</h2>{_table(service_rows, ["host", "service", "port", "status"])}
<h2>IDS statistics</h2><pre>{html.escape(json.dumps({"event_counts": summary["event_counts"], "packets_observed": summary["ids_packets_observed"], "packet_drops": summary["ids_packet_drops"]}, indent=2))}</pre>
<h2>Recent alerts</h2>{_table(summary["recent_alerts"], ["timestamp", "src_ip", "dest_ip", "dest_port", "protocol", "sid", "severity", "signature"])}
<h2>SSH authentication evidence</h2>{_table(summary["recent_auth"], ["timestamp", "message"])}
<h2>HTTP paths</h2>{_table([{"path": key, "records": value} for key, value in summary["top_http_paths"].items()], ["path", "records"])}
<h2>Evidence completeness</h2><pre>{html.escape(json.dumps(warnings, indent=2))}</pre>
<footer>Local-only output. No analytics, external assets, upload, cookies or credentials. Preserve live evidence privately; publish synthetic examples only.</footer>
</main></body></html>"""


def write_report(
    content: str, output: Path | str | None = None, *, synthetic: bool = False
) -> Path:
    """Keep real reports under ignored reports/private and refuse link/path escapes."""
    relative_base = Path("reports/examples" if synthetic else "reports/private")
    base = ROOT / relative_base
    selected = (
        Path(output)
        if output
        else base / ("synthetic-report.html" if synthetic else "cyberlab-report.html")
    )
    selected = selected if selected.is_absolute() else ROOT / selected
    if selected.suffix.lower() != ".html" or not selected.resolve().is_relative_to(base.resolve()):
        raise ConfigError("Report output must stay inside its dedicated HTML report directory")
    for path in (base, selected, *selected.parents):
        if path == ROOT.parent:
            break
        if path.is_symlink():
            raise ConfigError("Report directories and files must not be symlinks")
    selected.parent.mkdir(parents=True, exist_ok=True, mode=0o755 if synthetic else 0o700)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=selected.parent, prefix=".report-", delete=False
    ) as temporary:
        temporary.write(content)
        temporary_path = Path(temporary.name)
    try:
        os.chmod(temporary_path, 0o600)
        temporary_path.replace(selected)
    finally:
        temporary_path.unlink(missing_ok=True)
    return selected
