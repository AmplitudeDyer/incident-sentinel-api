from __future__ import annotations

from unittest.mock import patch

from briefs.services import get_service_from_env


def test_get_service_from_env_reads_mock_and_model() -> None:
    with patch.dict(
        "os.environ",
        {
            "LUMEN_MOCK_AGENT": "yes",
            "LUMEN_AGENT_MODEL": "openai:gpt-5-mini",
            "LUMEN_AGENT_TIMEOUT_SECONDS": "42",
            "LUMEN_AGENT_API_KEY": "placeholder",
        },
        clear=False,
    ):
        service = get_service_from_env()
        assert service.config.mock_mode is True
        assert service.config.model == "openai:gpt-5-mini"
        assert service.config.timeout_seconds == 42
        assert service.config.api_key == "placeholder"
