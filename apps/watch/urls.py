from django.urls import path

from . import views


urlpatterns = [
    path("watch/<uuid:id>", views.WatchView.as_view())
]