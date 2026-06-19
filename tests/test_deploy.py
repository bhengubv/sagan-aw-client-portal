"""DEMO_MODE mounts the provider sandbox into the app (single-service hosted demo)."""
from app import create_app
from app.config import TestConfig


def test_demo_mode_mounts_sandbox(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "1")
    app = create_app(TestConfig)
    c = app.test_client()
    # the sandbox is reachable under /provider-sandbox
    r = c.get("/provider-sandbox/healthz")
    assert r.status_code == 200
    assert r.get_json()["service"] == "provider-sandbox"
    # and the portal's own routes still work
    assert c.get("/healthz").get_json()["status"] == "ok"


def test_no_demo_mode_no_sandbox(monkeypatch):
    monkeypatch.delenv("DEMO_MODE", raising=False)
    app = create_app(TestConfig)
    c = app.test_client()
    assert c.get("/provider-sandbox/healthz").status_code == 404  # not mounted
    assert c.get("/healthz").get_json()["status"] == "ok"
