"""
Views for Bills Management (using only APIView)
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from vendor_app.models import Vendor, Material, MaterialPrice
from .serializers import VendorSerializer, MaterialSerializer, MaterialPriceSerializer


class VendorListAPIView(APIView):
    """Return list of all vendors"""

    def get(self, request):
        vendors = Vendor.objects.all()
        serializer = VendorSerializer(vendors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MaterialListAPIView(APIView):
    """Return list of all materials"""

    def get(self, request):
        materials = Material.objects.all()
        serializer = MaterialSerializer(materials, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MaterialPriceAPIView(APIView):
    """Return material price for a vendor"""

    def get(self, request):
        vendor_id = request.query_params.get("vendor_id")
        material_id = request.query_params.get("material_id")

        if not vendor_id or not material_id:
            return Response(
                {"error": "vendor_id and material_id are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            price = MaterialPrice.objects.get(
                vendor_fk=vendor_id, material_fk=material_id
            )
            serializer = MaterialPriceSerializer(price)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except MaterialPrice.DoesNotExist:
            return Response({"price_nn": 0}, status=status.HTTP_200_OK)
