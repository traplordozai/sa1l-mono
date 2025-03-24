from django.urls import path
from .dev_views import populate_fake_data

urlpatterns = [
    path("populate", populate_fake_data),
]
