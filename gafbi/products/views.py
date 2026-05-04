from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from .models import Product
from .serializers import ProductSerializer
from math import ceil


class ProductListView(APIView):
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

        products = products[start:end]

        serializer = ProductSerializer(products, many=True)

        return Response({
            "success": True,
            "message": "Product list fetched successfully",
            "meta": {
                "page": page,
                "limit": limit,
                "total": total,
                "totalPage": total_page,
            },
            "data": serializer.data,
        }, status=status.HTTP_200_OK)


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
        serializer = ProductSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        product = serializer.save(is_active=True)  

        return Response({
            "success": True,
            "message": "Product created successfully",
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