"""
Serializers for Vendor Management
"""

from rest_framework import serializers
from django.core.exceptions import ValidationError
from client_management.models import Material
from .models import (
    WorkType,
    Worker,
    Vendor,
    MaterialPrice,
)
from .utils import validate_phone_number, validate_name, validate_email


class WorkTypeSerializer(serializers.ModelSerializer):
    """Serializer for Work types"""

    class Meta:
        """Meta class for WorkTypeSerializer"""

        model = WorkType
        fields = [
            "id",
            "name_nn",
            "description",
            "created_at",
            "created_by",
            "updated_by",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "created_by",
            "updated_by",
            "updated_at",
        ]

    def __init__(self, *args, **kwargs):
        # accept a fields argument to control which fields are included to show
        fields = kwargs.pop("fields", None)
        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field in existing - allowed:
                self.fields.pop(field)

    def validate_name_nn(self, attr):
        """validate name_nn field."""
        try:
            work_type_name = validate_name(name=attr, ignored_chars="&()")
        except ValidationError as ve:
            raise serializers.ValidationError(str(ve))

        qs = WorkType.objects.filter(name_nn__iexact=work_type_name)
        # It exclude current instance when updating (can remove it not mandatory)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError({"name": "Name already exist."})

        return work_type_name


class WorkerSerializer(serializers.ModelSerializer):
    """
    Serializer for Worker model.
    Creates a User first (via utils.create_worker_user),
    then creates Worker instance linked to that User.
    """

    name_nn = serializers.CharField(write_only=True)
    phone_number_nn = serializers.CharField(write_only=True)
    work_type_fk = serializers.PrimaryKeyRelatedField(
        queryset=WorkType.objects.all(), required=True
    )

    class Meta:
        """Meta class for WorkerSerializer"""

        model = Worker
        fields = [
            "id",
            "name_nn",
            "phone_number_nn",
            "email",
            "work_type_fk",
            "status_nn",
            "extra_info",
            "created_at",
            "updated_at",
        ]

    def validate_name_nn(self, value):
        """Use utils.validate_name to validate Worker name."""
        try:
            return validate_name(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))

    def validate_email(self, value):
        """Use utils.validate_email to validate Worker email."""
        if value:
            try:
                email = validate_email(value)
            except ValidationError as e:
                raise serializers.ValidationError(str(e))
            if Worker.objects.filter(email__iexact=email).exists():
                raise serializers.ValidationError(
                    "A worker with this email already exists."
                )
        return email

    def validate_phone_number_nn(self, value):
        """Use utils.validate_phone_number to validate Worker phone."""
        try:
            phone = validate_phone_number(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        if Worker.objects.filter(phone_number_nn=phone).exists():
            raise serializers.ValidationError(
                "A worker with this phone number already exists."
            )
        return phone

    def create(self, validated_data):
        """Create and return a new Worker."""
        return Worker.objects.create(**validated_data)


class WorkerRetrieveSerializer(serializers.ModelSerializer):
    """This serializer retrieve workers data"""

    work_type = serializers.CharField(source="work_type_fk.name_nn", read_only=True)

    class Meta:
        """Meta class for WorkerRetrieveSerializer"""

        model = Worker
        fields = [
            "id",
            "name_nn",
            "phone_number_nn",
            "email",
            "work_type_fk",
            "work_type",
            "status_nn",
            "extra_info",
            "created_at",
            "updated_at",
        ]


class MaterialSerializer(serializers.ModelSerializer):
    """Serializer for Material model."""

    class Meta:
        """Meta class for MaterialSerializer"""

        model = Material
        fields = [
            "id",
            "name",
            "description",
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "created_by",
            "updated_by",
            "updated_at",
        ]

    def __init__(self, *args, **kwargs):
        # accept a fields argument to control which fields are included
        fields = kwargs.pop("fields", None)
        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field in existing - allowed:
                self.fields.pop(field)

    def validate_name(self, attr):
        """validate name_nn field."""
        try:
            material_name = validate_name(name=attr, ignored_chars="")
        except ValidationError as ve:
            raise serializers.ValidationError(str(ve))
        qs = Material.objects.filter(name__iexact=material_name)
        # It exclude current instance when updating (can remove it not mandatory)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError({"name": "Name already exist."})
        return material_name


class VendorSerializer(serializers.ModelSerializer):
    """Serializer for Vendor model."""

    materials = serializers.PrimaryKeyRelatedField(
        queryset=Material.objects.all(), many=True
    )
    phone_number_nn = serializers.CharField(
        validators=[],
    )

    class Meta:
        """Meta class for VendorSerializer"""

        model = Vendor
        fields = [
            "id",
            "name_nn",
            "location",
            "address",
            "phone_number_nn",
            "email",
            "materials",
            "extra_info",
            "created_at",
            "created_by",
            "updated_by",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "created_by",
            "updated_by",
            "updated_at",
        ]

    def __init__(self, *args, **kwargs):
        # accept a `fields` argument to control which fields are included
        fields = kwargs.pop("fields", None)
        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field in existing - allowed:
                self.fields.pop(field)

    def validate_name_nn(self, attr):
        """validate name_nn field."""
        try:
            return validate_name(name=attr)
        except ValidationError as ve:
            raise serializers.ValidationError(str(ve))

    def validate_email(self, value):
        """Use utils.validate_email to validate vendor email."""
        if value:
            try:
                email = validate_email(value)
            except ValidationError as e:
                raise serializers.ValidationError(str(e))
            if Vendor.objects.filter(email__iexact=email).exists():
                raise serializers.ValidationError(
                    "A vendor with this email already exists."
                )
        return email

    def validate_phone_number_nn(self, value):
        """Use utils.validate_phone_number to validate vendor phone."""
        try:
            phone = validate_phone_number(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        if Vendor.objects.filter(phone_number_nn=phone).exists():
            raise serializers.ValidationError(
                "A vendor with this phone number already exists."
            )
        return phone

    def validate(self, attrs: dict):
        """Validate unique Vendor (name_nn, location, phone_number_nn, address)."""
        name = attrs.get("name_nn")
        location = attrs.get("location")
        phone = attrs.get("phone_number_nn")
        address = attrs.get("address")

        # build query
        qs = Vendor.objects.filter(
            name_nn=name,
            location=location,
            phone_number_nn=phone,
            address=address,
        )

        # exclude current instance when updating (mandatory here)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)

        if qs.exists():
            raise serializers.ValidationError(
                {"vendor": "A vendor already exists with these data."}
            )

        return attrs


class MaterialPriceSerializer(serializers.ModelSerializer):
    """Serializer for MaterialPrice model."""

    vendor_fk = serializers.PrimaryKeyRelatedField(queryset=Vendor.objects.all())
    material_fk = serializers.PrimaryKeyRelatedField(queryset=Material.objects.all())

    class Meta:
        """Meta class for SuppliedMaterialPriceSerializer"""

        model = MaterialPrice
        fields = [
            "id",
            "vendor_fk",
            "material_fk",
            "price_nn",
            "created_at",
            "created_by",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "created_by",
            "updated_at",
        ]

    def __init__(self, *args, **kwargs):
        # accept a `fields` argument to control which fields are included
        fields = kwargs.pop("fields", None)
        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field in existing - allowed:
                self.fields.pop(field)

    def validate(self, attrs: dict):
        """Validate data before creation."""
        vendor_id = attrs.get("vendor_fk")
        material_id = attrs.get("material_fk")

        qs = MaterialPrice.objects.filter(vendor_fk=vendor_id, material_fk=material_id)

        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError(
                {"material price": "vendor with this material's price already defined."}
            )
        return attrs
