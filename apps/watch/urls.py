from django.urls import path

from . import views


urlpatterns = [
    path("", views.LiveStreamListView.as_view(), name="list_streams"),
    path("watch/<uuid:id>", views.WatchByStreamIdView.as_view(), name="watch"),
    path("watch/<str:key>", views.WatchByKeyView.as_view(), name="watch")
]
