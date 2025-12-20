from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView

from leads_app.models import CustomerLead, LeadStatusTimeLine, LeadNote
from quotations_app.models import BHKType, ScopeOfWork
from leads_app.serializers import *
from quotations_app.serializers import BHKTypeSerializer
from igolohomes.custom_logger import log_message
from utils.utils import CustomPagePagination
from utils.exports import export_to_csv, export_to_excel
from utils.response_utils import (
    response_success,
    response_created,
    response_bad_request,
    response_server_error,
)
from .filters import CustomSearchFilter, CustomerLeadCustomFilter

module = str((__name__).split(".")[0])
User = get_user_model()


class CustomerLeadCheckAPIView(APIView):
    """
    API View to check if a customer lead already exists.
    Handles POST requests to validate email and phone uniqueness.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Handles POST requests to check if a lead with given email or phone exists.
        Returns validation status for email and phone.
        """
        try:
            serializer = CustomerLeadCheckSerializer(data=request.data)
            if not serializer.is_valid():
                msg = f"[{request.method}] Lead Existance Check Validation Error {serializer.errors} "
                log_message(module_name=module, message=msg, level="WARNING")
                return response_bad_request(
                    errors=serializer.errors, message="Invalid Inputs"
                )

            email = serializer.data.get("email")
            phone = serializer.data.get("phone")

            if CustomerLead.objects.filter(email=email).exists():
                msg = f"[POST] Lead with this email already exists '{request.user}'."
                log_message(module_name=module, message=msg, level="WARNING")
                # return response_bad_request(
                #     errors="Bad Request", message="Lead with this email already exists."
                # )
                return response_success(
                    data={"exists": True},
                    message="Lead with this email already exists.",
                )

            if CustomerLead.objects.filter(phone=phone).exists():
                msg = f"[POST] Lead with this phone number already exists '{request.user}' error raised"
                log_message(module_name=module, message=msg, level="WARNING")
                return response_success(
                    data={"exists": True},
                    message="Lead with this phone already exists.",
                )

            msg = (
                f"[POST] Lead existence check passed for email: {email} phone: {phone}"
            )
            log_message(module_name=module, message=msg, level="INFO")
            return response_success(
                data={"exists": False},
                message="No existing lead found. You can proceed.",
            )

        except Exception as e:
            msg = f"[POST] Exception during Lead existence check: {str(e)}"
            log_message(module_name=module, message=msg, level="ERROR")
            return response_server_error(message="Failed to check leads existance.")


class CustomerLeadCreateAPIView(APIView):

    def post(self, request):
        """
        Handles POST requests to create a new customer lead.
        """
        try:
            data = request.data.copy()
            floor_plan_files = request.FILES.getlist("floor_plan")

            if "floor_plan" in data:
                del data["floor_plan"]

            serializer = CustomerLeadSerializer(data=data, context={"request": request})

            if not serializer.is_valid():
                msg = f"[{request.method}] Lead creation validation error: {serializer.errors}"
                log_message(module_name=module, message=msg, level="WARNING")
                return response_bad_request(
                    errors=serializer.errors, message="Invalid Inputs"
                )

            email = serializer.validated_data.get("email")
            phone = serializer.validated_data.get("phone")

            if CustomerLead.objects.filter(email=email).exists():
                msg = f"[POST] Lead with this email already exists '{request.user}' error raised"
                log_message(module_name=module, message=msg, level="WARNING")
                return response_bad_request(
                    errors={"email": "Lead with this email already exists."}
                )

            if CustomerLead.objects.filter(phone=phone).exists():
                msg = f"[POST] Lead with this phone number already exists '{request.user}' error raised"
                log_message(module_name=module, message=msg, level="WARNING")
                return response_bad_request(
                    errors={"phone": "Lead with this phone number already exists."}
                )

            with transaction.atomic():
                lead = serializer.save(created_by=request.user, updated_by=request.user)

                if floor_plan_files:
                    for file in floor_plan_files:
                        # --- THE KEY CHANGE IS HERE ---
                        # Convert file size from bytes to megabytes (MB)
                        file_size_mb = Decimal(file.size / (1024 * 1024)).quantize(
                            Decimal("0.01")
                        )

                        file_data = {
                            "lead_fk": lead.pk,
                            "file_path": file,
                            "file_name": file.name,
                            "file_size": file_size_mb,  # Use the converted MB size
                        }

                        file_serializer = LeadFileSerializer(
                            data=file_data, context={"request": request}
                        )

                        if not file_serializer.is_valid():
                            transaction.set_rollback(True)
                            msg = f"[POST] File '{file.name}' validation error: {file_serializer.errors}"
                            log_message(
                                module_name=module, message=msg, level="WARNING"
                            )
                            return response_bad_request(
                                errors=file_serializer.errors,
                                message=f"Invalid file: {file.name}. Lead creation failed.",
                            )

                        file_serializer.save(
                            created_by=request.user, updated_by=request.user
                        )

            msg = f"[POST] Lead (ID={lead.pk}) created by {request.user.username}"
            log_message(module_name=module, message=msg, level="INFO")

            lead_response_serializer = CustomerLeadSerializer(
                lead, context={"request": request}
            )
            return response_created(
                data=lead_response_serializer.data, message="Lead Created Successfully."
            )

        except ValidationError as e:
            msg = f"[POST] Validation error during Lead creation: {str(e.detail)}"
            log_message(module_name=module, message=msg, level="ERROR")
            return response_bad_request(errors=e.detail, message="Validation error.")

        except Exception as e:
            msg = f"[POST] Exception during Lead creation: {str(e)}"
            log_message(module_name=module, message=msg, level="ERROR")
            return response_bad_request(errors=str(e), message="Failed to create lead.")


class CustomerLeadRetrieveAPIView(APIView):
    """
    Retrieve details of a single CustomerLead, including all related notes and files.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            lead = CustomerLead.objects.get(pk=pk)
            if not lead:
                raise ValueError(f"Lead with id {pk} doesn't exist.")
            try:
                lead_serializer = CustomerLeadSerializer(
                    lead, context={"request": request}
                )
            except Exception as e:
                msg = f"[GET] Exception raised during fetching lead serializer data "
                log_message(module_name=module, message=msg, level="WARNING")
                return response_bad_request(
                    errors=str(e),
                    message="Exception raised during fetching lead serializer data",
                )
            try:
                notes_qs = lead.notes.all()
                notes_serializer = LeadNoteSerializer(
                    notes_qs, many=True, context={"request": request}
                )
            except Exception as e:
                msg = (
                    f"[GET] Exception raised during fetching lead Note serializer data "
                )
                log_message(module_name=module, message=msg, level="WARNING")
                return response_bad_request(
                    errors=str(e),
                    message="Exception raised during fetching lead note serializer data",
                )
            try:
                files_qs = lead.files.all()
                files_serializer = LeadFileRetrieveSerializer(
                    files_qs, many=True, context={"request": request}
                )
            except Exception as e:
                msg = (
                    f"[GET] Exception raised during fetching lead file serializer data "
                )
                log_message(module_name=module, message=msg, level="WARNING")
                return response_bad_request(
                    errors=str(e),
                    message="Exception raised during fetching lead file serializer data",
                )

            try:
                timeline_qs = lead.status_history.all()
                timeline_serializer = LeadStatusTimeLineSerializer(
                    timeline_qs, many=True
                )
            except Exception as e:
                msg = f"[GET] Exception raised during fetching lead status timeline serializer data "
                log_message(module_name=module, message=msg, level="WARNING")
                return response_bad_request(
                    errors=str(e),
                    message="Exception raised during fetching lead status timeline serializer data",
                )

            data = lead_serializer.data
            data["notes"] = notes_serializer.data
            data["files"] = files_serializer.data
            data["timeline"] = timeline_serializer.data

            msg = f"[GET] Lead details with id {pk} retrive successfully."
            log_message(module_name=module, message=msg, level="INFO")
            return response_success(data=data, message="Lead data found")

        except CustomerLead.DoesNotExist:
            msg = f"[PATCH] Lead with id {pk} doesn't exist."
            log_message(module_name=module, message=msg, level="WARNING")
            return response_bad_request(
                errors=f"Lead with id {pk} doesn't exist.",
                message=f"Lead with id {pk} doesn't exist.",
            )

        except Exception as e:
            msg = f"[GET] Exception Raised while Lead details  retrival successfully."
            log_message(module_name=module, message=msg, level="ERROR")
            return response_bad_request(
                errors=str(e),
                message="Exception Raised while Lead details  retrival successfully.",
            )


class CustomerLeadUpdateAPIView(APIView):
    """
    API View to update a customer lead by its primary key (pk).
    Handles PUT requests to update lead details with validation and logging.
    """

    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, pk):
        """
        Handles PUT requests to update a customer lead by its primary key (pk).
        Validates the request data using the CustomerLeadSerializer.
        Logs the update action and returns the updated lead details.
        """
        try:
            lead = get_object_or_404(CustomerLead, pk=pk)
            allowed_fields = set(CustomerLeadSerializer().get_fields().keys())
            invalid_fields = set(request.data.keys()) - allowed_fields
            if invalid_fields:
                msg = f"[PUT] Invalid fields in request for Lead {pk}: {invalid_fields}"
                log_message(module_name=module, message=msg, level="WARNING")
                return response_bad_request(
                    errors={"detail": f"Invalid field(s): {', '.join(invalid_fields)}"},
                    message="Invalid field(s)",
                )

            email = request.data.get("email")
            phone = request.data.get("phone")

            if (
                email
                and CustomerLead.objects.exclude(pk=pk).filter(email=email).exists()
            ):
                msg = f"[PUT] Lead with this email already exists '{request.user}' error raised"
                log_message(module_name=module, message=msg, level="WARNING")
                return response_bad_request(
                    errors="Bad Request", message="Lead with this email already exists."
                )

            if CustomerLead.objects.filter(phone=phone).exists():
                msg = f"[PUT] Lead with this phone number already exists '{request.user}' error raised"
                log_message(module_name=module, message=msg, level="WARNING")
                return response_bad_request(
                    errors="Bad Request",
                    message="Lead with this phone number already exists.",
                )

            serializer = CustomerLeadSerializer(
                lead, data=request.data, partial=True, context={"request": request}
            )
            if serializer.is_valid():
                serializer.save(updated_by=request.user)

                msg = f"[PUT] Lead {pk} updated by {request.user.username}"
                log_message(module_name=module, message=msg, level="INFO")
                return response_success(
                    data=serializer.data, message="Lead updated successfully"
                )

            msg = (
                f"[PUT] Serializer validation failed for Lead {pk}: {serializer.errors}"
            )
            log_message(module_name=module, message=msg, level="WARNING")
            return response_bad_request(
                errors=serializer.errors, message="Cannot update lead"
            )

        except Exception as e:
            msg = f"[PUT] Exception while updating lead {pk}: {str(e)}"
            log_message(module_name=module, message=msg, level="ERROR")
            return response_bad_request(errors=str(e), message="Unable to Update Lead.")


class CustomerLeadDeleteAPIView(APIView):
    """
    API View to delete a customer lead by its primary key (pk).
    """

    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        """
        Handles PATCH requests to update a customer lead by its primary key (pk).
        """
        try:
            lead = get_object_or_404(CustomerLead, pk=pk)
            lead.delete()
            msg = f"[DELETE] Lead {pk} deleted by {request.user.username}"
            log_message(module_name=module, message=msg, level="INFO")
            return response_success(message=f"Lead with id:{pk} deleted.")

        except Exception as e:
            msg = f"[DELETE] Exception while deleting lead {pk}: {str(e)}"
            log_message(module_name=module, message=msg, level="ERROR")
            return response_bad_request(errors=str(e), message="Unable to delete Lead")


class LeadNoteCreateAPIView(APIView):
    """
    Add a note to a specific CustomerLead.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            lead_fk = request.data.get("lead_fk")
            lead = get_object_or_404(CustomerLead, pk=lead_fk)
            data = request.data.copy()
            data["lead_fk"] = lead.id
            serializer = LeadNoteSerializer(data=data, context={"request": request})

            if serializer.is_valid():
                serializer.save(created_by=request.user)
                msg = f"[{request.method}] Note added successfully for lead {lead}"
                return response_success(
                    data=serializer.data, message="Note added successfully"
                )

            msg = f"[{request.method}] Validation error in note data {request.user.username}"
            log_message(module_name=module, message=msg, level="WARNING")
            return response_bad_request(
                errors=serializer.errors, message="Validation error in note data"
            )

        except Exception as e:
            msg = f"[{request.method}] Error creating note for lead {lead_fk}: {e}"
            log_message(module_name=module, message=msg, level="ERROR")
            return response_bad_request(errors=str(e), message="Failed to add note")


class LeadNoteDeleteAPIView(APIView):
    """
    API View to delete a lead note by its primary key (pk).
    """

    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        """
        Handles Delete requests to update a lead note by its primary key (pk).
        """
        try:
            lead = get_object_or_404(CustomerLead, pk=request.data.get("lead_fk"))
            if not lead:
                return ValueError("lead_fk must required.")
            lead_note = get_object_or_404(LeadNote, pk=pk)
            if lead_note.lead_fk != lead:
                msg = f"[DELETE] You Have No access for this content."
                log_message(module_name=module, message=msg, level="WARNING")
            lead_note.delete()
            msg = f"[DELETE] Lead note {pk} deleted by {request.user.username}"
            log_message(module_name=module, message=msg, level="INFO")
            return response_success(
                message=f"Lead note with id:{pk} deleted for {lead.client_name}."
            )

        except Exception as e:
            msg = f"[DELETE] Exception while deleting lead note {pk}: {str(e)}"
            log_message(module_name=module, message=msg, level="ERROR")
            return response_bad_request(
                errors=str(e), message="Unable to delete lead note"
            )


class LeadChangeStatusAPIView(APIView):
    """
    Update status of a CustomerLead and record history.
    """

    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            if not pk:
                raise ValueError("Lead's pk must required to change status")
            lead = get_object_or_404(CustomerLead, pk=pk)
            old_status = lead.status
            new_status = request.data.get("status")
            if new_status not in dict(CustomerLead.StatusChoices.choices):
                msg = f"[PATCH] Invalid status choice."
                log_message(module_name=module, message=msg, level="WARNING")
                return response_bad_request(
                    errors="Bad Request", message="Invalid status choice."
                )

            if old_status == new_status:
                msg = f"Lead status already changed to {new_status}."
                log_message(module_name=module, message=msg, level="WARNING")
                return response_bad_request(errors="Bad Request", message=msg)

            lead.status = new_status
            if new_status == CustomerLead.StatusChoices.CONVERTED:
                lead.is_converted_to_client = True
                lead.conversion_date = timezone.now()
            lead.save(
                update_fields=["status", "is_converted_to_client", "conversion_date"]
            )

            history = LeadStatusTimeLine.objects.create(
                lead_fk=lead,
                title_nn=f"Status changed to '{new_status}'",
                created_by=request.user,
            )
            history_serializer = LeadStatusTimeLineSerializer(history)

            msg = f"[PATCH] Status changed successfully."
            log_message(module_name=module, message=msg, level="INFO")
            return response_success(
                data=history_serializer.data, message="status changed successfully."
            )

        except Exception as e:
            msg = f"[PATCH] Exception raised during changinf lead status"
            log_message(module_name=module, message=msg, level="ERROR")
            return response_bad_request(
                errors=str(e), message="Exception raised during changing lead status."
            )


class LeadAssignSalesmanAPIView(APIView):
    """
    Assign a lead to a user.
    """

    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            user_id = request.data.get("assigned_to_fk")
            if not pk or not user_id:
                raise ValueError(
                    "Lead's pk and assigned_to_fk required to update its status."
                )

            lead = CustomerLead.objects.get(pk=pk)
            if not lead:
                raise ValueError(f"Lead with id {pk} doesn't exist.")

            try:
                user = User.objects.get(pk=user_id)
                if user.user_type_nn != "salesman":
                    msg = f"[PATCH] {user.username} is not a salesman."
                    log_message(module_name=module, message=msg, level="WARNING")
                    return response_bad_request(
                        errors="Bad Request", message="selected user is not a salesman."
                    )

            except User.DoesNotExist:
                msg = f"[PATCH] Assigned salesman doesn't exist."
                log_message(module_name=module, message=msg, level="WARNING")
                return response_bad_request(
                    errors={"assigned_to_fk": "User not found."}
                )

            lead.assigned_to_fk = user
            lead.save(update_fields=["assigned_to_fk"])
            serializer = CustomerLeadSerializer(
                lead, partial=True, context={"request": request}
            )

            msg = f"[PATCH] Assigned to salesman successfully."
            log_message(module_name=module, message=msg, level="INFO")
            return response_success(
                data=serializer.data, message="Assigned to salesman successfully."
            )

        except CustomerLead.DoesNotExist:
            msg = f"[PATCH] Lead with id {pk} doesn't exist."
            log_message(module_name=module, message=msg, level="WARNING")
            return response_bad_request(
                errors="Lead Doesn't Exist", message=f"Lead with id {pk} doesn't exist."
            )

        except Exception as e:
            msg = f"[PATCH] Exception raised during assigning salesman. ERROR: {str(e)}"
            log_message(module_name=module, message=msg, level="ERROR")
            return response_bad_request(
                errors=str(e), message="Exception raised during assigning salesman"
            )


class LeadExportAPIView(APIView):
    """
    API View to export customer leads in CSV, Excel, or PDF format.
    Accepts a query parameter `export` with values: csv, excel, pdf.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        export_format = request.query_params.get("export", "csv").lower()

        # Get queryset and serialize
        leads_qs = CustomerLead.objects.all()
        serializer = CustomerLeadListSerializer(
            leads_qs, many=True, context={"request": request}
        )
        data = serializer.data

        # If no data to export
        if not data:
            return HttpResponse("No data to export.", status=204)

        # Export based on format
        if export_format == "csv":
            return export_to_csv(data)
        elif export_format in ["excel", "xlsx"]:
            return export_to_excel(data)
        else:
            return Response(
                {
                    "error": f"Invalid export format: {export_format}. Use csv, excel, or pdf."
                },
                status=400,
            )


class SalesmanListAPIView(APIView):
    """
    API View to list all users with user_type_nn = 'salesman'.
    Supports search and pagination.
    """

    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagePagination

    def get(self, request):
        try:
            queryset = User.objects.filter(user_type_nn="salesman")
            if not queryset:
                msg = f"[GET] No Salesman found {request.user.username}"
                log_message(module_name=module, message=msg, level="INFO")
                return response_success(
                    data="No data found", message="No Salesman found"
                )

            serializer = UserSerializer(
                queryset, many=True, context={"request": request}
            )
            msg = f"[GET] Full salesman list viewed by {request.user.username}"
            log_message(module_name=module, message=msg, level="INFO")
            return response_success(
                data=serializer.data, message="Salesman list retrieved successfully"
            )

        except Exception as e:
            msg = f"[GET] Exception in SalesmanListAPIView: {str(e)}"
            log_message(module_name=module, message=msg, level="ERROR")
            return response_bad_request(
                errors=str(e), message="Error while retrieving salesman list"
            )


class LeadMarkAsDoneAPIView(APIView):
    """
    API View to update `mark_as_done` and conditionally update lead status and timeline.
    """

    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            lead = CustomerLead.objects.get(pk=pk)

            if not lead:
                raise ValueError(f"Lead with id {pk} doesn't exist.")

            follow_up_dt = request.data.get("follow_up_dt")
            follow_up_note = request.data.get("follow_up_note")
            follow_up_at = request.data.get("follow_up_at")
            is_reminder = request.data.get("is_reminder")

            old_status = lead.status

            if old_status in (
                CustomerLead.StatusChoices.NEW,
                CustomerLead.StatusChoices.CONTACTED,
            ):
                lead.status = CustomerLead.StatusChoices.FOLLOW_UP

            if follow_up_dt:
                lead.follow_up_dt = follow_up_dt
            if follow_up_note:
                lead.follow_up_note = follow_up_note
            if follow_up_at:
                lead.follow_up_at = follow_up_at
            if is_reminder is not None:
                lead.is_reminder = is_reminder

            lead.save()

            if old_status != CustomerLead.StatusChoices.FOLLOW_UP:
                LeadStatusTimeLine.objects.create(
                    lead_fk=lead,
                    title_nn=f"Status changed to '{CustomerLead.StatusChoices.FOLLOW_UP}'.",
                    created_by=request.user,
                )

            serializer = CustomerLeadSerializer(
                lead, data=request.data, partial=True, context={"request": request}
            )
            if serializer.is_valid():
                serializer.save()
            else:
                return response_bad_request(
                    errors=serializer.errors, message="Invalid data"
                )

            msg = f"[PATCH] mark_as_done updated for Lead ID {pk}. Status updated: True"
            log_message(module_name=module, message=msg, level="INFO")
            return response_success(
                data=serializer.data, message="Lead updated successfully."
            )

        except CustomerLead.DoesNotExist:
            msg = f"[PATCH] Lead with id {pk} doesn't exist."
            log_message(module_name=module, message=msg, level="WARNING")
            return response_bad_request(
                errors="Lead Doesn't Exist", message=f"Lead with id {pk} doesn't exist."
            )

        except Exception as e:
            msg = f"[PATCH] Exception raised during Marking as done. ERROR: {str(e)}"
            log_message(module_name=module, message=msg, level="ERROR")
            return response_bad_request(
                errors=str(e), message="Unable to submit mark_as_done"
            )


class LeadFileCreateAPIView(APIView):
    """
    Upload a file for a specific Customer Lead
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        post: Handle upload file for a customer lead
        """
        try:
            lead_fk = request.data.get("lead_fk")
            if not lead_fk:
                raise ValueError("lead_fk field must required")

            lead = CustomerLead.objects.get(pk=lead_fk)
            if not lead:
                msg = f"[{request.method}] Lead doesn't exist with id {lead_fk}"
                log_message(module_name=module, message=msg, level="WARNING")
                return response_bad_request(
                    errors="Bad Request",
                    message=f"Lead doesnot exist with id {lead_fk}",
                )

            serializer = LeadFileSerializer(
                data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                msg = f"[{request.method}] File added successfully for lead {lead}"
                return response_success(
                    data=serializer.data, message="File added successfully"
                )

            msg = f"[{request.method}] Validation error in file data {request.user.username}"
            log_message(module_name=module, message=msg, level="WARNING")
            return response_bad_request(
                errors=serializer.errors, message="Validation error in file data"
            )

        except CustomerLead.DoesNotExist:
            msg = f"[{request.method}] Lead doesn't exist with id {lead_fk}"
            log_message(module_name=module, message=msg, level="WARNING")
            return response_bad_request(
                errors="Bad Request", message=f"Lead doesn't exist with id {lead_fk}"
            )

        except Exception as e:
            msg = f"[{request.method}] Error creating file for lead {lead_fk}: {e}"
            log_message(module_name=module, message=msg, level="ERROR")
            return response_bad_request(errors=str(e), message="Failed to add file")


class LeadFileDeleteAPIView(APIView):
    """
    Delete a specific file from a CustomerLead.
    """

    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        try:
            file_obj = get_object_or_404(LeadFile, pk=pk)
            file_obj.delete()
            msg = f"[{request.method}] file deleted sucessfully."
            log_message(module_name=module, message=msg, level="INFO")
            return response_success(message="File deleted successfully")

        except Exception as e:
            msg = f"[{request.method}] Error deleting file ID {pk}: {e}"
            log_message(module_name=module, message=msg, level="ERROR")
            return response_bad_request(errors=str(e), message="Failed to delete file")


class CustomerLeadUnifiedAPIView(APIView):
    """
    Unified API for listing, searching, and filtering customer leads with pagination.
    Handles:
    - Simple list
    - Search (via `search` param)
    - Filters (via custom query params)
    """

    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagePagination

    def get(self, request):
        try:
            queryset = CustomerLead.objects.all().order_by("-created_at")
            # queryset = CustomerLead.objects.exclude(is_converted_to_client=True).order_by("-created_at")
            status_list = request.query_params.getlist("status")
            is_rejected_status_in_filter = "Rejected" in status_list
            print(is_rejected_status_in_filter, status_list, "fff")
            base_filter = Q(is_converted_to_client=False)
            if is_rejected_status_in_filter:
                # If 'Rejected' is in the filter list, add it as an OR condition
                base_filter |= Q(status__iexact="rejected")
            else:
                # If 'Rejected' is NOT in the filter list, explicitly exclude it
                base_filter &= ~Q(status__iexact="rejected")

            queryset = queryset.filter(base_filter)
            search_term = request.query_params.get("search")
            has_filters = any(
                key in CustomerLeadCustomFilter.ALLOWED_FILTERS
                for key in request.query_params.keys()
            )

            if search_term:
                search_fields = ["client_name", "email", "phone", "source", "city"]
                search_filter = CustomSearchFilter(queryset, request, search_fields)
                queryset = search_filter.apply_search()

            if has_filters:
                custom_filter = CustomerLeadCustomFilter(queryset, request)
                queryset = custom_filter.apply_filters()

            paginator = self.pagination_class()
            page = paginator.paginate_queryset(queryset, request, view=self)

            serializer = CustomerLeadListSerializer(
                page if page is not None else queryset,
                many=True,
                context={"request": request},
            )

            user = request.user.username
            current_page = request.query_params.get("page", 1)

            if search_term and has_filters:
                msg = f"[GET] Search & Filter '{search_term}' + filters - Page {current_page} by {user}"
            elif search_term:
                msg = f"[GET] Search '{search_term}' - Page {current_page} by {user}"
            elif has_filters:
                filters_applied = [
                    key
                    for key in request.query_params.keys()
                    if key in CustomerLeadCustomFilter.ALLOWED_FILTERS
                ]
                msg = f"[GET] Filters {filters_applied} - Page {current_page} by {user}"
            else:
                msg = f"[GET] Simple list - Page {current_page} by {user}"

            log_message(module_name=__name__, message=msg, level="INFO")

            if page is not None:
                return paginator.get_paginated_response(serializer.data)
            return response_success(
                data=serializer.data, message="Customer leads retrieved successfully"
            )

        except ValidationError as e:
            msg = f"[GET] Validation error in CustomerLead unified view: {str(e)}"
            log_message(module_name=__name__, message=msg, level="ERROR")
            return response_bad_request(errors=e.detail, message="Validation error.")

        except Exception as e:
            msg = f"[GET] Exception in CustomerLead unified view: {str(e)}"
            log_message(module_name=__name__, message=msg, level="ERROR")
            return response_bad_request(errors=str(e), message="Exception raised.")


class LeadDropdownListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            room_data = RoomToDesignSerializer(
                RoomToDesign.objects.all(), many=True
            ).data
            bhk_room_type = BHKTypeSerializer(BHKType.objects.all(), many=True).data
            brand_data = BrandTypeSerializer(BrandType.objects.all(), many=True).data
            service_data = ServiceTypeSerializer(
                ServiceType.objects.all(), many=True
            ).data
            scope_of_work = ScopeOfWorkSerializer(
                ScopeOfWork.objects.all(), many=True
            ).data
            log_message("leads_app", f"Dropdown data fetch successfully", level="INFO")
            return response_success(
                data={
                    "bhk_room_types": bhk_room_type,
                    "room_to_designs": room_data,
                    "brand_types": brand_data,
                    "service_types": service_data,
                    "scope_of_work": scope_of_work,
                },
                message="Dropdown data fetch successfully",
            )
        except Exception as e:
            log_message("leads_app", f"Dropdown data not fetch", level="ERROR")
            return response_bad_request(
                errors="Dropdown data not fetch", message="Dropdown data not fetch"
            )
