"""
Views: where all requests for vendor or worker being handle
"""

from rest_framework.views import APIView
from rest_framework.request import Request

from igolohomes.custom_logger import log_message
from utils.response_utils import (
    response_success,
    response_created,
    response_bad_request,
)
from client_management.models import Material
from .models import WorkType, Worker, Vendor, MaterialPrice
from .serializers import (
    WorkTypeSerializer,
    WorkerSerializer,
    WorkerRetrieveSerializer,
    MaterialSerializer,
    MaterialPriceSerializer,
    VendorSerializer,
)


class WorkTypeCreateAPIView(APIView):
    """
    Handle request to create work types
    """

    def post(self, request: Request):
        """
        handle post request to create work type.
        """
        name = request.data.get("name_nn")
        if not name:
            log_message(
                module_name="vendor_app",
                message="Work type name required.",
                level="WARNING",
            )
            return response_bad_request(
                errors="Work type name required.", message="Work type name required."
            )
        try:
            serializer = WorkTypeSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                log_message(
                    module_name="vendor_app",
                    message="Work type name required.",
                    level="WARNING",
                )
                return response_created(
                    data=serializer.data, message="Work type created."
                )
            # If the data is not valid
            log_message(
                module_name="vendor_app",
                message="Invalid Work type data.",
                level="WARNING",
            )
            return response_bad_request(
                errors=serializer.errors, message="Unable to create work type."
            )
        except (ValueError, NameError):
            log_message(
                module_name="vendor_app",
                message="Unable to create work type.",
                level="WARNING",
            )
            return response_bad_request(
                errors="Unable to create work type.",
                message="Unable to create work type.",
            )


class WorkTypeRetrieveAPIView(APIView):
    """
    Handle request to get all work type
    """

    def get(self, request: Request):
        """
        retrieve all work types.
        """
        queryset = WorkType.objects.all()
        serializer = WorkTypeSerializer(
            queryset,
            many=True,
            fields=["id", "name_nn", "description"],
        )

        log_message(
            module_name="vendor_app",
            message="Work types retrieved successfully.",
            level="INFO",
        )
        return response_success(data=serializer.data, message="Work types retrieved.")


class WorkerCreateAPIView(APIView):
    """
    Create a new worker
    """

    def post(self, request: Request):
        """handle post method to create worker."""

        try:
            serializer = WorkerSerializer(
                data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                log_message(
                    module_name="vendor_app",
                    message="Worker created.",
                    level="INFO",
                )
                return response_created(data=serializer.data, message="Worker created.")
            log_message(
                module_name="vendor_app",
                message="Invalid data provided for Worker.",
                level="WARNING",
            )
            return response_bad_request(
                errors=serializer.errors, message="Unable to create worker."
            )
        except (ValueError, NameError):
            log_message(
                module_name="vendor_app",
                message="Unable to create worker.",
                level="ERROR",
            )
            return response_bad_request(
                errors="Unable to create worker.", message="Unable to create worker."
            )


class WorkerListAPIView(APIView):
    """
    Retrieve Worker by ID
    """

    def get(self, request: Request):
        """handle request to retrive worker(s)"""
        try:
            worker_id = request.query_params.get("worker_id")
            work_type = request.query_params.get("work_type")

            queryset = Worker.objects.all()
            if worker_id:
                queryset = queryset.filter(pk=worker_id)

            if work_type:
                queryset = queryset.filter(work_type_fk__name_nn__icontains=work_type)

            serializer = WorkerRetrieveSerializer(queryset, many=True)
            if not serializer.data:
                log_message(
                    module_name="vendor_app",
                    message="No data found.",
                    level="INFO",
                )
                return response_success(message="No data found")

            log_message(
                module_name="vendor_app",
                message="Worker retrieved successfully.",
                level="INFO",
            )
            return response_success(data=serializer.data, message="Worker retrieved.")

        except Exception as e:
            # Catch any unexpected errors
            log_message(
                module_name="vendor_app",
                message=f"Error retrieving workers: {str(e)}",
                level="ERROR",
            )
            return response_bad_request(
                errors=str(e), message="Unable to retrieve workers."
            )


class MaterialCreateAPIView(APIView):
    """
    Handle request to create supplied materials.
    """

    def post(self, request: Request):
        """handle post method"""
        name = request.data.get("name")
        if not name:
            log_message("vendor_app", "Material name required.", "WARNING")
            return response_bad_request(
                errors="Name is required.", message="Material name required."
            )

        try:
            serializer = MaterialSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                log_message("vendor_app", "Supplied material created.", "INFO")
                return response_created(
                    data=serializer.data, message="Supplied material created."
                )
            log_message("vendor_app", "Invalid supplied material data.", "WARNING")
            return response_bad_request(
                errors=serializer.errors, message="Invalid data."
            )
        except Exception as e:
            log_message(
                "vendor_app",
                f"Error creating supplied material: {str(e)}",
                "ERROR",
            )
            return response_bad_request(
                errors=str(e), message="Unable to create supplied material."
            )


class MaterialListAPIView(APIView):
    """
    Handle request to list supplied materials.
    """

    def get(self, request: Request):
        """handle get request."""
        queryset = Material.objects.all()
        serializer = MaterialSerializer(
            queryset,
            many=True,
            fields=["id", "name", "description"],
        )
        log_message(
            module_name="vendor_app",
            message="Materials retrieved successfully.",
            level="INFO",
        )
        return response_success(
            data=serializer.data, message="Materials retrieved."
        )


class VendorCreateAPIView(APIView):
    """
    Handle request to create vendors.
    """

    def post(self, request: Request):
        """hande post request"""
        name = request.data.get("name_nn")
        phone = request.data.get("phone_number_nn")
        if not name or not phone:
            log_message("vendor_app", "Vendor name and phone required.", "WARNING")
            return response_bad_request(
                errors="Name and phone required.",
                message="Vendor name and phone required.",
            )

        try:
            serializer = VendorSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                log_message("vendor_app", "Vendor created successfully.", "INFO")
                return response_created(data=serializer.data, message="Vendor created.")
            log_message("vendor_app", "Invalid vendor data.", "WARNING")
            return response_bad_request(
                errors=serializer.errors, message="Invalid data."
            )
        except Exception as e:
            log_message("vendor_app", f"Error creating vendor: {str(e)}", "ERROR")
            return response_bad_request(
                errors=str(e), message="Unable to create vendor."
            )


class VendorListAPIView(APIView):
    """
    Handle request to list vendors.
    """

    def get(self, request: Request):
        """handle get request"""
        vendors = Vendor.objects.all()
        serializer = VendorSerializer(
            vendors,
            many=True,
            fields=[
                "id",
                "name_nn",
                "location",
                "materials",
            ],
        )
        log_message(
            module_name="vendor_app",
            message="Vendors retrieved successfully.",
            level="INFO",
        )
        return response_success(data=serializer.data, message="Vendors retrieved.")


class SuppliedMaterialPriceCreateAPIView(APIView):
    """
    Handle request to create vendor material price.
    """

    def post(self, request: Request):
        """handle post request."""
        try:
            serializer = MaterialPriceSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                log_message(
                    "vendor_app", "Material price created successfully.", "INFO"
                )
                return response_created(
                    data=serializer.data, message="Material price created."
                )
            log_message("vendor_app", "Invalid material price data.", "WARNING")
            return response_bad_request(
                errors=serializer.errors, message="Invalid data."
            )
        except Exception as e:
            log_message(
                "vendor_app", f"Error creating material price: {str(e)}", "ERROR"
            )
            return response_bad_request(
                errors=str(e), message="Unable to create material price."
            )


class SuppliedMaterialPriceListAPIView(APIView):
    """
    Handle request to list vendor material prices.
    """

    def get(self, request: Request):
        """handle get request"""
        querysets = MaterialPrice.objects.all()

        vendor_name = request.query_params.get("vendor")
        material_name = request.query_params.get("material")
        price = request.query_params.get("price")

        if vendor_name:
            querysets = querysets.filter(vendor_fk__name_nn__icontains=vendor_name)
        if material_name:
            querysets = querysets.filter(
                material_fk__name__icontains=material_name
            )
        if price:
            querysets = querysets.filter(price_nn__lte=price)

        serializer = MaterialPriceSerializer(
            querysets,
            many=True,
            fields=[
                "id",
                "vendor_fk",
                "material_fk",
                "price_nn",
            ],
        )
        log_message(
            module_name="vendor_app",
            message="Material prices retrieved successfully.",
            level="INFO",
        )
        return response_success(
            data=serializer.data, message="Material prices retrieved."
        )
