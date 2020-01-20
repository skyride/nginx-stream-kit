from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import Stream, Distribution, Segment
from .tasks import delete_storages_file


@receiver(post_delete, sender=Segment)
def delete_segment_file(sender, instance: Segment, using, **kwargs):
    """
    Triggered when a segment is deleted. Delete the file. Even though this is
    a small synchronous task we trigger it asynchronously on celery because
    deletions of distributions and streams can involve a lot of operations and
    we don't want to block the HTTP request.
    """
    delete_storages_file.delay(instance.file.name)