from rest_framework import mixins, viewsets, pagination

from apps.streams.models import Stream

from .serializers import StreamSerializer


class StreamViewSet(mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):
    queryset = (Stream.objects
        .prefetch_related("distributions")
        .order_by("-status", "-started"))
    serializer_class = StreamSerializer

    pagination_class = pagination.LimitOffsetPagination
    page_size = 100
    filterset_fields = ['status']