from uuid import uuid4

from django.db import models


STREAM_STATUS_CHOICES = [
    ("live", "Live"),
    ("finished", "Finished")
]

VIDEO_PROFILES = [
    "ultrafast",
    "superfast",
    "veryfast",
    "faster",
    "fast",
    "medium",
    "slow",
    "slower",
    "veryslow",
    "placebo"
]

VIDEO_CODEC_CHOICES = [
    ("libx264", "h264"),
    ("libx265", "h265 (HEVC)")
]

AUDIO_CODEC_CHOICES = [
    ("libfdk_aac", "AAC"),
]


class Stream(models.Model):
    """
    A stream from a user.
    """
    id = models.UUIDField(primary_key=True, default=uuid4)

    status = models.CharField(max_length=32, choices=STREAM_STATUS_CHOICES)
    key = models.CharField(max_length=128, db_index=True)

    app = models.CharField(max_length=255, default="")
    flash_version = models.CharField(max_length=255, default="")
    swf_url = models.CharField(max_length=255, default="")
    tcurl = models.CharField(max_length=255, default="")
    page_url = models.CharField(max_length=255, default="")
    client_id = models.IntegerField(default=0)
    source_ip = models.CharField(max_length=255, default="")

    started = models.DateTimeField(db_index=True, null=True, default=None)
    stopped = models.DateTimeField(db_index=True, null=True, default=None)

    created = models.DateTimeField(db_index=True, auto_now_add=True)
    last_updated = models.DateTimeField(db_index=True, auto_now=True)

    class Meta:
        ordering = ["created"]

    def __str__(self):
        return str(self.id)[:8] + "/" + self.key


class TranscodeProfile(models.Model):
    """
    A transcode profile for a distribution.
    """
    name = models.CharField(max_length=64)

    video_codec = models.CharField(max_length=64, choices=VIDEO_CODEC_CHOICES)
    video_bitrate = models.IntegerField()
    video_width = models.IntegerField()
    video_preset = models.CharField(
        max_length=32,
        choices=[(choice, choice.title()) for choice in VIDEO_PROFILES],
        default="veryfast")
    audio_codec = models.CharField(max_length=64, choices=AUDIO_CODEC_CHOICES)
    audio_bitrate = models.IntegerField()
    is_active = models.BooleanField(default=False)

    created = models.DateTimeField(db_index=True, auto_now_add=True)
    last_updated = models.DateTimeField(db_index=True, auto_now=True)

    def __str__(self):
        return self.name


class Distribution(models.Model):
    """
    A distribution is an encoded version of a stream. E.g. 480p, 240p,
    or source.
    """
    id = models.UUIDField(primary_key=True, default=uuid4)
    stream = models.ForeignKey(Stream,
        related_name="distributions",
        on_delete=models.CASCADE)
    transcode_profile = models.ForeignKey(TranscodeProfile,
        null=True,
        default=None,
        related_name="distributions",
        on_delete=models.CASCADE)
    name = models.CharField(max_length=64, db_index=True)

    created = models.DateTimeField(db_index=True, auto_now_add=True)
    last_updated = models.DateTimeField(db_index=True, auto_now=True)

    class Meta:
        unique_together = ("stream", "name")

    def __str__(self):
        return f"{self.stream}@{self.name}"


def generate_segment_filename(instance, filename):
    return f"{instance.distribution_id}/{uuid4()}.ts"


class Segment(models.Model):
    """
    A segment is a single video file as part of a distribution.
    """
    distribution = models.ForeignKey(Distribution,
        related_name="segments",
        on_delete=models.CASCADE)
    sequence_number = models.IntegerField()
    file = models.FileField(upload_to=generate_segment_filename)

    duration = models.FloatField()

    transcode_command = models.TextField(blank=True)
    transcode_stderr = models.TextField(blank=True)

    created = models.DateTimeField(db_index=True, auto_now_add=True)
    last_updated = models.DateTimeField(db_index=True, auto_now=True)

    class Meta:
        unique_together = ("distribution", "sequence_number")

    def __str__(self):
        return f"{self.distribution}:{self.sequence_number}"