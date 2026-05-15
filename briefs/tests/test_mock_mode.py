from __future__ import annotations

from unittest.mock import patch

from briefs.services import get_service_from_env
from .conftest import build_request


def test_mock_mode_service_generates_deterministic_plan():
    with patch.dict(
        "os.environ",
        {"LUMEN_MOCK_AGENT": "true", "LUMEN_AGENT_API_KEY": ""},
        clear=False,
    ):
        service = get_service_from_env()
        request = service.create_brief
        brief_request = request.model_validate(build_request())
        result = service.create_brief(brief_request)

        assert result.confidence == 0.73
        assert result.key_steps
        assert "Mocked brief" in result.executive_summary
