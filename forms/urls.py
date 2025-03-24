from django.urls import path
from .views import DynamicFormDetailView

urlpatterns = [
    path("forms/<int:form_id>/", DynamicFormDetailView.as_view()),
]
