from django.urls import reverse
from rest_framework import serializers

from apps.streams.models import Stream, Distribution, Still


class BaseSerializer(serializers.HyperlinkedModelSerializer):
    """
    Base serializer with links and ids.
    """
    id = serializers.ReadOnlyField()
    serializer_related_field = serializers.PrimaryKeyRelatedField


class StreamDistributionSerializer(serializers.ModelSerializer):
    playlist_url = serializers.SerializerMethodField()

    class Meta:
        model = Distribution
        fields = (
            "id", "name", "playlist_url")

    def get_playlist_url(self, instance: Distribution):
        """
        Return a django resolved URL for the playlist.
        """
        return reverse("playlists:distribution", kwargs={
            "distribution_id": instance.pk})

class StreamSerializer(BaseSerializer):
    distributions = StreamDistributionSerializer(many=True)
    playlist_url = serializers.SerializerMethodField()
    still_url = serializers.SerializerMethodField()

    def get_playlist_url(self, instance: Stream):
        """
        Return a django URL resolved URL for the playlist.
        """
        return reverse("playlists:stream", kwargs={
            "stream_id": instance.pk})

    def get_still_url(self, instance: Stream):
        """
        Returns the URL of the latest still.
        """
        try:
            still = instance.stills.latest("timecode")
            if still is not None:
                return still.file.url
        except Still.DoesNotExist:
            return None

    class Meta:
        model = Stream
        fields = (
            "id", "url", "status", "distributions", "name", "started",
            "stopped", "playlist_url", "still_url")