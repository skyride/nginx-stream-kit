from uuid import uuid4

from django.db import models
from sizefield.models import FileSizeField

from apps.authorisation.models import StreamKey


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
    ("copy", "Copy")
]


class Stream(models.Model):
    """
    A stream from a user.
    """
    id = models.UUIDField(primary_key=True, default=uuid4)

    status = models.CharField(max_length=32, choices=STREAM_STATUS_CHOICES)
    key = models.CharField(max_length=128, db_index=True)
    stream_key = models.ForeignKey(StreamKey,
        null=True,
        blank=True,
        related_name="streams",
        on_delete=models.SET_NULL)

    name = models.CharField(max_length=64, default="", blank=True)
    app = models.CharField(max_length=255, default="")
    flash_version = models.CharField(max_length=255, default="")
    swf_url = models.CharField(max_length=255, default="")
    tcurl = models.CharField(max_length=255, default="")
    page_url = models.CharField(max_length=255, blank=True, default="")
    client_id = models.IntegerField(default=0)
    source_ip = models.CharField(max_length=255, default="")

    started = models.DateTimeField(
        db_index=True, null=True, blank=True, default=None)
    stopped = models.DateTimeField(
        db_index=True, null=True, blank=True, default=None)

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
    is_active = models.BooleanField(default=True)

    created = models.DateTimeField(db_index=True, auto_now_add=True)
    last_updated = models.DateTimeField(db_index=True, auto_now=True)

    def __str__(self):
        if self.is_active:
            return self.name
        else:
            return f"{self.name} (INACTIVE)"

    @property
    def total_bitrate(self):
        bitrate = 0
        if self.video_bitrate is not None:
            bitrate += self.video_bitrate
        
        if self.audio_bitrate is not None:
            bitrate += self.audio_bitrate

        return bitrate or None

    def get_video_transcode_parameters(self):
        if self.video_codec == "copy":
            return "-vcodec", "copy"
        else:
            return "-vcodec", self.video_codec, "-vb", str(self.video_bitrate)

    def get_audio_transcode_parameters(self):
        if self.audio_codec == "copy":
            return "-acodec", "copy"
        else:
            return "-acodec", self.audio_codec, "-ab", str(self.audio_bitrate)


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
    file_size = FileSizeField()

    duration = models.FloatField()

    transcode_command = models.TextField(blank=True)
    transcode_stderr = models.TextField(blank=True)

    created = models.DateTimeField(db_index=True, auto_now_add=True)
    last_updated = models.DateTimeField(db_index=True, auto_now=True)

    class Meta:
        unique_together = ("distribution", "sequence_number")

    def __str__(self):
        return f"{self.distribution}:{self.sequence_number}"


def generate_still_filename(instance, filename):
    return f"{instance.distribution_id}/{uuid4()}.png"

class Still(models.Model):
    """
    A still is a single frame (likely the first frame) from the associated
    segment as a png.
    """
    segment = models.ForeignKey(Segment,
        related_name="stills",
        on_delete=models.CASCADE)

    file = models.ImageField(upload_to=generate_still_filename)

    created = models.DateTimeField(db_index=True, auto_now_add=True)
    last_updated = models.DateTimeField(db_index=True, auto_now=True)

    def __str__(self):
        return f"{self.segment}:still_{self.pk}"