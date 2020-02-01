from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register(r"streams", views.StreamViewSet)
router.register(r"distributions", views.DistributionViewSet)
router.register(r"segments", views.SegmentViewSet)


app_name = "streams"
urlpatterns = [
    re_path(r"internal-api/", include(router.urls)),
    path("nginx-callbacks/publish-start", views.OnPublishStartView.as_view()),
    path("nginx-callbacks/publish-done", views.OnPublishDoneView.as_view())
]