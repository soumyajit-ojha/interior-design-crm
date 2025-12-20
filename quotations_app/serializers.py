import re
from decimal import Decimal

from rest_framework import serializers
from .models import *
from leads_app.serializers import LeadForQuotationSerializer
from utils.constants import MAX_COMPANY_LOGO_SIZE
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "user_type_nn",
        ]


class BHKTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BHKType
        fields = ["id", "bhk_name", "description"]

    def validate_bhk_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("BHK name cannot be empty.")

        if not re.match(r"^[A-Za-z0-9 ]+$", value):
            raise serializers.ValidationError(
                "BHK name can only contain letters, digits, and spaces. Special characters are not allowed."
            )
        if not (1 <= len(value) <= 20):
            raise serializers.ValidationError("BHK name can be max 20 characters long.")
        return value


class ScopeOfWorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScopeOfWork
        fields = ["id", "scope_of_work", "description"]

    def validate_scope_of_work(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Scope of work cannot be empty.")

        if not re.match(r"^[A-Za-z0-9]+$", value):
            raise serializers.ValidationError(
                "Scope of work can only contain letters and digits. Spaces and special characters are not allowed."
            )
        if not (1 <= len(value) <= 20):
            raise serializers.ValidationError(
                "Scope of work can be max 20 characters long."
            )
        return value


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for Project model.
    Validates that the project name is not empty, within 50 characters,
    and contains only allowed characters: letters, digits, spaces, and symbols . , - & ( )
    Adds client_count: number of related ClientDetails.
    """

    client_count = serializers.SerializerMethodField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)

    class Meta:
        """Meta class"""

        model = Project
        fields = ["id", "project_name", "city_or_area", "society_type", "pincode", "client_count", "status"]

    def get_client_count(self, obj):
        # Assumes related_name='clientdetails_set' or similar on ClientDetails FK to Project
        # Adjust if your related_name is different
        return obj.project_clients.count()
    
    def get_status(self, obj):
        """
        Returns the overall status of the project's clients.
        - If any client is "Ongoing", returns "Ongoing"
        - Else if any client is "On Hold", returns "On Hold"
        - Else if all are "Completed", returns "Completed"
        - If no clients, returns None
        """
        statuses = list(obj.project_clients.values_list("status", flat=True))
        if not statuses:
            return "No Clients"
        if "Ongoing" in statuses:
            return "Ongoing"
        if "On Hold" in statuses:
            return "On Hold"
        if all(status == "Completed" for status in statuses):
            return "Completed"
        return "No Clients"

    def validate_project_name(self, value):
        """
        Validate project_name:
        - Not empty
        - Length between 3 and 30 characters
        - Only letters, numbers, spaces, and symbols: . , - & ( )
        - No consecutive special characters like ... or ---
        """
        stripped_value = value.strip()
        if not stripped_value:
            raise serializers.ValidationError("Project name cannot be empty.")

        if len(stripped_value) < 3 or len(stripped_value) > 30:
            raise serializers.ValidationError(
                "Project name must be between 3 and 30 characters long."
            )
        pattern = r"^[A-Za-z0-9\s.,\-&()]+$"
        if not re.match(pattern, stripped_value):
            raise serializers.ValidationError(
                "Project name can only contain letters, numbers, spaces, "
                "and symbols: . , - & ( )"
            )
        repeated_symbols_pattern = r"([.,\-&()])\1{1,}"
        if re.search(repeated_symbols_pattern, stripped_value):
            raise serializers.ValidationError(
                "Project name cannot contain repeated special characters like '...', '---', etc."
            )

        return stripped_value

    def validate_city_or_area(self, value):
        """
        Validate city_or_area:
        - Not empty
        - Minimum length 2 characters
        - Only allowed characters: A-Z, a-z, 0-9, space, . , - ' ()
        """
        stripped_value = value.strip()
        if not stripped_value:
            raise serializers.ValidationError("City/area cannot be empty.")

        if len(stripped_value) < 2 or len(stripped_value) > 30:
            raise serializers.ValidationError(
                "City/area must be between 2 and 30 characters long."
            )

        pattern = r"^[A-Za-z0-9\s.,'\-()]+$"
        if not re.match(pattern, stripped_value):
            raise serializers.ValidationError(
                "City/area may only contain letters, numbers, spaces, and symbols: . , - ' ( )"
            )

        return stripped_value

    def validate_society_type(self, value):
        """Ensure society_type is not empty or whitespace"""
        stripped_value = value.strip()
        if not stripped_value:
            raise serializers.ValidationError("Society type cannot be empty.")
        return stripped_value

    def validate_pincode(self, value):
        """Ensure pincode is not empty and is 6 digits"""
        stripped_value = value.strip()
        if not stripped_value:
            raise serializers.ValidationError("Pin code cannot be empty.")
        if not re.match(r"^\d{6}$", stripped_value):
            raise serializers.ValidationError("Pin code must be exactly 6 digits.")
        return stripped_value


class MaterialTierSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialTier
        fields = ["id", "tier_name", "tier_description"]

    def validate_tier_name(self, value):
        stripped_value = value.strip()
        if not stripped_value:
            raise serializers.ValidationError("Tier name cannot be empty.")

        if not re.match(r"^[A-Za-z ]+$", stripped_value):
            raise serializers.ValidationError(
                "Tier name can only contain alphabetic characters and spaces. Digits and special characters are not allowed."
            )
        if not (1 <= len(value) <= 20):
            raise serializers.ValidationError(
                "Tire name can be max 20 characters long."
            )
        return stripped_value


class RoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomType
        fields = ["id", "room_name", "room_description"]

    def validate_room_name(self, value):
        stripped_value = value.strip()
        if not stripped_value:
            raise serializers.ValidationError("room_name cannot be empty.")

        if not re.match(r"^[A-Za-z0-9 ]+$", stripped_value):
            raise serializers.ValidationError(
                "Room name can only contain alphabetic characters, spaces and digits. Special characters are not allowed."
            )
        if not (1 <= len(value) <= 20):
            raise serializers.ValidationError(
                "Room name can be max 20 characters long."
            )
        return value


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ["id", "unit_name", "unit_abbreviation"]

    def validate_unit_name(self, value):
        stripped_value = value.strip()
        if not stripped_value:
            raise serializers.ValidationError("Unit name cannot be empty.")

        if not re.match(r"^[A-Za-z]+$", stripped_value):
            raise serializers.ValidationError(
                "Unit name can only contain alphabetic characters."
            )
        if not (1 <= len(value) <= 20):
            raise serializers.ValidationError(
                "Unit name can be max 20 characters long."
            )
        return value

    def validate_unit_abbreviation(self, value):
        stripped_value = value.strip()
        if not stripped_value:
            raise serializers.ValidationError("Unit abbreviation cannot be empty.")

        if not re.match(r"^[A-Za-z.]+$", stripped_value):
            raise serializers.ValidationError(
                "Unit abbreviation can only contain alphabetic characters, spaces and digits. Special characters are not allowed."
            )
        if not (1 <= len(value) <= 10):
            raise serializers.ValidationError(
                "Unit abbreviation can be max 20 characters long."
            )
        return value


class ShutterFinishSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShutterFinish
        fields = ["id", "shutter_finish_name", "description"]

    def validate_shutter_finish_name(self, value):
        stripped_value = value.strip()
        if not stripped_value:
            raise serializers.ValidationError("Shutter Finish cannot be empty.")

        if not re.match(r"^[A-Za-z ]+$", stripped_value):
            raise serializers.ValidationError(
                "Shutter Finish can only contain alphabetic"
            )

        if not (1 <= len(value) <= 20):
            raise serializers.ValidationError(
                "Shutter Finish can be max 20 characters long."
            )
        return value


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ["id", "item_name", "has_dimension", "item_description"]

    def validate_item_name(self, value):
        stripped_value = value.strip()
        if not stripped_value:
            raise serializers.ValidationError("Item name cannot be empty.")

        if not re.match(r"^[A-Za-z ]+$", stripped_value):
            raise serializers.ValidationError(
                "Item name can only contain alphabetic character ans space."
            )

        if not (1 <= len(value) <= 20):
            raise serializers.ValidationError(
                "Item name can be max 20 characters long."
            )
        return value


class ItemPriceSerializer(serializers.ModelSerializer):
    shutter_finish = serializers.PrimaryKeyRelatedField(
        queryset=ShutterFinish.objects.all(), required=False, allow_null=True
    )
    unit = serializers.PrimaryKeyRelatedField(
        queryset=Unit.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = ItemPrice
        fields = ["id", "item", "shutter_finish", "unit", "price_per_unit"]

    def validate(self, data):
        item = data.get("item")
        # If Item does NOT have dimensions
        if item.has_dimension:
            missing_fields = []
            if not data.get("unit"):
                missing_fields.append("unit")
            if not data.get("shutter_finish"):
                missing_fields.append("shutter_finish")
            if not data.get("price_per_unit"):
                missing_fields.append("price_per_unit")

            if missing_fields:
                raise serializers.ValidationError(
                    {
                        field: f"{field} is required when item has dimensions."
                        for field in missing_fields
                    }
                )

        # If Item does NOT have dimensions
        else:
            unused_fields = []
            if data.get("unit") is not None:
                unused_fields.append("unit")
            if data.get("shutter_finish") is not None:
                unused_fields.append("shutter_finish")
            if not data.get("price_per_unit"):
                raise serializers.ValidationError(
                    {
                        "price_per_unit": "Price per unit must required when item has no dimensions."
                    }
                )
            if unused_fields:
                raise serializers.ValidationError(
                    {
                        field: f"{field} should not be provided when item has no dimensions."
                        for field in unused_fields
                    }
                )
        return data


class ItemPriceDetailsSerializer(serializers.ModelSerializer):
    """Serializer to retrieve item price and shutter_finish based on unit and item."""
    shutter_finish = ShutterFinishSerializer()
    price_per_unit = serializers.DecimalField(max_digits=10, decimal_places=2, required=False,
    allow_null=True)
    class Meta:
        model=ItemPrice
        fields=["item", "unit", "shutter_finish", "price_per_unit"]

    def to_representation(self, instance):
        """Convert to float for JSON output."""
        data = super().to_representation(instance)
        if data.get("price_per_unit") is not None:
            data["price_per_unit"] = float(data["price_per_unit"])
        return data


class ClientCompanyInfoSerializer(serializers.ModelSerializer):
    """Serializer for ClientCompanyInfo"""

    class Meta:
        """LeadFile Srializer meta class"""

        model = ClientCompanyInfo
        fields = [
            "id",
            "company_name_nn",
            "email",
            "address_nn",
            "phone",
            "gst_number",
            "pan_number",
            "logo",
            "website",
            "created_at",
            "created_by",
        ]
        read_only_fields = ["id", "created_at", "created_by"]

    def get_logo(self, obj):
        request = self.context.get("request")
        if obj.file and hasattr(obj.file, "url"):
            return request.build_absolute_uri(obj.file.url)
        return None

    def validate_logo(self, value):
        """Enforce same MAX_PDF_FILE_SIZE constraint."""
        if value and hasattr(value, "size") and value.size > MAX_COMPANY_LOGO_SIZE:
            max_mb = MAX_COMPANY_LOGO_SIZE // (1024 * 1024)
            raise serializers.ValidationError(
                f"File size should not exceed {max_mb} MB."
            )
        return value

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["created_by"] = user
        return super().create(validated_data)


class QuotationTermsAndConditionsSerializer(serializers.ModelSerializer):
    terms_and_conditions = serializers.CharField(required=True, allow_blank=False)

    class Meta:
        model = QuotationTermsAndConditions
        fields = [
            "id",
            "terms_and_conditions",
            "internal_notes",
            "footer_tagline",
            "show_contact_info",
            "quotation_logo",
        ]
        read_only_fields = ["id", "created_by", "created_at"]

    def validate_terms_and_conditions(self, value):
        stripped_value = value.strip()
        if not stripped_value:
            raise serializers.ValidationError("Quotation t&c cannot be empty.")
        if not (1 <= len(value) <= 500):
            raise serializers.ValidationError(
                "Quotation t&c must be in between 500 characters long."
            )
        return stripped_value

    def validate_footer_tagline(self, value):
        stripped_value = value.strip()
        if not stripped_value:
            raise serializers.ValidationError("Quotation footer cannot be empty.")
        if not (1 <= len(value) <= 250):
            raise serializers.ValidationError(
                "Quotation footer must be in between 500 characters long."
            )
        return stripped_value

    def validate_internal_notes(self, value):
        stripped_value = value.strip()
        if not stripped_value:
            raise serializers.ValidationError(
                "Quotation internal notes cannot be empty."
            )
        if not (1 <= len(value) <= 500):
            raise serializers.ValidationError(
                "Quotation internal notes must be between 500 characters long."
            )
        return stripped_value


class QuotationItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationItem
        fields = [
            "item_fk",
            "item_length",
            "item_length_unit_fk",
            "item_height",
            "item_height_unit_fk",
            "item_quantity",
            "rate",
            "shutter_finish_fk",
            "amount",
        ]

    def validate(self, data):
        item = data.get("item_fk")
        if not item:
            raise serializers.ValidationError({"item_fk": "Item is required."})

        has_dimension = item.has_dimension

        if has_dimension:
            length_unit = data.get("item_length_unit_fk")
            height_unit = data.get("item_height_unit_fk")
            if not height_unit or not height_unit:
                raise serializers.ValidationError(
                    "Both item length and height units are required for dimensional items."
                )

            if length_unit != height_unit:
                raise serializers.ValidationError(
                    "Item Length and Height units must match."
                )

            if float(data["item_length"]) <= 0 or float(data["item_height"]) <= 0:
                raise serializers.ValidationError(
                    "Item length and height must be greater than zero."
                )

            item_quantity = float(data["item_length"]) * float(data["item_height"])
            unit = data["item_length_unit_fk"]

            try:
                price_obj = ItemPrice.objects.get(
                    item=item, shutter_finish=data.get("shutter_finish_fk"), unit=unit
                )
            except ItemPrice.DoesNotExist:
                raise serializers.ValidationError(
                    "No price defined for this item + unit + shutter finish combination."
                )

        else:
            for field in (
                "item_length",
                "item_height",
                "item_length_unit_fk",
                "item_height_unit_fk",
            ):
                if data.get(field) is not None:
                    raise serializers.ValidationError(
                        {
                            field: f"{field} must not be provided for non-dimensional items."
                        }
                    )

            item_quantity = data.get("item_quantity")
            if not item_quantity:
                raise serializers.ValidationError(
                    {"item_quantity": "Quantity is required for non-dimensional items."}
                )

            try:
                price_obj = ItemPrice.objects.get(
                    item=item, shutter_finish__isnull=True, unit__isnull=True
                )
            except ItemPrice.DoesNotExist:
                raise serializers.ValidationError(
                    "No price defined for this non-dimensional item."
                )

        # Assign rate and amount
        data["rate"] = price_obj.price_per_unit
        data["item_quantity"] = item_quantity
        data["amount"] = float(item_quantity) * float(price_obj.price_per_unit)

        return data

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Optionally re-compute rate if item/unit/finish changes
        instance = super().update(instance, validated_data)
        instance.save()
        return instance


class QuotationItemDetailsSerializer(serializers.ModelSerializer):
    item_fk = ItemSerializer(read_only=True)
    item_length_unit_fk = UnitSerializer(read_only=True)
    item_height_unit_fk = UnitSerializer(read_only=True)
    shutter_finish_fk = ShutterFinishSerializer(read_only=True)

    class Meta:
        model = QuotationItem
        fields = [
            "item_fk",
            "item_length",
            "item_length_unit_fk",
            "item_height",
            "item_height_unit_fk",
            "item_quantity",
            "rate",
            "shutter_finish_fk",
            "amount",
        ]


class QuotationRoomSerializer(serializers.ModelSerializer):
    """Serializer for QuotationRoom."""

    items = QuotationItemSerializer(many=True)
    total_room_amount = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = QuotationRoom
        fields = ["room_type_fk", "room_name", "items", "total_room_amount"]

    def get_total_room_amount(self, instance):
        """Calculate the total amount for the room"""
        return sum(item.amount for item in instance.items.all())

    def validate_room_name(self, value):
        """
        Validate room_name to allow:
        - Letters, digits, spaces, hyphens, apostrophes, ampersands, periods
        """
        value = value.strip()
        pattern = r"^[A-Za-z0-9\s\-'.&]+$"
        if not re.match(pattern, value):
            raise serializers.ValidationError(
                "Room name may only contain letters, numbers, spaces, hyphens (-), "
                "apostrophes ('), ampersands (&), and periods (.)"
            )
        return value

    def validate(self, attrs):
        """Ensure at least one item is provided for the room"""
        items = attrs.get("items", [])
        if not items:
            raise serializers.ValidationError(
                {"items": "At least one item must be provided for the room."}
            )
        return attrs


class QuotationRoomDetailserializer(serializers.ModelSerializer):
    items = QuotationItemDetailsSerializer(many=True)
    total_room_amount = serializers.SerializerMethodField(read_only=True)
    room_type_fk = RoomTypeSerializer(read_only=True)

    class Meta:
        model = QuotationRoom
        fields = ["room_type_fk", "room_name", "items", "total_room_amount"]

    def get_total_room_amount(self, instance):
        return sum(item.amount for item in instance.items.all())


class PaymentMilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMilestone
        fields = [
            "id",
            "quotation_fk",
            "milestone_name",
            "percentage",
            "amount",
            "is_paid",
            "paid_date",
        ]
        read_only_fields = ["id", "quotation_fk"]


class QuotationCreateSerializer(serializers.ModelSerializer):
    rooms = QuotationRoomSerializer(many=True, required=True)
    # terms_and_conditions = QuotationTermsAndConditionsSerializer(required=True)

    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    discount_amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    tax_amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    grand_total = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )

    class Meta:
        model = Quotation
        fields = [
            "id",
            "quotation_number",
            "quotation_title",
            "scope_of_work",
            "project_fk",
            "client_fk",
            "salesperson_fk",
            "bhk_type_fk",
            "material_tier_fk",
            "quotation_date",
            "valid_until",
            "subtotal",
            "discount_percentage",
            "discount_amount",
            "tax_percentage",
            "tax_amount",
            "grand_total",
            "status",
            "notes",
            "rooms",
            # "terms_and_conditions",
        ]

    # def validate_quotation_title(self, value):
    #     stripped_value = value.strip()
    #     if not stripped_value:
    #         raise serializers.ValidationError("Quotation title cannot be empty.")

    #     if not re.match(r"^[A-Za-z0-9 ]+$", stripped_value):
    #         raise serializers.ValidationError(
    #             "Quotation title can only contain alphanumeric values and spaces. Digits and special characters are not allowed."
    #         )
    #     if not (1 <= len(value) <= 50):
    #         raise serializers.ValidationError(
    #             "Quotation title must be in between 50 characters long."
    #         )
    #     return stripped_value

    # def validate_scope_of_work(self, value):
    #     if not value:
    #         raise serializers.ValidationError("Scope of work is required.")

    #     if not isinstance(value, list):
    #         raise serializers.ValidationError("Scope of work must be a list.")

    #     if any(not v for v in value):
    #         raise serializers.ValidationError(
    #             "Scope of work list cannot contain empty or invalid values."
    #         )

    #     return value

    def get_grand_total(self, instance):
        return sum(item.total_room_amount for item in instance.total_room_amount.all())

    def validate(self, data):
        rooms = data.get("rooms", [])
        if not rooms:
            raise serializers.ValidationError(
                {"rooms": "At least one rooms must be provided for the quotation."}
            )
        return data

    def create(self, validated_data):
        rooms_data = validated_data.pop("rooms")
        # terms_data = validated_data.pop("terms_and_conditions", {})
        scope_of_work_ids = validated_data.pop("scope_of_work", [])
        scope_of_work_data = []
        for scope_id in scope_of_work_ids:
            try:
                work = ScopeOfWork.objects.get(id=scope_id)
                scope_of_work_data.append(
                    {"id": work.id, "scope_of_work": work.scope_of_work}
                )
            except ScopeOfWork.DoesNotExist:
                raise serializers.ValidationError(
                    {"scope_of_work": f"ScopeOfWork ID {scope_id} does not exist."}
                )

        validated_data["scope_of_work"] = scope_of_work_data

        quotation = Quotation.objects.create(**validated_data)

        # Create related rooms & items
        for room_data in rooms_data:
            items_data = room_data.pop("items")
            room = QuotationRoom.objects.create(quotation_fk=quotation, **room_data)
            for item_data in items_data:
                QuotationItem.objects.create(quotation_room_fk=room, **item_data)

        # Create terms and conditions
        # QuotationTermsAndConditions.objects.create(quotation_fk=quotation, **terms_data)
        subtotal = Decimal("0")
        for room in QuotationRoom.objects.filter(quotation_fk=quotation):
            room_total = sum(item.amount for item in room.items.all())
            subtotal += Decimal(room_total)

        if subtotal < 0:
            raise serializers.ValidationError(
                {"subtotal": "Subtotal cannot be negative."}
            )

        tax_percentage = Decimal("18")
        discount_amount = (
            Decimal("20000") if subtotal >= Decimal("100000") else Decimal("0")
        )
        taxable_amount = subtotal - discount_amount
        tax_amount = (taxable_amount * tax_percentage) / Decimal("100")
        grand_total = taxable_amount + tax_amount

        # Assign and save
        quotation.subtotal = subtotal
        quotation.discount_amount = discount_amount
        quotation.tax_amount = tax_amount.quantize(Decimal("0.01"))
        quotation.grand_total = grand_total.quantize(Decimal("0.01"))
        quotation.save(
            update_fields=["subtotal", "discount_amount", "tax_amount", "grand_total"]
        )

        return quotation


class QuotationSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Quotation
        fields = [
            "subtotal",
            "discount_amount",
            "tax_percentage",
            "tax_amount",
            "grand_total",
        ]
        read_only_fields = ["tax_amount", "grand_total"]

    def validate(self, data):
        subtotal = data.get("subtotal")
        tax_percentage = 18

        if subtotal is None:
            raise serializers.ValidationError(
                "subtotal must required for summary calculation."
            )
        if subtotal < 0:
            raise serializers.ValidationError(
                {"subtotal": "Subtotal cannot be negative."}
            )
        if not (0 <= tax_percentage <= 100):
            raise serializers.ValidationError(
                {"tax_percentage": "Tax percentage must be between 0 and 100."}
            )

        discount_amount = 20000 if subtotal >= 100000 else 0

        taxable_amount = subtotal - discount_amount
        tax_amount = (taxable_amount * tax_percentage) / 100
        grand_total = taxable_amount + tax_amount

        data["tax_amount"] = round(tax_amount, 2)
        data["grand_total"] = round(grand_total, 2)
        data["discount_amount"] = round(discount_amount, 2)
        # data["round_off"] = round_off

        return data


class QuotationDetailSerializer(serializers.ModelSerializer):
    rooms = QuotationRoomDetailserializer(many=True, read_only=True)
    milestones = PaymentMilestoneSerializer(many=True, read_only=True)
    # terms_and_conditions = serializers.SerializerMethodField()

    project_fk = ProjectSerializer(read_only=True)
    client_fk = LeadForQuotationSerializer(read_only=True)
    salesperson_fk = UserSerializer(read_only=True)
    bhk_type_fk = BHKTypeSerializer(read_only=True)
    material_tier_fk = MaterialTierSerializer(read_only=True)

    class Meta:
        model = Quotation
        fields = [
            "id",
            "quotation_number",
            "quotation_title",
            "scope_of_work",
            "project_fk",
            "client_fk",
            "salesperson_fk",
            "bhk_type_fk",
            "material_tier_fk",
            "quotation_date",
            "valid_until",
            "subtotal",
            "discount_percentage",
            "discount_amount",
            "tax_percentage",
            "tax_amount",
            "grand_total",
            "status",
            "notes",
            "rooms",
            "milestones",
            # "terms_and_conditions",
        ]

    # def get_terms_and_conditions(self, obj):
    #     terms_qs = obj.terms_and_conditions.all()
    #     if not terms_qs.exists():
    #         return None
    #     terms = terms_qs.first()
    #     return QuotationTermsAndConditionsSerializer(terms).data


class ProjectCreateSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(required=True)
    city_or_area = serializers.CharField(required=True)
    society_type = serializers.CharField(required=True)
    pincode = serializers.CharField(required=True, min_length=6, max_length=6)

    class Meta:
        model = Project
        fields = "__all__"

    def validate_pincode(self, value):
        if not re.match(r"^\d{6}$", value):
            raise serializers.ValidationError("Pincode must be a 6-digit number.")
        return value


class QuotationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quotation
        fields = "__all__"


class MaterialDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialTier
        fields = "__all__"


class BhkTypeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = BHKType
        fields = "__all__"


class ApprovedQuotationSerializer(serializers.ModelSerializer):
    material_tier_fk = MaterialDetailSerializer()
    bhk_type_fk = BhkTypeDetailSerializer()

    class Meta:
        model = Quotation
        fields = "__all__"
