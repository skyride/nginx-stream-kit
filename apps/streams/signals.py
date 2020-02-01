from typing import Iterable

from django.db.models.signals import post_delete, pre_save, post_save
from django.dispatch import receiver

from .models import Stream, Distribution, Segment, Still
from .tasks import (
    transcode_segment_high, transcode_segment_low,
    generate_still_from_segment_high, generate_still_from_segment_low,
    delete_storages_file)


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
@receiver(pre_save, sender=Still)
def populate_file_size(sender, instance, raw, **kwargs):
    """
    Populate the file_size field with the actual filesize of file.
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


@receiver(post_save, sender=Segment)
def generate_still(sender,
                   instance: Segment,
                   created: bool,
                   raw: bool,
                   **kwargs):
    """
    Trigger the generation of a still on every 5th segment from source.
    """
    if not raw and created:
        if instance.sequence_number % 5 == 0:
            distribution: Distribution = instance.distribution
            if distribution.transcode_profile_id is None:
                # Generate still, but base priority on whether its live
                if distribution.stream.status == "live":
                    generate_still_method = generate_still_from_segment_high
                else:
                    generate_still_method = generate_still_from_segment_low
                generate_still_method.apply_async(
                    countdown=5, args=(instance.pk, ))