"""
All endpoints for this feature app
"""

from django.urls import path
from .views import (
    WorkTypeCreateAPIView,
    WorkTypeRetrieveAPIView,
    WorkerCreateAPIView,
    WorkerListAPIView,
    MaterialCreateAPIView,
    MaterialListAPIView,
    VendorCreateAPIView,
    VendorListAPIView,
    SuppliedMaterialPriceCreateAPIView,
    SuppliedMaterialPriceListAPIView,
)

urlpatterns = [
    # ---- Work Type ----
    path("work-type/create/", WorkTypeCreateAPIView.as_view(), name="work-type-create"),
    path(
        "work-type/list/",
        WorkTypeRetrieveAPIView.as_view(),
        name="work-type-list",
    ),
    # ---- Worker ----
    path("worker/create/", WorkerCreateAPIView.as_view(), name="worker-create"),
    path("worker/", WorkerListAPIView.as_view(), name="worker-retrieve"),
    # ---- Supplied Materials ----
    path(
        "materials/create/",
        MaterialCreateAPIView.as_view(),
        name="supplied-material-create",
    ),
    path(
        "materials/list",
        MaterialListAPIView.as_view(),
        name="supplied-material-list",
    ),
    # ---- Vendors ----
    path("create/", VendorCreateAPIView.as_view(), name="vendor-create"),
    path("list/", VendorListAPIView.as_view(), name="vendor-list"),
    # ---- Supplied Material Prices ----
    path(
        "material-prices/create/",
        SuppliedMaterialPriceCreateAPIView.as_view(),
        name="material-price-create",
    ),
    path(
        "material-prices/",
        SuppliedMaterialPriceListAPIView.as_view(),
        name="material-price-list",
    ),
]
