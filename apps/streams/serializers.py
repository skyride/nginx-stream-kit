from rest_framework import serializers

from .models import Stream, Distribution, Segment
from .tasks import transcode_segment


class StreamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stream
        fields = "__all__"


class DistributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Distribution
        fields = "__all__"


class SegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Segment
        fields = "__all__"

    def create(self, validated_data) -> Segment:
        """
        Queue our transcode jobs for other distributions.
        """
        source_distribution: Distribution = validated_data['distribution']
        segment: Segment = super().create(validated_data)
        
        # Trigger queued jobs if this is the source distribution
        if source_distribution.transcode_profile is None:
            distributions = source_distribution.stream.distributions.exclude(
                pk=source_distribution.pk).prefetch_related('transcode_profile')
            for distribution in distributions:
                transcode_segment.delay(segment.pk, distribution.pk)

        return segment