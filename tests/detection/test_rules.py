"""Check custom rule scope and identifiers, without claiming engine validation."""

import re

import jinja2
import yaml

from cyberlab.config import ROOT


def test_rules_are_unique_alerts_scoped_to_lab():
    data = yaml.safe_load((ROOT / "config/lab.yml").read_text(encoding="utf-8"))
    text = (ROOT / "detection/rules/local.rules.j2").read_text(encoding="utf-8")
    rendered = (
        jinja2.Environment(undefined=jinja2.StrictUndefined)  # noqa: S701 — not an HTML template
        .from_string(text)
        .render(lab_config=data)
    )
    rules = rendered.splitlines()
    assert len(rules) == 8
    ids = []
    for rule in rules:
        assert rule.startswith("alert ")
        assert "$HOME_NET any -> $LAB_TARGET" in rule
        assert "drop " not in rule and "reject " not in rule
        ids.append(re.search(r"sid:(\d+);", rule).group(1))
    assert len(ids) == len(set(ids))


def test_capture_uses_private_interface_and_minimal_eve():
    data = yaml.safe_load((ROOT / "config/lab.yml").read_text(encoding="utf-8"))
    text = (ROOT / "detection/suricata/suricata.yaml.j2").read_text(encoding="utf-8")
    rendered = (
        jinja2.Environment(undefined=jinja2.StrictUndefined)  # noqa: S701 — not an HTML template
        .from_string(text)
        .render(lab_config=data)
    )
    config = yaml.safe_load(rendered)
    assert config["af-packet"][0]["interface"] == data["hosts"]["monitor"]["interface"]
    assert config["af-packet"][0]["bpf-filter"] == "ip and not ip multicast"
    assert config["vars"]["address-groups"]["EXTERNAL_NET"] == "any"
    assert "packet" not in str(config["outputs"])
