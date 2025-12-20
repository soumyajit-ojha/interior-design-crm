"""Serializer for the leads_app Django application."""

import re
from datetime import datetime, timedelta
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.timezone import now

from leads_app.models import CustomerLead
from decimal import Decimal
from utils.constants import MAX_PDF_FILE_SIZE
from quotations_app.models import BHKType, ScopeOfWork
from .models import (
    LeadNote,
    LeadFile,
    LeadStatusTimeLine,
    ServiceType,
    RoomToDesign,
    BrandType,
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name_nn",
            "last_name_nn",
            "user_type_nn",
        ]


class CustomerLeadCheckSerializer(serializers.ModelSerializer):
    """CustomerLead Check Serializer"""

    class Meta:
        """Meta class"""

        model = CustomerLead
        fields = ["id", "client_name", "email", "phone"]
        read_only_fields = ["id", "created_by", "created_at"]

    def validate_client_name(self, value):
        """
        Validate client_name:
        - Only allows uppercase/lowercase letters and spaces.
        - Disallows digits and other special characters.
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Client name is required.")
        value = value.strip()
        if not re.match(r"^[A-Za-z .,'\-]+$", value):
            raise serializers.ValidationError(
                "Client name can only contain letters, spaces, and basic punctuation (.,'-)."
            )

        return value

    def validate_email(self, value):
        """
        Validate email:
        - Must be lowercase only.
        - Only one '@' and '.' allowed.
        - Only lowercase letters, numbers, '@', and '.' are allowed.
        - No spaces or other special characters.
        Example: dummy12@email.com
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Email is required.")
        value = value.strip()
        if not re.match(r"^[a-z0-9._%-]+@[a-z0-9.-]+\.[a-z]{2,}$", value):
            raise serializers.ValidationError(
                "Email must be lowercase and in valid format (e.g., dummy12@email.com)."
            )
        return value

    def validate_phone(self, value):
        """
        Validate phone:
        - Must start with '+' followed by country code and number groups.
        - Only digits allowed after the '+'.
        Example: +919876543210
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Phone number is required.")
        value = value.strip()
        if not re.match(r"^\+\d{7,15}$", value):
            raise serializers.ValidationError(
                "Phone no. start with '+' and country code and length(min=7, max=15) only digits allowed. e.g., +919876543210."
            )
        return value


class CustomerLeadSerializer(serializers.ModelSerializer):
    """CustomerLead Serializer"""

    city = serializers.CharField(required=True)
    society_name = serializers.CharField(required=True)
    flat_number = serializers.CharField(required=True)
    move_in_date = serializers.DateField(required=False, allow_null=True)
    move_in_date_details = serializers.CharField(
        required=False, allow_blank=True, max_length=200
    )
    flat_type = serializers.CharField(required=True, allow_blank=False)
    # floor_plan = serializers.FileField(required=False, allow_null=True)

    class Meta:
        """Meta class"""

        model = CustomerLead
        fields = [
            "id",
            "client_name",
            "email",
            "phone",
            "call_back_time",
            "status",
            "society_name",
            "flat_number",
            "possession_date",
            "bhk_room_type",
            "flat_type",
            "service_type",
            "service_type_description",
            "rooms_to_design",
            "kitchen_platform_status",
            "kitchen_platform_description",
            "civil_work_type",
            "preferred_brand_type",
            "floor_plan",
            "budget_range",
            "past_experience",
            "reason",
            "follow_up_dt",
            "is_reminder",
            "mark_as_done",
            "follow_up_note",
            "follow_up_at",
            "interest_percentage",
            "source",
            "assigned_to_fk",
            "is_converted_to_client",
            "conversion_date",
            "city",
            "move_in_date",
            "move_in_date_details",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["id", "created_by", "created_at"]

    def validate_budget_range(self, value):
        """Validate budget range"""
        if value is not None:
            if value < 0:
                raise serializers.ValidationError("Budget must be positive.")
            if value > Decimal("9999999999.99"):
                raise serializers.ValidationError("Budget is unrealistically high.")
        return value

    def validate_client_name(self, value):
        """
        Validate client_name:
        - Only allows uppercase/lowercase letters and spaces.
        - Disallows digits and other special characters.
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Client name is required.")
        value = value.strip()
        if not re.match(r"^[A-Za-z .,'\-]+$", value):
            raise serializers.ValidationError(
                "Client name can only contain letters, spaces, and basic punctuation (.,'-)."
            )
        return value

    def validate_email(self, value):
        """
        Validate email:
        - Must be lowercase only.
        - Only one '@' and '.' allowed.
        - Only lowercase letters, numbers, '@', and '.' are allowed.
        - No spaces or other special characters.
        Example: dummy12@email.com
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Email is required.")
        value = value.strip()
        if not re.match(r"^[a-z0-9._%-]+@[a-z0-9.-]+\.[a-z]{2,}$", value):
            raise serializers.ValidationError(
                "Email must be lowercase and in valid format (e.g., dummy12@email.com)."
            )
        return value

    def validate_phone(self, value):
        """
        Validate phone:
        - Must start with '+' followed by country code and numbers.
        - Only digits and spaces allowed after the '+'.
        Example: +919876543210
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Phone number is required.")
        value = value.strip()
        if not re.match(r"^\+\d{7,15}$", value):
            raise serializers.ValidationError(
                "Phone no. start with '+' and country code and length(min=7, max=13) only digits allowed. e.g., +919876543210."
            )
        return value

    def validate_interest_percentage(self, value):
        """Validate interest percentage"""

        if value is not None and (value < 0 or value > 100):
            raise serializers.ValidationError(
                "Interest level must be between 0 and 100."
            )
        return value

    def validate_city(self, value):
        """Validate city field"""
        if not re.match(r"^[A-Za-z .-]+$", value.strip()):
            raise serializers.ValidationError(
                "City must contain only letters, spaces and hyphens."
            )
        if len(value.strip())<2 or len(value.strip())>50:
            raise serializers.ValidationError(
                "city must contains 2 to 50 characters long."
            )
        return value.strip()

    def validate_society_name(self, value):
        """Validate society name"""
        value = value.strip()

        if value and not re.match(r"^[A-Za-z0-9-,. ]+$", value):
            raise serializers.ValidationError(
                "Society name must contain letters, numbers, spaces, hyphens, commas, and dot(.)."
            )
        if len(value) < 3 or len(value) > 50:
            raise serializers.ValidationError(
                "Society name must be between 3 and 50 characters long."
            )
        return value

    def validate_flat_number(self, value):
        """Validate flat number"""
        if value and not re.match(r"^[A-Za-z0-9\-/ ]+$", value.strip()):
            raise serializers.ValidationError(
                "Flat no. must contain only letters, numbers, spaces, hyphens (-), or slashes (/)."
            )
        return value.strip()

    def validate_possession_date(self, value):
        """Validate possession date"""
        if value:
            today = now().date()
            valid_past_days = today - timedelta(days=365)
            valid_future_days = today + timedelta(days=365)
            if value < valid_past_days or value > valid_future_days:
                raise serializers.ValidationError(
                    "Possession date must be within 1 year before or after today's date."
                )
        return value

    def validate_follow_up_dt(self, value):
        """Validate follow up date"""
        today = now().date()
        current_time = now().time()
        if value < today:
            raise serializers.ValidationError("Follow-up date cannot be in the past.")

        if value == today:
            follow_up_at = self.initial_data.get("follow_up_at")
            if not follow_up_at:
                raise serializers.ValidationError(
                    "Follow-up time is required when follow-up date is today."
                )

            try:
                follow_up_time = datetime.strptime(follow_up_at, "%H:%M:%S").time()
            except ValueError:
                raise serializers.ValidationError(
                    "Invalid time format for follow-up_at."
                )

            if follow_up_time <= current_time:
                raise serializers.ValidationError(
                    "Follow-up time must be in the future when follow-up date is today."
                )

        return value

    def validate_service_type(self, value):
        """Ensure service_type is not an empty list"""
        if isinstance(value, list) and not value:
            raise serializers.ValidationError("Service type must not be an empty list.")
        if value is None:
            raise serializers.ValidationError("Service type is required.")
        return value

    def validate_service_type_description(self, value):
        """Validate service type description"""
        if value in ("", None):
            return value
        if not 1 < len(value.strip()) < 300:
            return "Service type description must be in maximum 300 charaters."
        return value

    def validate_kitchen_platform_description(self, value):
        """Validate kitchen platform status"""
        if value in ("", None):
            return value
        if not 1 < len(value.strip()) < 300:
            return "Service type description must be in maximum 300 charaters."
        return value

    def validate_reason(self, value):
        """Validate reason for kitchen platform status"""
        if value in ("", None):
            return value
        if not 1 < len(value.strip()) < 300:
            return "Service type description must be in maximum 300 charaters."
        return value

    def validate(self, data):
        """Validate all fields of model"""
        is_reminder = data.get("is_reminder")
        follow_up_at = data.get("follow_up_at")
        service_type_list = data.get("service_type", [])
        service_type_description = str(data.get("service_type_description")).strip()
        possession_date = data.get("possession_date")
        move_in_date = data.get("move_in_date")

        if possession_date and move_in_date:
            if move_in_date <= possession_date:
                raise serializers.ValidationError({
                    "move_in_date": "Move-in date must be after possession date."
                })

        if is_reminder is True:
            if not follow_up_at:
                raise serializers.ValidationError(
                    {
                        "follow_up_at": "This field is required when 'is_reminder' is True."
                    }
                )
        elif is_reminder is False:
            if follow_up_at:
                raise serializers.ValidationError(
                    {
                        "follow_up_at": "You cannot set 'follow_up_at' when 'is_reminder' is False."
                    }
                )

        if data.get("past_experience") and not data.get("reason"):
            raise serializers.ValidationError(
                {
                    "reason": "Please provide details about your past experience or your expectation from us."
                }
            )

        for service_id in service_type_list:
            try:
                service_name = ServiceType.objects.get(id=service_id).name
                if service_name.lower() in ("other", "others"):
                    if service_type_description in ("", None):
                        raise serializers.ValidationError(
                            {
                                "service_type_description": "Please provide service details when your service type is 'Others'."
                            }
                        )
            except ServiceType.DoesNotExist:
                raise serializers.ValidationError(
                    {"service_type": f"ServiceType ID {service_id} does not exist."}
                )
        return data

    def validate_move_in_date(self, move_in_date):
        if move_in_date and move_in_date < now().date():
            raise serializers.ValidationError("Move-in date must be a future date.")
        return move_in_date

    def validate_move_in_date_details(self, details):
        if details and len(details) > 200:
            raise serializers.ValidationError(
                "Move-in date details must not exceed 200 characters."
            )
        return details

    def create(self, validated_data):
        service_type_ids = validated_data.pop("service_type", [])
        bhk_room_type_ids = validated_data.pop("bhk_room_type", [])
        rooms_to_design_ids = validated_data.pop("rooms_to_design", [])
        preferred_brand_type_ids = validated_data.pop("preferred_brand_type", [])

        bhk_room_type_data = []
        for bhk_room_id in bhk_room_type_ids:
            try:
                bhk_room = BHKType.objects.get(id=bhk_room_id)
                bhk_room_type_data.append(
                    {"id": bhk_room.id, "bhk_room_name": bhk_room.bhk_name}
                )
            except BHKType.DoesNotExist:
                raise serializers.ValidationError(
                    {"bhk_room_type": f"BHKType ID {bhk_room_id} does not exist."}
                )

        service_type_data = []
        for service_id in service_type_ids:
            try:
                service = ServiceType.objects.get(id=service_id)
                service_type_data.append(
                    {"id": service.id, "service_name": service.name}
                )
            except ServiceType.DoesNotExist:
                raise serializers.ValidationError(
                    {"service_type": f"ServiceType ID {service_id} does not exist."}
                )

        rooms_to_design_data = []
        for room_id in rooms_to_design_ids:
            try:
                room = ScopeOfWork.objects.get(id=room_id)
                rooms_to_design_data.append(
                    {"id": room.id, "scope_of_work": room.scope_of_work}
                )
            except ScopeOfWork.DoesNotExist:
                raise serializers.ValidationError(
                    {"rooms_to_design": f"RoomToDesign ID {room_id} does not exist."}
                )

        preferred_brand_data = []
        for brand_id in preferred_brand_type_ids:
            try:
                brand = BrandType.objects.get(id=brand_id)
                preferred_brand_data.append({"id": brand.id, "brand_name": brand.name})
            except BrandType.DoesNotExist:
                raise serializers.ValidationError(
                    {"preferred_brand_type": f"Brand ID {brand_id} does not exist."}
                )

        validated_data["bhk_room_type"] = bhk_room_type_data
        validated_data["service_type"] = service_type_data
        validated_data["rooms_to_design"] = rooms_to_design_data
        validated_data["preferred_brand_type"] = preferred_brand_data

        instance = super().create(validated_data)
        return instance


class LeadNoteSerializer(serializers.ModelSerializer):
    """LeadNote Srializer"""

    created_by = UserSerializer(read_only=True)

    class Meta:
        "LeadNote Srializer class"

        model = LeadNote
        fields = ["lead_fk", "note_nn", "tags", "created_by", "created_at"]
        read_only_fields = ["created_at", "created_by"]


class CustomerLeadListSerializer(serializers.ModelSerializer):
    assigned_to = serializers.StringRelatedField(source="assigned_to_fk")
    created_date = serializers.DateTimeField(
        source="created_at", format="%Y-%m-%d %H:%M:%S"
    )

    class Meta:
        model = CustomerLead
        fields = [
            "id",
            "client_name",
            "phone",
            "email",
            "service_type",
            "source",
            "status",
            "assigned_to",
            "created_date",
        ]


class LeadFileSerializer(serializers.ModelSerializer):
    """LeadFile Serializer"""

    # This field is for POST/PUT requests. It expects a primary key.
    # We will use this in the view to save the file.
    lead_fk = serializers.PrimaryKeyRelatedField(
        queryset=CustomerLead.objects.all(),
        write_only=True,  # This is the key change. This field is for writing only.
    )

    # This field is for GET requests. It displays the nested lead data.
    # We will use a separate field for this.
    lead_details = CustomerLeadListSerializer(source="lead_fk", read_only=True)

    created_by = UserSerializer(read_only=True)

    class Meta:
        """LeadFile Serializer meta class"""

        model = LeadFile
        fields = [
            "id",
            "lead_fk",  # The field for POST requests (accepts PK)
            "lead_details",  # The field for GET requests (shows nested data)
            "file_name",
            "file_size",
            "file_path",
            "created_at",
            "created_by",
        ]
        read_only_fields = ["id", "created_at", "created_by", "lead_details"]

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["created_by"] = user
        return super().create(validated_data)

    def validate_file_path(self, file_object):
        """Custom validator for file field."""
        if file_object and file_object.size > MAX_PDF_FILE_SIZE:
            max_mb = MAX_PDF_FILE_SIZE // (1024 * 1024)
            raise serializers.ValidationError(
                f"File size should not exceed {max_mb} MB."
            )
        return file_object


class LeadFileRetrieveSerializer(serializers.ModelSerializer):
    """Lead Retrieve serializer"""

    class Meta:
        """Meta class"""

        model = LeadFile
        fields = [
            "id",
            "file_name",
            "file_size",
            "file_path",
            "created_by",
            "created_at",
        ]


class LeadStatusTimeLineSerializer(serializers.ModelSerializer):
    """LeadStatusTimeLine serializer"""

    class Meta:
        """LeadStatusTimeLine serializer meta class"""

        model = LeadStatusTimeLine
        fields = ["id", "lead_fk", "title_nn", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_title_nn(self, value):
        """
        Method to validate title
        """
        if len(value) > 300:
            raise serializers.ValidationError("Title must be under 300 characters.")
        return value


class LeadForQuotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerLead
        fields = [
            "id",
            "client_name",
            "phone",
            "email",
            "society_name",
            "flat_number",
            "flat_type",
            "city",
        ]


class RoomToDesignSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomToDesign
        fields = ["id", "name"]


class BrandTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandType
        fields = ["id", "name"]


class ServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceType
        fields = ["id", "name"]


class ScopeOfWorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScopeOfWork
        fields = ["id", "scope_of_work", "description"]
