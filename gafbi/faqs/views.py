from math import ceil

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from .models import FAQ
from .serializers import FAQSerializer


class FAQListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))

        if page < 1:
            page = 1

        if limit < 1:
            limit = 10

        faqs = FAQ.objects.filter(is_active=True)

        total = faqs.count()
        total_page = ceil(total / limit) if total > 0 else 1

        start = (page - 1) * limit
        end = start + limit

        faqs = faqs[start:end]
        serializer = FAQSerializer(faqs, many=True)

        return Response({
            "success": True,
            "message": "FAQ list fetched successfully",
            "data": serializer.data,
            "meta": {
                "page": page,
                "limit": limit,
                "total": total,
                "totalPage": total_page,
            }
        }, status=status.HTTP_200_OK)


class FAQCreateView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = FAQSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        faq = serializer.save(is_active=True)

        return Response({
            "success": True,
            "message": "FAQ created successfully",
            "data": FAQSerializer(faq).data
        }, status=status.HTTP_201_CREATED)


class FAQUpdateView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        faq = FAQ.objects.filter(pk=pk).first()

        if not faq:
            return Response({
                "success": False,
                "message": "FAQ not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = FAQSerializer(faq, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        faq = serializer.save()

        return Response({
            "success": True,
            "message": "FAQ updated successfully",
            "data": FAQSerializer(faq).data
        }, status=status.HTTP_200_OK)


class FAQDeleteView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, pk):
        faq = FAQ.objects.filter(pk=pk).first()

        if not faq:
            return Response({
                "success": False,
                "message": "FAQ not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        faq.delete()

        return Response({
            "success": True,
            "message": "FAQ deleted successfully",
            "data": None
        }, status=status.HTTP_200_OK)