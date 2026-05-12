from django.contrib import admin
from .models import SupportSession, SupportMessage


@admin.register(SupportSession)
class SupportSessionAdmin(admin.ModelAdmin):
    list_display = ["user__username", "supporter__username", "session_date", "status"]
    ordering = ["-created_at"]
    date_hierarchy = "created_at"


@admin.register(SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):
    list_display = ["sender__username", "session_id", "created_at"]
    ordering = ["-created_at"]
    date_hierarchy = "created_at"
    search_fields = ["text"]
