"""
All endpoints for this feature app
"""

from django.urls import path
from .views import VendorListAPIView, MaterialListAPIView, MaterialPriceAPIView

urlpatterns = [
    path("vendors/", VendorListAPIView.as_view(), name="vendor-list"),
    path("materials/", MaterialListAPIView.as_view(), name="material-list"),
    path("material-price/", MaterialPriceAPIView.as_view(), name="material-price"),
]
