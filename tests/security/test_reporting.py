"""HTML escaping and private output path restrictions."""

import pytest

from cyberlab.config import ROOT, ConfigError, load_config
from cyberlab.monitoring import read_events, summarize_events
from cyberlab.reporting import render_report, write_report


@pytest.fixture
def summary():
    sources = [
        read_events(ROOT / "detection/test-events" / f"{name}.ndjson", load_config())
        for name in ("eve", "auth", "http")
    ]
    return summarize_events(*sources)


def test_untrusted_html_is_escaped(summary):
    summary["recent_alerts"][0]["signature"] = '<script>alert("example")</script>'
    summary["recent_auth"][0]["message"] = '<img src="example.invalid" onerror="alert(1)">'
    document = render_report(load_config(), summary)
    assert "<script>" not in document
    assert '<img src="example.invalid"' not in document
    assert "&lt;script&gt;" in document
    assert "default-src 'none'" in document
    assert "PRIVATE LOCAL REPORT" in document


@pytest.mark.parametrize(
    "path", ["README.md", "reports/examples/leak.html", "reports/private/../../leak.html"]
)
def test_live_output_cannot_escape(tmp_path, monkeypatch, path):
    from cyberlab import reporting

    monkeypatch.setattr(reporting, "ROOT", tmp_path)
    with pytest.raises(ConfigError):
        write_report("private example", path)


def test_synthetic_and_private_output_are_separate(tmp_path, monkeypatch, summary):
    from cyberlab import reporting

    monkeypatch.setattr(reporting, "ROOT", tmp_path)
    sample = write_report(render_report(load_config(), summary, synthetic=True), synthetic=True)
    live = write_report(render_report(load_config(), summary))
    assert sample.parent.name == "examples"
    assert live.parent.name == "private"
    assert "SYNTHETIC EXAMPLE" in sample.read_text(encoding="utf-8")
    assert "System health: UNVERIFIED" in live.read_text(encoding="utf-8")
