"""Review deployment guard ordering and log ownership without connecting to guests."""

import yaml

from cyberlab.config import ROOT


def test_controller_prechecks_fail_before_remote_changes():
    plays = yaml.safe_load((ROOT / "ansible/playbooks/site.yml").read_text())
    first = plays[0]
    assert first["hosts"] == "localhost"
    assert first["any_errors_fatal"] is True
    preflight = (ROOT / "ansible/tasks/controller-preflight.yml").read_text()
    assert "verify-guest" in preflight
    assert "ansible_host" in preflight
    for play in plays[1:]:
        assert play["gather_facts"] is False
        assert play["any_errors_fatal"] is True
        assert (
            play["pre_tasks"][0]["ansible.builtin.import_tasks"]
            == "../tasks/controller-preflight.yml"
        )
        assert "ansible.builtin.setup" in play["pre_tasks"][1]


def test_common_role_checks_vmware_and_config_before_package_changes():
    tasks = yaml.safe_load((ROOT / "ansible/roles/common/tasks/main.yml").read_text())
    assert "VMware" in str(tasks[0]["ansible.builtin.assert"])
    apt_index = next(index for index, task in enumerate(tasks) if "ansible.builtin.apt" in task)
    assert "verify-guest" in str(tasks[:apt_index])
    assert "Synchronize config/lab.yml" in str(tasks[:apt_index])


def test_suricata_validation_preserves_eve_and_runs_as_capture_user():
    tasks = yaml.safe_load((ROOT / "ansible/roles/monitor/tasks/suricata.yml").read_text())
    eve = next(
        task["ansible.builtin.file"]
        for task in tasks
        if task.get("ansible.builtin.file", {}).get("path") == "/var/log/suricata/eve.json"
    )
    assert eve["state"] == "touch" and eve["modification_time"] == "preserve"
    assert eve["owner"] == "suricata" and eve["mode"] == "0640"
    validator = next(
        task for task in tasks if "suricata -T" in task.get("ansible.builtin.command", "")
    )
    assert validator["become_user"] == "suricata"
    for role in ("common", "target", "monitor"):
        handlers = yaml.safe_load((ROOT / f"ansible/roles/{role}/handlers/main.yml").read_text())
        for handler in handlers:
            if "notify" in handler:
                assert handler["changed_when"] is True


def test_launcher_supplies_compose_variables_for_diagnostics():
    source = (ROOT / "scripts/monitoring/start-stack.sh").read_text()
    assert "ps) compose ps --all" in source
    assert "logs) compose logs --tail 100" in source
    assert source.index(
        "alloy validate /etc/alloy/config.alloy", source.index("  up)")
    ) < source.index("compose up -d")
    assert "verify-guest --source-role monitor --confirm-lab-guest" in source
    assert (
        "CYBERLAB_LOG_GID=$log_gid" in source
        and "CYBERLAB_GRAFANA_ROOT_URL=$grafana_root_url" in source
    )
