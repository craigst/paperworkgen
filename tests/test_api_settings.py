from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app


@pytest.fixture
def client(monkeypatch):
    original = {
        "host": settings.host,
        "port": settings.port,
        "output_dir": settings.output_dir,
        "templates_dir": settings.templates_dir,
        "signatures_dir": settings.signatures_dir,
        "pdf_override": getattr(settings, "_pdf_enabled_override", None),
    }
    client = TestClient(app)
    yield client
    settings.host = original["host"]
    settings.port = original["port"]
    settings.output_dir = original["output_dir"]
    settings.templates_dir = original["templates_dir"]
    settings.signatures_dir = original["signatures_dir"]
    settings._pdf_enabled_override = original["pdf_override"]


def test_get_settings_returns_current_config(monkeypatch, client):
    monkeypatch.setattr(settings, "host", "0.0.0.0")
    monkeypatch.setattr(settings, "port", 9000)
    monkeypatch.setattr(settings, "output_dir", Path("/tmp/out"))
    monkeypatch.setattr(settings, "templates_dir", Path("/tmp/templates"))
    monkeypatch.setattr(settings, "signatures_dir", Path("/tmp/sig"))
    settings.set_pdf_enabled(False)

    resp = client.get("/api/settings")
    body = resp.json()

    assert resp.status_code == 200
    assert body["host"] == "0.0.0.0"
    assert body["port"] == 9000
    assert body["output_dir"] == "/tmp/out"
    assert body["templates_dir"] == "/tmp/templates"
    assert body["signatures_dir"] == "/tmp/sig"
    assert body["pdf_enabled"] is False


def test_update_settings_toggles_pdf(monkeypatch, client):
    settings.clear_pdf_override()
    monkeypatch.setenv("PAPERWORK_DISABLE_PDF", "true")

    resp = client.post("/api/settings", json={"pdf_enabled": True})
    body = resp.json()

    assert resp.status_code == 200
    assert body["pdf_enabled"] is True
    assert settings.pdf_enabled is True

    resp_reset = client.post("/api/settings", json={"reset_pdf_override": True})
    body_reset = resp_reset.json()

    assert resp_reset.status_code == 200
    assert body_reset["pdf_enabled"] is False
    assert settings.pdf_enabled is False
