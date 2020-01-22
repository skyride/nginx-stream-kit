from functools import partial

from django.contrib.auth.models import User
from django.db import models
from django.utils.crypto import get_random_string


class StreamKey(models.Model):
    """
    A stream key is owned by a user and all streams are initiated against
    a key.
    """
    key = models.CharField(max_length=16,
        default=partial(get_random_string, 16),
        unique=True)
    default_stream_name = models.CharField(max_length=64, default="")
    user = models.ForeignKey(User,
        null=True,
        related_name="stream_keys",
        on_delete=models.SET_NULL)
    transcode_profiles = models.ManyToManyField("streams.TranscodeProfile",
        related_name="stream_keys",
        blank=True)

    is_active = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_updated = models.DateTimeField(auto_now=True, db_index=True)

    def __str__(self):
        return self.key