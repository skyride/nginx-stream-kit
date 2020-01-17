from django.contrib import admin

from .models import Stream


@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "status",
        "app",
        "key",
        "source_ip",
        "started",
        "stopped"
    )
    list_filter = (
        "app",
        "status"
    )