from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"auth", views.AuthViewSet, basename="auth")
router.register(r"users", views.UserViewSet)
router.register(r"roles", views.RoleViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
