from __future__ import annotations

from django.contrib import admin

from .models import Brief


@admin.register(Brief)
class BriefAdmin(admin.ModelAdmin):
    list_display = ("mission_title", "created_at")
    list_filter = ("created_at",)
    search_fields = ("mission_title",)
