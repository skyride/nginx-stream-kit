from django.http import HttpResponse
from django.utils.timezone import now
from django.views import View
from rest_framework import mixins, viewsets, pagination

from .serializers import (
    StreamSerializer, DistributionSerializer, SegmentSerializer)
from .models import Stream, Distribution, Segment


class OnPublishStartView(View):
    def post(self, request):
        """
        Triggered by nginx-rtmp when a stream starts.
        """
        stream: Stream = Stream.objects.create(
            status="live",
            app=request.POST['app'],
            key=request.POST['name'],
            flash_version=request.POST['flashver'],
            swf_url=request.POST['swfurl'],
            tcurl=request.POST['tcurl'],
            page_url=request.POST['pageurl'],
            client_id=int(request.POST['clientid']),
            source_ip=request.POST['addr'],
            started=now())

        # Also create a "source" distribution
        Distribution.objects.create(
            stream=stream,
            name="source")

        print(f"Started stream {stream.id} from /{stream.app}/{stream.key}")
        return HttpResponse()


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