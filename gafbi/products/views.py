from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from .models import Product
from .serializers import ProductSerializer


class ProductListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        products = Product.objects.filter(is_active=True)
        serializer = ProductSerializer(products, many=True, context={"request": request})

        return Response({
            "success": True,
            "data": serializer.data
        })


class ProductDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        product = Product.objects.filter(pk=pk, is_active=True).first()

        if not product:
            return Response({"error": "Not found"}, status=404)

        serializer = ProductSerializer(product, context={"request": request})

        return Response({
            "success": True,
            "data": serializer.data
        })


class ProductCreateView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = ProductSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        product = serializer.save()

        return Response({
            "success": True,
            "data": ProductSerializer(product, context={"request": request}).data
        }, status=201)


class ProductUpdateView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        product = Product.objects.filter(pk=pk).first()

        if not product:
            return Response({"error": "Not found"}, status=404)

        serializer = ProductSerializer(product, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"success": True, "data": serializer.data})


class ProductDeleteView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, pk):
        product = Product.objects.filter(pk=pk).first()

        if not product:
            return Response({"error": "Not found"}, status=404)

        product.delete()

        return Response({"success": True})