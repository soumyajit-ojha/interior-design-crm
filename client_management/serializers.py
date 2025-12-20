"""
Serializer for Client Management
"""

from datetime import date, timedelta, datetime
from django.db.models import Sum
from rest_framework import serializers
from users.models import User
from quotations_app.models import Quotation, Project, MaterialTier, BHKType
from client_management.models import (
    ClientDetails,
    ClientExpense,
    # ClientMaterialExpense,
    # ClientMiscellaneousExpense,
    ClientPaymanets,
    ClientTimeline,
    # ClientTransportExpense,
    Sprint,
    SprintChecklistItem,
    # DraftClientExpense,
    # ExpenseAttachment,
    SavedProjectExpense,
    SavedClientExpense,
    ClientExpenseSubmission,
    ProjectExpenseSubmission
)
from utils.constants import MAX_PDF_FILE_SIZE
from .models import Material
from vendor_app.models import Vendor


class ConvertLeadToClientSerializer(serializers.Serializer):
    """
    Convert to lead Serialzer
    """

    lead_id = serializers.IntegerField(required=True)
    project_start_date = serializers.DateField(required=True)
    project_duration_in_days = serializers.IntegerField(required=True, min_value=1)
    total_amount_received = serializers.IntegerField(
        required=False, default=0, min_value=0
    )

    def validate_lead_id(self, value):
        """
        Validations for quotation ID
        """

        quotation = (
            Quotation.objects.select_related("client_fk", "project_fk")
            .filter(client_fk__id=value, status__iexact="Approved")
            .first()
        )
        if not quotation:
            raise serializers.ValidationError("No Approved Quotation found")

        lead = quotation.client_fk
        if not lead:
            raise serializers.ValidationError("Associated lead not found")
        # Commenting out as we have to allow the creation of multiple client projects
        # if lead.status in ("Converted", "Rejected") or lead.is_converted_to_client:
        #     raise serializers.ValidationError(f"Lead is already {lead.status or 'converted'}")
        self.context["quotation"] = quotation
        self.context["lead"] = lead
        return value

    def validate_project_duration_in_days(self, value):
        """
        Ensure duration is between 1 and 60 days.
        """
        if not 1 <= value <= 60:
            raise serializers.ValidationError(
                "Project duration must be between 1 and 60 days."
            )
        return value

    def validate(self, attrs):
        """
        project_start_date validation
        to check either its in between possession_date and move_in_date of the lead or not.
        """
        lead = self.context.get("lead")
        if lead:
            possession_date = lead.possession_date
            move_in_date = lead.move_in_date
            start_date = attrs.get("project_start_date")

            if not possession_date and not move_in_date:
                today = date.today()
                if start_date <= today:
                    raise serializers.ValidationError(
                        {"project_start_date": "Must be a future date."}
                    )
                return attrs
            if possession_date and not move_in_date:
                if start_date <= possession_date:
                    raise serializers.ValidationError(
                        {"project_start_date": f"Must be after {possession_date}"}
                    )
            if possession_date and move_in_date:
                if not possession_date < start_date < move_in_date:
                    raise serializers.ValidationError(
                        {
                            "project_start_date": f"Must between {possession_date} and {move_in_date}"
                        }
                    )

        return attrs

    def create(self, validated_data):
        # Implement creation logic or return validated_data
        return validated_data

    def update(self, instance, validated_data):
        # Implement update logic or return instance
        return instance


class UserDetailSerializer(serializers.ModelSerializer):
    """
    User Details Serializer
    """

    class Meta:
        model = User
        fields = ("id", "username", "first_name_nn", "last_name_nn", "user_type_nn")


class MaterialDetailSerializer(serializers.ModelSerializer):
    """
    Material Details Serializer
    """

    class Meta:
        model = MaterialTier
        fields = "__all__"


class BHKTypeDetailSerializer(serializers.ModelSerializer):
    """
    BHKType Details Serializer
    """

    class Meta:
        model = BHKType
        fields = "__all__"


class QuotationDetailSerializer(serializers.ModelSerializer):
    """
    Quotation Details Serializer
    """

    salesperson_fk = UserDetailSerializer()
    bhk_type_fk = BHKTypeDetailSerializer()
    material_tier_fk = MaterialDetailSerializer()

    class Meta:
        model = Quotation
        fields = "__all__"


class ProjectDetailSerializer(serializers.ModelSerializer):
    """
    Project Details Serializer
    """

    class Meta:
        model = Project
        fields = "__all__"


# class ClientMaterialExpenseSerializer(serializers.ModelSerializer):
#     """
#     ClientMaterialExpense Details Serializer
#     """

#     created_by = UserDetailSerializer(read_only=True)

#     class Meta:
#         model = ClientMaterialExpense
#         fields = "__all__"


# class ClientTransportExpenseSerializer(serializers.ModelSerializer):
#     """
#     ClientTransportExpense Details Serializer
#     """

#     class Meta:
#         model = ClientTransportExpense
#         fields = "__all__"


# class ClientMiscellaneousExpenseSerializer(serializers.ModelSerializer):
#     """
#     ClientMiscellaneousExpense Details Serializer
#     """

#     class Meta:
#         model = ClientMiscellaneousExpense
#         fields = "__all__"

class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = '__all__'

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'


class ClientExpenseSerializer(serializers.ModelSerializer):
    """
    ClientExpense Details Serializer
    """
    
    # client_material_expense = ClientMaterialExpenseSerializer(many=True, read_only=True)
    # client_transport_expense = ClientTransportExpenseSerializer(
    #     many=True, read_only=True
    # )
    # client_miscellanieous_expense = ClientMiscellaneousExpenseSerializer(
    #     many=True, read_only=True
    # )
    materials = MaterialSerializer(many=True, read_only=True)
    vendor = VendorSerializer(read_only=True)
    class Meta:
        model = ClientExpense
        fields = "__all__"

class RecentActivitySerializer(serializers.ModelSerializer):
    updated_by = UserDetailSerializer(read_only=True)

    class Meta:
        model = __import__("client_management.models", fromlist=["RecentActivity"]).RecentActivity
        fields = ("id", "activity_date", "activity", "client_name", "service_type", "updated_by")


class ProjectExpenseSerializer(serializers.ModelSerializer):
    """
    ProjectExpense Details Serializer
    """

    vendor = VendorSerializer(read_only=True)
    manager_fk = UserDetailSerializer(read_only=True)
    class Meta:
        model = Project
        # We'll serialize ProjectExpense fields; use Client management ProjectExpense model
        model = __import__("client_management.models", fromlist=["ProjectExpense"]).ProjectExpense
        fields = "__all__"


class ClientTimelineSerializer(serializers.ModelSerializer):
    """
    ClientTimeline Details Serializer
    """
    created_by = UserDetailSerializer(read_only=True)
    attachment = serializers.SerializerMethodField()

    def get_attachment(self, obj):
        try:
            # Try common attribute names for file/file relations
            att_attr = None
            for name in ("attachments", "attachment", "files", "attachment_set"):
                if hasattr(obj, name):
                    att_attr = getattr(obj, name)
                    break

            if not att_attr:
                return None

            # Related manager / queryset: pick the first item
            if hasattr(att_attr, "all"):
                item = att_attr.all().first()
                if not item:
                    return None
                file_field = getattr(item, "file", None) or getattr(item, "attachment", None) or item
                if hasattr(file_field, "url"):
                    return {"url": file_field.url, "filename": getattr(file_field, "name", "").split("/")[-1]}
                return None

            # Single FileField-like object
            if hasattr(att_attr, "url"):
                return {"url": att_attr.url, "filename": getattr(att_attr, "name", "").split("/")[-1]}

            # Iterable of file-like objects: return the first valid one
            if isinstance(att_attr, (list, tuple)):
                for file_field in att_attr:
                    if not file_field:
                        continue
                    ff = getattr(file_field, "file", file_field)
                    if hasattr(ff, "url"):
                        return {"url": ff.url, "filename": getattr(ff, "name", "").split("/")[-1]}
                return None

            return None
        except Exception:
            return None
        # Attachments are always None in this use-case, so return an empty list.
    class Meta:
        model = ClientTimeline
        fields = "__all__"


class ClientPaymanetSerializer(serializers.ModelSerializer):
    """
    ClientPaymanets Details Serializer
    """

    created_by = UserDetailSerializer()

    class Meta:
        model = ClientPaymanets
        fields = "__all__"


class ClientDetailsSerializer(serializers.ModelSerializer):
    """
    Client Details Serializer
    """

    user_fk = UserDetailSerializer()
    quotation_fk = QuotationDetailSerializer()
    project_fk = ProjectDetailSerializer()

    class Meta:
        model = ClientDetails
        fields = "__all__"


class ClientListSerializer(serializers.ModelSerializer):
    """
    Client Details Serializer
    """

    user_fk = UserDetailSerializer()
    quotation_fk = QuotationDetailSerializer()
    project_fk = ProjectDetailSerializer()

    class Meta:
        model = ClientDetails
        fields = "__all__"


class ClientTimelineCreateSerializer(serializers.ModelSerializer):
    """
    Client Timeline Serializer
    """

    class Meta:
        model = ClientTimeline
        exclude = ("client_details_fk",)

    def validate_description(self, value):
        """
        Method to validate description
        """
        if len(value) > 300:
            raise serializers.ValidationError(
                "Description must be under 300 characters."
            )
        return value


class ClientPaymentsCreateSerializer(serializers.ModelSerializer):
    """
    Client Payment create serializer
    """

    class Meta:
        model = ClientPaymanets
        exclude = ("client_details_fk",)

    def validate_amount(self, value):
        """
        Method to validate amount
        """
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate_mode_of_payment(self, value):
        """
        Method to validate pyament
        """
        allowed_modes = ["cash", "cheque", "online"]
        if value.lower() not in allowed_modes:
            raise serializers.ValidationError(
                f"Mode of payment must be one of: {', '.join(allowed_modes)}."
            )
        return value

    def validate_payment_date(self, value):
        """
        Method to validate payment date
        """
        if not value:
            raise serializers.ValidationError("Payment date is required.")
        today = date.today()
        one_year_ago = today - timedelta(days=365)
        one_year_future = today + timedelta(days=365)

        if value < one_year_ago:
            raise serializers.ValidationError(
                "Payment date cannot be more than 1 year in the past."
            )
        if value > one_year_future:
            raise serializers.ValidationError(
                "Payment date cannot be more than 1 year in the future."
            )
        return value


class ClientPaymentsUpdateSerializer(serializers.ModelSerializer):
    """
    Client payments Update Serializer
    """

    class Meta:
        model = ClientPaymanets
        exclude = ("client_details_fk",)


class ClientBudgetStatusSerializer(serializers.ModelSerializer):
    """
    Client budget status serializer
    """

    total_spent = serializers.SerializerMethodField()
    remaining_budget = serializers.SerializerMethodField()
    this_month_expense = serializers.SerializerMethodField()
    budget_status = serializers.SerializerMethodField()
    remaining_amount = serializers.SerializerMethodField()

    class Meta:
        model = ClientDetails
        fields = (
            "id",
            "total_budget",
            "total_amount_received",
            "total_spent",
            "remaining_budget",
            "this_month_expense",
            "budget_status",
            "remaining_amount",
        )

    def get_total_spent(self, obj):
        """
        Method to get total spent amount
        """
        client_expense_ids = obj.client_expenses.values_list("id", flat=True)

        # material = (
        #     ClientMaterialExpense.objects.filter(
        #         client_expense_fk__in=client_expense_ids
        #     ).aggregate(total=Sum("total"))["total"]
        #     or 0
        # )
        # transport = (
        #     ClientTransportExpense.objects.filter(
        #         client_expense_fk__in=client_expense_ids
        #     ).aggregate(total=Sum("total"))["total"]
        #     or 0
        # )
        # misc = (
        #     ClientMiscellaneousExpense.objects.filter(
        #         client_expense_fk__in=client_expense_ids
        #     ).aggregate(total=Sum("total"))["total"]
        #     or 0
        # )

        return 0 #round(material + transport + misc, 2)

    def get_remaining_budget(self, obj):
        """
        Method to get remaining budget
        """
        total_budget = obj.total_budget or 0
        spent = self.get_total_spent(obj)
        return round(total_budget - spent, 2)

    def get_remaining_amount(self, obj):
        """
        Method to get remaining budget
        """
        total_budget = obj.total_budget or 0
        total_amount_received = obj.total_amount_received
        return round(total_budget - total_amount_received, 2)

    def get_this_month_expense(self, obj):
        """
        Method to get month expense
        """
        client_expense_ids = obj.client_expenses.values_list("id", flat=True)
        today = datetime.today()
        first_day = today.replace(day=1)

        # material = (
        #     ClientMaterialExpense.objects.filter(
        #         client_expense_fk__in=client_expense_ids, created_at__gte=first_day
        #     ).aggregate(total=Sum("total"))["total"]
        #     or 0
        # )

        # transport = (
        #     ClientTransportExpense.objects.filter(
        #         client_expense_fk__in=client_expense_ids, created_at__gte=first_day
        #     ).aggregate(total=Sum("total"))["total"]
        #     or 0
        # )

        # misc = (
        #     ClientMiscellaneousExpense.objects.filter(
        #         client_expense_fk__in=client_expense_ids, created_at__gte=first_day
        #     ).aggregate(total=Sum("total"))["total"]
        #     or 0
        # )

        return 0 ## round(material + transport + misc, 2)

    def get_budget_status(self, obj):
        """
        Method to get budget status
        """
        client_expense_ids = obj.client_expenses.values_list("id", flat=True)

        # material_total = (
        #     ClientMaterialExpense.objects.filter(
        #         client_expense_fk__in=client_expense_ids
        #     ).aggregate(total=Sum("total"))["total"]
        #     or 0
        # )

        # transport_total = (
        #     ClientTransportExpense.objects.filter(
        #         client_expense_fk__in=client_expense_ids
        #     ).aggregate(total=Sum("total"))["total"]
        #     or 0
        # )

        # misc_total = (
        #     ClientMiscellaneousExpense.objects.filter(
        #         client_expense_fk__in=client_expense_ids
        #     ).aggregate(total=Sum("total"))["total"]
        #     or 0
        # )

        total_expenses = 0 ##material_total + transport_total + misc_total
        total_budget = obj.total_budget or 0

        if total_budget > 0:
            percent_used = (total_expenses / total_budget) * 100
            return f"{percent_used:.1f}"

        return f"{total_expenses} spent"


class SprintChecklistItemSerializer(serializers.ModelSerializer):
    """
    Sprint Checklist Serializer
    """

    class Meta:
        model = SprintChecklistItem
        fields = ["id", "description", "is_completed_ind"]


class SprintCreateSerializer(serializers.ModelSerializer):
    """
    Sprint Create Serializer
    """

    checklist_items = SprintChecklistItemSerializer(many=True, required=False)

    class Meta:
        model = Sprint
        fields = [
            "id",
            "client_fk",
            "sprint_name",
            "start_date",
            "end_date",
            "status",
            "points",
            "description",
            "checklist_items",
        ]

    def create(self, validated_data):
        checklist_data = validated_data.pop("checklist_items", [])
        sprint = Sprint.objects.create(**validated_data)
        for item in checklist_data:
            SprintChecklistItem.objects.create(sprint_fk=sprint, **item)
        return sprint


# class ExpenseAttachmentSerializer(serializers.ModelSerializer):
#     """Expense attachment serializer"""

#     client_expense_fk = serializers.IntegerField(required=False)

#     class Meta:
#         """Meta class"""

#         model = ExpenseAttachment
#         fields = [
#             "id",
#             "draft_expense_fk",
#             "client_expense_fk",
#             "file",
#             "created_at",
#             "created_by",
#         ]
#         read_only_fields = ["id", "created_at", "created_by"]

#     def validate_file(self, file_object):
#         """Custom validator for file field."""
#         if file_object and file_object.size > MAX_PDF_FILE_SIZE:
#             raise serializers.ValidationError(
#                 f"File size should not exceed {MAX_PDF_FILE_SIZE // (1024 * 1024)} MB."
#             )
#         return file_object

#     def create(self, validated_data):
#         user = self.context["request"].user
#         validated_data["created_by"] = user
#         return super().create(validated_data)


# class DraftExpenseSerializer(serializers.ModelSerializer):
#     """Drafted client expense serializer."""

#     attachments = serializers.ListField(
#         child=serializers.FileField(), write_only=True, required=False
#     )

#     class Meta:
#         """meta data"""

#         model = DraftClientExpense
#         fields = [
#             "id",
#             "client_details_fk",
#             "level_nn",
#             "status",
#             "expense_date",
#             "expense_category",
#             "vendors",
#             "materials",
#             "payment_method",
#             "amount",
#             "extra_info",
#             "attachments",
#             "created_at",
#             "created_by"
#         ]
#     read_only_fields = ["id", "created_at", "created_by"]
#     def create(self, validated_data):
#         attachment_files = validated_data.pop("attachments", [])
#         # validated_data["amount"] = validated_data.get("total")
#         # print("AMOUNT FOUND FOR EXPENSE", validated_data["amount"])
#         print("CONTEXT FOUND", self.context)
#         # first draft created to be used in file saving.
#         instance = super().create(validated_data)

#         # validate all files first then keep them to list and create all at once.
#         attachments_to_create = []
#         for file in attachment_files:
#             file_serializer = ExpenseAttachmentSerializer(
#                 data={"draft_expense_fk": instance.id, "file": file},
#                 context=self.context,
#             )
#             file_serializer.is_valid(raise_exception=True)
#             attachments_to_create.append(
#                 ExpenseAttachment(**file_serializer.validated_data)
#             )

#         # bulk save after validation
#         ExpenseAttachment.objects.bulk_create(attachments_to_create)

#         return instance


class SavedProjectExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedProjectExpense
        fields = '__all__'

class SavedClientExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedClientExpense
        fields = '__all__'


class ClientExpenseSubmissionSerializer(serializers.ModelSerializer):
    # Show material and vendor names instead of their IDs
    materials = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name"
    )
    # vendor is stored as a plain string on the model, so use CharField to avoid attribute access on a str
    vendor = serializers.CharField(read_only=True)

    class Meta:
        model = ClientExpenseSubmission
        fields = "__all__"


class ProjectExpenseSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectExpenseSubmission
        fields = '__all__'
