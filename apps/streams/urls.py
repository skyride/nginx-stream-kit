from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register(r"distributions", views.DistributionViewSet)
router.register(r"segments", views.SegmentViewSet)


urlpatterns = [
    re_path(r"api/", include(router.urls)),
    path("nginx-callbacks/publish-start", views.OnPublishStartView.as_view()),
    path("nginx-callbacks/publish-done", views.OnPublishDoneView.as_view())
]