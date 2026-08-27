from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from .models import Product, ProductReview
from math import ceil

from .serializers import (
    ProductSerializer,
    ProductDetailSerializer,
    ProductReviewSerializer,
)


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
            return Response({
                "success": False,
                "message": "Product not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductDetailSerializer(
            product,
            context={"request": request}
        )

        return Response({
            "success": True,
            "message": "Product details fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


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
            return Response({
                "success": False,
                "message": "Product not found",
                "data": None
            }, status=404)

        serializer = ProductSerializer(
            product,
            data=request.data,
            partial=True,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        product = serializer.save()

        return Response({
            "success": True,
            "message": "Product updated successfully",
            "data": ProductSerializer(product, context={"request": request}).data
        }, status=200)


# class ProductDeleteView(APIView):
#     permission_classes = [IsAdminUser]

#     def delete(self, request, pk):
#         product = Product.objects.filter(pk=pk).first()

#         if not product:
#             return Response({
#                 "success": False,
#                 "message": "Product not found",
#                 "data": None
#             }, status=404)

#         product.delete()

#         return Response({
#             "success": True,
#             "message": "Product deleted successfully",
#             "data": None
#         }, status=200)
    
class ProductDeleteView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, pk):
        product = Product.objects.filter(
            pk=pk,
            is_active=True
        ).first()

        if not product:
            return Response({
                "success": False,
                "message": "Product not found",
                "data": None
            }, status=404)

        product.is_active = False
        product.save(update_fields=["is_active"])

        return Response({
            "success": True,
            "message": "Product deleted successfully",
            "data": None
        }, status=200)

class ProductReviewCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, pk):
        product = Product.objects.filter(pk=pk, is_active=True).first()

        if not product:
            return Response({
                "success": False,
                "message": "Product not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review = serializer.save(product=product)

        return Response({
            "success": True,
            "message": "Review submitted successfully",
            "data": ProductReviewSerializer(review).data
        }, status=status.HTTP_201_CREATED)
    

class AllProductReviewListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        reviews = ProductReview.objects.filter(
            is_active=True,
            product__is_active=True
        ).select_related("product").order_by("-rating", "-created_at")

        serializer = ProductReviewSerializer(reviews, many=True)

        return Response({
            "success": True,
            "message": "All product reviews fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)