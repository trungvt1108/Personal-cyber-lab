"""Check forwarding destinations and reader scope using safe templates."""

import jinja2
import yaml

from cyberlab.config import ROOT


def test_log_templates_use_shared_ip_configuration():
    data = yaml.safe_load((ROOT / "config/lab.yml").read_text(encoding="utf-8"))
    env = jinja2.Environment(undefined=jinja2.StrictUndefined)  # noqa: S701 — not HTML
    sender = env.from_string((ROOT / "configs/target/rsyslog-forward.conf.j2").read_text()).render(
        lab_config=data
    )
    receiver = env.from_string(
        (ROOT / "configs/monitor/rsyslog-receive.conf.j2").read_text()
    ).render(lab_config=data)
    assert f'Target="{data["hosts"]["monitor"]["ip"]}"' in sender
    assert f"$fromhost-ip != '{data['hosts']['target']['ip']}'" in receiver
    assert 'fileCreateMode="0640"' in receiver


def test_collector_reads_selected_logs_and_has_no_cloud_destination():
    config = (ROOT / "docker/monitoring/config.alloy").read_text()
    assert "/var/log/suricata/eve.json" in config
    assert "/var/log/cyberlab-target/auth.jsonl" in config
    assert 'url = "http://loki:3100/loki/api/v1/push"' in config
    assert "/var/log/*" not in config
    assert "docker.sock" not in config
