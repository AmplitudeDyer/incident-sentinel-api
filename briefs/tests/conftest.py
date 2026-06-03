from __future__ import annotations


def build_request(
    *,
    mission_title: str = "North Star Market Expansion",
    context: str = "Launch a new support channel for premium customers.",
    objectives: list[str] | None = None,
    constraints: list[str] | None = None,
    target_date: str | None = "2026-12-31",
) -> dict[str, object]:
    return {
        "mission_title": mission_title,
        "context": context,
        "objectives": objectives or ["Define rollout cadence", "Collect adoption metrics"],
        "constraints": constraints or ["No budget increase"],
        "target_date": target_date,
    }


def build_incident_request(
    *,
    incident_title: str = "API Throughput Degradation",
    description: str = "Monitoring reported elevated latency and increased 5xx responses on the public API.",
    severity: str = "high",
    affected_systems: list[str] | None = None,
    observed_signals: list[str] | None = None,
    reported_by: str | None = "on-call-ops",
) -> dict[str, object]:
    return {
        "incident_title": incident_title,
        "description": description,
        "severity": severity,
        "affected_systems": affected_systems or ["api-gateway", "checkout-service"],
        "observed_signals": observed_signals or ["latency p95 spike", "error rate growth"],
        "reported_by": reported_by,
    }
