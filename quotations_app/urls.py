from django.urls import path
from .views import *
from .quotation_main_views import ProjectListAPIView, ProjectDetailsWithClientAPIView

urlpatterns = [
    path("projects/", ProjectListAPIView.as_view(), name="project-list"),
    path("bhk_types_create/", BHKTypeCreateAPIView.as_view(), name="bhk-types-create"),
    path(
        "material_tiers_create/",
        MaterialTiersCreateAPIView.as_view(),
        name="material-tiers-create",
    ),
    path(
        "room_types_create/", RoomTypesCreateAPIView.as_view(), name="room-types-create"
    ),
    path("units_create/", UnitsCreateAPIView.as_view(), name="units-create"),
    path("item_create/", ItemCreateAPIView.as_view(), name="item-create"),
    path(
        "scope_of_work_create/",
        ScopeOfWorkCreateAPIView.as_view(),
        name="scope-of-work-create",
    ),
    path(
        "shutter_finish_create/",
        ShutterFinishAPIView.as_view(),
        name="shutter-finish-create",
    ),
    path("project_create/", ProjectCreateAPIView.as_view(), name="create-project"),
    # company-info
    path(
        "client_company_create/",
        ClientCompanyInfoAPIView.as_view(),
        name="client-company-create",
    ),
    path(
        "client_company_logo_add/<int:pk>/",
        ClientCompanyLogoAddAPIView.as_view(),
        name="client-company-create",
    ),
    # quotation-endpoints
    path(
        "quotation_terms/<int:pk>/",
        QuotationTermsAndConditionsRetrieveAPIView.as_view(),
        name="quotation-terms-retrieve",
    ),
    path(
        "quotation_terms/create/",
        QuotationTermsAndConditionsCreateAPIView.as_view(),
        name="quotation-terms-create",
    ),
    # create-quotation
    path("create/", QuotationCreateAPIView.as_view(), name="create-quotation"),
    path(
        "detail/<int:pk>/", QuotationDetailsAPIView.as_view(), name="details-quotation"
    ),
    path(
        "get_dropdown/",
        RetrieveAllDropdownDataAPIView.as_view(),
        name="get-all-drop-downs",
    ),
    # Item-price
    path("item_price_add/", ItemPriceCreateAPIView.as_view(), name="item-price-add"),
    path("item_price_get/", ItemPriceRetrieveAPIView.as_view(), name="item-price-get"),
    # get-summary-details
    path("get_summary/", QuotationSummaryAPIView.as_view(), name="summary_api"),
    # Patment-term-section
    path("payment_terms/", PaymentTermsSectionAPIView.as_view(), name="payment-terms"),
    path("add_project/", AddProjectAPIView.as_view(), name="add_project"),
    path('quotations-list/<int:lead_id>/',LeadQuotationsListView.as_view(), name="lead-quotations"),
    path(
        "upload_csv_file/<str:model_name>/",
        CSVModelUploadView.as_view(),
        name="upload_csv_file"
    ),
    # path("add_project/", AddProjectAPIView.as_view(), name="add_project"),
    path("change_status/", QuotationStatusChangeAPIView.as_view(), name="change-status"),
    path("get-approved-quotation/<int:lead_id>/",GetApprovedQuotationAPIView.as_view(), name="get-approved-quotation" ),
    # Project details with client details
    path(
        "project_details/<int:pk>/",
        ProjectDetailsWithClientAPIView.as_view(),
        name="project-details-with-client"
    ),
]
