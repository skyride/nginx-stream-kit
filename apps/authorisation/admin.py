from django.contrib import admin
from django.db.models import Count

from .models import StreamKey


@admin.register(StreamKey)
class StreamKeyAdmin(admin.ModelAdmin):
    list_display = (
        "key",
        "user",
        "no_of_streams",
        "active_transcode_profiles",
        "is_active",
        "created",
        "last_updated"
    )

    def no_of_streams(self, instance: StreamKey):
        return instance.streams_count

    def active_transcode_profiles(self, instance: StreamKey):
        profiles = instance.transcode_profiles.filter(is_active=True)
        if profiles.count() > 0:
            return ", ".join(profiles.values_list('name', flat=True))

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            streams_count=Count("streams"))