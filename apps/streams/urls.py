from django.urls import path

from . import views


urlpatterns = [
    path("nginx-callbacks/publish-start", views.OnPublishStartView.as_view()),
    path("nginx-callbacks/publish-done", views.OnPublishDoneView.as_view()),
    path("nginx-callbacks/distribution-start", views.OnDistributionStartView.as_view()),
    path("nginx-callbacks/distribution-done", views.OnDistributionDoneView.as_view())
]