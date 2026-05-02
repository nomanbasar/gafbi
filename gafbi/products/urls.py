from django.urls import path
from .views import *

urlpatterns = [
    path("", ProductListView.as_view()),
    path("<int:pk>/", ProductDetailView.as_view()),

    path("admin/create/", ProductCreateView.as_view()),
    path("admin/<int:pk>/update/", ProductUpdateView.as_view()),
    path("admin/<int:pk>/delete/", ProductDeleteView.as_view()),
]