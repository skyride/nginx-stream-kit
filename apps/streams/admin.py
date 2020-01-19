from django.contrib import admin

from .models import Stream, TranscodeProfile, Distribution, Segment


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


@admin.register(TranscodeProfile)
class TranscodeProfileAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "video_codec",
        "video_bitrate",
        "video_width",
        "audio_codec",
        "audio_bitrate",
        "is_active"
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