from django.urls import path

from . import views


urlpatterns = [
    path("playlists/distributions/<uuid:distribution_id>.m3u8",
        views.DistributionPlaylistView.as_view(),
        name="distribution_playlist")
]
