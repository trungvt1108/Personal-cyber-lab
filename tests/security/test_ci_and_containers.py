"""Guard against external container exposure and live work on hosted CI."""

import jinja2
import yaml

from cyberlab.config import ROOT


def test_ssh_private_listener_is_not_bypassed_by_socket_activation():
    data = yaml.safe_load((ROOT / "config/lab.yml").read_text())
    template = (ROOT / "configs/ssh/00-cyberlab.conf.j2").read_text()
    for role in ("target", "monitor"):
        rendered = (
            jinja2.Environment(undefined=jinja2.StrictUndefined)  # noqa: S701 — not HTML
            .from_string(template)
            .render(lab_config=data, lab_admin="labuser", lab_role=role)
        )
        assert f"ListenAddress {data['hosts'][role]['ip']}" in rendered
        assert "PasswordAuthentication no" in rendered
    tasks = yaml.safe_load((ROOT / "ansible/roles/common/tasks/main.yml").read_text())
    socket = next(
        task["ansible.builtin.systemd_service"]
        for task in tasks
        if task.get("ansible.builtin.systemd_service", {}).get("name") == "ssh.socket"
    )
    assert socket["enabled"] is False and socket["state"] == "stopped"


def test_containers_are_restricted_and_loopback_only():
    for stack in ("target", "monitoring"):
        compose = yaml.safe_load((ROOT / "docker" / stack / "compose.yml").read_text())
        for service in compose["services"].values():
            assert service["read_only"] is True
            assert "ALL" in service["cap_drop"]
            assert "no-new-privileges:true" in service["security_opt"]
            assert not service.get("privileged")
            assert service["user"] not in ("root", "0", "0:0")
            assert all(port.startswith("127.0.0.1:") for port in service.get("ports", []))
            assert "docker.sock" not in str(service.get("volumes", []))
        for service in compose["services"].values():
            for name in service["networks"]:
                network = compose["networks"][name]
                if network["internal"] is not True:
                    assert service.get("ports")
                    assert network["driver"] == "bridge"
                    assert (
                        network["driver_opts"]["com.docker.network.bridge.enable_ip_masquerade"]
                        == "false"
                    )


def test_grafana_has_no_literal_password_default():
    compose = yaml.safe_load((ROOT / "docker/monitoring/compose.yml").read_text())
    environment = compose["services"]["grafana"]["environment"]
    assert "GF_SECURITY_ADMIN_PASSWORD" not in environment
    assert environment["GF_SECURITY_ADMIN_PASSWORD__FILE"].startswith("/run/secrets/")
    assert environment["GF_AUTH_ANONYMOUS_ENABLED"] == "false"
    assert environment["GF_ANALYTICS_REPORTING_ENABLED"] == "false"


def test_ci_cannot_run_lab_or_publish_private_artifacts():
    workflow = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text())
    triggers = workflow.get("on", workflow.get(True))
    assert "pull_request_target" not in triggers
    assert workflow["permissions"] == {"contents": "read"}
    for job in workflow["jobs"].values():
        assert not job.get("services")
        for step in job["steps"]:
            action = step.get("uses", "")
            command = step.get("run", "")
            if action:
                assert len(action.split("@", 1)[1]) == 40
            assert "upload-artifact" not in action
            assert "--run-lab" not in command
            assert "--confirm-isolated" not in command
            assert "cyberlab.py simulate" not in command
            assert "compose up" not in command
            assert "printenv" not in command
            if "checkout" in action:
                assert step["with"]["persist-credentials"] is False
