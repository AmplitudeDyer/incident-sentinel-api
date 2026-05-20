from __future__ import annotations

import inspect
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .schemas import BriefRequest, BriefResponse

try:  # Optional runtime dependency, tests can run in mock mode.
    from pydantic_ai import Agent  # type: ignore[import-not-found]
except Exception:  # pragma: no cover - optional dependency path.
    Agent = None


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name, str(default)).strip().lower()
    return value in {"1", "true", "yes", "on"}


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
        return _run_agent(self.config.model, self.config.api_key, brief_request)


def get_service_from_env() -> MissionBriefService:
    return MissionBriefService(
        config=AgentConfig(
            model=os.getenv("LUMEN_AGENT_MODEL", "openai:gpt-4o-mini"),
            timeout_seconds=int(os.getenv("LUMEN_AGENT_TIMEOUT_SECONDS", "30")),
            api_key=os.getenv("LUMEN_AGENT_API_KEY"),
            mock_mode=_env_bool("LUMEN_MOCK_AGENT", False),
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


def _run_agent(model: str, api_key: str | None, brief_request: BriefRequest) -> BriefResponse:
    if Agent is None:
        raise RuntimeError("PydanticAI is not installed. Enable mock mode or install dependencies.")

    if not api_key:
        raise RuntimeError("LUMEN_AGENT_API_KEY is required when mock mode is disabled.")

    os.environ.setdefault("OPENAI_API_KEY", api_key)

    instructions = (
        "You are a strategic planning assistant. Return structured JSON for each brief request "
        "using the output schema. Be concise but complete and include concrete steps."
    )

    params = inspect.signature(Agent.__init__).parameters
    model_keyword = "model" if "model" in params else None
    output_keyword = "result_type" if "result_type" in params else "output_type"
    prompt_keyword = "system_prompt" if "system_prompt" in params else "instructions"

    kwargs: dict[str, Any] = {
        output_keyword: BriefResponse,
        prompt_keyword: instructions,
        "timeout": int(os.getenv("LUMEN_AGENT_TIMEOUT_SECONDS", "30")),
    }

    if "api_key" in params:
        kwargs["api_key"] = api_key

    try:
        if model_keyword is None:
            agent = Agent(model=model, **kwargs)
        else:
            agent = Agent(**{model_keyword: model, **kwargs})
    except TypeError as exc:
        raise RuntimeError(f"Failed to initialize agent: {exc}") from exc

    prompt = (
        "Produce a structured mission brief for the following JSON request."
        f"\n\n{brief_request.model_dump_json()}"
    )

    try:
        result = agent.run_sync(prompt)
    except Exception as exc:  # pragma: no cover - integration surface.
        raise RuntimeError(f"Agent execution failed: {exc}") from exc

    if isinstance(result, BriefResponse):
        return result

    # Common PydanticAI response containers expose typed output in these attributes.
    for attr in ("data", "output", "result", "parsed"):
        value = getattr(result, attr, None)
        if isinstance(value, BriefResponse):
            return value

    if isinstance(result, dict):
        return BriefResponse.model_validate(result)

    raise RuntimeError("Unexpected response type from agent")


def validate_request_payload(payload: object) -> BriefRequest:
    return BriefRequest.model_validate(payload)


def format_error_payload(error: Exception) -> dict[str, object]:
    return {
        "error": str(error),
        "type": type(error).__name__,
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
    }
