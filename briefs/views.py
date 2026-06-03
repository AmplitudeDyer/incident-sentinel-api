from __future__ import annotations

import json
from http import HTTPStatus

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .services import (
    format_error_payload,
    get_service_from_env,
    validate_brief_request_payload,
    validate_incident_triage_payload,
)


def _parse_json_body(request: HttpRequest) -> object:
    return json.loads(request.body.decode("utf-8") if request.body else "{}")


@csrf_exempt
@require_http_methods(["POST"])
def create_brief(request: HttpRequest) -> HttpResponse:
    try:
        payload = _parse_json_body(request)
        brief_request = validate_brief_request_payload(payload)
    except json.JSONDecodeError as exc:
        return JsonResponse(format_error_payload(exc), status=HTTPStatus.BAD_REQUEST)
    except Exception as exc:
        return JsonResponse(format_error_payload(exc), status=HTTPStatus.BAD_REQUEST)

    try:
        service = get_service_from_env()
        brief = service.create_brief(brief_request)
    except Exception as exc:
        return JsonResponse(format_error_payload(exc), status=HTTPStatus.BAD_REQUEST)

    return JsonResponse(brief.model_dump(), status=HTTPStatus.CREATED)


@csrf_exempt
@require_http_methods(["POST"])
def triage_incident(request: HttpRequest) -> HttpResponse:
    try:
        payload = _parse_json_body(request)
        incident_request = validate_incident_triage_payload(payload)
    except json.JSONDecodeError as exc:
        return JsonResponse(format_error_payload(exc), status=HTTPStatus.BAD_REQUEST)
    except Exception as exc:
        return JsonResponse(format_error_payload(exc), status=HTTPStatus.BAD_REQUEST)

    try:
        service = get_service_from_env()
        triage = service.triage_incident(incident_request)
    except Exception as exc:
        return JsonResponse(format_error_payload(exc), status=HTTPStatus.BAD_REQUEST)

    return JsonResponse(triage.model_dump(), status=HTTPStatus.CREATED)


@require_http_methods(["GET"])
def health_view(_request: HttpRequest) -> HttpResponse:
    return JsonResponse({"status": "ok", "service": "incident-sentinel-api"})
