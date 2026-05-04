from math import ceil

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from .models import ContactMessage
from .serializers import ContactMessageSerializer


class ContactMessageCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        contact = serializer.save()

        return Response({
            "success": True,
            "message": "Contact message submitted successfully",
            "data": ContactMessageSerializer(contact).data
        }, status=status.HTTP_201_CREATED)


class ContactMessageListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))

        if page < 1:
            page = 1

        if limit < 1:
            limit = 10

        messages = ContactMessage.objects.all()

        total = messages.count()
        total_page = ceil(total / limit) if total > 0 else 1

        start = (page - 1) * limit
        end = start + limit

        messages = messages[start:end]
        serializer = ContactMessageSerializer(messages, many=True)

        return Response({
            "success": True,
            "message": "Contact message list fetched successfully",
            "meta": {
                "page": page,
                "limit": limit,
                "total": total,
                "totalPage": total_page,
            },
            "data": serializer.data,
        }, status=status.HTTP_200_OK)


class ContactMessageDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        contact = ContactMessage.objects.filter(pk=pk).first()

        if not contact:
            return Response({
                "success": False,
                "message": "Contact message not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ContactMessageSerializer(contact)

        return Response({
            "success": True,
            "message": "Contact message fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class ContactMessageDeleteView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, pk):
        contact = ContactMessage.objects.filter(pk=pk).first()

        if not contact:
            return Response({
                "success": False,
                "message": "Contact message not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        contact.delete()

        return Response({
            "success": True,
            "message": "Contact message deleted successfully",
            "data": None
        }, status=status.HTTP_200_OK)