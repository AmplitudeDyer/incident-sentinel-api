from __future__ import annotations

import inspect
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, cast

from pydantic import BaseModel

from .schemas import (
    BriefRequest,
    BriefResponse,
    IncidentPriority,
    IncidentTriageRequest,
    IncidentTriageResponse,
)

try:  # Optional runtime dependency, tests can run in mock mode.
    from pydantic_ai import Agent
except Exception:  # pragma: no cover - optional dependency path.
    Agent = None


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name, str(default)).strip().lower()
    return value in {"1", "true", "yes", "on"}


def is_mock_agent_enabled() -> bool:
    """Return whether mock mode is enabled via env flag."""

    return _env_bool("LUMEN_MOCK_AGENT", False)


@dataclass(frozen=True)
class AgentConfig:
    model: str
    timeout_seconds: int
    api_key: str | None
    mock_mode: bool


@dataclass(frozen=True)
class MissionBriefService:
    """Service wrapper around the PydanticAI agent used by API views."""

    config: AgentConfig

    def create_brief(self, brief_request: BriefRequest) -> BriefResponse:
        if self.config.mock_mode:
            return _mock_brief(brief_request)
        instructions = (
            "You are a strategic planning assistant. Return structured JSON for each brief "
            "request using the output schema. Be concise but complete and include concrete steps."
        )
        return _run_agent(
            model=self.config.model,
            api_key=self.config.api_key,
            timeout_seconds=self.config.timeout_seconds,
            request_payload=brief_request,
            output_model=BriefResponse,
            instructions=instructions,
        )

    def triage_incident(
        self,
        incident_request: IncidentTriageRequest,
    ) -> IncidentTriageResponse:
        if self.config.mock_mode:
            return _mock_triage(incident_request)
        instructions = (
            "You are an incident-triage assistant for a security-focused operations team. "
            "Return structured JSON that assigns priority and a concrete action plan. "
            "The response must be concise, prioritized, and safe."
        )
        return _run_agent(
            model=self.config.model,
            api_key=self.config.api_key,
            timeout_seconds=self.config.timeout_seconds,
            request_payload=incident_request,
            output_model=IncidentTriageResponse,
            instructions=instructions,
        )


def get_service_from_env() -> MissionBriefService:
    return MissionBriefService(
        config=AgentConfig(
            model=os.getenv("LUMEN_AGENT_MODEL", "openai:gpt-4o-mini"),
            timeout_seconds=int(os.getenv("LUMEN_AGENT_TIMEOUT_SECONDS", "30")),
            api_key=os.getenv("LUMEN_AGENT_API_KEY"),
            mock_mode=is_mock_agent_enabled(),
        )
    )


def _mock_brief(brief_request: BriefRequest) -> BriefResponse:
    mission_title = brief_request.mission_title.strip()
    target = brief_request.target_date or "unspecified date"
    return BriefResponse(
        mission_title=mission_title,
        executive_summary=(
            f"Mocked brief for {mission_title}. Generated for {target} with "
            "deterministic fallback logic."
        ),
        key_steps=[
            "Confirm mission scope and acceptance criteria.",
            "Draft a phased plan with owners and dependencies.",
            "Review risks and publish the execution checklist.",
        ],
        deliverables=["Mission charter", "Execution roadmap", "Risk tracker"],
        resources=["Mission Lead", "Cross-functional SME", "Ops support"],
        risks=["Unexpected dependencies", "Scope drift", "Data incompleteness"],
        confidence=0.73,
    )


def _mock_triage(incident_request: IncidentTriageRequest) -> IncidentTriageResponse:
    incident_title = incident_request.incident_title.strip()
    severity = incident_request.severity
    affected = ", ".join(sorted(set(filter(None, incident_request.affected_systems))))
    affected_clause = f" Affecting {affected}." if affected else ""

    priority = cast(
        IncidentPriority,
        {
            "low": "P4",
            "medium": "P3",
            "high": "P2",
            "critical": "P1",
        }[severity],
    )

    confidence_by_severity: dict[str, float] = {
        "low": 0.79,
        "medium": 0.86,
        "high": 0.92,
        "critical": 0.97,
    }

    immediate_actions = {
        "low": [
            "Validate impact and reproduce in a controlled environment.",
            "Confirm no customer-facing blast radius.",
            "Document workaround and monitor for escalation.",
        ],
        "medium": [
            "Acknowledge incident in dispatch channel and assign an incident lead.",
            "Contain potential blast radius and validate rollback boundary.",
            "Run focused diagnostics on affected systems.",
        ],
        "high": [
            "Declare incident response in active mode.",
            "Enable communication bridges and assign roles.",
            "Isolate impacted components and initiate mitigation.",
        ],
        "critical": [
            "Activate full incident command and escalation procedures.",
            "Freeze non-critical changes and isolate high-risk services.",
            "Begin customer-impact reporting and mitigation immediately.",
        ],
    }

    investigation_steps = [
        "Review recent deployments and configuration changes.",
        "Check monitoring, alert history, and error-rate deltas.",
        "Correlate with dependency health and external provider status.",
    ]

    return IncidentTriageResponse(
        incident_title=incident_title,
        severity=severity,
        priority=priority,
        triage_summary=(
            f"Mocked triage for {incident_title}.{affected_clause} "
            "Generated with deterministic fallback logic for predictable environments."
        ),
        immediate_actions=immediate_actions[severity],
        investigation_steps=investigation_steps,
        communication_updates=[
            "Send initial notification to on-call channel.",
            "Update incident ticket with first findings and owner assignments.",
            "Broadcast interim status every 15 minutes until stabilized.",
        ],
        stakeholders_to_notify=[
            "Incident Lead",
            "Platform Engineering",
            "Customer Support",
        ],
        confidence=confidence_by_severity[severity],
    )


def _run_agent(
    *,
    model: str,
    api_key: str | None,
    timeout_seconds: int,
    request_payload: BaseModel,
    output_model: type[Any],
    instructions: str,
) -> Any:
    if Agent is None:
        raise RuntimeError("PydanticAI is not installed. Enable mock mode or install dependencies.")

    if not api_key:
        raise RuntimeError("LUMEN_AGENT_API_KEY is required when mock mode is disabled.")

    os.environ.setdefault("OPENAI_API_KEY", api_key)

    params = inspect.signature(Agent.__init__).parameters
    model_keyword = "model" if "model" in params else None
    output_keyword = "result_type" if "result_type" in params else "output_type"
    prompt_keyword = "system_prompt" if "system_prompt" in params else "instructions"

    kwargs: dict[str, Any] = {
        output_keyword: output_model,
        prompt_keyword: instructions,
    }

    if "api_key" in params:
        kwargs["api_key"] = api_key

    if "timeout" in params:
        kwargs["timeout"] = timeout_seconds
    elif "timeout_seconds" in params:
        kwargs["timeout_seconds"] = timeout_seconds

    try:
        if model_keyword is None:
            agent = Agent(model=model, **kwargs)
        else:
            agent = Agent(**{model_keyword: model, **kwargs})
    except TypeError as exc:
        raise RuntimeError(f"Failed to initialize agent: {exc}") from exc

    prompt = (
        "Produce structured output for the following request payload.\n\n"
        f"{request_payload.model_dump_json()}"
    )

    try:
        result = agent.run_sync(prompt)
    except Exception as exc:  # pragma: no cover - integration surface.
        raise RuntimeError(f"Agent execution failed: {exc}") from exc

    return _extract_agent_output(result, output_model)


def _extract_agent_output(result: Any, output_model: type[Any]) -> Any:
    if isinstance(result, output_model):
        return result

    for attr in ("data", "output", "result", "parsed"):
        value = getattr(result, attr, None)
        if isinstance(value, output_model):
            return value

    if isinstance(result, dict):
        return output_model.model_validate(result)

    raise RuntimeError("Unexpected response type from agent")


def validate_brief_request_payload(payload: object) -> BriefRequest:
    return BriefRequest.model_validate(payload)


def validate_request_payload(payload: object) -> BriefRequest:
    return validate_brief_request_payload(payload)


def validate_incident_triage_payload(payload: object) -> IncidentTriageRequest:
    return IncidentTriageRequest.model_validate(payload)


def format_error_payload(error: Exception) -> dict[str, object]:
    return {
        "error": str(error),
        "type": type(error).__name__,
        "timestamp": datetime.now(tz=UTC).isoformat(),
    }
