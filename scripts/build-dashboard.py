"""Build the committed Grafana dashboard without contacting a service."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOKI = {"type": "loki", "uid": "cyberlab-loki"}


def panel(
    panel_id: int,
    title: str,
    kind: str,
    query: str,
    x: int,
    y: int,
    width: int = 6,
    height: int = 5,
    instant: bool = False,
) -> dict[str, object]:
    """Create a panel with consistent spacing, datasource and display defaults."""
    result: dict[str, object] = {
        "id": panel_id,
        "title": title,
        "type": kind,
        "datasource": LOKI,
        "gridPos": {"x": x, "y": y, "w": width, "h": height},
        "targets": [
            {
                "refId": "A",
                "expr": query,
                "datasource": LOKI,
                "queryType": "instant" if instant else "range",
                "legendFormat": "{{label}}",
            }
        ],
        "fieldConfig": {"defaults": {"color": {"mode": "palette-classic"}}, "overrides": []},
        "options": {},
    }
    if kind in ("stat", "bargauge"):
        result["options"] = {
            "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False},
            "orientation": "auto",
            "colorMode": "value",
            "graphMode": "none",
        }
    if kind == "logs":
        result["options"] = {
            "showTime": True,
            "showLabels": False,
            "wrapLogMessage": True,
            "sortOrder": "Descending",
            "enableLogDetails": True,
            "dedupStrategy": "none",
        }
    return result


def main() -> None:
    panels = [
        panel(
            1,
            "Collected lab events",
            "stat",
            'sum(count_over_time({job=~"suricata|target"}[$__range]))',
            0,
            0,
            instant=True,
        ),
        panel(
            2,
            "IDS alerts",
            "stat",
            'sum(count_over_time({job="suricata",event_type="alert"}[$__range]))',
            6,
            0,
            instant=True,
        ),
        panel(
            3,
            "SSH rejection log lines",
            "stat",
            'sum(count_over_time({job="target",kind="auth"} |~ "Invalid user|Failed (password|publickey)|Connection closed by invalid user" [$__range]))',
            12,
            0,
            instant=True,
        ),
        panel(
            4,
            "HTTP requests",
            "stat",
            'sum(count_over_time({job="target",kind="nginx_access"}[$__range]))',
            18,
            0,
            instant=True,
        ),
        panel(
            5,
            "Events per minute by stream",
            "timeseries",
            'sum by (job) (count_over_time({job=~"suricata|target"}[1m]))',
            0,
            5,
            width=12,
            height=7,
        ),
        panel(
            6,
            "IDS alerts over time",
            "timeseries",
            'sum(count_over_time({job="suricata",event_type="alert"}[1m]))',
            12,
            5,
            width=12,
            height=7,
        ),
        panel(
            7,
            "Top alert source hosts",
            "bargauge",
            'topk(5, sum by (src_ip) (count_over_time({job="suricata",event_type="alert"} | json | __error__="" [$__range])))',
            0,
            12,
            height=6,
            instant=True,
        ),
        panel(
            8,
            "Alert destination IP",
            "bargauge",
            'sum by (dest_ip) (count_over_time({job="suricata",event_type="alert"} | json | __error__="" [$__range]))',
            6,
            12,
            height=6,
            instant=True,
        ),
        panel(
            9,
            "Alert protocol",
            "bargauge",
            'sum by (proto) (count_over_time({job="suricata",event_type="alert"} | json | __error__="" [$__range]))',
            12,
            12,
            height=6,
            instant=True,
        ),
        panel(
            10,
            "Signature priority (not verdict)",
            "bargauge",
            'sum by (alert_severity) (count_over_time({job="suricata",event_type="alert"} | json | __error__="" [$__range]))',
            18,
            12,
            height=6,
            instant=True,
        ),
        panel(
            11,
            "Most requested paths",
            "bargauge",
            'topk(8, sum by (path) (count_over_time({job="target",kind="nginx_access"} | json | __error__="" [$__range])))',
            0,
            18,
            width=12,
            height=6,
            instant=True,
        ),
        panel(
            12,
            "Recent security alerts · expand for IP / protocol / SID",
            "logs",
            '{job="suricata",event_type="alert"} | json | __error__=""',
            12,
            18,
            width=12,
            height=8,
        ),
        panel(
            13,
            "SSH investigation · count lines, correlate attempts",
            "logs",
            '{job="target",kind="auth"} |~ "Invalid user|Failed |Accepted |Connection closed"',
            0,
            26,
            width=12,
            height=8,
        ),
        panel(
            14,
            "HTTP request evidence",
            "logs",
            '{job="target",kind="nginx_access"} | json | __error__=""',
            12,
            26,
            width=12,
            height=8,
        ),
    ]
    for item in panels:
        item["targets"][0]["legendFormat"] = (
            "{{src_ip}}{{dest_ip}}{{proto}}{{alert_severity}}{{path}}{{job}}"
        )
    dashboard = {
        "uid": "personal-cyber-lab",
        "title": "Personal Cyber Lab · SOC Overview",
        "description": "Educational telemetry; alerts and rejection log lines are not proof of compromise. Empty panels require pipeline verification.",
        "tags": ["cyberlab", "defensive-security", "suricata"],
        "timezone": "utc",
        "schemaVersion": 39,
        "version": 1,
        "editable": False,
        "refresh": "10s",
        "time": {"from": "now-30m", "to": "now"},
        "panels": panels,
        "templating": {"list": []},
        "annotations": {"list": []},
        "links": [],
    }
    destination = ROOT / "dashboards/grafana/cyberlab.json"
    destination.write_text(
        json.dumps(dashboard, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print("Generated dashboards/grafana/cyberlab.json with 14 provisioned panels.")


if __name__ == "__main__":
    main()
