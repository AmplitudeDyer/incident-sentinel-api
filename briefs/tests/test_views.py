from __future__ import annotations

import json
from unittest.mock import ANY, patch

from django.test import Client, TestCase

from briefs.schemas import BriefResponse
from .conftest import build_request


class BriefApiTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    @patch("briefs.views.get_service_from_env")
    def test_create_brief_endpoint_returns_structured_response(self, mock_service_factory):
        payload = build_request()

        brief_response = BriefResponse(
            mission_title=payload["mission_title"],
            executive_summary="Mocked summary",
            key_steps=["Define scope", "Set checkpoints"],
            deliverables=["Playbook", "Timeline"],
            resources=["PM", "Ops"],
            risks=["Unknown external dependency"],
            confidence=0.91,
        )

        service = mock_service_factory.return_value
        service.create_brief.return_value = brief_response

        response = self.client.post(
            "/api/v1/briefs/",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 201
        body = response.json()
        assert body["mission_title"] == payload["mission_title"]
        assert body["confidence"] == brief_response.confidence
        service.create_brief.assert_called_once()
        mock_service_factory.assert_called_once_with()

    @patch("briefs.views.get_service_from_env")
    def test_create_brief_endpoint_rejects_invalid_payload(self, mock_service_factory):
        payload = build_request(mission_title="No")

        response = self.client.post(
            "/api/v1/briefs/",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 400
        body = response.json()
        assert body["error"] == "4 validation error for BriefRequest"
        mock_service_factory.assert_not_called()

    def test_create_brief_endpoint_rejects_invalid_json(self) -> None:
        response = self.client.post(
            "/api/v1/briefs/",
            data="{bad json}",
            content_type="application/json",
        )

        assert response.status_code == 400
        body = response.json()
        assert body["type"] == "JSONDecodeError"

    def test_health_endpoint_returns_ok(self) -> None:
        response = self.client.get("/api/v1/health/")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "service": "lumen-agent-api"}
