"""
Helper class and functions for Django models
This module provides a base model class with metadata fields and a utility function for file upload paths.
"""

from rest_framework.request import Request
from django.db import models
from django.contrib.auth import get_user_model
from rest_framework.pagination import PageNumberPagination
# This module defines a base model that includes fields for tracking

User = get_user_model()

class BaseModel(models.Model):
    """
    Abstract base model capturing creation and update metadata.page

    Fields:
        created_by (ForeignKey): User who created the record.
        created_dt (DateTimeField): Timestamp when the record was created.
        updated_by (ForeignKey): User who last updated the record.
        updated_dt (DateTimeField): Timestamp when the record was last updated.
    """
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='%(class)s_created',
        null=True,
        db_column="Created_By",
        verbose_name="Created By"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_column="Created_At",
        verbose_name="Created At"
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='%(class)s_updated',
        null=True,
        db_column="Updated_By",
        verbose_name="Updated By"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        db_column="Updated_At",
        verbose_name="Updated At"
    )

    class Meta:
        abstract = True

def file_upload_path(self, filename):
    """
    Returns a callable that generates a file upload path based on the instance's primary key / email.
    This is useful for organizing uploaded files in a structured directory.
    """
    user = "temp" if not self.email else self.email.split('@')[0]
    return f"floor_plans/{user}/{filename}"

def company_logo_upload_path(self, filename):
    """
    Returns a callable that generates a file upload path based on the instance's company_name.
    This is useful for organizing uploaded files in a structured directory.
    """
    company_name = "temp" if not self.company_name_nn else self.company_name_nn
    return f"company_logo/{company_name}/{filename}"

def get_cleaned_data(request: Request) -> dict:
    """
    Cleans the input data by removing empty strings and converting None to empty strings.
    """
    data = request.data
    if data:
        cleaned_data = {}
        for key, value in data.items():
            if isinstance(value, str):
                cleaned_data[key] = value.strip() if value.strip() else None
            else:
                cleaned_data[key] = value if value is not None else None
        return cleaned_data
    return {}
        

def lead_file_upload_path(self, filename):
    """
    Returns a callable that generates a file upload path based on the instance's lead_fk primary key.
    This is useful for organizing uploaded files in a structured directory.
    """
    user = "temp" if not self.lead_fk else self.lead_fk
    return f"leadfile/{user}/{filename}"


class CustomPagePagination(PageNumberPagination):
    """
    Custom pagination settings for CustomerLead list.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

def quotation_logo_upload_path(self, filename):
    """
    Returns a callable that generates a file upload path based on the instance's company_name.
    This is useful for organizing uploaded files in a structured directory.
    """
    company_name = "temp" if not self.company_name_nn else self.company_name_nn
    return f"company_logo/{company_name}/{filename}"