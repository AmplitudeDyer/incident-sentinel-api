from __future__ import annotations

from unittest.mock import patch

import pytest
from pydantic import ValidationError

from briefs.schemas import BriefRequest, IncidentTriageRequest
from briefs.services import (
    is_mock_agent_enabled,
    validate_brief_request_payload,
    validate_incident_triage_payload,
)

from .conftest import build_incident_request, build_request


def test_validate_request_payload_accepts_valid_payload() -> None:
    payload = build_request()
    request = validate_brief_request_payload(payload)
    assert isinstance(request, BriefRequest)
    assert request.mission_title == payload["mission_title"]


def test_validate_request_payload_rejects_short_title() -> None:
    payload = build_request(mission_title="No")
    with pytest.raises(ValidationError):
        validate_brief_request_payload(payload)


def test_validate_incident_request_payload_accepts_valid_payload() -> None:
    payload = build_incident_request()
    request = validate_incident_triage_payload(payload)
    assert isinstance(request, IncidentTriageRequest)
    assert request.incident_title == payload["incident_title"]


def test_validate_incident_request_payload_rejects_invalid_severity() -> None:
    payload = build_incident_request(severity="catastrophic")
    with pytest.raises(ValidationError):
        validate_incident_triage_payload(payload)


def test_is_mock_agent_enabled_respects_truthy_env_value() -> None:
    with patch.dict("os.environ", {"LUMEN_MOCK_AGENT": "1"}, clear=False):
        assert is_mock_agent_enabled() is True
