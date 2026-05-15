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
