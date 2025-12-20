from rest_framework import generics, permissions
from .models import Project
from .serializers import ProjectSerializer
from datetime import date
import csv
import io

from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework import permissions
from rest_framework import generics
from django.contrib.auth import get_user_model
from django.utils.timezone import now

from utils.utils import get_cleaned_data
from igolohomes.custom_logger import log_message
from .serializers import *
from .models import *
from utils.response_utils import (
    response_success,
    response_created,
    response_bad_request,
    response_server_error,
)
from decimal import Decimal, ROUND_DOWN
from rest_framework.parsers import MultiPartParser
from leads_app.models import CustomerLead, ServiceType, BrandType, RoomToDesign
from leads_app.serializers import LeadStatusTimeLineSerializer
from client_management.serializers import ClientDetailsSerializer


module = str((__name__).split(".")[0])
User = get_user_model()




# List all projects
class ProjectListAPIView(generics.ListAPIView):
    """
    API to list, search, and filter Projects.
    Supports:
    - Simple list
    - Search (via `search` param)
    - Filters (via query params, e.g. client_status=on_hold)
    """
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Project.objects.all().order_by("-created_at")

        # Search by project name
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(project_name__icontains=search)

        # Filter by client status (e.g., client_status=on_hold)
        client_status = self.request.query_params.get("client_status")
        if client_status:
            # Support multiple comma-separated statuses
            status_list = [s.strip() for s in client_status.split(",") if s.strip()]
            if status_list:
                queryset = queryset.filter(project_clients__status__in=status_list).distinct()

        # Filter by project status
        project_status = self.request.query_params.get("status")
        if project_status:
            queryset = queryset.filter(status__iexact=project_status)

        # Filter by created_by user
        created_by = self.request.query_params.get("created_by")
        if created_by:
            queryset = queryset.filter(created_by_id=created_by)

        # Filter by date range
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        if start_date and end_date:
            queryset = queryset.filter(created_at__date__range=[start_date, end_date])

        return queryset
class ProjectDetailsWithClientAPIView(APIView):
    """
    API View to retrieve project details along with related client information.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            project = Project.objects.get(pk=pk)
            serializer = ProjectSerializer(project)
            # Assuming Project has a related_name 'project_clients' for clients
            clients = project.project_clients.all() if hasattr(project, 'project_clients') else []
            # You may need to adjust the serializer for clients as per your models
            client_data = []
            for client in clients:
                # Use ClientDetailsSerializer for each client
                if hasattr(client, 'client'):
                    serialized = ClientDetailsSerializer(client.client).data
                else:
                    serialized = ClientDetailsSerializer(client).data
                # Remove 'quotation_fk' if present
                serialized.pop('quotation_fk', None)
                client_data.append(serialized)
            data = serializer.data
            data['clients'] = client_data
            return response_success(data=data, message="Project details with clients retrieved successfully.")
        except Project.DoesNotExist:
            return response_bad_request(
                errors="Project not found.",
                message="Project not found."
            )
        except Exception as e:
            return response_bad_request(
                errors=str(e),
                message="Unable to retrieve project details."
            )
class BHKTypeCreateAPIView(APIView):
    """
    API View to handle BHK Type creation.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request):
        """
        Create a new BHK Type.
        """
        try:
            cleaned_data = get_cleaned_data(request)
            bhk_name = cleaned_data.get("bhk_name")
            if not bhk_name:
                log_message(
                    module_name=module,
                    message=f"[{request.method}] bhk_name required",
                    level="WARNING",
                )
                return response_bad_request(
                    errors="BHK name is required.", message="BHK name is required."
                )

            if BHKType.objects.filter(bhk_name__iexact=bhk_name).exists():
                log_message(
                    module_name=module,
                    message=f"[{request.method}] bhk_name already exist.",
                    level="INFO",
                )
                return response_success(
                    data={"exists": True},
                    message="BHK Type with this name already exists.",
                )

            serializer = BHKTypeSerializer(data=cleaned_data)
            if serializer.is_valid():
                serializer.save(created_by=request.user, updated_by=request.user)
                log_message(
                    module_name=module,
                    message=f"[{request.method}] BHK Type created successfully",
                    level="INFO",
                )
                return response_created(
                    data=serializer.data, message="BHK Type created successfully"
                )
            log_message(
                module_name=module,
                message=f"[{request.method}] Invalid data provided. {serializer.errors}",
                level="WARNING",
            )
            return response_bad_request(
                errors=serializer.errors, message="Invalid data provided."
            )

        except Exception as e:
            log_message(
                module_name=module,
                message=f"[{request.method}] Unable to create bhk type. {str(2)}",
                level="WARNING",
            )
            return response_bad_request(message=str(e), errors=str(e))


class MaterialTiersCreateAPIView(APIView):
    """
    API View to handle Material Tier operations.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request):
        """
        Create a new Material Tier.
        """
        try:
            cleaned_data = get_cleaned_data(request)
            tier_name = cleaned_data.get("tier_name")
            if not tier_name:
                log_message(
                    module_name=module,
                    message=f"[{request.method}] tier_name required",
                    level="WARNING",
                )
                return response_bad_request(
                    errors="Tier name is required.", message="Tier name is required."
                )

            if MaterialTier.objects.filter(tier_name__iexact=tier_name).exists():
                log_message(
                    module_name=module,
                    message=f"[{request.method}] Material Tier already exist.",
                    level="INFO",
                )
                return response_success(
                    data={"exists": True},
                    message="Material Tier with this name already exists.",
                )

            serializer = MaterialTierSerializer(data=cleaned_data)
            if serializer.is_valid():
                serializer.save(created_by=request.user, updated_by=request.user)
                log_message(
                    module_name=module,
                    message=f"[{request.method}] Material Tier created successfully.",
                    level="INFO",
                )
                return response_created(
                    data=serializer.data, message="Material Tier created successfully"
                )

            log_message(
                module_name=module,
                message=f"[{request.method}] Invalid data provided.{serializer.errors}",
                level="WARNING",
            )
            return response_bad_request(
                errors=serializer.errors, message="Invalid data provided."
            )

        except Exception as e:
            log_message(
                module_name=module,
                message=f"[{request.method}] Unable to create material tyre. error: {str(e)}",
                level="WARNING",
            )
            return response_bad_request(message=str(e))


class RoomTypesCreateAPIView(APIView):
    """
    API View to handle Room Type operations.
    """

    permission_classes = [permissions.AllowAny]

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request):
        """Create a new Room Type."""

        try:
            cleaned_data = get_cleaned_data(request)
            room_name = cleaned_data.get("room_name")
            if not room_name:
                log_message(
                    module_name=module,
                    message=f"[{request.method}] room_name is required.",
                    level="WARNING",
                )
                return response_bad_request(
                    errors="room_name is required.", message="room_name is required."
                )

            room_name_lower = room_name.lower()
            split_room_name = room_name_lower.split(" ")

            serializer = RoomTypeSerializer(data=cleaned_data)
            if not any(
                keyword in split_room_name for keyword in ["bedroom", "bathroom"]
            ):
                if RoomType.objects.filter(room_name__iexact=room_name).exists():
                    log_message(
                        module_name=module,
                        message=f"[{request.method}] Room Type with this name already exists.",
                        level="WARNING",
                    )
                    return response_bad_request(
                        errors="Room Type with this name already exists.",
                        message="Room Type with this name already exists.",
                    )
            if serializer.is_valid():
                serializer.save(created_by=request.user, updated_by=request.user)
                log_message(
                    module_name=module,
                    message=f"[{request.method}] Room Type created successfully",
                    level="INFO",
                )
                return response_created(
                    data=serializer.data, message="Room Type created successfully."
                )
            log_message(
                module_name=module,
                message=f"[{request.method}] Invalid data provided.",
                level="WARNING",
            )
            return response_bad_request(
                errors=serializer.errors, message="Invalid data provided."
            )

        except Exception as e:
            log_message(
                module_name=module,
                message=f"[{request.method}] Unable to create Room",
                level="WARNING",
            )
            return response_bad_request(message="Unable to create Room", errors=str(e))


class UnitsCreateAPIView(APIView):
    """
    API View to handle Unit operations.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request):
        """Create a new Unit."""

        try:
            cleaned_data = get_cleaned_data(request)
            unit_name = cleaned_data.get("unit_name")
            unit_abbreviation = cleaned_data.get("unit_abbreviation")
            if not unit_abbreviation or not unit_name:
                log_message(
                    module_name=module,
                    message=f"[{request.method}] Unit abbreviation and Unit name required.",
                    level="WARNING",
                )
                return response_bad_request(
                    errors="Unit abbreviation and unit name is required.",
                    message="Unit abbreviation and unit name required.",
                )

            if Unit.objects.filter(
                unit_abbreviation__iexact=unit_abbreviation
            ).exists():
                log_message(
                    module_name=module,
                    message=f"[{request.method}] Unit with this abbreviation already exists.",
                    level="INFO",
                )
                return response_success(
                    data={"exists": True},
                    message="Unit with this abbreviation already exists.",
                )

            if Unit.objects.filter(unit_name__iexact=unit_name).exists():
                log_message(
                    module_name=module,
                    message=f"[{request.method}] Unit with this name already exists.",
                    level="INFO",
                )

            serializer = UnitSerializer(data=cleaned_data)
            if serializer.is_valid():
                serializer.save(created_by=request.user, updated_by=request.user)
                log_message(
                    module_name=module,
                    message=f"[{request.method}] Unit created successfully. {serializer.errors}",
                    level="INFO",
                )
            log_message(
                module_name=module,
                message=f"[{request.method}] Invalid data provided. {serializer.errors}",
                level="WARNING",
            )
            return response_bad_request(
                errors=serializer.errors, message="Invalid data provided."
            )

        except Exception as e:
            log_message(
                module_name=module,
                message=f"[{request.method}] Unable to create unit. {serializer.errors}",
                level="WARNING",
            )
            return response_bad_request(errors=str(e), message="Unable to create unit.")


class ItemCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            data = get_cleaned_data(request)
            item_name = data.get("item_name")
            has_dimension = data.get("has_dimension")

            if not item_name or has_dimension is None:
                log_message(
                    module_name=module,
                    message=f"[POST] item_name and has_dimension is required.",
                    level="WARNING",
                )
                return response_bad_request(
                    errors="item_name and has_dimension field is required.",
                    message="item_name and has_dimension is required.",
                )

            if Item.objects.filter(item_name__iexact=item_name).exists():
                log_message(
                    module_name=module,
                    message=f"[POST] Item already exist.",
                    level="INFO",
                )
                return response_success(
                    data={"exists": True}, message="Item already exists."
                )
            serializer = ItemSerializer(data=data)
            if serializer.is_valid():
                item = serializer.save(created_by=request.user, updated_by=request.user)
                log_message(
                    module_name=module,
                    message=f"[POST] Created Item id={item.id}",
                    level="INFO",
                )

                return response_created(
                    data=serializer.data, message="Item created successfully"
                )
            log_message(
                module_name=module,
                message=f"[POST] Invalid data provided.",
                level="WARNING",
            )
            return response_bad_request(
                errors=serializer.errors, message="Invalid data provided."
            )

        except Exception as e:
            log_message(
                module_name=module,
                message=f"[POST] Exception in creating Item: {e}",
                level="ERROR",
            )
            return response_server_error(message="Unable to create item.")


class ScopeOfWorkCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            data = get_cleaned_data(request)
            name = data.get("scope_of_work")

            if not name:
                log_message(
                    module_name=module,
                    message=f"[POST] scope_of_work field is required.",
                    level="WARNING",
                )
                return response_bad_request(
                    errors="scope_of_work field is required",
                    message="scope_of_work field is required.",
                )

            if ScopeOfWork.objects.filter(scope_of_work__iexact=name).exists():
                log_message(
                    module_name=module,
                    message=f"[POST] Scope of work already exists.",
                    level="INFO",
                )
                return response_success(
                    data={"exists": True}, message="Scope of work already exists."
                )

            serializer = ScopeOfWorkSerializer(data=data)
            if serializer.is_valid():
                scope = serializer.save(
                    created_by=request.user, updated_by=request.user
                )
                log_message(
                    module_name=module,
                    message=f"[POST] Created ScopeOfWork id={scope.id}",
                    level="INFO",
                )
                return response_created(
                    data=serializer.data, message="scope_of_work created successfully"
                )

            log_message(
                module_name=module,
                message=f"[POST] Invalid data provided.",
                level="WARNING",
            )
            return response_bad_request(
                errors=serializer.errors, message="Invalid data provided."
            )

        except Exception as e:
            log_message(
                module_name=module,
                message=f"[POST] Exception creating ScopeOfWork: {str(e)}",
                level="ERROR",
            )
            return response_server_error(message="Unable to create scope of work")


class ShutterFinishAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            data = get_cleaned_data(request)
            shutter_finish_name = data.get("shutter_finish_name")

            if not shutter_finish_name:
                log_message(
                    module_name=module,
                    message=f"[{request.method}] shutter finish  field is required.",
                    level="WARNING",
                )
                return response_bad_request(
                    errors="shutter_finish_name This field is required.",
                    message="shutter_finish_name is required.",
                )

            if ShutterFinish.objects.filter(
                shutter_finish_name__iexact=shutter_finish_name
            ).exists():
                log_message(
                    module_name=module,
                    message=f"[{request.method}] shutter finish name already exists",
                )
                return response_success(
                    data={"exists": True}, message="shutter finish name already exists."
                )

            serializer = ShutterFinishSerializer(data=data)
            if serializer.is_valid():
                shutter_finish = serializer.save(
                    created_by=request.user, updated_by=request.user
                )
                log_message(
                    module_name=module,
                    message=f"[POST] Created Shutter Finish id={shutter_finish.id}",
                    level="INFO",
                )
                return response_created(
                    data=serializer.data, message="Shutter Finish created successfully"
                )
            log_message(
                module_name=module,
                message=f"[POST] Invalid data provided.",
                level="INFO",
            )
            return response_bad_request(
                errors=serializer.errors, message="Invalid data provided."
            )

        except Exception as e:
            log_message(
                module_name=module,
                message=f"[POST] Exception creating Shutter Finish : {e}",
                level="ERROR",
            )
            return response_server_error(message="Unable to create shutter finish.")


class ClientCompanyInfoAPIView(APIView):
    """
    Upload a file for a specific Customer Lead
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        post: Handle Client company creation
        """
        try:
            cleaned_data = get_cleaned_data(request)

            email = cleaned_data.get("email")
            company_name_nn = cleaned_data.get("company_name_nn")
            address_nn = cleaned_data.get("address_nn")
            phone = cleaned_data.get("phone")

            if not email or not company_name_nn or not address_nn or not phone:
                msg = f"[{request.method}] company name, emai, phone and address must required to create company."
                log_message(module_name=module, message=msg, level="WARNING")
                return response_bad_request(
                    errors="Bad Request",
                    message="Company name, email, phone and address must required.",
                )

            serializer = ClientCompanyInfoSerializer(
                data=cleaned_data, context={"request": request}
            )
            if serializer.is_valid():
                serializer.save(created_by=request.user, updated_by=request.user)
                msg = f"[{request.method}] {company_name_nn} company created successfully."
                return response_success(
                    data=serializer.data,
                    message=f"{company_name_nn} company created successfully.",
                )

            msg = f"[{request.method}] Validation error in company creation {serializer.errors}"
            log_message(module_name=module, message=msg, level="WARNING")
            return response_bad_request(
                errors=serializer.errors, message="Validation error in file data"
            )

        except Exception as e:
            msg = (
                f"[{request.method}] Exception raised during company info creation {e}"
            )
            log_message(module_name=module, message=msg, level="ERROR")
            return response_bad_request(
                errors=str(e), message="Failed to create company info."
            )


class ClientCompanyLogoAddAPIView(APIView):
    """Client company Logo upload apiview"""

    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request: Request, pk=None):
        try:
            logo = request.data.get("logo")
            if not logo:
                msg = f"[{request.method}] logo must required for add/update it."
                log_message(module_name=module, message=msg, level="WARNING")
                response_bad_request(
                    errors="logo must required",
                    message="logo must required for add/update it.",
                )

            if not pk:
                msg = f"[{request.method}] company pk/id must required for add/update its logo."
                log_message(module_name=module, message=msg, level="WARNING")
                response_bad_request(
                    errors="company pk/id must required.",
                    message="company pk/id must required for add/update its logo.",
                )
            try:
                company = ClientCompanyInfo.objects.get(pk=pk)
            except AttributeError as e:
                msg = f"[{request.method}] company pk/id must required for add/update its logo."
                log_message(module_name=module, message=msg, level="WARNING")
            serializer = ClientCompanyInfoSerializer(
                company, data=request.data, partial=True, context={"request": request}
            )
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                msg = f"[{request.method}] logo updated by {request.user} successfully."
                log_message(module_name=module, message=msg, level="INFO")
                return response_success(
                    data=serializer.data,
                    message=f"logo updated by {request.user} successfully.",
                )
            msg = f"[{request.method}] Serializer validation error {request.user}."

            log_message(module_name=module, message=msg, level="INFO")
            return response_success(
                data=serializer.data,
                message=f"Serializer validation error {request.user}.",
            )

        except ClientCompanyInfo.DoesNotExist:
            msg = f"[{request.method}] company not found with id {pk}"
            log_message(module_name=module, message=msg, level="WARNING")
            return response_bad_request(
                errors="Company Not Found", message=f"Company not found with id {pk}"
            )

        except Exception as e:
            msg = (
                f"[{request.method}] compException raised during logo update. {str(e)}"
            )
            log_message(module_name=module, message=msg, level="WARNING")
            return response_bad_request(
                errors=str(e), message=f"Exception raised during logo update. {str(e)}"
            )


class QuotationTermsAndConditionsCreateAPIView(APIView):
    """
    POST: Create a new Terms & Conditions record for a given Quotation.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request):
        try:
            data = request.data
            terms_and_conditions = data.get("terms_and_conditions")
            internal_notes = data.get("internal_notes")

            if not terms_and_conditions or not internal_notes:
                msg = f"[{request.method}] terms_and_conditions and internal_notes required by User {request.user.id}"
                log_message(module_name=module, message=msg, level="WARNING")
                return response_bad_request(
                    message="Both 'terms_and_conditions' and 'internal_notes' are required."
                )

            serializer = QuotationTermsAndConditionsSerializer(data=data)
            if serializer.is_valid():
                serializer.save(created_by=request.user, updated_by=request.user)
                msg = f"[{request.method}] created TermsAndConditions by User {request.user.id}"
                log_message(module_name=module, message=msg, level="INFO")
                return response_created(
                    data=serializer.data,
                    message="TermsAndConditions created successfully.",
                )
            else:
                msg = f"[{request.method}] Validation failed: {serializer.errors} by User {request.user.id}"
                log_message(module_name=module, message=msg, level="WARNING")
                return response_bad_request(
                    errors=serializer.errors, message="Validation failed."
                )
        except Exception as e:
            msg = f"[{request.method}] Exception during TermsAndConditions creation: {str(e)} by User {request.user.id}"
            log_message(module_name=module, message=msg, level="ERROR")
            return response_bad_request(
                errors=str(e),
                message="Exception occurred while creating TermsAndConditions.",
            )


class QuotationTermsAndConditionsRetrieveAPIView(APIView):
    """
    GET: Retrieve an existing Terms & Conditions record by its PK.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            obj = QuotationTermsAndConditions.objects.get(pk=pk)
            serializer = QuotationTermsAndConditionsSerializer(instance=obj)

            msg = f"[{request.method}] Retrieved TermsAndConditions ID={pk} by User {request.user.id}"
            log_message(module_name=module, message=msg, level="INFO")
            return response_success(
                data=serializer.data,
                message="Terms and Conditions retrieved successfully.",
            )

        except QuotationTermsAndConditions.DoesNotExist:
            msg = f"[{request.method}] TermsAndConditions not found for ID={pk} by User {request.user.id}"
            log_message(module_name=module, message=msg, level="WARNING")
            return response_bad_request(message="Terms and Conditions not found.")

        except Exception as e:
            msg = f"[{request.method}] Exception retrieving TermsAndConditions ID={pk} by User {request.user.id} - {str(e)}"
            log_message(module_name=module, message=msg, level="ERROR")
            return response_bad_request(
                errors=str(e), message="Error occurred during retrieval."
            )

    def put(self, request, pk, *args, **kwargs):
        """
        To Update Terms and condition.
        """
        try:
            obj = QuotationTermsAndConditions.objects.get(pk=pk)
            is_partial = request.method == "PATCH"
            serializer = QuotationTermsAndConditionsSerializer(
                instance=obj, data=request.data, partial=is_partial
            )

            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                action = "Partially updated" if is_partial else "Fully updated"
                msg = f"[{request.method}] {action} TermsAndConditions ID={pk} by User {request.user.id}"
                log_message(module_name=module, message=msg, level="INFO")
                return response_success(
                    data=serializer.data,
                    message=f"Terms and Conditions {action.lower()}.",
                )
            else:
                msg = f"[{request.method}] Validation failed for update ID={pk} - {serializer.errors}"
                log_message(module_name=module, message=msg, level="WARNING")
                return response_bad_request(
                    errors=serializer.errors, message="Validation failed."
                )

        except QuotationTermsAndConditions.DoesNotExist:
            msg = f"[{request.method}] TermsAndConditions not found for update ID={pk} by User {request.user.id}"
            log_message(module_name=module, message=msg, level="WARNING")
            return response_bad_request(
                message="Terms and Conditions not found for update."
            )

        except Exception as e:
            msg = f"[{request.method}] Exception during update of TermsAndConditions ID={pk} - {str(e)}"
            log_message(module_name=module, message=msg, level="ERROR")
            return response_bad_request(
                errors=str(e), message="Error occurred during update."
            )

    def delete(self, request, pk):
        try:
            obj = obj = QuotationTermsAndConditions.objects.get(pk=pk)
            obj.delete()

            msg = f"[{request.method}] Deleted TermsAndConditions ID={pk} by User {request.user.id}"
            log_message(module_name=module, message=msg, level="INFO")
            return response_success(
                message="Terms and Conditions deleted successfully."
            )

        except QuotationTermsAndConditions.DoesNotExist:
            msg = f"[{request.method}] TermsAndConditions not found for delete ID={pk} by User {request.user.id}"
            log_message(module_name=module, message=msg, level="WARNING")
            return response_bad_request(
                message="Terms and Conditions not found for deletion."
            )

        except Exception as e:
            msg = f"[{request.method}] Exception during delete of TermsAndConditions ID={pk} - {str(e)}"
            log_message(module_name=module, message=msg, level="ERROR")
            return response_bad_request(
                errors=str(e), message="Error occurred during deletion."
            )


class RetrieveAllDropdownDataAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            response_data = {}

            projects = Project.objects.all()
            bhk_types = BHKType.objects.all()
            material_tiers = MaterialTier.objects.all()
            sales_people = User.objects.filter(user_type_nn="salesman")
            items = Item.objects.all()
            units = Unit.objects.all()
            shutter_finish = ShutterFinish.objects.all()
            scope_of_work = ScopeOfWork.objects.all()
            room_types = RoomType.objects.all()

            response_data["projects"] = ProjectSerializer(projects, many=True).data
            response_data["bhk_types"] = BHKTypeSerializer(bhk_types, many=True).data
            response_data["material_tiers"] = MaterialTierSerializer(
                material_tiers, many=True
            ).data
            response_data["sales_people"] = UserSerializer(sales_people, many=True).data
            response_data["items"] = ItemSerializer(items, many=True).data
            response_data["units"] = UnitSerializer(units, many=True).data
            response_data["shutter_finish"] = ShutterFinishSerializer(
                shutter_finish, many=True
            ).data
            response_data["scope_of_work"] = ScopeOfWorkSerializer(
                scope_of_work, many=True
            ).data
            response_data["room_types"] = RoomTypeSerializer(room_types, many=True).data

            log_message(
                module_name=module,
                message=f"[{request.method}] ALL drop down data retrieved.",
                level="INFO",
            )
            return response_success(
                data=response_data, message="ALL drop down data retrieved."
            )

        except Exception as e:
            log_message(
                module_name=module,
                message=f"[{request.method}] Unable to retrieve all drop down data.",
            )
            return response_bad_request(
                errors=str(e), message="Unable to retrieve all drop down data."
            )


class QuotationCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            request_data = request.data.copy()
            if (
                # request_data.get("quotation_title") in (None, "")
                # or request_data.get("scope_of_work") in (None, "")
                request_data.get("project_fk") in (None, "")
                or request_data.get("client_fk") in (None, "")
                or request_data.get("salesperson_fk") in (None, "")
                or request_data.get("bhk_type_fk") in (None, "")
                or request_data.get("client_fk") in (None, "")
                # or request_data.get("material_tier_fk") in (None, "")
            ):
                log_message(
                    module_name=module,
                    message=f"[{request.method}] client name, quotation title, scope of work, project, salesperson, bhk type fk and material tier must required.",
                    level="WARNING",
                )
                return response_bad_request(
                    errors="quotation title, project, salesperson, bhk type fk must required.",
                    message="All fields are required.",
                )

            today = now().strftime("%Y%m%d")  # Format: 20250716
            last_quotation = (
                Quotation.objects.filter(quotation_number__startswith=f"QTN-{today}")
                .order_by("id")
                .last()
            )
            if last_quotation:
                last_number = int(last_quotation.quotation_number[-4:])
                new_number = last_number + 1
            else:
                new_number = 1
            quotation_number = f"QTN-{today}-{new_number:04d}"
            request_data["quotation_number"] = quotation_number
            request_data["quotation_date"] = now().date()
            response_data = {}
            serializer = QuotationCreateSerializer(data=request_data)
            if serializer.is_valid():
                quotation = serializer.save(
                    created_by=request.user, updated_by=request.user
                )
                if quotation.client_fk:
                    lead = quotation.client_fk
                    if lead.status != CustomerLead.StatusChoices.QUOTED:
                        lead.status = CustomerLead.StatusChoices.QUOTED
                        lead.save()
                    # Create new status-timeline whenever a new quotation created
                    timeline_serializer = LeadStatusTimeLineSerializer(
                        data={
                            "lead_fk": lead.pk,
                            "title_nn": f"New quotation {quotation_number} created.",
                        }
                    )
                    try:
                        timeline_serializer.is_valid()
                        timeline_serializer.save(created_by=request.user)
                    except:
                        return response_bad_request(
                            errors=timeline_serializer.errors,
                            message="Unable to create Lead timeline.",
                        )

                default_milestones = [
                    {"name": "Order confirmation", "percentage": 10},
                    {"name": "Before starting the work", "percentage": 50},
                    {"name": "Mid of the work", "percentage": 35},
                    {"name": "Handover", "percentage": 5},
                ]

                total_calculated_amount = Decimal(0)

                milestone_data = []

                for i in range(len(default_milestones) - 1):
                    milestone = default_milestones[i]

                    amount = (
                        quotation.grand_total * Decimal(milestone["percentage"])
                    ) / Decimal(100)
                    rounded_amount = amount.quantize(Decimal("1"), rounding=ROUND_DOWN)

                    total_calculated_amount += rounded_amount

                    milestone_data.append(
                        {
                            "milestone_name": milestone["name"],
                            "percentage": milestone["percentage"],
                            "amount": int(rounded_amount),
                        }
                    )

                final_milestone = default_milestones[-1]
                final_amount = quotation.grand_total - total_calculated_amount

                milestone_data.append(
                    {
                        "milestone_name": final_milestone["name"],
                        "percentage": final_milestone["percentage"],
                        "amount": int(final_amount),
                    }
                )

                for data in milestone_data:
                    try:
                        payment_serializer = PaymentMilestoneSerializer(
                            data={
                                "milestone_name": data["milestone_name"],
                                "percentage": data["percentage"],
                                "amount": data["amount"],
                            }
                        )
                        payment_serializer.is_valid(raise_exception=True)
                        payment_serializer.save(quotation_fk=quotation)
                    except Exception as e:
                        msg = f"[{request.method}] Serializer validation failed. error: {e}"
                        log_message(module_name=module, message=msg, level="WARNING")
                        return response_bad_request(
                            errors=payment_serializer.errors,
                            message="Quotation Serializer validation failed.",
                        )
                response_data = {
                    "id": quotation.id,
                    "quotation_number": quotation.quotation_number,
                    "client_fk": (
                        quotation.client_fk.id if quotation.client_fk else None
                    ),
                    "salesperson_fk": (
                        quotation.salesperson_fk.id
                        if quotation.salesperson_fk
                        else None
                    ),
                    "bhk_type_fk": (
                        quotation.bhk_type_fk.id if quotation.bhk_type_fk else None
                    ),
                    "material_tier_fk": (
                        quotation.material_tier_fk.id
                        if quotation.material_tier_fk
                        else None
                    ),
                    "quotation_date": quotation.quotation_date,
                    "quotation_title": quotation.quotation_title,
                    "subtotal": int(quotation.subtotal),
                    "discount_amount": int(quotation.discount_amount),
                    "tax_percentage": quotation.tax_percentage,
                    "tax_amount": int(quotation.tax_amount),
                    "grand_total": int(quotation.grand_total),
                    "status": quotation.status,
                    "created_at": quotation.created_at,
                }
                msg = f"[{request.method}] Quotation created successfully."
                log_message(module_name=module, message=msg, level="INFO")
                return response_created(
                    data=response_data, message="Quotation created successfully."
                )

            else:
                msg = f"[{request.method}] Serializer validation failed. error: {serializer.errors}"
                log_message(module_name=module, message=msg, level="WARNING")
                return response_bad_request(
                    errors=serializer.errors,
                    message="Quotation Serializer validation failed.",
                )

        except Exception as e:
            msg = f"[{request.method}] Exception raised during quotation creation: {str(e)}"
            log_message(module_name=module, message=msg, level="WARNING")
            return response_bad_request(
                errors=str(e), message="Exception raised during quotation creation."
            )


class ItemPriceRetrieveAPIView(APIView):
    """
    View to retrieve shutter_finish and price based on item and unit.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request):
        """Handle get request"""
        try:
            # Required parameters check
            item_id = request.query_params.get("item")
            unit_id = request.query_params.get("unit")

            if not item_id:
                return response_bad_request(
                    errors={"item": "At least item is required."},
                    message="Missing required parameters",
                )
            item = Item.objects.get(id=item_id)

            # check for dimensional items
            if item.has_dimension:
                if not unit_id:
                    return response_bad_request(
                    errors={"item": "Unit required for dimensional item."},
                    message="Missing required parameters",
                    )
                Unit.objects.get(id=unit_id)
                qs = ItemPrice.objects.filter(item_id=item_id, unit_id=unit_id)

            # check for dimensional items
            qs = ItemPrice.objects.filter(item_id=item_id)

            # Prepare reduced response
            serializer = ItemPriceDetailsSerializer(qs, many=True)

            msg = f"[{request.method}] Item price retrieved successfully."
            log_message(module_name=module, message=msg, level="INFO")
            return response_success(
                data=serializer.data, message="Item price retrieved successfully"
            )
        except Item.DoesNotExist:
            msg = f"[{request.method}] Item not found."
            log_message(module_name=module, message=msg, level="WARNING")
            return response_bad_request(
                errors="Item not found.", message="Item not found."
            )
        except Unit.DoesNotExist:
            msg = f"[{request.method}] Unit not found."
            log_message(module_name=module, message=msg, level="WARNING")
            return response_bad_request(
                errors="Unit not found.", message="Unit not found."
            )
        except ItemPrice.DoesNotExist:
            return response_bad_request(
                    errors="No price data found for the given parameters.",
                    message="Item price not found."
            )
        except Exception as e:
            msg = f"[{request.method}] Exception raised."
            log_message(module_name=module, message=msg, level="WARNING")
            return response_bad_request(
                errors=str(e), message="Unable to retrieve price of item"
            )


class ItemPriceCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            item = request.data.get("item")
            if not item:
                log_message(
                    module_name=module,
                    message=f"[{request.method}] item field is required.",
                    level="WARNING",
                )
                return response_bad_request(
                    errors="item field is required.", message="item field is required."
                )
            try:
                item = Item.objects.get(pk=item)
            except Item.DoesNotExist:
                log_message(
                    module_name=module,
                    message=f"[{request.method}] Item does not exist.",
                    level="WARNING",
                )
                return response_bad_request(
                    errors="Invalid item ID.", message="Item does not exist."
                )
            # if item has dimension
            if item.has_dimension:
                shutter_finish = request.data.get("shutter_finish")
                unit = request.data.get("unit")

                if not shutter_finish or not unit:
                    log_message(
                        module_name=module,
                        message=f"[{request.method}] shutter_finish and unit are required for dimensional items.",
                        level="WARNING",
                    )
                    return response_bad_request(
                        errors="shutter_finish and unit are required for dimensional items.",
                        message="Missing required fields.",
                    )

                if ItemPrice.objects.filter(
                    item=item, shutter_finish_id=shutter_finish, unit_id=unit
                ).exists():
                    log_message(
                        module_name=module,
                        message=f"[{request.method}] Item price already defined for this combination.",
                        level="INFO",
                    )
                    return response_success(
                        data={"exists": True},
                        message="Item price already defined for this combination.",
                    )
            # if item has no dimension
            else:
                if ItemPrice.objects.filter(
                    item=item, shutter_finish__isnull=True, unit__isnull=True
                ).exists():
                    log_message(
                        module_name=module,
                        message=f"[{request.method}] Price already exists for non-dimensional item.",
                        level="INFO",
                    )
                    return response_success(
                        data={"exists": True}, message="Item price already exists."
                    )

            # Proceed with serializer
            serializer = ItemPriceSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(created_by=request.user, updated_by=request.user)
                msg = f"[{request.method}] Item price added successfully. User {request.user}"
                log_message(module_name=module, message=msg, level="INFO")
                return response_created(
                    data=serializer.data, message="Item price added successfully."
                )

            msg = f"[{request.method}] Validation failed User {request.user}"
            log_message(module_name=module, message=msg, level="WARNING")
            return response_bad_request(
                errors=serializer.errors, message="Validation failed."
            )

        except Exception as e:
            msg = f"[{request.method}] Exception raised. User {request.user}. Error: {str(e)}"
            log_message(module_name=module, message=msg, level="WARNING")
            return response_bad_request(errors=str(e), message="Failed to add price.")


class ProjectCreateAPIView(APIView):
    """
    API View to handle Project creation.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request):
        """Handle post request"""
        try:
            cleaned_data = get_cleaned_data(request)
            project_name = cleaned_data.get("project_name")

            if not project_name:
                log_message(
                    module_name=module,
                    message=f"[{request.method}] project_name is required.",
                    level="WARNING",
                )
                return response_bad_request(
                    errors="project_name is required.",
                    message="Project name is required.",
                )

            if Project.objects.filter(project_name__iexact=project_name).exists():
                log_message(
                    module_name=module,
                    message=f"[{request.method}] Project with name '{project_name}' already exists",
                    level="INFO",
                )
                return response_success(
                    data={"exists": True}, message="project already exist."
                )

            serializer = ProjectSerializer(data=cleaned_data)
            if serializer.is_valid():
                serializer.save(created_by=request.user, updated_by=request.user)
                log_message(
                    module_name=module,
                    message=f"[{request.method}] Project '{project_name}' created successfully.",
                    level="INFO",
                )
                return response_created(
                    data=serializer.data, message="Project created successfully."
                )

            log_message(
                module_name=module,
                message=f"[{request.method}] Validation error: {serializer.errors}",
                level="WARNING",
            )
            return response_bad_request(
                errors=serializer.errors, message="Invalid data provided."
            )

        except Exception as e:
            log_message(
                module_name=module,
                message=f"[{request.method}] Internal error: {str(e)}",
                level="ERROR",
            )
            return response_server_error(
                message="An error occurred while creating the project."
            )


class QuotationSummaryAPIView(APIView):
    "API for generate create quotation summery."

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            serializer = QuotationSummarySerializer(data=request.data)
            if serializer.is_valid():
                log_message(
                    "create_quotation",
                    message="quotation summary calculated successfully",
                    level="INFO",
                )
                return response_success(
                    data=serializer.validated_data,
                    message="quotation summary calculated successfully.",
                )
            log_message(
                "create_quotation",
                message="invalid data for quotation summary",
                level="WARNING",
            )
            return response_bad_request(
                errors=serializer.errors, message="invalid data for quotation summary."
            )
        except Exception as e:
            log_message(
                "create_quotation",
                message="quotation summary not calculated",
                level="WARNING",
            )
            return response_bad_request(
                errors=str(e),
                message="quotation summary not calculated",
            )


class PaymentTermsSectionAPIView(APIView):
    """
    It calculate the each payment phase ammount
    based on grand total cmmount.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request):
        try:
            grand_total = request.data.get("grand_total")
            if grand_total in ("", None):
                msg = f"[{request.method}] grand_total value must be required to calculate payment terms."
                log_message(module_name=module, message=msg, level="WARNING")
                return response_bad_request(
                    errors="grand_total value must be required",
                    message="grand_total value must be required",
                )

            response_data = {}
            default_milestones = [
                {"name": "Order confirmation", "percentage": 10},
                {"name": "Before starting the work", "percentage": 50},
                {"name": "Mid of the work", "percentage": 35},
                {"name": "Handover", "percentage": 5},
            ]

            total_calculated_amount = 0
            for milestone_data in default_milestones[:-1]:
                amount = int((grand_total * milestone_data["percentage"]) / 100)
                total_calculated_amount += amount
                response_data[milestone_data["name"]] = {
                    "percentage": milestone_data["percentage"],
                    "amount": amount,
                }

            last_milestone = default_milestones[-1]
            remaining_amount = grand_total - total_calculated_amount
            response_data[last_milestone["name"]] = {
                "percentage": last_milestone["percentage"],
                "amount": remaining_amount,
            }

            msg = f"[{request.method}] payment terms retrive successflly."
            log_message(module_name=module, message=msg, level="INFO")
            return response_success(
                data=response_data, message="payment terms retrive successflly."
            )

        except Exception as e:
            msg = f"[{request.method}] payment terms can't retrived."
            log_message(module_name=module, message=msg, level="WARNING")
            return response_bad_request(
                errors=str(e), message="payment terms can't retrived."
            )


class QuotationDetailsAPIView(APIView):
    """Get Quotation Details"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            if not pk:
                raise ValueError("pk must be provided")

            quotation = Quotation.objects.get(pk=pk)
            serializer = QuotationDetailSerializer(quotation)

            log_message(
                module_name=module,
                message=f"[{request.method}] Quotation details id {pk} retrieved successfully.",
                level="INFO",
            )

            return response_success(
                data=serializer.data, message="Data retrieved successfully."
            )

        except Quotation.DoesNotExist:
            log_message(
                module_name=module,
                message=f"[{request.method}] Quotation with id:{pk} does not exist.",
                level="WARNING",
            )
            return response_bad_request(
                errors=f"Quotation with id:{pk} does not exist.",
                message=f"Quotation with id:{pk} does not exist.",
            )

        except Exception as e:
            log_message(
                module_name=module,
                message=f"[{request.method}] Unable to fetch quotation details. Error: {str(e)}",
                level="WARNING",
            )


class AddProjectAPIView(APIView):
    def post(self, request):
        try:
            data = request.data.copy()
            data["created_by"] = request.user.id
            data["updated_by"] = request.user.id
            serializer = ProjectCreateSerializer(data=data)
            if serializer.is_valid():
                project = serializer.save()
                response_data = ProjectCreateSerializer(project).data
                return response_created(
                    message="Project created successfully", data=response_data
                )
            return response_bad_request(
                errors=serializer.errors, message="Project not created"
            )
        except Exception as e:
            return response_bad_request(
                errors="Project is not created", message="Project is not created"
            )


class LeadQuotationsListView(APIView):
    """
    Lead quotations list view
    """

    def get(self, request, lead_id):
        """
        Get Quotations by lead
        """
        quotations = Quotation.objects.filter(client_fk_id=lead_id).order_by("id")
        serializer = QuotationListSerializer(quotations, many=True)
        return response_success(data=serializer.data)


class CSVModelUploadView(APIView):
    """
    Adding csv file api for upload multiple file
    """

    parser_classes = [MultiPartParser]

    def post(self, request, model_name):
        """
        post method for adding csv file
        """
        model_name = model_name.lower()

        MODEL_MAP = {
            "item": Item,
            "unit": Unit,
            "shutterfinish": ShutterFinish,
            "roomtype": RoomType,
            "materialtier": MaterialTier,
            "bhktype": BHKType,
            "scopeofwork": ScopeOfWork,
            "project": Project,
            "itemprice": ItemPrice,
            "servicetype": ServiceType,
            "brandtype": BrandType,
            "roomtodesign": RoomToDesign,
        }

        FOREIGN_KEY_MAPPINGS = {
            "itemprice": {
                "item": Item,
                "shutter_finish": ShutterFinish,
                "unit": Unit,
            },
        }

        LOOKUP_FIELD_MAP = {
            "item": "item_name",
            "unit": "unit_abbreviation",
            "shutterfinish": "shutter_finish_name",
            "roomtype": "room_type_name",
            "materialtier": "tier_name",
            "bhktype": "bhk_type_name",
            "scopeofwork": "scope_name",
            "project": "project_name",
            "servicetype": "service_name",
            "brandtype": "brand_name",
            "roomtodesign": "room_name",
        }

        model = MODEL_MAP.get(model_name)
        if not model:
            return response_bad_request(
                errors=f"Invalid model name: {model_name}",
                message=f"Invalid model name: {model_name}",
            )

        file = request.FILES.get("file")
        if not file or not file.name.endswith(".csv"):
            return response_bad_request(
                errors="Invalid or missing CSV file.",
                message="Invalid or missing CSV file.",
            )

        decoded_file = file.read().decode("utf-8")
        csv_reader = csv.DictReader(io.StringIO(decoded_file))

        model_fields = {
            field.name for field in model._meta.fields if field.name != "id"
        }

        created = 0
        skipped = 0
        errors = []

        for idx, row in enumerate(csv_reader, start=2):
            try:
                field_data = {}
                fk_mappings = FOREIGN_KEY_MAPPINGS.get(model_name, {})

                for k in row:
                    if k in model_fields:
                        value = row[k].strip()
                        if value == "":
                            field_data[k] = None
                        elif k in fk_mappings:
                            related_model = fk_mappings[k]
                            try:
                                if related_model == Item:
                                    related_obj = related_model.objects.get(
                                        item_name__iexact=value
                                    )
                                elif related_model == ShutterFinish:
                                    related_obj = related_model.objects.get(
                                        shutter_finish_name__iexact=value
                                    )
                                elif related_model == Unit:
                                    related_obj = related_model.objects.get(
                                        unit_abbreviation__iexact=value
                                    )
                                else:
                                    related_obj = related_model.objects.get(
                                        name__iexact=value
                                    )

                                field_data[k] = related_obj
                            except related_model.DoesNotExist:
                                errors.append(
                                    f"Row {idx}: {related_model.__name__} with name '{value}' does not exist."
                                )
                                continue
                            except related_model.MultipleObjectsReturned:
                                errors.append(
                                    f"Row {idx}: Multiple {related_model.__name__} objects found with name '{value}'."
                                )
                                continue
                        else:
                            field_data[k] = value

                if len(errors) > len([e for e in errors if f"Row {idx}" not in e]):
                    continue

                lookup_field = LOOKUP_FIELD_MAP.get(model_name)

                if lookup_field and lookup_field in field_data:
                    lookup_value = field_data.get(lookup_field)
                    if (
                        lookup_value
                        and not model.objects.filter(
                            **{f"{lookup_field}__iexact": lookup_value}
                        ).exists()
                    ):
                        model.objects.create(**field_data)
                        created += 1
                    else:
                        skipped += 1
                else:
                    if model_name == "itemprice":
                        existing_obj = model.objects.filter(
                            item=field_data.get("item"),
                            shutter_finish=field_data.get("shutter_finish"),
                            unit=field_data.get("unit"),
                        ).first()

                        if existing_obj:
                            existing_obj.price_per_unit = field_data.get(
                                "price_per_unit"
                            )
                            existing_obj.save()
                            skipped += 1
                        else:
                            model.objects.create(**field_data)
                            created += 1
                    else:
                        model.objects.create(**field_data)
                        created += 1

            except Exception as e:
                errors.append(f"Row {idx}: {str(e)}")

        return response_success(
            data={
                "message": f"Processed {created + skipped} rows.",
                "created": created,
                "skipped": skipped,
                "errors": errors,
            },
            message="csv file upload successfully",
        )
