from __future__ import annotations

from unittest.mock import patch

from briefs.schemas import BriefRequest, IncidentTriageRequest
from briefs.services import get_service_from_env

from .conftest import build_incident_request, build_request


def test_mock_mode_service_generates_deterministic_plan() -> None:
    with patch.dict(
        "os.environ",
        {"LUMEN_MOCK_AGENT": "true", "LUMEN_AGENT_API_KEY": ""},
        clear=False,
    ):
        service = get_service_from_env()
        brief_request = BriefRequest.model_validate(build_request())
        result = service.create_brief(brief_request)

        assert result.confidence == 0.73
        assert result.key_steps
        assert "Mocked brief" in result.executive_summary


def test_mock_mode_triage_service_returns_deterministic_payload() -> None:
    with patch.dict(
        "os.environ",
        {"LUMEN_MOCK_AGENT": "true", "LUMEN_AGENT_API_KEY": ""},
        clear=False,
    ):
        service = get_service_from_env()
        request = IncidentTriageRequest.model_validate(build_incident_request())
        first = service.triage_incident(request)
        second = service.triage_incident(request)

        assert first == second
        assert first.incident_title == "API Throughput Degradation"
        assert first.priority == "P2"
        assert first.confidence == 0.92
        assert first.severity == "high"
