from django.urls import path
from .views import MyOrganizationView

urlpatterns = [
    path("profile/", MyOrganizationView.as_view()),
]
