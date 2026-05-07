from math import ceil

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db.models import Q
from authentication.models import User

from products.models import Product
from .models import CareBoxApplication
from .serializers import (
    CareBoxProductSerializer,
    CareBoxApplicationCreateSerializer,
    CareBoxApplicationListSerializer,
    CareBoxFeedbackSerializer,
    AdminCareBoxStatusSerializer,
    AdminDashboardUserSerializer,
    AdminDashboardOrderListSerializer,
    AdminDashboardOrderDetailsSerializer,
    AdminConfirmShipmentSerializer,
    AdminDashboardApplicationListSerializer,
    AdminDashboardApplicationDetailsSerializer,
    AdminApplicationDecisionSerializer,
)


class CareBoxProductListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))

        if page < 1:
            page = 1
        if limit < 1:
            limit = 10

        products = Product.objects.filter(is_active=True)

        total = products.count()
        total_page = ceil(total / limit) if total > 0 else 1

        start = (page - 1) * limit
        end = start + limit

        serializer = CareBoxProductSerializer(products[start:end], many=True)

        return Response({
            "success": True,
            "message": "Care box product list fetched successfully",
            "meta": {
                "page": page,
                "limit": limit,
                "total": total,
                "totalPage": total_page,
               
            },
            "data": serializer.data,
        }, status=status.HTTP_200_OK)


class CareLevelListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        levels = [
            {"id": i, "name": f"Level of care {i}"}
            for i in range(1, 11)
        ]

        return Response({
            "success": True,
            "message": "Care level list fetched successfully",
            "data": levels,
        }, status=status.HTTP_200_OK)


class CareBoxEligibilityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        current_month = timezone.now().strftime("%Y-%m")

        already_exists = CareBoxApplication.objects.filter(
            user=request.user,
            application_month=current_month
        ).exclude(status="cancelled").exists()

        return Response({
            "success": True,
            "message": "Care box eligibility checked successfully",
            "data": {
                "eligible": not already_exists,
                "currentMonthUsed": already_exists,
                "maxTotalAmount": 42,
                "maxItems": 6,
                "month": current_month,
            }
        }, status=status.HTTP_200_OK)


class CareBoxApplyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CareBoxApplicationCreateSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        application = serializer.save()

        return Response({
            "success": True,
            "message": "Care box application submitted successfully",
            "data": CareBoxApplicationListSerializer(application).data,
        }, status=status.HTTP_201_CREATED)


class MyCareBoxApplicationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        applications = CareBoxApplication.objects.filter(
            user=request.user
        ).order_by("-created_at")

        serializer = CareBoxApplicationListSerializer(applications, many=True)

        return Response({
            "success": True,
            "message": "My care box application list fetched successfully",
            "data": serializer.data,
        }, status=status.HTTP_200_OK)


class MyCareBoxApplicationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        application = CareBoxApplication.objects.filter(
            pk=pk,
            user=request.user
        ).first()

        if not application:
            return Response({
                "success": False,
                "message": "Care box application not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "success": True,
            "message": "Care box application details fetched successfully",
            "data": CareBoxApplicationListSerializer(application).data,
        }, status=status.HTTP_200_OK)


class CareBoxFeedbackView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CareBoxFeedbackSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        feedback = serializer.save()

        return Response({
            "success": True,
            "message": "Feedback submitted successfully",
            "data": CareBoxFeedbackSerializer(feedback).data,
        }, status=status.HTTP_201_CREATED)


class AdminCareBoxApplicationListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        applications = CareBoxApplication.objects.all().order_by("-created_at")
        serializer = CareBoxApplicationListSerializer(applications, many=True)

        return Response({
            "success": True,
            "message": "Care box application list fetched successfully",
            "data": serializer.data,
        }, status=status.HTTP_200_OK)


class AdminCareBoxApplicationStatusUpdateView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        application = CareBoxApplication.objects.filter(pk=pk).first()

        if not application:
            return Response({
                "success": False,
                "message": "Care box application not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = AdminCareBoxStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        application.status = serializer.validated_data["status"]
        application.admin_note = serializer.validated_data.get("admin_note")
        application.save()

        return Response({
            "success": True,
            "message": "Care box application status updated successfully",
            "data": CareBoxApplicationListSerializer(application).data,
        }, status=status.HTTP_200_OK)
    


def admin_paginate_queryset(queryset, request):
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))

    if page < 1:
        page = 1
    if limit < 1:
        limit = 10

    total = queryset.count()
    total_page = ceil(total / limit) if total > 0 else 1

    start = (page - 1) * limit
    end = start + limit

    return queryset[start:end], {
        "page": page,
        "limit": limit,
        "total": total,
        "totalPage": total_page,
    }


class AdminDashboardUserListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        search = request.GET.get("search", "")

        users = User.objects.filter(is_staff=False).order_by("-created_at")

        if search:
            users = users.filter(
                Q(email_address__icontains=search) |
                Q(carebox_applications__first_name__icontains=search) |
                Q(carebox_applications__last_name__icontains=search)
            ).distinct()

        users, meta = admin_paginate_queryset(users, request)
        serializer = AdminDashboardUserSerializer(users, many=True)

        return Response({
            "success": True,
            "message": "Admin user list fetched successfully",
            "meta": meta,
            "data": serializer.data,
        }, status=status.HTTP_200_OK)


class AdminDashboardOrderListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        search = request.GET.get("search", "")
        shipment_status = request.GET.get("status", "")

        orders = CareBoxApplication.objects.all().order_by("-created_at")

        if search:
            orders = orders.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(id__icontains=search)
            )

        if shipment_status == "shipped":
            orders = orders.filter(status="delivered")
        elif shipment_status == "unshipped":
            orders = orders.exclude(status__in=["delivered", "cancelled"])
        elif shipment_status == "cancelled":
            orders = orders.filter(status="cancelled")

        orders, meta = admin_paginate_queryset(orders, request)
        serializer = AdminDashboardOrderListSerializer(orders, many=True)

        return Response({
            "success": True,
            "message": "Admin order list fetched successfully",
            "meta": meta,
            "data": serializer.data,
        }, status=status.HTTP_200_OK)


class AdminDashboardOrderDetailsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        order = CareBoxApplication.objects.filter(pk=pk).first()

        if not order:
            return Response({
                "success": False,
                "message": "Order not found",
                "data": None,
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = AdminDashboardOrderDetailsSerializer(order)

        return Response({
            "success": True,
            "message": "Order details fetched successfully",
            "data": serializer.data,
        }, status=status.HTTP_200_OK)


class AdminConfirmShipmentView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        order = CareBoxApplication.objects.filter(pk=pk).first()

        if not order:
            return Response({
                "success": False,
                "message": "Order not found",
                "data": None,
            }, status=status.HTTP_404_NOT_FOUND)

        if order.status == "delivered":
            return Response({
                "success": False,
                "message": "This order is already shipped",
                "data": AdminDashboardOrderDetailsSerializer(order).data,
            }, status=status.HTTP_400_BAD_REQUEST)

        order.status = "delivered"
        order.shipped_at = timezone.now()
        order.save(update_fields=["status", "shipped_at"])

        return Response({
            "success": True,
            "message": "Shipment confirmed successfully",
            "data": AdminDashboardOrderDetailsSerializer(order).data,
        }, status=status.HTTP_200_OK)


class AdminDashboardApplicationListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        search = request.GET.get("search", "")
        application_status = request.GET.get("status", "")

        applications = CareBoxApplication.objects.all().order_by("-created_at")

        if search:
            applications = applications.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )

        if application_status:
            applications = applications.filter(status=application_status)

        applications, meta = admin_paginate_queryset(applications, request)
        serializer = AdminDashboardApplicationListSerializer(applications, many=True)

        return Response({
            "success": True,
            "message": "Admin application list fetched successfully",
            "meta": meta,
            "data": serializer.data,
        }, status=status.HTTP_200_OK)


class AdminDashboardApplicationDetailsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        application = CareBoxApplication.objects.filter(pk=pk).first()

        if not application:
            return Response({
                "success": False,
                "message": "Application not found",
                "data": None,
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = AdminDashboardApplicationDetailsSerializer(application)

        return Response({
            "success": True,
            "message": "Application details fetched successfully",
            "data": serializer.data,
        }, status=status.HTTP_200_OK)


class AdminApplicationDecisionView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        application = CareBoxApplication.objects.filter(pk=pk).first()

        if not application:
            return Response({
                "success": False,
                "message": "Application not found",
                "data": None,
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = AdminApplicationDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        application.status = serializer.validated_data["status"]
        application.admin_note = serializer.validated_data.get("admin_note")
        application.save()

        return Response({
            "success": True,
            "message": "Application decision updated successfully",
            "data": AdminDashboardApplicationDetailsSerializer(application).data,
        }, status=status.HTTP_200_OK)