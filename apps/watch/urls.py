from django.urls import path

from . import views


urlpatterns = [
    path("watch/<uuid:id>", views.WatchByStreamIdView.as_view()),
    path("watch/<str:key>", views.WatchByKeyView.as_view())
]
