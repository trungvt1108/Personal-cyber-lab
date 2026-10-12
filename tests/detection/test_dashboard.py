"""Validate committed dashboard structure, references and evidence distinctions."""

import json

import yaml

from cyberlab.config import ROOT


def test_dashboard_datasource_references_and_panels():
    dashboard = json.loads((ROOT / "dashboards/grafana/cyberlab.json").read_text(encoding="utf-8"))
    datasource = yaml.safe_load(
        (ROOT / "dashboards/grafana/provisioning/datasources/loki.yml").read_text()
    )
    uid = datasource["datasources"][0]["uid"]
    assert len(dashboard["panels"]) == 14
    assert len({panel["id"] for panel in dashboard["panels"]}) == 14
    for panel in dashboard["panels"]:
        assert panel["datasource"]["uid"] == uid
        assert panel["targets"][0]["expr"]
    assert "SSH rejection log lines" in {panel["title"] for panel in dashboard["panels"]}
