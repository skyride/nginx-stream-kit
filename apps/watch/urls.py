from django.urls import path

from . import views


app_name = "watch"
urlpatterns = [
    path("", views.LiveStreamListView.as_view(), name="list_streams"),
    path("watch/<uuid:id>", views.WatchByStreamIdView.as_view(), name="watch"),
    path("watch/<str:name>", views.WatchByNameView.as_view(), name="watch")
]