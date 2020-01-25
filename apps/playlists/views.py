from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views import View

from apps.streams.models import Stream, Distribution, Segment


class DistributionPlaylistView(View):
    """
    Generates m3u8 playlist files for a distribution.
    """

    def get(self, request, distribution_id):
        distribution: Distribution = get_object_or_404(Distribution,
            id=distribution_id)

        # Handle live/finished status
        if distribution.stream.status == "live":
            return self._do_live(request, distribution)
        else:
            return self._do_vod(request, distribution)

    def _do_live(self, request, distribution: Distribution):
        """
        Generate and return a live playlist.
        """
        segments = distribution.segments.order_by('-sequence_number')[:6]
        segments = list(reversed(segments))

        context = {'segments': segments}

        return HttpResponse(
            content=render(request, "playlists/live.m3u8", context),
            content_type="application/x-mpegURL")

    def _do_vod(self, request, distribution: Distribution):
        """
        Generate and return a vod playlist.
        """
        context = {
            'segments': distribution.segments.order_by('sequence_number')}

        return HttpResponse(
            content=render(request, "playlists/vod.m3u8", context),
            content_type="application/x-mpegURL")


class StreamPlaylistView(View):
    """
    Generates m3u8 playlist files for a stream.
    """
    def get(self, request, stream_id):
        stream: Stream = get_object_or_404(Stream,
            id=stream_id)

        context = {'distributions':
            stream.distributions.select_related("transcode_profile")}

        return HttpResponse(
            content=render(request, "playlists/variants.m3u8", context),
            content_type="application/x-mpegURL")