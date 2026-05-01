"""End-to-end cross-environment isolation: a fake prod client sees 403."""
from __future__ import annotations

import os

import httpx
import pytest

REGISTRY_URL = os.environ.get("REGISTRY_URL", "http://localhost:8090")
DATA_MCP_URL = os.environ.get("DATA_MCP_URL", "http://localhost:8080")
INTERNAL_API_KEY = os.environ.get("INTERNAL_API_KEY", "sk-ent-local-dev-changeme")


@pytest.mark.integration
def test_fake_prod_client_against_registry_returns_403():
    """A POST /api/services with X-Environment: prod is rejected."""
    r = httpx.post(
        f"{REGISTRY_URL}/api/services",
        json={"name": "evil", "url": "http://evil/", "type": "agent"},
        headers={
            "Authorization": f"Bearer {INTERNAL_API_KEY}",
            "X-Environment": "prod",
        },
    )
    assert r.status_code == 403
    body = r.json()
    assert body.get("detail", {}).get("error") == "environment_mismatch"


@pytest.mark.integration
def test_no_x_environment_header_rejected():
    """Missing X-Environment is treated the same as a mismatch."""
    r = httpx.post(
        f"{REGISTRY_URL}/api/services",
        json={"name": "evil", "url": "http://evil/", "type": "agent"},
        headers={"Authorization": f"Bearer {INTERNAL_API_KEY}"},
    )
    assert r.status_code == 403
