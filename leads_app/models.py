"""Data models for the leads_app Django application."""

from django.contrib.auth import get_user_model
from django.db import models
from django.core.exceptions import ValidationError

from utils.utils import BaseModel
from utils.utils import file_upload_path

User = get_user_model()


class RoomToDesign(BaseModel):
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Room To Design",
        db_column="Room_To_Design",
    )

    def _str_(self):
        return self.name


class BrandType(BaseModel):
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="BrandType",
        db_column="BrandType",
    )

    def _str_(self):
        return self.name


class ServiceType(BaseModel):
    name = models.CharField(
        max_length=50, db_column="Service_Type", verbose_name="Service Type"
    )

    def _str_(self):
        return self.name


class CustomerLead(BaseModel):
    """
    Data model representing a potential customer in your sales pipeline.

    A CustomerLead captures key contact details, engagement metrics, and follow-up scheduling.

    Attributes:
        client_name (str): Customer's complete name.
        email (str, optional): Contact email address.
        phone (str, optional): Contact phone number.

    Inherited from BaseModel:
        created_by (ForeignKey): Who created this lead record.
        created_at (datetime): When this record was created.
        updated_by (ForeignKey): Who last updated this lead.
        updated_at (datetime): When this record was last updated.
    """

    class StatusChoices(models.TextChoices):
        """Status choices"""

        NEW = "New", "New"
        FOLLOW_UP = "Follow-up", "Follow-up"
        CONTACTED = "Contacted", "Contacted"
        QUOTED = "Quoted", "Quoted"
        CONVERTED = "Converted", "Converted"
        REJECTED = "Rejected", "Rejected"

    class SourceChoices(models.TextChoices):
        """Source Choices"""

        WEBSITE = "Website", "Website"
        REFERRAL = "Referral", "Referral"
        SOCIAL_MEDIA = "Social Media", "Social Media"
        ADVERTISEMENT = "Advertisement", "Advertisement"
        PHONE_CALL = "Phone Call", "Phone Call"
        OTHER = "Other", "Other"

    class CivilWorkType(models.TextChoices):
        """Civil work Choices"""

        GRANITE_WORK = "Granite Work", "Granite Work"
        PLUMBING = "Plumbing Work", "Plumbing Work"
        ELECTRICAL = "Electrical Work", "Electrical Work"
        TILES_WORK = "Tiles Work", "Tiles Work"
        OTHER = "Other", "Other"

    client_name = models.CharField(
        max_length=100,
        blank=False,
        null=False,
        verbose_name="Client Name",
        db_column="Client_Name",
        help_text="Full name of the prospective customer",
    )
    email = models.EmailField(
        max_length=254,
        blank=False,
        null=False,
        verbose_name="Email Address",
        db_column="Email_Address",
        help_text="Contact email address",
    )
    phone = models.CharField(
        max_length=20,
        blank=False,
        null=False,
        verbose_name="Phone Number",
        db_column="Phone_Number",
        help_text="Contact phone number",
    )
    call_back_time = models.TimeField(
        null=True, blank=True, verbose_name="Call-Back Time", db_column="Call_Back_Time"
    )
    status = models.CharField(
        null=True,
        blank=True,
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.NEW,
        verbose_name="Status",
        db_column="Status",
        help_text="Current stage in the sales process",
    )
    society_name = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name="Society Name",
        db_column="Society_Name",
    )
    flat_number = models.CharField(
        null=True,
        blank=True,
        max_length=50,
        verbose_name="Flat Number",
        db_column="Flat_Number",
    )
    flat_type = models.CharField(
        null=True,
        blank=True,
        max_length=50,
        verbose_name="Flat Type",
        db_column="Flat_Type",
    )
    bhk_room_type = models.JSONField(
        null=True,
        blank=True,
        default=list,
        verbose_name="BHK Room Type",
        db_column="BHK_Room_Type",
    )
    possession_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Possession Date",
        db_column="Possession_Date",
    )
    service_type = models.JSONField(
        null=True,
        blank=True,
        default=list,
        verbose_name="Service Type",
        db_column="Service_Type",
    )
    service_type_description = models.TextField(
        null=True,
        blank=True,
        verbose_name="Service Type Description",
        db_column="Service_Type_Description",
    )
    rooms_to_design = models.JSONField(
        null=True,
        blank=True,
        default=list,
        verbose_name="Rooms_To_Design",
        db_column="Rooms_To_Design",
    )
    kitchen_platform_status = models.BooleanField(
        null=True,
        blank=True,
        default=False,
        verbose_name="Kitchen Platform Status",
        db_column="Kitchen_Platform_Status",
    )
    kitchen_platform_description = models.CharField(
        max_length=300,
        null=True,
        blank=True,
        verbose_name="Kitchen Platform Description",
        db_column="Kitchen_Platform_Description",
    )
    civil_work_type = models.CharField(
        null=True,
        blank=True,
        max_length=20,
        choices=CivilWorkType.choices,
        verbose_name="Civil Work Type",
        db_column="Civil_Work_Type",
    )
    preferred_brand_type = models.JSONField(
        null=True,
        blank=True,
        default=list,
        verbose_name="Preferred Material",
        db_column="Preferred_Material",
    )
    floor_plan = models.FileField(
        upload_to=file_upload_path,
        null=True,
        blank=True,
        max_length=255,
        verbose_name="Floor Plan Details",
        db_column="Floor_Plan_Details",
    )
    budget_range = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Budget Range (INR)",
        db_column="Budget_Range",
    )
    past_experience = models.BooleanField(
        null=True,
        blank=True,
        default=False,
        verbose_name="Previous Interior Design Experience?",
        db_column="Previous_Design_Experience",
    )
    reason = models.TextField(
        null=True,
        blank=True,
        verbose_name="Experience Details",
        db_column="Experience_Details",
    )
    follow_up_dt = models.DateField(
        null=True,
        blank=True,
        verbose_name="Follow-up Date",
        db_column="Follow_up_Date",
        help_text="Calendar date to follow up with the customer",
    )
    is_reminder = models.BooleanField(
        default=False,
        verbose_name="Enable Reminder",
        db_column="Is_Reminder",
        help_text="Whether to send a reminder for this follow-up",
    )
    follow_up_note = models.CharField(
        max_length=300,
        null=True,
        blank=True,
        verbose_name="Follow-Up Note",
        db_column="Follow_Up_Note",
    )
    follow_up_at = models.TimeField(
        null=True, blank=True, verbose_name="Follow-up Time", db_column="Follow_up_at"
    )
    mark_as_done = models.BooleanField(
        default=False, verbose_name="Mark as Done", db_column="Mark_as_Done"
    )
    interest_percentage = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Interest Level (%)",
        db_column="Interest_Level_Percent",
    )
    source = models.CharField(
        max_length=20,
        choices=SourceChoices.choices,
        null=True,
        blank=True,
        verbose_name="Lead Source",
        db_column="Lead_Source",
        help_text="How did the customer find us",
    )
    assigned_to_fk = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="assigned_leads",
        verbose_name="Assigned Salesman",
        db_column="Assigned_To",
        help_text="Sales person responsible for this lead",
    )
    is_converted_to_client = models.BooleanField(
        default=False,
        verbose_name="Converted to Client",
        db_column="Is_Converted_To_Client",
    )
    conversion_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Conversion Date",
        db_column="Conversion_Date",
    )
    city = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default="Hyderabad",
        verbose_name="City",
        db_column="City",
        help_text="Customer's city location",
    )
    move_in_date = models.DateField(
        null=True, blank=True, verbose_name="Move In Date", db_column="Move_In_Date"
    )
    move_in_date_details = models.TextField(
        null=True,
        blank=True,
        db_column="Move In Date Details",
        verbose_name="Move_In_Date_Details",
    )

    def save(self, *args, **kwargs):
        # Ensure clean() is called on every save()
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        """Meta class"""

        db_table = "customer_lead"
        verbose_name = "Customer Lead"
        verbose_name_plural = "Customer Leads"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.client_name} ({self.status})"


class LeadNote(BaseModel):
    """
    Notes/comments for each lead. Multiple notes can be added per lead.
    """

    lead_fk = models.ForeignKey(
        CustomerLead,
        on_delete=models.CASCADE,
        related_name="notes",
        verbose_name="Customer Lead",
    )
    note_nn = models.TextField(
        verbose_name="Note",
        help_text="Add notes about customer interactions or requirements",
    )
    tags = models.JSONField(
        default=list, blank=True, verbose_name="Tags", db_column="Tags"
    )
    is_done = models.BooleanField(
        default=False, verbose_name="Is Done", db_column="Is Done"
    )
    is_reminder = models.BooleanField(
        default=False, verbose_name="Is Reminder", db_column="Is_Reminder"
    )
    follow_up_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Follow-up Scheduled",
        db_column="Follow_up_Scheduled",
    )

    class Meta:
        db_table = "lead_notes"
        verbose_name = "Lead Note"
        verbose_name_plural = "Lead Notes"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Note for {self.lead_fk.client_name} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class LeadFile(BaseModel):
    """
    Additional files for each lead (e.g. floor plans, images).
    """

    lead_fk = models.ForeignKey(
        CustomerLead,
        on_delete=models.CASCADE,
        related_name="files",
        verbose_name="Customer Lead",
    )
    file_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_column="File_Name",
        verbose_name="File Name",
    )
    file_size = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        db_column="File_Size",
        verbose_name="File Size (MB)",
    )
    file_path = models.FileField(
        null=True,
        blank=True,
        upload_to='leads/',
        verbose_name="File Attachment",
    )

    class Meta:
        db_table = "lead_files"
        verbose_name = "Lead File"
        verbose_name_plural = "Lead Files"
        ordering = ["-created_at"]

    def __str__(self):
        return f"File for {self.lead_fk.client_name} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class LeadStatusTimeLine(BaseModel):
    """
    Tracks each time a CustomerLead's status changes.
    """

    lead_fk = models.ForeignKey(
        CustomerLead,
        on_delete=models.CASCADE,
        related_name="status_history",
        verbose_name="Customer Lead",
    )
    title_nn = models.CharField(
        max_length=300,
        verbose_name="Title",
        db_column="Title",
    )

    class Meta:
        db_table = "lead_status_history"
        ordering = ["created_at"]
        verbose_name = "Lead Status History"
        verbose_name_plural = "Lead Status History"

    def __str__(self):
        return f"{self.lead_fk.client_name}: {self.title_nn} "
