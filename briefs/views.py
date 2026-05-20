from __future__ import annotations

import json
from http import HTTPStatus

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .services import (
    format_error_payload,
    get_service_from_env,
    validate_request_payload,
)


@csrf_exempt
@require_http_methods(["POST"])
def create_brief(request: HttpRequest) -> HttpResponse:
    try:
        payload = json.loads(request.body.decode("utf-8") if request.body else "{}")
    except json.JSONDecodeError as exc:
        return JsonResponse(format_error_payload(exc), status=HTTPStatus.BAD_REQUEST)

    try:
        brief_request = validate_request_payload(payload)
    except Exception as exc:
        return JsonResponse(format_error_payload(exc), status=HTTPStatus.BAD_REQUEST)

    try:
        service = get_service_from_env()
        brief = service.create_brief(brief_request)
    except Exception as exc:
        return JsonResponse(format_error_payload(exc), status=HTTPStatus.BAD_REQUEST)

    return JsonResponse(brief.model_dump(), status=HTTPStatus.CREATED)


@require_http_methods(["GET"])
def health_view(request: HttpRequest) -> HttpResponse:
    return JsonResponse({"status": "ok", "service": "lumen-agent-api"})
