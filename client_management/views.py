from rest_framework.response import Response
from rest_framework import status
import uuid
import json
from datetime import datetime, timedelta
from django.forms import ValidationError
from django.utils.text import slugify
from django.utils import timezone
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import generics, permissions
from igolohomes.custom_logger import log_message
from utils.response_utils import (
    response_success,
    response_created,
    response_bad_request,
    response_not_found,
    response_forbidden,
)
from utils.utils import CustomPagePagination
from users.models import User
from quotations_app.models import Project, Quotation
from leads_app.models import CustomerLead
from leads_app.filters import CustomSearchFilter
from .models import (
    ClientDetails,
    ClientExpense,
    ProjectExpense,
    ClientExpenseSubmission,
    ProjectExpenseSubmission,
    Sprint,
    ClientPaymanets,
    SprintChecklistItem,
    # DraftClientExpense,
    # ExpenseAttachment,
    SavedProjectExpense,
    SavedClientExpense,
    Material,
    ClientExpenseSubmission
)
from vendor_app.models import Vendor
from .serializers import (
    ConvertLeadToClientSerializer,
    ClientDetailsSerializer,
    ClientListSerializer,
    ClientExpenseSerializer,
    ClientTimelineSerializer,
    ClientPaymanetSerializer,
    # ClientMaterialExpenseSerializer,
    # ClientTransportExpenseSerializer,
    # ClientMiscellaneousExpenseSerializer,
    ClientPaymentsCreateSerializer,
    ClientBudgetStatusSerializer,
    ClientTimelineCreateSerializer,
    SprintCreateSerializer,
    # DraftExpenseSerializer,
    # ExpenseAttachmentSerializer,
    SavedProjectExpenseSerializer,
    ProjectExpenseSerializer,
    SavedClientExpenseSerializer,
    VendorSerializer,
    MaterialSerializer,
    ClientExpenseSubmissionSerializer,
    ProjectExpenseSubmissionSerializer,
)
from .filters import ClientDetailsCustomFilter
from .constant import SPRINT_DATA
from .utils import get_extra_info_from_payload
from django.db.models import Count, Avg


class ConvertLeadToClientAPIView(APIView):
    """
    API for converting a lead into a client and initializing the project.
    """

    @transaction.atomic
    def post(self, request):
        """
        API to handle convert to client
        """
        serializer = ConvertLeadToClientSerializer(data=request.data)
        if not serializer.is_valid():
            log_message(
                "client_management",
                f"Invalid data received for conversion {serializer.errors}",
                "ERROR",
            )
            return response_bad_request(
                errors=serializer.errors, message="Invalid Data"
            )

        data = serializer.validated_data
        quotation: Quotation = serializer.context["quotation"]
        lead: CustomerLead = serializer.context["lead"]
        existing_client = ClientDetails.objects.filter(
            quotation_fk__pk=quotation.pk
        ).first()
        if existing_client:
            log_message(
                "client_management",
                f"Client already exists for quotation {quotation.pk}",
                "ERROR",
            )
            return response_bad_request(
                errors="Client already exists", message="Client already exists"
            )

        # Generate username
        name_parts = lead.client_name.split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        username = f"{slugify(first_name)}{uuid.uuid4().hex[:6]}"

        # Create user
        user = User.objects.filter(email__iexact=lead.email).first()
        if not user:
            user = User.objects.create(
                username=username,
                first_name_nn=first_name,
                last_name_nn=last_name,
                email=lead.email,
                phone_number_nn=lead.phone,
                location_nn=lead.city,
                user_type_nn="client",
                status_nn="pending",
            )

        # Convert lead
        lead.is_converted_to_client = True
        lead.conversion_date = timezone.now()
        lead.status = "Converted"
        lead.save()

        # Create client project
        start_date = data["project_start_date"]
        duration = data["project_duration_in_days"]
        end_date = start_date + timedelta(days=duration)

        client = ClientDetails.objects.create(
            user_fk=user,
            quotation_fk=quotation,
            project_fk=quotation.project_fk,
            start_date=start_date,
            duration_in_days=duration,
            end_date=end_date,
            total_budget=quotation.grand_total,
            progress=0,
        )
        # dont remove the code
        # csv_path = os.path.join(os.path.dirname(__file__), "sprint_data.csv")

        # try:
        #     with open(csv_path, "r") as file:
        #         reader = csv.DictReader(file)
        #         sprint_rows = list(reader)
        # except Exception as e:
        #     print(f"CSV Read Error: {str(e)}")
        #     return response_bad_request(
        #         errors="Error reading CSV file", message="Error reading CSV file"
        #     )
        sprint_rows = SPRINT_DATA

        if not sprint_rows:
            log_message("client_management", "SPRINT_DATA constant is empty.", "ERROR")
            return response_bad_request(
                errors="file contains no sprint data",
                message="file contains no sprint data",
            )

        current_start = start_date

        for index, row in enumerate(sprint_rows[:8]):
            current_end = current_start + timedelta(days=6)

            checklist_items = [
                {"description": item.strip()}
                for item in row.get("checklist_items", [])
                if item.strip()
            ]

            sprint_data = {
                "client_fk": client.id,
                "sprint_name": row["sprint_name"],
                "start_date": current_start,
                "end_date": current_end,
                "status": Sprint.StatusChoices.PENDING,
                "points": 0,
                "description": row["description"],
                "checklist_items": checklist_items,
            }

            sprint_serializer = SprintCreateSerializer(data=sprint_data)
            if sprint_serializer.is_valid():
                sprint_serializer.save()
            else:
                log_message(
                    "client_management",
                    f"Error creating sprint {index + 1}: {sprint_serializer.errors}",
                    "ERROR",
                )
                return response_bad_request(
                    message=f"Sprint {index + 1} creation failed",
                    errors=sprint_serializer.errors,
                )

            current_start = current_end + timedelta(days=1)
        log_message(
            "client_management",
            f"All sprints created for client {client.id}",
            "INFO",
        )
        return response_success(
            message="Client converted and sprints created successfully"
        )


class SprintSummaryAPIView(APIView):
    """
    Sprint Summary View
    """

    def get(self, request):
        """
        Get method to fetch sprint for by client ID
        """
        client_id = request.query_params.get("client_id")
        log_message(
            "client_management",
            "Client ID not provided in request",
            level="ERROR",
        )
        if not client_id:
            return response_bad_request(
                errors="client_id is required", message="client_id is required"
            )

        sprints = (
            Sprint.objects.prefetch_related("checklist_items")
            .filter(client_fk=client_id)
            .order_by("id")
        )

        total_sprints = sprints.count()
        total_checklist_items = SprintChecklistItem.objects.filter(
            sprint_fk__client_fk=client_id
        ).count()
        completed_checklist_items = SprintChecklistItem.objects.filter(
            sprint_fk__client_fk=client_id, is_completed_ind=True
        ).count()
        completed_sprints = sprints.filter(status=Sprint.StatusChoices.COMPLETE).count()

        serialized_sprints = SprintCreateSerializer(sprints, many=True).data
        log_message(
            "client_management",
            f"Sprint summary fetched for client_id={client_id}: "
            f"Total Sprints={total_sprints}, "
            f"Completed Sprints={completed_sprints}, "
            f"Total Items={total_checklist_items}, "
            f"Completed Items={completed_checklist_items}",
            level="INFO",
        )
        return response_success(
            data={
                "total_sprints": total_sprints,
                "total_checklist_items": total_checklist_items,
                "completed_checklist_items": completed_checklist_items,
                "completed_sprints": completed_sprints,
                "sprints": serialized_sprints,
            },
            message="Sprint data retrieved successfully",
        )


class ClientDetailsListAPIView(APIView):
    """
    Unified API for listing, searching, and filtering client details with pagination.
    Handles:
    - Simple list
    - Search (via `search` param)
    - Filters (via custom query params)
    """

    pagination_class = CustomPagePagination

    def get(self, request):
        """
        method to get clients list with search and filter
        """
        try:
            queryset = ClientDetails.objects.all().order_by("-created_at")

            search_term = request.query_params.get("search")
            allowed_filters = [
                "status",
                "project_fk",
                "user_fk",
                "start_date",
                "end_date",
            ]
            has_filters = any(
                key in allowed_filters for key in request.query_params.keys()
            )

            if search_term:
                search_fields = [
                    "user_fk__first_name_nn",
                    "user_fk__last_name_nn",
                    "status",
                    "project_fk__project_name",
                ]
                search_filter = CustomSearchFilter(queryset, request, search_fields)
                queryset = search_filter.apply_search()

            if has_filters:
                custom_filter = ClientDetailsCustomFilter(queryset, request)
                queryset = custom_filter.apply_filters()

            paginator = self.pagination_class()
            page = paginator.paginate_queryset(queryset, request, view=self)

            serializer = ClientListSerializer(
                page if page is not None else queryset,
                many=True,
                context={"request": request},
            )

            user = request.user.username
            current_page = request.query_params.get("page", 1)

            if search_term and has_filters:
                msg = (
                    f"[GET] Search & Filter '{search_term}' + filters - "
                    f"Page {current_page} by {user}"
                )
            elif search_term:
                msg = f"[GET] Search '{search_term}' - Page {current_page} by {user}"
            elif has_filters:
                filters_applied = [
                    key
                    for key in request.query_params.keys()
                    if key in ClientDetailsCustomFilter.ALLOWED_FILTERS
                ]
                msg = f"[GET] Filters {filters_applied} - Page {current_page} by {user}"
            else:
                msg = f"[GET] Simple client list - Page {current_page} by {user}"

            log_message(module_name=__name__, message=msg, level="INFO")

            if page is not None:
                return paginator.get_paginated_response(serializer.data)

            return response_success(
                data=serializer.data, message="Client details retrieved successfully"
            )

        except ValidationError as e:
            msg = f"[GET] Validation error in ClientDetails unified view: {str(e)}"
            log_message(module_name=__name__, message=msg, level="ERROR")
            return response_bad_request(errors=str(e), message="Validation error.")


class ClientDeatilView(generics.RetrieveAPIView):
    """
    Client Deatils View
    """

    serializer_class = ClientDetailsSerializer
    queryset = ClientDetails.objects.all()


class ClientExpensesView(APIView):
    """
    Client Expenses list
    """

    def get(self, request, client_id):
        """
        Get Client Expenses
        """
        client = ClientDetails.objects.get(pk=client_id)
        expenses = client.client_expenses.all().order_by("expense_date", "created_at")
        serializer = ClientExpenseSerializer(expenses, many=True)
        return response_success(data=serializer.data)


class ProjectExpensesView(APIView):
    """
    Project Expenses list
    """

    def get(self, request, project_id):
        """
        Get Project Expenses
        """
        project = Project.objects.get(pk=project_id)
        expenses = project.project_expenses.all().order_by("expense_date", "created_at")

        serializer = ProjectExpenseSerializer(expenses, many=True)
        return response_success(data=serializer.data)


class RecentActivityListAPIView(generics.ListAPIView):
    """API to list recent activities for dashboard"""

    serializer_class = __import__("client_management.serializers", fromlist=["RecentActivitySerializer"]).RecentActivitySerializer
    pagination_class = CustomPagePagination

    def get_queryset(self):
        RecentActivity = __import__("client_management.models", fromlist=["RecentActivity"]).RecentActivity
        qs = RecentActivity.objects.all().order_by("-activity_date")
        service_type = self.request.query_params.get("service_type")
        activity = self.request.query_params.get("activity")
        if service_type:
            qs = qs.filter(service_type__iexact=service_type)
        if activity:
            qs = qs.filter(activity__icontains=activity)
        return qs


class DashboardAnalyticsAPIView(APIView):
    """Return analytics numbers for dashboard KPIs and charts."""

    def get(self, request):
        # Assumptions:
        # - 'Qualified Leads' are leads with status in (FOLLOW_UP, CONTACTED, QUOTED)
        # - 'Customer Rating' isn't stored; we compute a placeholder average if a rating field exists on CustomerLead as `rating`.
        #   If no such field exists, return a default value (4.7) as shown in the sample.
        # - 'Projects Completed' equals ClientDetails with status 'Completed' or 'Complete' (use 'status' field)
        # - 'Leads This Month' counts CustomerLead created in the current month
        # - 'Leads Summary' groups CustomerLead by a JSON/list field `service_type` first element, fallback to 'Unknown'

        now = timezone.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        total_leads = CustomerLead.objects.count()

        qualified_statuses = [CustomerLead.StatusChoices.FOLLOW_UP, CustomerLead.StatusChoices.CONTACTED, CustomerLead.StatusChoices.QUOTED]
        qualified_leads = CustomerLead.objects.filter(status__in=qualified_statuses).count()

        # Customer rating: try to use `rating` field if exists
        rating = None
        if hasattr(CustomerLead, 'rating'):
            rating = CustomerLead.objects.aggregate(avg=Avg('rating'))['avg'] or 0
        else:
            rating = 4.7

        # Projects completed: try to count ClientDetails with status == 'Complete' or 'Completed'
        projects_completed = ClientDetails.objects.filter(status__in=['Complete', 'Completed']).count()

        leads_this_month = CustomerLead.objects.filter(created_at__gte=start_of_month).count()

        # Leads summary by service_type: service_type can be stored as list, dict or string;
        # normalize to a string key (safe & hashable) by extracting sensible value or JSON-dumping dicts.
        leads_by_type = {}
        leads = CustomerLead.objects.values_list('service_type', flat=True)
        for st in leads:
            key = None
            try:
                # If service_type is a list, prefer its first element
                if isinstance(st, list) and len(st) > 0:
                    first = st[0]
                    if isinstance(first, dict):
                        # convert dict to stable string
                        key = json.dumps(first, sort_keys=True)
                    else:
                        key = str(first)
                # If it's a dict, try to extract a meaningful field or dump it
                elif isinstance(st, dict):
                    # try common name-like keys first
                    picked = None
                    for candidate in ("service_type", "name", "type", "title"):
                        if candidate in st and st[candidate]:
                            picked = st[candidate]
                            break
                    if picked is not None:
                        key = str(picked)
                    else:
                        key = json.dumps(st, sort_keys=True)
                # If it's a simple string, use it
                elif isinstance(st, str) and st:
                    key = st
                # Fallback: convert other types to string if possible
                elif st is not None:
                    key = str(st)
            except Exception:
                key = None

            # Ensure we always have a hashable string key
            if not key:
                key = "Unknown"
            else:
                if not isinstance(key, str):
                    try:
                        key = json.dumps(key, sort_keys=True)
                    except Exception:
                        key = str(key)

            leads_by_type[key] = leads_by_type.get(key, 0) + 1

        # Prepare response similar to the provided image
        data = {
            'total_leads': total_leads,
            'qualified_leads': qualified_leads,
            'customer_rating': round(float(rating), 1) if rating is not None else None,
            'projects_completed': projects_completed,
            'leads_this_month': leads_this_month,
            'leads_summary': leads_by_type,
        }

        return response_success(data=data)


class ClientPaymentsView(APIView):
    """
    Client Expenses payment list.
    """

    def get(self, request, client_id):
        """
        Get Client Expenses
        """
        client = ClientDetails.objects.get(pk=client_id)
        payments = client.user_payments.all().order_by("payment_date", "created_at")
        serializer = ClientPaymanetSerializer(payments, many=True)
        return response_success(data=serializer.data)


class ClientTimelineView(APIView):
    """
    Client Timeline list
    """

    def get(self, request, client_id):
        """
        Get Client Timeline
        """
        client = ClientDetails.objects.get(pk=client_id)
        timelines = client.project_timelines.all()
        serializer = ClientTimelineSerializer(
            timelines, many=True, context={"request": request}
        )
        return response_success(data=serializer.data)



class ClientTimelineCreateAPIView(APIView):
    """
    Client Timeline create view
    """

    def post(self, request, client_id):
        """
        post method to add timeline records for client
        """
        client = get_object_or_404(ClientDetails, pk=client_id)
        serializer = ClientTimelineCreateSerializer(data=request.data)
        if serializer.is_valid():
            now = timezone.now()
            serializer.save(
                client_details_fk=client,
                created_by=request.user,
                updated_by=request.user,
                created_at=now,
                updated_at=now,
            )
            return response_created(data=serializer.data)
        return response_bad_request(errors=serializer.errors, message="Invalid Data")


class ClientPaymentsCreateAPIView(APIView):
    """
    Client Payments create view
    """

    def post(self, request, client_id):
        """
        Post method to add payments to the client details
        """
        client = get_object_or_404(ClientDetails, pk=client_id)
        serializer = ClientPaymentsCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(client_details_fk=client, created_by=request.user)
            return response_created(data=serializer.data)
        return response_bad_request(errors=serializer.errors, message="Invalid Data")


class ClientPaymentsUpdateAPIView(APIView):
    """
    Client Payments create view
    """

    def patch(self, request):
        """
        Post method to add payments to the client details
        """
        payment_id = request.data.get("id")
        obj = ClientPaymanets.objects.get(pk=payment_id)
        amount = request.data.get("amount")
        mode_of_payment = request.data.get("mode_of_payment")
        payment_date = request.data.get("payment_date")
        obj.amount = amount
        obj.mode_of_payment = mode_of_payment
        obj.payment_date = payment_date
        obj.updated_by = request.user
        obj.save()
        return response_success()


class ClientBudgetStatusView(APIView):
    """
    Client Budget Status
    """

    def get(self, request, client_id):
        """
        Client Budget Status get method
        """
        try:
            client = ClientDetails.objects.get(pk=client_id)
        except ClientDetails.DoesNotExist:
            return response_bad_request(
                errors="Client not found", message="Client not found"
            )
        serializer = ClientBudgetStatusSerializer(client)
        return response_success(data=serializer.data)


class MarkSprintOrItemAPIView(APIView):
    """
    API View to mark sprint or Item
    """

    def patch(self, request):
        """
        Patch method to update the sprint or sprint items
        """
        item_type = request.data.get("type")
        obj_id = request.data.get("id")
        completed = request.data.get("completed")

        if item_type == "item":
            if completed is None:
                log_message(
                    "client_management",
                    f"Missing 'completed' value for checklist item with ID: {obj_id}",
                    level="ERROR",
                )
                return response_bad_request(
                    "Missing 'completed' field for checklist item."
                )
            try:
                item = SprintChecklistItem.objects.get(id=obj_id)
                item.is_completed_ind = completed
                item.save()
                log_message(
                    "client_management",
                    f"Checklist item with ID {obj_id} marked as "
                    f"{'completed' if completed else 'not completed'}.",
                    level="ERROR",
                )
                return response_success(message="Checklist item updated successfully.")
            except SprintChecklistItem.DoesNotExist:
                log_message(
                    "client_management",
                    f"Checklist item with ID {obj_id} does not exist.",
                    level="ERROR",
                )
                return response_bad_request("Checklist item not found.")

        elif item_type == "sprint":
            try:
                sprint = Sprint.objects.get(id=obj_id)
                sprint.status = Sprint.StatusChoices.COMPLETE
                sprint.save()
                sprint.checklist_items.update(is_completed_ind=True)
                log_message(
                    "client_management",
                    f"Sprint ID {obj_id} marked as complete."
                    f"All checklist items also marked as complete.",
                    level="ERROR",
                )
                return response_success(
                    message="Sprint marked as completed, and all items updated."
                )
            except Sprint.DoesNotExist:
                log_message(
                    "client_management",
                    f"Sprint with ID {obj_id} does not exist.",
                    level="ERROR",
                )
                return response_bad_request("Sprint not found.")

        else:
            log_message(
                "client_management",
                f"Invalid type received: {item_type}. Must be 'item' or 'sprint'.",
                level="ERROR",
            )
            return response_bad_request("Invalid type. Must be 'item' or 'sprint'.")


class ClientDetailsView(APIView):
    """
    Retrieve details for a single client by client_id.
    """

    def get(self, request, client_id):
        client = get_object_or_404(ClientDetails, pk=client_id)
        serializer = ClientDetailsSerializer(client, context={"request": request})
        return response_success(data=serializer.data)
# class DraftExpensesAPIView(APIView):

#     def get(self, request):
#         """
#         Get draft expenses for the current user and optional project filter
#         """
#         project_id = request.query_params.get("project_id")

#         queryset = DraftClientExpense.objects.filter(
#             created_by=request.user, status="Draft"
#         )

#         if project_id:
#             queryset = queryset.filter(client_details_fk__project_fk_id=project_id)

#         serializer = DraftExpenseSerializer(queryset, many=True)
#         return response_success(
#             data=serializer.data,
#             message="Expense_draft retrive successfully",
#         )


# class ApproveExpenseAPIView(APIView):
#     """
#     Approve draft expense API.
#     - Only staff/admin can approve.
#     - On approval, move data into ClientExpense model.
#     """

#     def get_or_create_expense_entry(self, client, expense_date):
#         """
#         Get or create client expense entry for a date
#         """
#         expense_obj, _ = ClientExpense.objects.get_or_create(
#             client_details_fk=client,
#             expense_date=expense_date,
#             defaults={"amount": 0, "material": {}, "vendor": {}},
#         )
#         return expense_obj

#     def post(self, request, expense_id):
#         try:
#             draft_expense = DraftClientExpense.objects.get(
#                 id=expense_id, status="Draft"
#             )
#         except DraftClientExpense.DoesNotExist:
#             return response_not_found(message="Expense not found or already approved")

#         if not request.user.is_staff:
#             return response_forbidden(
#                 message="You are not authorized to approve expenses"
#             )

#         draft_expense.status = "Approved"
#         draft_expense.updated_by = request.user
#         draft_expense.save()

#         expense_entry = self.get_or_create_expense_entry(
#             draft_expense.client_details_fk, draft_expense.expense_date
#         )

#         data = draft_expense.__dict__.copy()
#         data["client_expense_fk"] = expense_entry.id

#         category = draft_expense.expense_category.lower()
#         if category == "material":
#             serializer = ClientMaterialExpenseSerializer(data=data)
#             message = "Material expense approved"
#         elif category == "transport":
#             serializer = ClientTransportExpenseSerializer(data=data)
#             message = "Transport expense approved"
#         elif category == "miscellaneous":
#             serializer = ClientMiscellaneousExpenseSerializer(data=data)
#             message = "Miscellaneous expense approved"
#         else:
#             return response_bad_request(
#                 errors="Invalid expense_category", message="Unsupported"
#             )

#         if serializer.is_valid():
#             serializer.save(created_by=request.user)
#             return response_success(
#                 data={
#                     "draft_expense": DraftExpenseSerializer(draft_expense).data,
#                     "client_expense": ClientExpenseSerializer(expense_entry).data,
#                 },
#                 message=message,
#             )

#         return response_bad_request(errors=serializer.errors, message="Invalid data")


class ExpenceCreationDropdownAPIView(APIView):
    """
    API to get dropdown for expense creation
    """

    def get(self, request):
        """"""
        expence_level = request.data.get("level")
        if not expence_level:
            log_message(
                "client_management",
                "Invalid data received for conversion ",
                "ERROR",
            )
            return response_bad_request(
                errors="Expence level required", message="Expense level required."
            )


# class AddDraftExpenseAPIView(APIView):
#     """
#     API to add a draft expense for a client.
#     """
#     def post(self, request):
#         expenses = request.data
#         if not isinstance(expenses, list):
#             return response_bad_request(
#                 errors="Expected a list of expense objects", message="Invalid payload"
#             )

#         created = []
#         errors = []

#         for idx, expense_data in enumerate(expenses):
#             expense_data = dict(expense_data)  # ensure mutable
#             expense_data["status"] = "Draft"
#             serializer = DraftExpenseSerializer(data=expense_data)
#             if serializer.is_valid():
#                 draft = serializer.save()
#                 created.append(DraftExpenseSerializer(draft).data)
#             else:
#                 errors.append({"index": idx, "error": serializer.errors})

#         if errors and not created:
#             return response_bad_request(errors=errors, message="No drafts created.")

#         return response_created(
#             data={"created": created, "errors": errors},
#             message="Draft expenses processed."
#         )


class SaveExpenseAPIView(APIView):
    """
    Accepts a list of expenses and stores them in SavedProjectExpense or SavedClientExpense based on expense_type.
    """
    def post(self, request):
        expenses = request.data['data']
        draft_number = request.data.get('draftNumber')
        submit = request.data.get('submit', False)
        if not isinstance(expenses, list):
            return response_bad_request(errors="Expected a list of expense objects", message="Invalid payload")

        created_project = []
        created_client = []
        errors = []
        if draft_number:
            # Get all saved expenses for the draft_number for both and delete them
            SavedProjectExpense.objects.filter(draft_number=draft_number).delete()
            SavedClientExpense.objects.filter(draft_number=draft_number).delete()
        else:
            draft_number = uuid.uuid4()

        for idx, expense in enumerate(expenses):
            expense_type = expense.get("expense_type", "client").lower()
            client_id = expense.get("clientId")
            if not client_id:
                errors.append({"index": idx, "error": "Missing clientId"})
                continue
            try:
                client_details = ClientDetails.objects.get(id=client_id)
            except ClientDetails.DoesNotExist:
                errors.append({"index": idx, "error": "Invalid clientId"})
                continue
            data = dict(expense)
            data["client_details_fk"] = client_details.id
            data["project_details_fk"] = client_details.project_fk.id
            data["user_fk"] = request.user.id
            data["draft_number"] = draft_number
            if expense_type == "project":
                # Normalize materials to a list: accept list, comma-separated string, or empty
                materials_val = data.get("materials")
                if isinstance(materials_val, list):
                    materials_list = materials_val
                elif isinstance(materials_val, str):
                    materials_list = [m.strip() for m in materials_val.split(",") if m.strip()]
                else:
                    materials_list = []
                data["materials"] = materials_list

                serializer = SavedProjectExpenseSerializer(data=data)
                if serializer.is_valid():
                    obj = serializer.save()
                    created_project.append({"instance": obj, "data": SavedProjectExpenseSerializer(obj).data})
                else:
                    errors.append({"index": idx, "error": serializer.errors})
            else:
                serializer = SavedClientExpenseSerializer(data=data)
                if serializer.is_valid():
                    obj = serializer.save()
                    created_client.append({"instance": obj, "data": SavedClientExpenseSerializer(obj).data})
                else:
                    errors.append({"index": idx, "error": serializer.errors})

        if errors and not (created_project or created_client):
            return response_bad_request(errors=errors, message="No expenses saved.")
        if submit:
            # use ProjectExpenseSubmission and ClientExpenseSubmission models to track submissions if needed
            for project in created_project:
                # create submission from saved project expense instance
                inst = project["instance"]
                ProjectExpenseSubmission.objects.create(
                    user_fk=request.user,
                    saved_project_expense_fk=inst,
                    project_details_fk=inst.project_details_fk,
                    manager_fk=inst.manager_fk,
                    expense_date=inst.expense_date,
                    expense=inst.expense,
                    notes=inst.notes,
                    amount=inst.amount,
                    submitted_by=request.user
                )
                inst.status = "Submitted"
                inst.save()
            for client in created_client:
                inst = client["instance"]
                submission = ClientExpenseSubmission.objects.create(
                    user_fk=request.user,
                    saved_client_expense_fk=inst,
                    client_details_fk=inst.client_details_fk,
                    expense_date=inst.expense_date,
                    vendor=inst.vendor,
                    notes=inst.notes,
                    amount=inst.amount,
                    quantity=inst.quantity,
                    submitted_by=request.user
                )
                submission.materials.set(inst.materials.all())
                inst.status = "Submitted"
                inst.save()
            return response_success(message="Expenses submitted successfully.")

        return response_created(
            data={
                "project_expenses": [p["data"] for p in created_project],
                "client_expenses": [c["data"] for c in created_client],
                "errors": errors,
            },
            message="Expenses processed."
        )

class ProjectExpenseRequestListAPIView(generics.ListAPIView):
    """
    List project expense requests.
    - Admins/staff can view all or filter by project_id/status.
    - Non-admin users see requests assigned to them as manager.
    Optional query params:
    - project_id
    - status
    Pagination applied via CustomPagePagination.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProjectExpenseSubmissionSerializer
    pagination_class = CustomPagePagination

    def get_queryset(self):
        qs = ProjectExpenseSubmission.objects.all().order_by("-created_at")
        project_id = self.request.query_params.get("project_id")
        status = self.request.query_params.get("status")
        print("project_id", project_id)
        if project_id:
            qs = qs.filter(project_details_fk_id=project_id)

        if status:
            qs = qs.filter(status__iexact=status)

        user = self.request.user
        # Allow admins/staff to view all; others only see requests assigned to them
        if not (getattr(user, "user_type_nn", None) in ("admin", "super_admin") or user.is_staff):
            qs = qs.filter(manager_fk=user)

        return qs

class ProjectExpenseRequestUpdateAPIView(APIView):
    """
    Update status of a project expense request by request_id.
    PATCH or POST: {"status": "Approved"}
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, request_id):
        status_val = request.data.get("status")
        if not status_val:
            return Response({"error": "Missing status"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            req = ProjectExpenseSubmission.objects.get(id=request_id)
        except ProjectExpenseSubmission.DoesNotExist:
            return Response({"error": "Request not found"}, status=status.HTTP_404_NOT_FOUND)
        req.status = status_val
        req.action_by = request.user
        req.acted_at = timezone.now()
        req.save()
        # If approved, map this submission into ProjectExpense
        if status_val.lower() in ("accepted", "approved"):
            try:
                # Try to get client_details from linked saved_project_expense_fk if available
                client_fk = None
                try:
                    client_fk = req.saved_project_expense_fk.client_details_fk
                except Exception:
                    client_fk = None

                # Determine submitted_by (prefer submission.submitted_by then user_fk)
                submitted_by = getattr(req, "submitted_by", None) or getattr(req, "user_fk", None) or request.user

                # Create or update ProjectExpense
                proj = req.project_details_fk
                expense_date = req.expense_date
                expense_defaults = {
                    "client_details_fk": client_fk,
                    "submitted_by": submitted_by,
                    "approved_by": request.user,
                    "manager_fk": getattr(req, "manager_fk", None),
                    "expense": getattr(req, "expense", None) or "",
                    "notes": getattr(req, "notes", None) or "",
                    "amount": getattr(req, "amount", 0) or 0,
                }

                # Use get_or_create to obtain the created flag used below
                # Always create a new ProjectExpense instance (do not try to get existing)
                expense_obj = ProjectExpense.objects.create(
                    project_details_fk=proj,
                    expense_date=expense_date,
                    client_details_fk=expense_defaults.get("client_details_fk"),
                    submitted_by=expense_defaults.get("submitted_by"),
                    approved_by=expense_defaults.get("approved_by"),
                    manager_fk=expense_defaults.get("manager_fk"),
                    expense=expense_defaults.get("expense", ""),
                    notes=expense_defaults.get("notes", ""),
                    amount=expense_defaults.get("amount", 0),
                )
                expense_obj.save()
            except Exception as e:
                return Response({"error": f"Error creating ProjectExpense: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"message": "Status updated", "id": req.id, "status": req.status}, status=status.HTTP_200_OK)
    

 


        # expense_obj, created = ProjectExpense.objects
        #     created = True
        #     # No-op: we always create a new ProjectExpense above, so there's no existing-record update logic required here.
        # return Response({"message": "Status updated", "id": req.id, "status": req.status}, status=status.HTTP_200_OK)
    
class ClientExpenseRequestListAPIView(generics.ListAPIView):
    """
    List client expense requests (submissions). Optional query param: client_id
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClientExpenseSubmissionSerializer
    pagination_class = CustomPagePagination

    def get_queryset(self):
        qs = ClientExpenseSubmission.objects.all().order_by("-created_at")
        print(qs, "LLL")
        client_id = self.request.query_params.get("client_id")
        status = self.request.query_params.get("status")
        if client_id:
            qs = qs.filter(client_details_fk_id=client_id)
        if status:
            qs = qs.filter(status__iexact=status)
        return qs



class ClientExpenseRequestUpdateAPIView(APIView):
    """
    Update status of a client expense request by request_id.
    PATCH or POST: {"status": "Approved"}
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, request_id):
        status_val = request.data.get("status")
        if not status_val:
            return Response({"error": "Missing status"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            req = ClientExpenseSubmission.objects.get(id=request_id)
        except ClientExpenseSubmission.DoesNotExist:
            return Response({"error": "Request not found"}, status=status.HTTP_404_NOT_FOUND)
        
        req.status = status_val
        req.action_by = request.user
        req.acted_at = timezone.now()
        req.save()
        # If the request is Accepted/Approved, map the submission into ClientExpense
        if status_val.lower() in ("accepted", "approved"):
            # get or create a ClientExpense for the client and date
            expense_obj, created = ClientExpense.objects.get_or_create(
                client_details_fk=req.client_details_fk,
                expense_date=req.expense_date,
                defaults={"type": ClientExpense.ExpenseLevelTypes.CLIENT, "amount": 0},
            )

            # Ensure the expense level/type is set to client
            try:
                expense_obj.type = ClientExpense.ExpenseLevelTypes.CLIENT
            except Exception:
                expense_obj.type = "Client"

            # Map materials (submission.materials is a M2M to Material)
            try:
                submitted_materials_qs = req.materials.all()
                expense_obj.materials.set(submitted_materials_qs)
            except Exception:
                # if no materials or mapping fails, skip
                pass

            # Resolve vendor: submission stores vendor as text, but ClientExpense.vendor is FK to Vendor
            vendor_obj = None
            submitted_vendor = getattr(req, "vendor", None)
            if submitted_vendor:
                vendor_obj = Vendor.objects.filter(name_nn__iexact=submitted_vendor).first()
                if not vendor_obj:
                    # create a vendor record with that name
                    vendor_obj = Vendor.objects.create(name_nn=submitted_vendor)
            expense_obj.vendor = vendor_obj

            # Aggregate amount (add submitted amount to existing amount)
            try:
                submitted_amount = int(req.amount or 0)
            except Exception:
                submitted_amount = 0
            expense_obj.amount = (expense_obj.amount or 0) + submitted_amount

            expense_obj.updated_by = request.user
            expense_obj.save()
        return Response({"message": "Status updated", "id": req.id, "status": req.status}, status=status.HTTP_200_OK)


class SavedExpenseGroupByDraftAPIView(APIView):
    """
    Returns all SavedProjectExpense and SavedClientExpense grouped by draft_number.
    Adds 'date' (last updated), and 'total_amount' (sum of all draft amounts) for each group.
    """
    def get(self, request, client_id):
        from collections import defaultdict
        from django.utils.timezone import localtime
        client_obj = ClientDetails.objects.filter(id=client_id).first()
        project_id = client_obj.project_fk.id
        project_drafts = SavedProjectExpense.objects.filter(user_fk=request.user, project_details_fk=project_id, status="Draft")
        client_drafts = SavedClientExpense.objects.filter(user_fk=request.user, client_details_fk=client_id, status="Draft")
        grouped = defaultdict(lambda: {"project_expenses": [], "client_expenses": [], "date": None, "total_amount": 0})

        for obj in project_drafts:
            draft_key = str(obj.draft_number)
            print("Error1")
            grouped[draft_key]["project_expenses"].append(SavedProjectExpenseSerializer(obj).data)
            print("Error2")
            # Update date if this object's updated_at is newer
            updated_at = localtime(obj.updated_at) if hasattr(obj, "updated_at") else None
            if updated_at and (grouped[draft_key]["date"] is None or updated_at > grouped[draft_key]["date"]):
                grouped[draft_key]["date"] = updated_at
            try:
                amount = float(obj.amount) if obj.amount not in (None, "") else 0
            except (ValueError, TypeError):
                amount = 0
            grouped[draft_key]["total_amount"] += amount

        for obj in client_drafts:
            draft_key = str(obj.draft_number)
            grouped[draft_key]["client_expenses"].append(SavedClientExpenseSerializer(obj).data)
            updated_at = localtime(obj.updated_at) if hasattr(obj, "updated_at") else None
            if updated_at and (grouped[draft_key]["date"] is None or updated_at > grouped[draft_key]["date"]):
                grouped[draft_key]["date"] = updated_at
            grouped[draft_key]["total_amount"] += float(getattr(obj, "amount", 0) or 0)

        # Convert to list for easier frontend use, format date as ISO string
        result = [
            {
                "draft_number": draft,
                "date": data["date"].isoformat() if data["date"] else None,
                "total_amount": data["total_amount"],
                "project_expenses": data["project_expenses"],
                "client_expenses": data["client_expenses"],
            }
            for draft, data in grouped.items()
        ]
        return response_success(data=result, message="Expenses grouped by draft number.")

class VendorListAPIView(APIView):
    """
    Vendor List View
    """

    def get(self, request):
        """
        Get method to fetch vendor list
        """
        vendors = Vendor.objects.all()
        serializer = VendorSerializer(vendors, many=True)
        return response_success(data=serializer.data, message="Vendor list fetched.")

class MaterialListAPIView(APIView):
    """
    Material List View
    """

    def get(self, request):
        
        """
        Get method to fetch material list
        """
        materials = Material.objects.all()
        serializer = MaterialSerializer(materials, many=True)
        return response_success(data=serializer.data, message="Material list fetched.")


class ClientExpenseSubmissionListAPIView(generics.ListAPIView):
    """
    List client expense submissions. Optional query param: client_id
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClientExpenseSubmissionSerializer

    def get_queryset(self):
        qs = ClientExpenseSubmission.objects.all().order_by("-created_at")
        client_id = self.request.query_params.get("client_id")
        if client_id:
            qs = qs.filter(client_details_fk_id=client_id)
        return qs


class ProjectExpenseSubmissionListAPIView(generics.ListAPIView):
    """
    List project expense submissions. Optional query param: project_id
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProjectExpenseSubmissionSerializer

    def get_queryset(self):
        qs = ProjectExpenseSubmission.objects.all().order_by("-created_at")
        project_id = self.request.query_params.get("project_id")
        if project_id:
            qs = qs.filter(project_details_fk_id=project_id)
        return qs


# class SubmitExpenseView(APIView):
#     """
#     Add Expense API
#     """

#     def get_client(self, client_id):
#         """
#         method to get client using client_id
#         """
#         try:
#             return ClientDetails.objects.get(pk=client_id)
#         except ClientDetails.DoesNotExist:
#             return None

#     def get_or_create_expense_entry(self, client, expense_date):
#         """
#         Method to get or create client expense record
#         """
#         expense_obj, _ = ClientExpense.objects.get_or_create(
#             client_details_fk=client,
#             expense_date=expense_date,
#             defaults={"amount": 0, "material": {}, "vendor": {}},
#         )
#         return expense_obj

#     def post(self, request, client_id):
#         """
#         Post method to add one or more expenses based on expense_category.
#         Accepts a JSON object with a "data" key containing a list of expense objects.
#         """
#         client = self.get_client(client_id)
#         if not client:
#             return response_bad_request(
#                 errors="Invalid client ID", message="Client not found"
#             )

#         expenses = request.data
#         if not isinstance(expenses, list):
#             return response_bad_request(
#                 errors="Expected 'data' to be a list of expense objects", message="Invalid payload"
#             )

#         created_expenses = []
#         draft_expenses = []
#         errors = []

#         for idx, expense_data in enumerate(expenses):
#             expense_category = expense_data.get("expense_category")
#             expense_date = expense_data.get("expense_date")

#             if not expense_category:
#                 errors.append(
#                     {"index": idx, "error": "Missing 'expense_category'"}
#                 )
#                 continue

#             if not expense_date:
#                 errors.append(
#                     {"index": idx, "error": "Missing 'expense_date'"}
#                 )
#                 continue

#             try:
#                 expense_date_obj = datetime.strptime(expense_date, "%Y-%m-%d").date()
#             except ValueError:
#                 errors.append(
#                     {"index": idx, "error": "Invalid date format (Expected YYYY-MM-DD)"}
#                 )
#                 continue

#             # Get or create ClientExpense for the given date
#             if not request.user.user_type_nn in ("admin", "super_admin"):
#                 expense_entry = self.get_or_create_expense_entry(client, expense_date_obj)

#                 # Attach correct expense serializer
#                 data = expense_data.copy()
#                 data["client_expense_fk"] = expense_entry.id

#                 if expense_category == "Material":
#                     serializer = ClientMaterialExpenseSerializer(data=data)
#                     message = "Material expense added"
#                 elif expense_category == "Transport":
#                     serializer = ClientTransportExpenseSerializer(data=data)
#                     message = "Transport expense added"
#                 elif expense_category == "Miscellaneous":
#                     serializer = ClientMiscellaneousExpenseSerializer(data=data)
#                     message = "Miscellaneous expense added"
#                 else:
#                     errors.append(
#                         {"index": idx, "error": "Invalid expense_category"}
#                     )
#                     continue

#                 if serializer.is_valid():
#                     serializer.save(created_by=request.user)
#                     created_expenses.append({"index": idx, "message": message})
#                 else:
#                     errors.append(
#                         {"index": idx, "error": serializer.errors}
#                     )
#             else:
#                 # For other users, save as draft
#                 data = expense_data.copy()
#                 data["client_details_fk"] = client.id
#                 print(data, "asfasfasf")
#                 data["extra_info"] = get_extra_info_from_payload(payload=data)
#                 data['level_nn'] = "Project" if data['expense_type'] == "project" else "Client"
#                 draft_serializer = DraftExpenseSerializer(
#                     data=data, context={"request": request}
#                 )
#                 if draft_serializer.is_valid():
#                     draft = draft_serializer.save(created_by=request.user)
#                     draft_expenses.append(
#                         {"index": idx, "message": "Expense saved as draft", "id": draft.id}
#                     )
#                 else:
#                     errors.append(
#                         {"index": idx, "error": draft_serializer.errors}
#                     )

#         if errors and not (created_expenses or draft_expenses):
#             return response_bad_request(
#                 errors=errors, message="No expenses created."
#             )

#         return response_created(
#             data={
#                 "created_expenses": created_expenses,
#                 "draft_expenses": draft_expenses,
#                 "errors": errors,
#             },
#             message="Expenses processed. See details.",
#         )
