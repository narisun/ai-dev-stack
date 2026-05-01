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
    """All five services should appear in the registry catalog under their
    short names (matches what BaseAgentApp / McpService self-register under,
    and matches config/registry.yaml seed)."""
    r = httpx.get(f"{REGISTRY_URL}/api/services", timeout=5)
    assert r.status_code == 200
    services = {s["name"]: s for s in r.json().get("services", [])}
    expected = {"analytics-agent", "data-mcp", "salesforce-mcp",
                "payments-mcp", "news-search-mcp"}
    assert expected.issubset(services.keys())


def test_registry_all_services_registered():
    """After ~75s of warmup (CI does its own wait), all five expected services
    should be in state='registered' — i.e. they each successfully called
    POST /api/services on startup. This is the headline E2E assertion."""
    def all_registered() -> bool:
        r = httpx.get(f"{REGISTRY_URL}/api/services", timeout=5)
        if r.status_code != 200:
            return False
        states = {s["name"]: s["state"] for s in r.json().get("services", [])}
        expected = {"analytics-agent", "data-mcp", "salesforce-mcp",
                    "payments-mcp", "news-search-mcp"}
        return all(states.get(n) == "registered" for n in expected)

    _wait_for(all_registered, timeout=60.0, interval=2.0)
