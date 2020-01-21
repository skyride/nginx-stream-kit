import ffmpeg
import os
import subprocess

from uuid import UUID, uuid4

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from storages.backends.s3boto3 import S3Boto3Storage

from streamkit.celery import app
from .media import MediaWorker
from .models import (
    TranscodeProfile, Distribution, Segment,
    generate_segment_filename)


@app.task(queue="transcode", ignore_result=True)
def transcode_segment(segment_id: UUID, distribution_id: UUID) -> UUID:
    """
    Transcode the segment provided and add it to the distribution specified.
    """
    distribution: Distribution = Distribution.objects.get(pk=distribution_id)
    source_segment: Segment = Segment.objects.get(pk=segment_id)
    profile: TranscodeProfile = distribution.transcode_profile

    # Stop now if this distribution doesn't actually have a profile
    if profile is None:
        return None

    # Perform transcode
    worker = MediaWorker()
    file_data, stderr, transcode_command = worker.transcode_segment(
        source_segment.file.url,
        profile)

    segment: Segment = Segment(
        distribution=distribution,
        sequence_number=source_segment.sequence_number,
        transcode_command=" ".join(transcode_command),
        transcode_stderr=stderr)
    segment.file.save(f"{uuid4()}.ts", ContentFile(file_data))

    print(f"Transcoded segment {source_segment.sequence_number} of "
          f"{distribution.id} at {profile.name}, locally deleting now")


@app.task(queue="s3ops", ignore_result=True)
def delete_storages_file(path):
    """
    Delete a file in our Django-storages S3 object. This method assumes any
    database references have already been deleted, so it's merely the file
    we're concerned with.
    """
    storage: S3Boto3Storage = default_storage
    storage.delete(path)
    print(f"Deleted {path}")