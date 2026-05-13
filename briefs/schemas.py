from __future__ import annotations

from pydantic import BaseModel, Field, ValidationError


class BriefRequest(BaseModel):
    """Input schema for a mission-brief request."""

    mission_title: str = Field(min_length=3, max_length=140)
    context: str = Field(min_length=10, max_length=2_000)
    objectives: list[str] = Field(min_length=1)
    constraints: list[str] = Field(default_factory=list)
    target_date: str | None = None


class BriefResponse(BaseModel):
    """Structured response returned by the mission planning agent."""

    mission_title: str
    executive_summary: str
    key_steps: list[str] = Field(default_factory=list)
    deliverables: list[str] = Field(default_factory=list)
    resources: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
