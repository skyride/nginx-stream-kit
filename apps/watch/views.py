from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from apps.streams.models import Stream, Distribution


class WatchView(TemplateView):
    template_name = "watch/watch.html"

    def get_context_data(self, **kwargs):
        stream: Stream = get_object_or_404(Stream,
        id=self.kwargs['id'],
        status="live")
        distribution: Distribution = stream.distributions.get(key="source")

        context = super().get_context_data(**kwargs)
        context['distribution'] = distribution
        return context