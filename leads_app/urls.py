from django.urls import path
from leads_app.views import *

urlpatterns = [
    path("check/", CustomerLeadCheckAPIView.as_view(), name="lead-check"),
    path("create/", CustomerLeadCreateAPIView.as_view(), name="lead-create"),
    path("update/<int:pk>/", CustomerLeadUpdateAPIView.as_view(), name="lead-update"),
    # list of leads
    path(
        "list/", CustomerLeadUnifiedAPIView.as_view(), name="customer-lead-simple-list"
    ),
    path(
        "retrieve/<int:pk>/",
        CustomerLeadRetrieveAPIView.as_view(),
        name="lead-retrieve",
    ),
    path("delete/<int:pk>/", CustomerLeadDeleteAPIView.as_view(), name="lead-delete"),
    # notes
    path("note/add/", LeadNoteCreateAPIView.as_view(), name="lead-note-create"),
    path(
        "note/delete/<int:pk>/",
        LeadNoteDeleteAPIView.as_view(),
        name="lead-note-delete",
    ),
    # Assign and status change
    path(
        "assign/salesman/<int:pk>/",
        LeadAssignSalesmanAPIView.as_view(),
        name="lead-assign-salesman",
    ),
    path(
        "change/status/<int:pk>/",
        LeadChangeStatusAPIView.as_view(),
        name="lead-change-status",
    ),
    # export
    path("export/", LeadExportAPIView.as_view(), name="lead-export"),
    path("salesmen/list/", SalesmanListAPIView.as_view(), name="salesman-list"),
    # mark-as-done
    path(
        "mark_as_done/<int:pk>/",
        LeadMarkAsDoneAPIView.as_view(),
        name="lead-mark-as-done",
    ),
    # files
    path("file/add/", LeadFileCreateAPIView.as_view(), name="lead-files-add"),
    path(
        "file/delete/<int:pk>/",
        LeadFileDeleteAPIView.as_view(),
        name="lead-file-delete",
    ),
    path(
        "leadintake-dropdown/",
        LeadDropdownListAPIView.as_view(),
        name="room-to-designs",
    ),
]
