import os

from uuid import uuid4

from django.core.cache import cache
from rest_framework import serializers

from .media import MediaWorker
from .models import Stream, Distribution, Segment
from .tasks import transcode_segment_high


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
        read_only_fields = ["duration"]

    def create(self, validated_data) -> Segment:
        """
        Queue our transcode jobs for other distributions.
        """
        # Load into ffmpeg and get metadata
        tmp_path = f"/tmp/{uuid4()}.ts"
        with open(tmp_path, "wb") as f:
            f.write(validated_data['file'].read())
        media_worker = MediaWorker()
        stderr = media_worker.get_stderr_output(tmp_path)
        validated_data['duration'] = (
            media_worker.parse_duration_from_stderr(stderr))
        os.remove(tmp_path)

        segment: Segment = super().create(validated_data)
        
        # Trigger queued jobs if this is the source distribution
        source_distribution: Distribution = validated_data['distribution']
        if source_distribution.transcode_profile is None:
            distributions = source_distribution.stream.distributions.exclude(
                pk=source_distribution.pk).prefetch_related('transcode_profile')
            for distribution in distributions:
                transcode_segment_high.delay(segment.pk, distribution.pk)

        return segment