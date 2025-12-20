from django.contrib import admin
from .models import *


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["id", "project_name", "created_by"]
    list_filter = ["created_at"]


@admin.register(BHKType)
class BHKTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "bhk_name", "description", "created_at", "updated_at")
    search_fields = ("bhk_name",)
    list_filter = ("created_at", "updated_at")


@admin.register(ScopeOfWork)
class ScopeOfWorkAdmin(admin.ModelAdmin):
    list_display = ["id", "scope_of_work", "description", "created_by"]
    list_filter = ["created_at"]


@admin.register(MaterialTier)
class MaterialTierAdmin(admin.ModelAdmin):
    list_display = ("id", "tier_name", "tier_description", "created_at", "updated_at")
    search_fields = ("tier_name",)
    list_filter = ("created_at", "updated_at")


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "room_name", "room_description", "created_at", "updated_at")
    search_fields = ("room_name",)
    list_filter = ("created_at",)


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ("id", "unit_name", "unit_abbreviation", "created_at", "updated_at")
    search_fields = ("unit_name", "unit_abbreviation")
    list_filter = ("created_at",)


@admin.register(ShutterFinish)
class ShutterFinishAdmin(admin.ModelAdmin):
    list_display = ("id", "shutter_finish_name", "description")
    list_filter = ("created_at",)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("id", "item_name", "item_description", "created_at", "created_by")
    list_filter = ("created_at",)


@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "quotation_number",
        "client_fk",
        "salesperson_fk",
        "created_at",
        "created_by",
    )
    list_filter = ("created_at",)


@admin.register(QuotationRoom)
class QuotationRoom(admin.ModelAdmin):
    list_display = [
        "id",
        "quotation_fk",
        "room_type_fk",
        "room_name",
        "total_room_amount",
    ]
    list_filter = ["created_at", "quotation_fk"]


@admin.register(QuotationItem)
class QuotationItemAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "quotation_room_fk",
        "item_fk",
        "item_quantity",
        "rate",
        "amount",
    ]
    list_filter = ["created_at", "quotation_room_fk"]


@admin.register(ItemPrice)
class ItemPriceAdmin(admin.ModelAdmin):
    list_display = ("id", "item", "shutter_finish", "unit", "price_per_unit")
    list_filter = ("created_at",)


@admin.register(QuotationTermsAndConditions)
class QuotationTermsAndConditions(admin.ModelAdmin):
    list_display = ["id", "terms_and_conditions", "footer_tagline"]
    list_filter = ["created_at"]


@admin.register(PaymentMilestone)
class PaymentMilestoneAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "milestone_name",
        "percentage",
        "amount",
        "is_paid",
        "paid_date",
    ]
    list_filter = ["created_at"]
