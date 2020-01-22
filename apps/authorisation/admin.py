from django.contrib import admin

from .models import StreamKey


@admin.register(StreamKey)
class StreamKeyAdmin(admin.ModelAdmin):
    list_display = (
        "key",
        "user",
        "active_transcode_profiles",
        "is_active",
        "created",
        "last_updated"
    )

    def active_transcode_profiles(self, instance: StreamKey):
        profiles = instance.transcode_profiles.filter(is_active=True)
        if profiles.count() > 0:
            return ", ".join(profiles.values_list('name', flat=True))