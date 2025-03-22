from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"logs", views.ImportLogViewSet)
router.register(r"imports", views.ImportViewSet, basename="imports")

urlpatterns = [
    path("", include(router.urls)),
]
