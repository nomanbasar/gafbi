from django.urls import path
from .views import *

urlpatterns = [
    path("products/", CareBoxProductListView.as_view()),
    path("care-levels/", CareLevelListView.as_view()),
    path("eligibility/", CareBoxEligibilityView.as_view()),

    path("apply/", CareBoxApplyView.as_view()),

    path("my-applications/", MyCareBoxApplicationListView.as_view()),
    path("my-applications/<int:pk>/", MyCareBoxApplicationDetailView.as_view()),

    path("feedback/", CareBoxFeedbackView.as_view()),

    path("admin/applications/", AdminCareBoxApplicationListView.as_view()),
    path("admin/applications/<int:pk>/status/", AdminCareBoxApplicationStatusUpdateView.as_view()),

    path("admin-dashboard/users/", AdminDashboardUserListView.as_view()),

    path("admin-dashboard/orders/", AdminDashboardOrderListView.as_view()),
    path("admin-dashboard/orders/<int:pk>/", AdminDashboardOrderDetailsView.as_view()),
    path("admin-dashboard/orders/<int:pk>/confirm-shipment/", AdminConfirmShipmentView.as_view()),

    path("admin-dashboard/applications/", AdminDashboardApplicationListView.as_view()),
    path("admin-dashboard/applications/<int:pk>/", AdminDashboardApplicationDetailsView.as_view()),
    path("admin-dashboard/applications/<int:pk>/decision/", AdminApplicationDecisionView.as_view()),
]