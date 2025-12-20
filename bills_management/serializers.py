"""
Serializers for bills management
"""
from rest_framework import serializers
from vendor_app.models import Vendor, MaterialPrice
from client_management.models import Material


class MaterialSerializer(serializers.ModelSerializer):
    """
    Serializer for material
    """
    class Meta:
        model = Material
        fields = ["id", "name", "description"]


class VendorSerializer(serializers.ModelSerializer):
    """
    Serializer for vendor
    """
    materials = MaterialSerializer(many=True, read_only=True)

    class Meta:
        model = Vendor
        fields = [
            "id", "name_nn", "location", "address",
            "phone_number_nn", "email", "materials", "extra_info"
        ]


class MaterialPriceSerializer(serializers.ModelSerializer):
    """
    Serializer for Material Prices
    """
    vendor = serializers.CharField(source="vendor_fk.name_nn", read_only=True)
    material = serializers.CharField(source="material_fk.name", read_only=True)

    class Meta:
        model = MaterialPrice
        fields = ["id", "vendor_fk", "vendor", "material_fk", "material", "price_nn"]
