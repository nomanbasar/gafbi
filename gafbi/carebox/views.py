from math import ceil

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

from products.models import Product
from .models import CareBoxApplication
from .serializers import (
    CareBoxProductSerializer,
    CareBoxApplicationCreateSerializer,
    CareBoxApplicationListSerializer,
    CareBoxFeedbackSerializer,
    AdminCareBoxStatusSerializer,
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
    permission_classes = [AllowAny]

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