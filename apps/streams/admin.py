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
        "created",
        "last_updated"
    )
    list_filter = (
        "app",
        "status"
    )