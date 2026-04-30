"""Root conftest — most fixtures now ship in platform_sdk.testing.plugin.

The plugin is auto-registered via the [project.entry-points.pytest11] hook
in platform-sdk/pyproject.toml. This file keeps only the legacy
PERSONA_* module-level constants that some tests still import directly.
"""
from platform_sdk.testing import TEST_PERSONAS


def _persona_to_jwt_payload(persona: dict) -> dict:
    return {
        "sub": persona["rm_id"],
        "name": persona["rm_name"],
        "role": persona["role"],
        "team_id": persona["team_id"],
        "assigned_account_ids": persona["assigned_account_ids"],
        "compliance_clearance": persona["compliance_clearance"],
    }


PERSONA_MANAGER = _persona_to_jwt_payload(TEST_PERSONAS["manager"])
PERSONA_SENIOR_RM = _persona_to_jwt_payload(TEST_PERSONAS["senior_rm"])
PERSONA_RM = _persona_to_jwt_payload(TEST_PERSONAS["rm"])
PERSONA_READONLY = _persona_to_jwt_payload(TEST_PERSONAS["readonly"])
