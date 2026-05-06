"""WSGI config for the Mission Brief API Django project."""

from __future__ import annotations

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lumen_agent_api.settings")

application = get_wsgi_application()
