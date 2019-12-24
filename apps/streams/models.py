from uuid import uuid4

from django.db import models


STREAM_STATUS_CHOICES = [
    ("live", "Live"),
    ("finished", "Finished")
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
        return str(self.id)


class Distribution(models.Model):
    """
    A distribution of a stream.
    """
    stream = models.ForeignKey(Stream,
        related_name="distributions",
        on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    key = models.CharField(max_length=128)

    created = models.DateTimeField(db_index=True, auto_now_add=True)
    last_updated = models.DateTimeField(db_index=True, auto_now=True)

    def __str__(self):
        return f"{self.stream.id} - {self.name}"

    def get_playlist_path(self):
        return f"/hls/{self.stream.key}__{self.key}.m3u8"