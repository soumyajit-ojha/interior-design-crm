"""
This module contains all required models(tables).
For Vendor and worker management feature.
"""

from django.db import models

from utils.utils import BaseModel



class Material(BaseModel):
    """
    Store all materias to be used on material expenses
    """

    name = models.CharField(max_length=255, db_column="Name", verbose_name="Name")
    description = models.TextField(
        blank=True,
        null=True,
        db_column="Description",
        verbose_name="Description",
    )

    def __str__(self):
        return str(self.name)


class WorkType(BaseModel):
    """
    Stores different types of work that a worker can perform.
    Example: Electrician, Plumber, Carpenter, Painter, etc.
    """

    name_nn = models.CharField(
        max_length=100,
        unique=True,
        db_column="Work_Type",
        verbose_name="Work Type",
    )
    description = models.TextField(
        blank=True,
        null=True,
        db_column="Description",
        verbose_name="Description",
    )

    class Meta:
        """Meta Info for WorkType model."""

        db_table = "vendor_app_work_type"
        verbose_name = "Work Type"
        verbose_name_plural = "Work Types"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name_nn}"


class Worker(BaseModel):
    """
    Stores worker details with their work types.
    """

    class StatusTypes(models.TextChoices):
        """Status types for workers."""

        ASSIGNED = "Assigned", "Assigned"
        AVAILABLE = "Available", "Available"
        LEAVE = "Leave", "Leave"

    name_nn = models.CharField(
        max_length=150,
        db_column="Worker_Name",
        verbose_name="Worker Name",
    )
    phone_number_nn = models.CharField(
        max_length=15,
        db_column="Phone_Number",
        verbose_name="Phone Number",
    )
    email = models.EmailField(
        null=True,
        blank=True,
        db_column="Email",
        verbose_name="Email",
    )
    work_type_fk = models.ForeignKey(
        WorkType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="workers",
        db_column="Work_Type",
        verbose_name="Work Type",
    )
    status_nn = models.CharField(
        max_length=20,
        default=StatusTypes.AVAILABLE,
        choices=StatusTypes.choices,
        db_column="Status",
        verbose_name="Status",
    )
    extra_info = models.TextField(
        blank=True,
        null=True,
        db_column="Extra_Info",
        verbose_name="Extra Information",
    )

    class Meta:
        """Meta Info for Worker model"""

        db_table = "vendor_app_worker"
        verbose_name = "Worker"
        verbose_name_plural = "Workers"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name_nn}, {self.work_type_fk}"


class Vendor(BaseModel):
    """
    Stores vendor/shop details with multiple supplied materials.
    """

    name_nn = models.CharField(
        max_length=150,
        db_column="Vendor_Name",
        verbose_name="Vendor/Shop Name",
    )
    location = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        db_column="Location",
        verbose_name="Location",
    )
    address = models.TextField(
        null=True,
        blank=True,
        db_column="Address",
        verbose_name="Address",
    )
    phone_number_nn = models.CharField(
        max_length=15,
        unique=True,
        db_column="Phone_Number",
        verbose_name="Phone Number",
    )
    email = models.EmailField(
        null=True,
        blank=True,
        db_column="Email",
        verbose_name="Email",
    )
    materials = models.ManyToManyField(
        Material,
        related_name="vendors",
        db_column="Materials",
        verbose_name="Materials",
    )
    extra_info = models.TextField(
        blank=True,
        null=True,
        db_column="Extra_Info",
        verbose_name="Extra Information",
    )

    class Meta:
        db_table = "vendor_app_vendor"
        verbose_name = "Vendor"
        verbose_name_plural = "Vendors"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name_nn}"


class MaterialPrice(BaseModel):
    """
    Stores the price of supplied material for a specific vendor.
    """

    vendor_fk = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name="material_prices",
        db_column="vendor_id",
        verbose_name="Vendor ID",
    )
    material_fk = models.ForeignKey(
        Material,
        on_delete=models.CASCADE,
        related_name="vendor_prices",
        db_column="material_id",
        verbose_name="Material ID",
    )
    price_nn = models.DecimalField(
        max_digits=12, decimal_places=2, db_column="Price", verbose_name="Price"
    )

    class Meta:
        """Meta Info for MaterialPrice"""

        db_table = "vendor_app_material_price"
        verbose_name = "Vendor Material Price"
        verbose_name_plural = "Vendor Material Prices"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.vendor_fk},\
            {self.material_fk}, {self.price_nn}"
