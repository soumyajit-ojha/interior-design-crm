"""
Views to handle Quotation endpoints
"""

from rest_framework.request import Request
from rest_framework.views import APIView

from leads_app.models import CustomerLead
from leads_app.serializers import LeadStatusTimeLineSerializer
from .models import Quotation
from .serializers import QuotationListSerializer,ApprovedQuotationSerializer
from igolohomes.custom_logger import log_message
from utils.response_utils import (
    response_success,
    response_created,
    response_bad_request,
    response_server_error,
)


module = str((__name__).split(".")[0])


class QuotationStatusChangeAPIView(APIView):
    """
    Handles quotation status changes via PATCH.
    """
    def patch(self, request: Request):
        """update quotation status"""
        quotation_id = request.data.get("quotation_id")
        status = str(request.data.get("status")).strip().title()

        if not quotation_id or not status:
            log_message(
                module_name=module,
                message="quotation_id and status required.",
                level="WARNING",
            )
            return response_bad_request(errors="quotation_id and status are required.")

        valid_choices = list(dict(Quotation.StatusChoices.choices).keys())
        if status not in valid_choices:
            log_message(
                module_name=module,
                message=f"[{request.method}] invalid status. Valid choices: {valid_choices}",
                level="WARNING",
            )
            return response_bad_request(
                errors=f"Invalid status '{status}'. Valid choices: {valid_choices}",
                message=f"Invalid status '{status}'.",
            )

        try:
            quotation = Quotation.objects.get(id=quotation_id)
            lead = quotation.client_fk
            quotations_list = lead.quotation_client.all()


            if quotation.status == status:
                log_message(
                    module_name=module,
                    message=f"[{request.method}] Status already set to '{status}'.",
                    level="WARNING",
                )
                return response_bad_request(
                    errors="No change: Status is already set.",
                    message=f"Status is already '{status}'.",
                )

            # Prevent multiple approvals
            found = quotations_list.filter(status__iexact=Quotation.StatusChoices.APPROVED).first()
            if found:
                log_message(
                    module_name=module,
                    message=f"[{request.method}] Quotation {found.quotation_number} already Approved.",
                    level="WARNING",
                )
                return response_bad_request(
                    errors=f"Quotation {found.quotation_number} is already approved.",
                    message="Another quotation is already approved."
                )

            serializer = QuotationListSerializer(
                quotation, data={"status": status}, partial=True
            )
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                if status in ("Sent", "Approved"):
                    timeline_serializer = LeadStatusTimeLineSerializer(data={
                        'lead_fk':lead.pk,
                        'title_nn': (
                            f"Quotation No. {quotation.quotation_number} has been "
                            f"{'sent to the client' if status == 'Sent' else 'approved'}."
                        )
                    })
                    try:
                        timeline_serializer.is_valid()
                        timeline_serializer.save(created_by=request.user)
                    except Exception as e:
                        return response_bad_request(
                            errors=str(e),
                            message="Unable to create Quotation timeline"
                        )
                log_message(
                    module_name=module,
                    message=f"[{request.method}] Status updated to '{status}'.",
                    level="INFO",
                )
                return response_success(
                    data=serializer.data,
                    message=f"Quotation status changed to '{status}'.",
                )
            log_message(
                module_name=module,
                message=f"[{request.method}] Invalid serializer data.",
                level="WARNING",
            )
            return response_bad_request(
                errors=serializer.errors, message="Invalid data."
            )

        except Quotation.DoesNotExist:
            log_message(
                module_name=module,
                message=f"[{request.method}] Quotation ID '{quotation_id}' not found.",
                level="WARNING",
            )
            return response_bad_request(
                errors={"exists": False},
                message=f"Quotation with ID '{quotation_id}' does not exist.",
            )

        except Exception as e:
            log_message(
                module_name=module,
                message=f"[{request.method}] Error while changing status: {str(e)}",
                level="ERROR",
            )
            return response_bad_request(
                errors=str(e),
                message="Failed to change status due to an unexpected error.",
            )


class GetApprovedQuotationAPIView(APIView):
    def get(self, request, lead_id):
        client = CustomerLead.objects.get(pk=lead_id)
        quotation = Quotation.objects.filter(client_fk=client,status="Approved").first()
        if not quotation:
            return response_bad_request(errors="Approved Quotation not found",message="Approved Quotation not found")

        serializer = ApprovedQuotationSerializer(quotation)
        return response_success(serializer.data)