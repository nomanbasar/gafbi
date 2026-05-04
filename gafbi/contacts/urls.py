from django.urls import path
from .views import (
    ContactMessageCreateView,
    ContactMessageListView,
    ContactMessageDetailView,
    ContactMessageDeleteView,
)

urlpatterns = [
    path("submit/", ContactMessageCreateView.as_view()),
    path("admin/", ContactMessageListView.as_view()),
    path("admin/<int:pk>/", ContactMessageDetailView.as_view()),
    path("admin/<int:pk>/delete/", ContactMessageDeleteView.as_view()),
]