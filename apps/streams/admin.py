from django.contrib import admin

from .models import Stream, Distribution


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


@admin.register(Distribution)
class DistributionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "stream",
        "name",
        "key",
        "created",
        "last_updated"
    )
    list_filter = (
        "name",
        "key"
    )