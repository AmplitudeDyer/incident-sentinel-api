from __future__ import annotations

from __future__ import annotations

from pydantic import ValidationError

from .conftest import build_request
from briefs.schemas import BriefRequest
from briefs.services import validate_request_payload


def test_validate_request_payload_accepts_valid_payload() -> None:
    payload = build_request()
    request = validate_request_payload(payload)
    assert isinstance(request, BriefRequest)
    assert request.mission_title == payload["mission_title"]


def test_validate_request_payload_rejects_short_title() -> None:
    payload = build_request(mission_title="No")
    with ValidationError:
        validate_request_payload(payload)
