from django.urls import path
from .views import ConflictCheckView, ConflictDetailView, ConflictSummaryView, OfferCountdownView

urlpatterns = [
    path('conflicts/', ConflictCheckView.as_view(), name='conflict-check'),
    path('conflicts/<int:conflict_id>/', ConflictDetailView.as_view(), name='conflict-detail'),
    path('conflicts/summary/', ConflictSummaryView.as_view(), name='conflict-summary'),
    path('countdown/<int:application_id>/', OfferCountdownView.as_view(), name='offer-countdown'),
]
