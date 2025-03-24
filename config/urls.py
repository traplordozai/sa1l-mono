from django.urls import path
from .views import deepseek_chat, semantic_filter_parse

urlpatterns = [
    path("ai/chat", deepseek_chat),
    path("search/parse", semantic_filter_parse),
]
