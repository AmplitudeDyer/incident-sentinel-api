#!/usr/bin/env python
"""Django management command entrypoint for the Mission Brief API project."""

from __future__ import annotations

import os
import sys


def main() -> None:
    """Run the Django command-line utility."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lumen_agent_api.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django is required to run this project. Install it before continuing"
        ) from exc

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
