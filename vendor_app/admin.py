"""
This module will responsible to display registerd models.
"""

from django.contrib import admin
from .models import (
    Worker,
    WorkType,
    Vendor,
    MaterialPrice,
)


@admin.register(WorkType)
class WorkTypeAdmin(admin.ModelAdmin):
    """This model used to disply WorkType on admin pannel"""

    list_display = ("id", "name_nn", "description", "created_at", "created_by")
    search_fields = ("name_nn",)
    list_filter = ("created_at", "created_by")


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    """This model used to disply Worker on admin pannel"""

    list_display = (
        "id",
        "name_nn",
        "phone_number_nn",
        "email",
        "work_type_fk",
        "status_nn",
        "created_at",
        "extra_info",
        "created_by",
    )
    search_fields = ("user",)
    list_filter = ("created_at", "created_by")


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    """This model used to disply Vendor on admin pannel"""

    list_display = (
        "id",
        "name_nn",
        "location",
        "address",
        "phone_number_nn",
        "email",
        "extra_info",
        "created_at",
        "created_by",
    )
    search_fields = ("name_nn",)
    list_filter = ("created_at", "created_by")


@admin.register(MaterialPrice)
class MaterialPriceAdmin(admin.ModelAdmin):
    """This model used to disply MaterialPrice on admin pannel"""

    list_display = (
        "id",
        "vendor_fk",
        "material_fk",
        "price_nn",
        "created_at",
        "created_by",
    )
    list_filter = ("created_at", "created_by")
