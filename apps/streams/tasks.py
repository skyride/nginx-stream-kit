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
    TranscodeProfile, Distribution, Segment, Still,
    generate_segment_filename)
    

def _transcode_segment(segment_id: UUID, distribution_id: UUID) -> UUID:
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
    media_worker = MediaWorker()
    file_data, stderr, transcode_command = media_worker.transcode_segment(
        source_segment.file.url,
        profile)

    # Parse metadata from stderr
    duration = media_worker.parse_duration_from_stderr(stderr)

    # Create segment
    segment: Segment = Segment(
        distribution=distribution,
        sequence_number=source_segment.sequence_number,
        transcode_command=" ".join(transcode_command),
        transcode_stderr=stderr,
        duration=duration)
    segment.file.save(f"{uuid4()}.ts", ContentFile(file_data))
    print(f"Transcoded segment {source_segment.sequence_number} of "
          f"{distribution.id} at {profile.name}")
    return segment.pk


@app.task(queue="transcode_high", autoretry_on=Exception)
def transcode_segment_high(segment_id: UUID, distribution_id: UUID) -> UUID:
    return _transcode_segment(segment_id, distribution_id)


@app.task(queue="transcode_low", autoretry_on=Exception)
def transcode_segment_low(segment_id: UUID, distribution_id: UUID) -> UUID:
    return _transcode_segment(segment_id, distribution_id)


def _generate_still_from_segment(segment_id: UUID) -> UUID:
    """
    Generate a still from a segment.
    """
    segment: Segment = Segment.objects.get(pk=segment_id)

    # Generate still
    media_worker = MediaWorker()
    file_data, timecode, stderr = media_worker.generate_still_from_video(
        segment.file.url)

    # Calculate timecode of this still

    # Create the still in our database and storage
    still: Still = Still(
        stream_id=segment.distribution.stream_id,
        timecode=timecode)
    still.file.save(f"{uuid4()}.jpg", ContentFile(file_data))
    print(f"Generated still from segment {segment.sequence_number} of "
          f"{segment.distribution_id}")
    return still.pk


@app.task(queue="transcode_high")
def generate_still_from_segment_high(segment_id: UUID) -> UUID:
    return _generate_still_from_segment(segment_id)

@app.task(queue="transcode_low")
def generate_still_from_segment_low(segment_id: UUID) -> UUID:
    return _generate_still_from_segment(segment_id)


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