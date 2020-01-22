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
        "no_of_segments",
        "size",
        "source_ip",
        "started",
        "stopped"
    )
    list_filter = (
        "status",
    )

    def no_of_segments(self, instance: Distribution):
        return instance.segments_count

    def size(self, instance: Distribution):
        return filesize(instance.size)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            segments_count=Count("distributions__segments"),
            size=Sum("distributions__segments__file_size"))


@admin.register(TranscodeProfile)
class TranscodeProfileAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "no_of_distributions",
        "video_codec",
        "video_bitrate",
        "video_width",
        "audio_codec",
        "audio_bitrate",
        "is_active"
    )

    def no_of_distributions(self, instance: TranscodeProfile):
        return instance.distributions_count

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            distributions_count=Count("distributions"))


@admin.register(Distribution)
class DistributionAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "no_of_segments",
        "duration",
        "size",
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

    def size(self, instance: Distribution):
        return filesize(instance.size)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            segments_count=Count("segments"),
            duration=Sum("segments__duration"),
            size=Sum("segments__file_size"))


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