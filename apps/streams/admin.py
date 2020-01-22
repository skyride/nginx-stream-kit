from django.contrib import admin
from django.db.models import Count, Sum, Func
from sizefield.templatetags.sizefieldtags import filesize

from .models import Stream, TranscodeProfile, Distribution, Segment


@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "status",
        "key",
        "source_ip",
        "no_of_segments",
        "started",
        "stopped"
    )
    list_filter = (
        "status",
    )

    def no_of_segments(self, instance: Distribution):
        return instance.segments_count

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            segments_count=Count("distributions__segments"))


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
        "__str__",
        "no_of_segments",
        "duration",
        "transcode_profile",
        "stream",
        "created",
    )
    list_filter = (
        "transcode_profile",
    )

    def no_of_segments(self, instance: Distribution):
        return instance.segments_count

    def duration(self, instance: Distribution):
        if instance.duration is not None:
            return '{:.2f}'.format(instance.duration)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            segments_count=Count("segments"),
            duration=Sum("segments__duration"))


@admin.register(Segment)
class SegmentAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "distribution",
        "sequence_number",
        "duration",
        "filesize",
        "created"
    )

    def filesize(self, instance: Segment):
        return filesize(instance.file_size)