"""Prevent VMware state and private/generated files from entering source exports."""

import pytest

from scripts import publication_audit


@pytest.mark.parametrize(
    "name",
    [
        "LAB-MONITOR.vmx",
        "LAB-MONITOR.vmdk",
        "LAB-MONITOR.nvram",
        "LAB-MONITOR.vmem",
        ".generated/private.txt",
        ".codex/settings.json",
        "reports/private/case.html",
        "captures/session.pcap",
    ],
)
def test_private_candidate_paths_are_rejected(tmp_path, monkeypatch, name):
    monkeypatch.setattr(publication_audit, "ROOT", tmp_path)
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("private example", encoding="utf-8")
    assert publication_audit.scan_file(path)


def test_labelled_synthetic_source_is_allowed(tmp_path, monkeypatch):
    monkeypatch.setattr(publication_audit, "ROOT", tmp_path)
    path = tmp_path / "example.md"
    path.write_text("Synthetic documentation for 192.168.56.20", encoding="utf-8")
    assert publication_audit.scan_file(path) == []
