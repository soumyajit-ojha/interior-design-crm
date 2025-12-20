from django.contrib import admin
from .models import (
    CustomerLead,
    LeadNote,
    LeadFile,
    RoomToDesign,
    BrandType,
    ServiceType,
    LeadStatusTimeLine,
)


class AdminCustomerLead(admin.ModelAdmin):
    list_display = [
        "id",
        "client_name",
        "email",
        "phone",
        "status",
        "created_by",
        "created_at",
    ]
    search_fields = ["client_name", "email", "phone", "status"]


admin.site.register(CustomerLead, AdminCustomerLead)


class AdminLeadNote(admin.ModelAdmin):
    list_display = [
        "id",
        "lead_fk",
        "is_done",
        "is_done",
        "follow_up_at",
        "created_by",
        "created_at",
    ]
    search_fields = ["lead_fk", "is_done", "is_done"]


admin.site.register(LeadNote, AdminLeadNote)


class AdminLeadFile(admin.ModelAdmin):
    list_display = [
        "id",
        "lead_fk",
        "file_name",
        "file_size",
        "file_path",
        "created_by",
        "created_at",
    ]
    search_fields = ["lead_fk", "file"]


admin.site.register(LeadFile, AdminLeadFile)


class AdminRoomToDesign(admin.ModelAdmin):
    list_display = ["id", "name", "created_by", "created_at"]
    search_fields = ["name"]


admin.site.register(RoomToDesign, AdminRoomToDesign)


class AdminBrandType(admin.ModelAdmin):
    list_display = ["id", "name", "created_by", "created_at"]
    search_fields = ["name"]


admin.site.register(BrandType, AdminBrandType)


class AdminServiceType(admin.ModelAdmin):
    list_display = ["id", "name", "created_by", "created_at"]
    search_fields = ["name"]


admin.site.register(ServiceType, AdminServiceType)


class AdminLeadStatusTimeline(admin.ModelAdmin):
    list_display = ["id", "lead_fk", "title_nn", "created_by"]
    search_fields = ["lead_fk"]


admin.site.register(LeadStatusTimeLine, AdminLeadStatusTimeline)
