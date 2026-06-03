from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

IncidentSeverity = Literal["low", "medium", "high", "critical"]
IncidentPriority = Literal["P4", "P3", "P2", "P1"]


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


class IncidentTriageRequest(BaseModel):
    """Input schema for an incident triage payload."""

    incident_title: str = Field(min_length=3, max_length=140)
    description: str = Field(min_length=12, max_length=4_000)
    severity: IncidentSeverity = "medium"
    affected_systems: list[str] = Field(default_factory=list)
    observed_signals: list[str] = Field(default_factory=list)
    reported_by: str | None = None


class IncidentTriageResponse(BaseModel):
    """Structured response returned by the incident triage assistant."""

    incident_title: str
    severity: IncidentSeverity
    priority: IncidentPriority
    triage_summary: str
    immediate_actions: list[str] = Field(default_factory=list)
    investigation_steps: list[str] = Field(default_factory=list)
    communication_updates: list[str] = Field(default_factory=list)
    stakeholders_to_notify: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
