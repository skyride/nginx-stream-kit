from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404

from apps.streams.models import Stream, Distribution


class WatchView(TemplateView):
    template_name = "watch/watch.html"

    def get_context_data(self, **kwargs):
        stream = self._get_stream()
        distribution: Distribution = stream.distributions.get(name="source")

        context = super().get_context_data(**kwargs)
        context['distribution'] = distribution
        return context

    def _get_stream(self) -> Stream:
        """
        Returns a stream object. This is a dummy method which should be
        overriden by a subclass.
        """
        raise NotImplementedError


class WatchByStreamIdView(WatchView):
    def _get_stream(self) -> Stream:
        """
        Attempts to get the stream by using the UUID kwarg provided from
        the URL pattern.
        """
        return get_object_or_404(Stream,
            id=self.kwargs['id'],
            status="live")


class WatchByNameView(WatchView):
    def _get_stream(self) -> Stream:
        """
        Attempts to get the stream using the stream's name.
        """
        return get_object_or_404(Stream.objects.exclude(name=""),
            name=self.kwargs['name'],
            status="live")


class LiveStreamListView(TemplateView):
    """
    Very basic listing view which shows currently live streams.
    """    
    template_name = "watch/list_streams.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['streams'] = Stream.objects.filter(status="live")
        return context