from __future__ import annotations

from django.urls import path

from . import views

urlpatterns = [
    path("briefs/", views.create_brief, name="create-brief"),
    path("health/", views.health_view, name="health"),
]
