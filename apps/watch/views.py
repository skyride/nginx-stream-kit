from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from apps.streams.models import Stream, Distribution


class WatchView(TemplateView):
    template_name = "watch/watch.html"

    def get_context_data(self, **kwargs):
        stream = self._get_stream()
        distribution: Distribution = stream.distributions.get(key="source")

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


class WatchByKeyView(WatchView):
    def _get_stream(self) -> Stream:
        """
        Attempts to get the stream using the key used on the ingest.
        """
        return get_object_or_404(Stream,
            key=self.kwargs['key'],
            status="live")
