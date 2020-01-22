from typing import Iterable

from django.db.models.signals import post_delete, pre_save, post_save
from django.dispatch import receiver

from .models import Stream, Distribution, Segment
from .tasks import (
    transcode_segment_high, transcode_segment_low, delete_storages_file)


@receiver(post_delete, sender=Segment)
def delete_segment_file(sender, instance: Segment, using, **kwargs):
    """
    Triggered when a segment is deleted. Delete the file. Even though this is
    a small synchronous task we trigger it asynchronously on celery because
    deletions of distributions and streams can involve a lot of operations and
    we don't want to block the HTTP request.
    """
    delete_storages_file.delay(instance.file.name)


@receiver(pre_save, sender=Segment)
def populate_file_size(sender, instance: Segment, raw, **kwargs):
    """
    Populate the file_size filed with the actual filesize of file.
    """
    instance.file_size = instance.file.size


@receiver(post_delete, sender=Distribution)
def delete_distribution_folder(sender, instance: Distribution, using, **kwargs):
    """
    Triggered when a distribution is deleted. Delete the folder.
    """
    delete_storages_file.delay(str(instance.pk))


@receiver(post_save, sender=Distribution)
def backfill_segments(sender,
                      instance: Distribution,
                      created: bool,
                      raw: bool,
                      **kwargs):
    """
    When a distribution is created try to backfill missing segments.
    """
    if not raw and created and instance.transcode_profile is not None:
        stream: Stream = instance.stream
        source_distribution: Distribution = stream.distributions.get(
            transcode_profile__isnull=True)
        
        if stream.status == "live":
            # Trigger high priority jobs for the 10 most recent segments
            # then low priority for the rest
            segments = source_distribution.segments.order_by("-sequence_number")
            for i, segment in enumerate(segments):
                if i < 10:
                    transcode_segment_high.apply_async(
                        countdown=5, args=(segment.pk, instance.pk))
                else:
                    transcode_segment_low.apply_async(
                        countdown=5, args=(segment.pk, instance.pk))
        else:
            # Trigger low priority jobs start to finish
            segments = source_distribution.segments.order_by("sequence_number")
            for segment in segments:
                transcode_segment_low.apply_async(
                    countdown=5, args=(segment.pk, instance.pk))