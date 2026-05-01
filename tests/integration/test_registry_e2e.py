"""E2E test — verifies all expected services register against the live registry."""
from __future__ import annotations

import os
import time

import httpx
import pytest

pytestmark = pytest.mark.integration


REGISTRY_URL = os.environ.get("REGISTRY_URL", "http://localhost:8090")


def _wait_for(predicate, timeout: float = 30.0, interval: float = 1.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if predicate():
            return
        time.sleep(interval)
    raise AssertionError("timeout")


def test_registry_health_endpoint():
    r = httpx.get(f"{REGISTRY_URL}/health", timeout=5)
    assert r.status_code == 200
    body = r.json()
    assert body["db_ok"] is True


def test_registry_seeded_services_visible():
    """Services seeded in registry.yaml should appear (possibly as expected_unregistered
    if SDK is still 0.4.0 — Task 19 bumps services to 0.5.0 and they self-register)."""
    r = httpx.get(f"{REGISTRY_URL}/api/services", timeout=5)
    assert r.status_code == 200
    services = {s["name"]: s for s in r.json().get("services", [])}
    expected = {"ai-agent-analytics", "ai-mcp-data", "ai-mcp-salesforce",
                "ai-mcp-payments", "ai-mcp-news-search"}
    assert expected.issubset(services.keys())
