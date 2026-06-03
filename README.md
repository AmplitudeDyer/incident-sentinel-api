# Incident Sentinel API

Incident Sentinel API is a Django-based REST-style service for operational planning.
It powers two workflows:

- mission brief planning via `/api/v1/briefs/`
- incident triage and action-plan generation via `/api/v1/incidents/triage/`

The service is built on Pydantic and PydanticAI, with deterministic mock mode for
safe local testing and CI.

## Project goals

- Expose minimal, predictable endpoints for planning and incident triage.
- Keep agent behavior deterministic in test environments via a safe mock mode.
- Maintain strict local code quality tooling and CI across Python 3.12, 3.13 and 3.14.

## Layout

- `manage.py` - Django command entrypoint.
- `lumen_agent_api/` - Django project settings, ASGI/WSGI and root URLs.
- `briefs/` - API app with schemas, service layer, views, tests and config.
- `.github/workflows/ci.yml` - CI matrix on 3.12/3.13/3.14.
- `pyproject.toml` - dependencies and lint/type-check configuration.
- `.pre-commit-config.yaml` - local git hook config.

## Requirements

- Python 3.12+ (supports 3.12, 3.13, 3.14)
- Optional OpenAI-compatible API key for live agent runs.

## Environment

Copy `.env.example` to `.env` and set values.

## Local workflow

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python manage.py migrate
python manage.py runserver
```

### Common commands

- Install or update dependencies: `python -m pip install -e ".[dev]"`
- Start dev server: `python manage.py runserver`
- Run tests: `python manage.py test`
- Run lint: `make lint`

## API

### POST `/api/v1/briefs/`

Submit a mission brief request as JSON:

```json
{
  "mission_title": "North Star Market Expansion",
  "context": "Launch a new support channel for premium customers.",
  "objectives": ["Define rollout cadence", "Collect adoption metrics"],
  "constraints": ["No budget increase"],
  "target_date": "2026-12-31"
}
```

### POST `/api/v1/incidents/triage/`

Submit an incident report for triage and a proposed action plan:

```json
{
  "incident_title": "API Throughput Degradation",
  "description": "The public API has rising 5xx errors and latency for checkout traffic.",
  "severity": "high",
  "affected_systems": ["api-gateway", "checkout-service"],
  "observed_signals": ["latency spike", "increased error rate"],
  "reported_by": "on-call-ops"
}
```

### GET `/api/v1/health/`

Simple service health check returning:

```json
{
  "status": "ok",
  "service": "incident-sentinel-api"
}
```

## Mock mode

Set `LUMEN_MOCK_AGENT=true` to skip external model calls. Useful for local development
and tests.
