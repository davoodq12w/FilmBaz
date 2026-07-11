from django.contrib import admin
from .models import *


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'content_type', 'object_id', 'timestamp')
    list_filter = ('action', 'content_type')
    search_fields = ('details', 'user__username')
