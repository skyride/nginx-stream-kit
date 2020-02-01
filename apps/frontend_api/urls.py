from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()


app_name = "frontend_api"
urlpatterns = [
    path("", include(router.urls)),
]