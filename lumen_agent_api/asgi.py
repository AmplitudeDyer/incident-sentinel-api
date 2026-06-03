"""ASGI config for the Incident Sentinel API Django project."""

from __future__ import annotations

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lumen_agent_api.settings")

application = get_asgi_application()
