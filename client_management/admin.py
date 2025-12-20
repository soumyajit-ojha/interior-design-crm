"""
File to register models in django admin
"""

from django.contrib import admin
from .models import (
    ClientDetails,
    ClientExpense,
    ProjectExpense,
    # ClientMaterialExpense,
    # ClientMiscellaneousExpense,
    ClientPaymanets,
    ClientTimeline,
    # ClientTransportExpense,
    Sprint,
    SprintChecklistItem,
    Material,
    SavedClientExpense,
    SavedProjectExpense,
    ClientExpenseSubmission,
    ProjectExpenseSubmission
)

admin.site.register(ClientDetails)


class ClientExpenseAdmin(admin.ModelAdmin):
    """For admin panel presentation of ClientExpense Model"""

    list_display = (
        "id",
        "client_details_fk",
        "type",
        "expense_date",
        "vendor",
        "amount",
    )
    search_fields = ("name", "expense_date")
    list_filter = ("created_at", "updated_at")


admin.site.register(ClientExpense, ClientExpenseAdmin)
admin.site.register(ProjectExpense)

# admin.site.register(ClientMaterialExpense)
# admin.site.register(ClientMiscellaneousExpense)
admin.site.register(ClientPaymanets)
admin.site.register(ClientTimeline)
# admin.site.register(ClientTransportExpense)


class SprintChecklistItemInline(admin.TabularInline):
    model = SprintChecklistItem
    extra = 0


@admin.register(Sprint)
class SprintAdmin(admin.ModelAdmin):
    inlines = [SprintChecklistItemInline]
    list_display = ["sprint_name", "start_date", "end_date", "status"]


admin.site.register(SprintChecklistItem)


# class DraftClientExpenseAdmin(admin.ModelAdmin):
#     """For admin panel presentation of DraftClientExpense Model"""

#     list_display = (
#         "id",
#         "client_details_fk",
#         "status",
#         "level_nn",
#         "expense_date",
#         "materials",
#         "vendors",
#         "payment_method",
#         "amount",
#     )
#     search_fields = ("name", "expense_date")
#     list_filter = ("created_at", "updated_at")


# admin.site.register(DraftClientExpense, DraftClientExpenseAdmin)


# class ExpenseAttachmentAdmin(admin.ModelAdmin):
#     """For admin panel presentation of ExpenseAttachment Model"""

#     list_display = ("id", "draft_expense_fk", "client_expense_fk", "file", "created_at")


# admin.site.register(ExpenseAttachment, ExpenseAttachmentAdmin)


class VenderAdmin(admin.ModelAdmin):
    """For admin panel presentation of Vender Model"""

    list_display = ("id", "name", "contact", "email")
    search_fields = ("name", "contact")
    list_filter = ("created_at", "updated_at")


# admin.site.register(Vendor, VenderAdmin)


@admin.register(Material)
class SuppliedMaterialAdmin(admin.ModelAdmin):
    """This model used to disply Material on admin pannel"""

    list_display = ("id", "name", "description", "created_at", "created_by")
    search_fields = ("name",)
    list_filter = ("created_at", "created_by")


admin.site.register(SavedClientExpense)
admin.site.register(SavedProjectExpense)
admin.site.register(ClientExpenseSubmission)
admin.site.register(ProjectExpenseSubmission)


from .models import RecentActivity


@admin.register(RecentActivity)
class RecentActivityAdmin(admin.ModelAdmin):
    list_display = ("activity_date", "activity", "client_name", "service_type", "updated_by")
    search_fields = ("activity", "client_name")
    list_filter = ("activity_date",)
