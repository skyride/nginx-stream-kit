from django.contrib import admin

from .models import Stream, Distribution, Segment


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


@admin.register(Distribution)
class DistributionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "stream",
        "name",
        "created"
    )


@admin.register(Segment)
class SegmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "distribution",
        "sequence_number",
        "created"
    )