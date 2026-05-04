from django.urls import path
from .views import (
    FAQListView,
    FAQCreateView,
    FAQUpdateView,
    FAQDeleteView,
)

urlpatterns = [
    path("", FAQListView.as_view()),
    path("admin/create/", FAQCreateView.as_view()),
    path("admin/<int:pk>/update/", FAQUpdateView.as_view()),
    path("admin/<int:pk>/delete/", FAQDeleteView.as_view()),
]