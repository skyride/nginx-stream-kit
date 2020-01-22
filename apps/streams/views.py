from typing import Iterable

from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.utils.timezone import now
from django.views import View
from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets, pagination

from apps.authorisation.models import StreamKey

from .serializers import (
    StreamSerializer, DistributionSerializer, SegmentSerializer)
from .models import Stream, TranscodeProfile, Distribution, Segment


class OnPublishStartView(View):
    def post(self, request):
        """
        Triggered by nginx-rtmp when a stream starts.
        """
        key = request.POST['name']
        stream_key = self._authorise_key(key)

        stream: Stream = Stream.objects.create(
            status="live",
            app=request.POST['app'],
            key=request.POST['name'],
            name=stream_key.default_stream_name,
            stream_key=stream_key,
            flash_version=request.POST['flashver'],
            swf_url=request.POST['swfurl'],
            tcurl=request.POST['tcurl'],
            page_url=request.POST['pageurl'],
            client_id=int(request.POST['clientid']),
            source_ip=request.POST['addr'],
            started=now())

        # Create a "source" distribution
        Distribution.objects.create(
            stream=stream,
            name="source")

        # Create transcode distributions
        for transcode_profile in self._get_distributions(stream_key):
            Distribution.objects.create(
                stream=stream,
                name=transcode_profile.name,
                transcode_profile=transcode_profile)

        print(f"Started stream {stream.id} from /{stream.app}/{stream.key}")
        return HttpResponse()

    def _authorise_key(self, key: str) -> StreamKey:
        """
        Check the key is valid and return the StreamKey object, otherwise
        raise a 4xx error.
        """
        stream_key = get_object_or_404(StreamKey,
            key=key,
            is_active=True)

        # Check no other streams are live
        if stream_key.streams.filter(status="live").count() > 0:
            raise PermissionDenied("A stream is already live with this key.")

        return stream_key

    def _get_distributions(self,
                           stream_key: StreamKey) -> Iterable[TranscodeProfile]:
        """
        Returns a queryset of transcode profiles for the stream key.
        """
        return stream_key.transcode_profiles.filter(is_active=True)


class OnPublishDoneView(View):
    def post(self, request):
        """
        Triggered by nginx-rtmp when a stream stops.
        """
        stream: Stream = Stream.objects.get(
            app=request.POST['app'],
            key=request.POST['name'],
            status="live")
        stream.status = "finished"
        stream.stopped = now()
        stream.save()

        print(f"Stopped stream {stream.id} from /{stream.app}/{stream.key}")
        return HttpResponse()


class StreamViewSet(mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):
    queryset = Stream.objects.all()
    serializer_class = StreamSerializer
    filterset_fields = ['status', 'key']


class DistributionViewSet(mixins.ListModelMixin,
                          mixins.CreateModelMixin,
                          viewsets.GenericViewSet):
    queryset = Distribution.objects.all()
    serializer_class = DistributionSerializer
    filterset_fields = ['stream', 'name']


class SegmentViewSet(mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     viewsets.GenericViewSet):
    queryset = Segment.objects.order_by('-sequence_number')
    serializer_class = SegmentSerializer
    pagination_class = pagination.LimitOffsetPagination
    page_size = 150
    filterset_fields = ['distribution']