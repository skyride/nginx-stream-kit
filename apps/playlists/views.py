from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views import View

from apps.streams.models import Distribution, Segment


class DistributionPlaylistView(View):
    template = "playlists/distribution.m3u8"

    def get(self, request, distribution_id):
        """
        Return a live m3u8 file for this distribution.
        """
        distribution: Distribution = get_object_or_404(Distribution,
            id=distribution_id,
            stream__status="live")

        segments = distribution.segments.order_by('-sequence_number')[:6]
        segments = list(reversed(segments))
        context = {'segments': segments}

        return HttpResponse(
            content=render(request, self.template, context),
            content_type="application/x-mpegURL"
            )