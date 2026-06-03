from __future__ import annotations

from django.urls import path

from . import views

urlpatterns = [
    path("briefs/", views.create_brief, name="create-brief"),
    path("incidents/triage/", views.triage_incident, name="triage-incident"),
    path("health/", views.health_view, name="health"),
]
