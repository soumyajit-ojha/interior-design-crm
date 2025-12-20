"""
Models for client Management
"""

import uuid
from django.db import models
from quotations_app.models import Quotation, Project
from users.models import User
from utils.utils import BaseModel
from vendor_app.models import Vendor
from vendor_app.models import Material




class ClientDetails(BaseModel):
    """
    Stores details of a client's project engagement.
    """

    user_fk = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_projects",
        db_column="User_FK",
        verbose_name="User",
    )
    quotation_fk = models.ForeignKey(
        Quotation,
        on_delete=models.CASCADE,
        related_name="client_projects",
        db_column="Quotation_FK",
        verbose_name="Quotation",
    )
    project_fk = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="project_clients",
        db_column="Project_FK",
        verbose_name="Project",
    )
    start_date = models.DateField(db_column="Start_Date", verbose_name="Start Date")
    duration_in_days = models.PositiveIntegerField(
        db_column="Duration_Days", verbose_name="Duration (Days)"
    )
    end_date = models.DateField(db_column="End_Date", verbose_name="End Date")
    total_budget = models.IntegerField(
        default=0, verbose_name="Total Budget", db_column="Total_Budget"
    )
    total_amount_received = models.IntegerField(
        default=0, verbose_name="Total Received", db_column="Total_Amount_Received"
    )
    progress = models.IntegerField(
        default=0, verbose_name="Progress (%)", db_column="Progress"
    )
    status = models.CharField(
        max_length=50, verbose_name="Status", db_column="Status", default="Ongoing"
    )

    class Meta:
        db_table = "Client_Details"
        verbose_name = "Client Detail"
        verbose_name_plural = "Client Details"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Project for {self.user_fk.first_name_nn} - {self.start_date}"

class RecentActivity(BaseModel):
    """
    Lightweight model to surface recent activities in a single table for dashboards.

    Fields:
      - activity_date: when the activity happened (uses created_at from source by default)
      - activity: short description (e.g. "New lead captured", "Quotation sent")
      - client_name: cached client/lead name for quick display
      - service_type: optional, text representation of service type
      - updated_by: FK to User where available
      - source_type/source_id: optional pointers back to the original record so this table can be rebuilt idempotently
    """

    activity_date = models.DateTimeField(verbose_name="Date", db_column="Date")
    activity = models.CharField(max_length=255, verbose_name="Activity", db_column="Activity")
    client_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Client Name", db_column="Client_Name")
    service_type = models.CharField(max_length=100, null=True, blank=True, verbose_name="Service Type", db_column="Service_Type")
    updated_by = models.ForeignKey(
        'users.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='recent_activities',
        db_column='Updated_By',
        verbose_name='Updated By',
    )
    # Optional pointers to original source row for idempotent population
    source_type = models.CharField(max_length=100, null=True, blank=True, db_column='Source_Type')
    source_id = models.IntegerField(null=True, blank=True, db_column='Source_Id')

    class Meta:
        db_table = 'recent_activities'
        verbose_name = 'Recent Activity'
        verbose_name_plural = 'Recent Activities'
        ordering = ['-activity_date']

    def __str__(self):
        return f"{self.activity} - {self.client_name or 'N/A'} ({self.activity_date.date()})"


class ClientExpense(BaseModel):
    """
    Tracks expenses related to a client's project.
    """

    class ExpenseLevelTypes(models.TextChoices):
        """Expence level types"""

        CLIENT = "Client", "Client"
        PROJECT = "Project", "Project"

    client_details_fk = models.ForeignKey(
        ClientDetails,
        on_delete=models.CASCADE,
        related_name="client_expenses",
        db_column="Client_Detail_FK",
        verbose_name="Client",
    )
    type = models.CharField(
        max_length=50,
        choices=ExpenseLevelTypes.choices,
        db_column="Expence_Level",
        verbose_name="Expense Level",
    )
    expense_date = models.DateField(
        db_column="Expense_Date",
        verbose_name="Expense Date",
    )
    materials = models.ManyToManyField(
        Material,
        null=True,
        blank=True,
        verbose_name="Materials",
        db_column="Materials",
    )
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Vendors",
        db_column="Vendors",
    )
    amount = models.IntegerField(
        default=0,
        verbose_name="Amount",
        db_column="Amount",
    )

    class Meta:
        db_table = "Client_Expense"
        verbose_name = "Client Expense"
        verbose_name_plural = "Client Expenses"
        ordering = ["-created_at"]
        unique_together = ("client_details_fk", "expense_date")
class ProjectExpense(BaseModel):
    """
    Tracks expenses related to a specific project.
    """
    project_details_fk = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="project_expenses",
        db_column="Project_FK",
        verbose_name="Project",
    )
    client_details_fk = models.ForeignKey(
        ClientDetails,
        on_delete=models.CASCADE,
        related_name="project_client_details",
        db_column="Client_Detail_FK",
        verbose_name="Client",
    )
    submitted_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="submitted_project_expenses",
        db_column="Submitted_By",
        verbose_name="Submitted By",
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="approved_project_expenses",
        db_column="Approved_By",
        verbose_name="Approved By",
    )
    manager_fk = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="managed_client_expenses_project",
        db_column="Manager_FK",
        verbose_name="Manager",
    )
    expense_date = models.DateField(
        db_column="Expense_Date",
        verbose_name="Expense Date",
    )
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Vendors",
        db_column="Vendors",
    )
    expense = models.CharField(max_length=255, db_column="Expense", verbose_name="Expense")
    notes = models.TextField(max_length=500, db_column="Notes", verbose_name="Notes")
    amount = models.IntegerField(
        default=0,
        verbose_name="Amount",
        db_column="Amount",
    )

    class Meta:
        db_table = "Project_Expense"
        verbose_name = "Project Expense"
        verbose_name_plural = "Project Expenses"
        ordering = ["-created_at"]
        unique_together = ("project_details_fk", "expense_date")

    def __str__(self):
        return f"Expense for {self.project_details_fk} - {self.expense_date}"

# class ClientMaterialExpense(BaseModel):
#     """
#     Stores material expenses for a client project.
#     """

#     client_expense_fk = models.ForeignKey(
#         ClientExpense,
#         on_delete=models.CASCADE,
#         related_name="client_material_expense",
#         db_column="Client_Expense_FK",
#         verbose_name="Client Expense",
#     )
#     item = models.CharField(
#         max_length=100,
#         verbose_name="Item",
#         db_column="Item",
#     )
#     vendor = models.CharField(
#         max_length=100,
#         verbose_name="Vendor",
#         db_column="Vendor",
#     )
#     description = models.TextField(
#         max_length=300,
#         verbose_name="Description",
#         db_column="Description",
#     )
#     quantity = models.IntegerField(
#         default=0,
#         verbose_name="Quantity",
#         db_column="Quantity",
#     )
#     total = models.IntegerField(
#         default=0,
#         verbose_name="Total",
#         db_column="Total",
#     )

#     def save(self, *args, **kwargs):
#         # is_new = self._state.adding
#         super().save(*args, **kwargs)

#         expense = self.client_expense_fk

#         # Unique material items
#         unique_items = list(
#             set(expense.client_material_expense.all().values_list("item", flat=True))
#         )
#         expense.material = unique_items

#         unique_vendors = list(
#             set(expense.client_material_expense.all().values_list("vendor", flat=True))
#         )
#         expense.vendor = unique_vendors

#         # Step 3: Update amount (sum of total from related items)
#         total_amount = (
#             expense.client_material_expense.aggregate(total=models.Sum("total"))[
#                 "total"
#             ]
#             or 0
#         )
#         expense.amount += total_amount

#         expense.save()

#     class Meta:
#         db_table = "Client_Material_Expense"
#         verbose_name = "Client Material Expense"
#         verbose_name_plural = "Client Material Expenses"
#         ordering = ["-created_at"]


# class ClientTransportExpense(BaseModel):
#     """
#     Stores transport-related expenses for a client project.
#     """

#     client_expense_fk = models.ForeignKey(
#         ClientExpense,
#         on_delete=models.CASCADE,
#         related_name="client_transport_expense",
#         db_column="Client_Expense_FK",
#         verbose_name="Client Expense",
#     )
#     vehicle_type = models.CharField(
#         max_length=100,
#         verbose_name="Vehicle Type",
#         db_column="Vehicle_Type",
#     )
#     from_to = models.TextField(
#         max_length=300,
#         verbose_name="Route (From-To)",
#         db_column="From_To",
#     )
#     distance = models.IntegerField(
#         default=0,
#         verbose_name="Distance (KM)",
#         db_column="Distance",
#     )
#     total = models.IntegerField(
#         default=0,
#         verbose_name="Total",
#         db_column="Total",
#     )

#     def save(self, *args, **kwargs):
#         # is_new = self._state.adding
#         super().save(*args, **kwargs)

#         expense = self.client_expense_fk
#         total_amount = (
#             expense.client_transport_expense.aggregate(total=models.Sum("total"))[
#                 "total"
#             ]
#             or 0
#         )
#         expense.amount += total_amount

#         expense.save()

#     class Meta:
#         db_table = "Client_Transport_Expense"
#         verbose_name = "Client Transport Expense"
#         verbose_name_plural = "Client Transport Expenses"
#         ordering = ["-created_at"]


# class ClientMiscellaneousExpense(BaseModel):
#     """
#     Stores miscellaneous expenses for a client project.
#     """

#     client_expense_fk = models.ForeignKey(
#         ClientExpense,
#         on_delete=models.CASCADE,
#         related_name="client_miscellanieous_expense",
#         db_column="Client_Expense_FK",
#         verbose_name="Client Expense",
#     )
#     expense_type = models.CharField(
#         max_length=100,
#         verbose_name="Expense Type",
#         db_column="Expense_Type",
#     )
#     description = models.TextField(
#         max_length=300,
#         verbose_name="Description",
#         db_column="Description",
#     )
#     total = models.IntegerField(
#         default=0,
#         verbose_name="Total",
#         db_column="Total",
#     )

#     def save(self, *args, **kwargs):
#         # is_new = self._state.adding
#         super().save(*args, **kwargs)

#         expense = self.client_expense_fk
#         total_amount = (
#             expense.client_miscellanieous_expense.aggregate(total=models.Sum("total"))[
#                 "total"
#             ]
#             or 0
#         )
#         expense.amount += total_amount

#         expense.save()

#     class Meta:
#         db_table = "Client_Miscellaneous_Expense"
#         verbose_name = "Client Miscellaneous Expense"
#         verbose_name_plural = "Client Miscellaneous Expenses"
#         ordering = ["-created_at"]


class ClientTimeline(BaseModel):
    """
    Tracks timeline updates for a client project.
    """

    client_details_fk = models.ForeignKey(
        ClientDetails,
        on_delete=models.CASCADE,
        related_name="project_timelines",
        db_column="Client_Detail_FK",
        verbose_name="Client",
    )
    title_nn = models.CharField(
        max_length=150,
        verbose_name="Title",
        db_column="Title",
    )
    description = models.TextField(
        max_length=300,
        verbose_name="Description",
        db_column="Description",
    )
    tags = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Tags",
        db_column="Tags",
    )
    attachment = models.FileField(
        null=True,
        blank=True,
        upload_to="clientTimeline/",
        verbose_name="File Attachment",
        db_column="Attachment",
    )

    class Meta:
        db_table = "Client_Timeline"
        verbose_name = "Client Timeline"
        verbose_name_plural = "Client Timelines"
        ordering = ["-created_at"]


class ClientPaymanets(BaseModel):
    """
    Tracks payments made by the client.
    """

    client_details_fk = models.ForeignKey(
        ClientDetails,
        on_delete=models.CASCADE,
        related_name="user_payments",
        db_column="Client_Detail_FK",
        verbose_name="Client",
    )
    amount = models.IntegerField(
        default=0,
        verbose_name="Amount",
        db_column="Amount",
    )
    mode_of_payment = models.CharField(
        max_length=20,
        verbose_name="Mode of Payment",
        db_column="Mode_Of_Payment",
    )
    payment_date = models.DateField(
        verbose_name="Payment Date",
        db_column="Payment_date",
    )

    class Meta:
        db_table = "Client_Payments"
        verbose_name = "Client Payment"
        verbose_name_plural = "Client Payments"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        # is_new = self._state.adding  # Check if it's a new object
        super().save(*args, **kwargs)

        # if is_new:
        # Update the total_amount_received on the client
        client = self.client_details_fk
        total = client.user_payments.aggregate(total=models.Sum("amount"))["total"] or 0
        client.total_amount_received = total
        client.save(update_fields=["total_amount_received"])


class Sprint(BaseModel):
    """
    Tracks Client Sprint
    """

    class StatusChoices(models.TextChoices):
        """
        Status choices for Sprint
        """

        COMPLETE = "Complete", "Complete"
        PENDING = "Pending", "Pending"
        INPROGRESS = "In-progress", "In-progress"

    client_fk = models.ForeignKey(
        ClientDetails,
        on_delete=models.CASCADE,
        related_name="sprints",
        verbose_name="Project Fk",
        db_column="Project_FK",
    )
    sprint_name = models.CharField(
        max_length=255, db_column="Sprint_Name", verbose_name="Sprint Name"
    )
    start_date = models.DateField(db_column="Start_Date", verbose_name="Start Date")
    end_date = models.DateField(db_column="End_Date", verbose_name="End Date")
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        db_column="Status",
        verbose_name="status",
    )
    points = models.PositiveIntegerField(
        default=0, db_column="Points", verbose_name="Points"
    )
    description = models.TextField(
        db_column="Description",
        verbose_name="Sprint Description",
        null=True,
        blank=True,
    )

    def __str__(self):
        return str(self.sprint_name)


class SprintChecklistItem(BaseModel):
    """
    Sprint Check list items for the Sprint.
    """

    sprint_fk = models.ForeignKey(
        Sprint,
        on_delete=models.CASCADE,
        related_name="checklist_items",
        verbose_name="Sprint Fk",
        db_column="Sprint_FK",
    )
    description = models.TextField(db_column="Description", verbose_name="Description")
    is_completed_ind = models.BooleanField(
        default=False, db_column="Is_Completed_Ind", verbose_name="Is Completed Ind"
    )

    def __str__(self):
        return f"{self.description}"


# class DraftClientExpense(BaseModel):
#     """
#     Stores draft expenses before admin approval.
#     """

#     class StatusTypes(models.TextChoices):
#         """Expense Status Types"""
#         DRAFT = "Draft", "Draft"
#         SUBMITTED = "Submitted", "Submitted"
#         APPROVED = "Approved", "Approved"
#         REJECTED = "Rejected", "Rejected"

#     class ExpenseLevelTypes(models.TextChoices):
#         """Expence level types"""

#         CLIENT = "Client", "Client"
#         PROJECT = "Project", "Project"

#     class ExpenseCategoryTypes(models.TextChoices):
#         """Expense category types"""

#         MATERIAL = "Material", "Material"
#         TRANSPORT = "Transport", "Transport"
#         MISCELLANEOUS = "Miscellaneous", "Miscellaneous"

#     class PaymentMethodTypes(models.TextChoices):
#         """Payment methods different types"""

#         CASH = "Cash", "Cash"
#         CHEQUE = "Cheque", "Cheque"
#         BANK_TRANSFER = "Bank_Transfer", "Bank_Transfer"
#         ONLINE = "Online", "Online"

#     client_details_fk = models.ForeignKey(
#         ClientDetails,
#         on_delete=models.CASCADE,
#         related_name="draft_expenses",
#         db_column="Client_Detail_FK",
#         verbose_name="Client",
#     )
#     level_nn = models.CharField(
#         max_length=50,
#         choices=ExpenseLevelTypes.choices,
#         db_column="Expence_Level",
#         verbose_name="Expense Level",
#     )
#     status = models.CharField(
#         max_length=20,
#         default=StatusTypes.SUBMITTED,
#         choices=StatusTypes.choices,
#         verbose_name="Status",
#         db_column="Status",
#     )
#     expense_date = models.DateField(
#         db_column="Expense_Date",
#         verbose_name="Expense Date",
#     )
#     expense_category = models.CharField(
#         max_length=50,
#         choices=ExpenseCategoryTypes.choices,
#         db_column="Expense_Category",
#         verbose_name="Expense Category",
#     )
#     vendors = models.JSONField(
#         null=True,
#         blank=True,
#         default=list,
#         db_column="Vendor Fk",
#         verbose_name="Vendor_Fk",
#     )
#     materials = models.JSONField(
#         null=True,
#         blank=True,
#         default=list,
#         db_column="Expense_Materials",
#         verbose_name="Materials",
#     )
#     payment_method = models.CharField(
#         choices=PaymentMethodTypes.choices,
#         null=True,
#         blank=True,
#         verbose_name="Payment Method",
#         db_column="Payment_Method",
#     )
#     amount = models.IntegerField(
#         default=0,
#         verbose_name="Amount",
#         db_column="Amount",
#     )
#     extra_info = models.JSONField(
#         blank=True, null=True, db_column="Extra_Info", verbose_name="Extra Info"
#     )

#     class Meta:
#         """Meta data about drafted expenses"""

#         db_table = "Client_Expense_Draft"
#         verbose_name = "Draft Client Expense"
#         verbose_name_plural = "Draft Client Expenses"
#         ordering = ["-created_at"]


# class ExpenseAttachment(BaseModel):
#     """
#     Store attachments associated to expence,
#     any image or pdf it can be 1 or more.
#     """

#     draft_expense_fk = models.ForeignKey(
#         DraftClientExpense,
#         on_delete=models.CASCADE,
#         related_name="draft_attachments",
#         db_column="Draft_Expense_Fk",
#         verbose_name="Draft Expense Fk",
#     )
#     client_expense_fk = models.ForeignKey(
#         ClientExpense,
#         on_delete=models.CASCADE,
#         related_name="attachments",
#         blank=True,
#         null=True,
#         db_column="Client_Expense_Fk",
#         verbose_name="Client Expense Fk",
#     )
#     file = models.FileField(
#         upload_to="expenses/attachments/", db_column="File", verbose_name="File"
#     )

#     class Meta:
#         """Meta data about expenses attachments"""

#         db_table = "Client_Expense_Attachments"
#         verbose_name = "Client Expense Attachments"
#         verbose_name_plural = "Client Expense Attachments"
#         ordering = ["-created_at"]


# --- SavedProjectExpense and SavedClientExpense ---
class SavedProjectExpense(BaseModel):
    """
    Stores project-level expenses submitted by users.
    """
    class StatusTypes(models.TextChoices):
        """Expense Status Types"""
        DRAFT = "Draft", "Draft"
        SUBMITTED = "Submitted", "Submitted"

    status = models.CharField(
        max_length=20,
        choices=StatusTypes.choices,
        default=StatusTypes.DRAFT,
        db_column="Status",
        verbose_name="Status",
    )
    project_details_fk = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="saved_project_expenses",
        db_column="Project_FK",
        verbose_name="Project",
    )
    client_details_fk = models.ForeignKey(
        ClientDetails,
        on_delete=models.CASCADE,
        related_name="saved_project_expenses",
        db_column="Client_Detail_FK",
        verbose_name="Client",
    )
    user_fk = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="saved_project_expenses",
        db_column="User_FK",
        verbose_name="User",
    )
    manager_fk = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="managed_client_expenses",
        db_column="Manager_FK",
        verbose_name="Manager",
    )
    draft_number = models.UUIDField(db_column="Draft_Number", verbose_name="Draft Number")
    expense_date = models.DateField(db_column="Expense_Date", verbose_name="Expense Date")
    expense = models.CharField(max_length=255, db_column="Expense", verbose_name="Expense")
    notes = models.TextField(max_length=500, db_column="Notes", verbose_name="Notes")
    amount = models.IntegerField(default=0, db_column="amount", verbose_name="amount")

    class Meta:
        db_table = "Saved_Project_Expense"
        verbose_name = "Saved Project Expense"
        verbose_name_plural = "Saved Project Expenses"
        ordering = ["-created_at"]

class SavedClientExpense(BaseModel):
    """
    Stores client-level expenses submitted by users.
    """
    class StatusTypes(models.TextChoices):
        """Expense Status Types"""
        DRAFT = "Draft", "Draft"
        SUBMITTED = "Submitted", "Submitted"
    status = models.CharField(
        max_length=20,
        choices=StatusTypes.choices,
        default=StatusTypes.DRAFT,
        db_column="Status",
        verbose_name="Status",
    )
    client_details_fk = models.ForeignKey(
        ClientDetails,
        on_delete=models.CASCADE,
        related_name="saved_client_expenses",
        db_column="Client_Detail_FK",
        verbose_name="Client",
    )
    user_fk = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="saved_client_expenses",
        db_column="User_FK",
        verbose_name="User",
    )
    draft_number = models.UUIDField(db_column="Draft_Number", verbose_name="Draft Number")
    expense_date = models.DateField(db_column="Expense_Date", verbose_name="Expense Date")
    materials = models.ManyToManyField(
        Material,
        blank=True,
        related_name="saved_client_expenses",
        verbose_name="Materials",
    )
    vendor = models.CharField(max_length=255, db_column="Vendor", verbose_name="Vendor")
    notes = models.TextField(max_length=500, db_column="Notes", verbose_name="Notes")
    quantity = models.IntegerField(default=0, db_column="Quantity", verbose_name="Quantity")
    amount = models.IntegerField(default=0, db_column="amount", verbose_name="amount")
    expense_category = models.CharField(max_length=50, db_column="Expense_Category", verbose_name="Expense Category")

    class Meta:
        db_table = "Saved_Client_Expense"
        verbose_name = "Saved Client Expense"
        verbose_name_plural = "Saved Client Expenses"
        ordering = ["-created_at"]


class ProjectExpenseSubmission(BaseModel):
    class StatusTypes(models.TextChoices):
        SUBMITTED = "Submitted", "Submitted"
        APPROVED = "Approved", "Approved"
        REJECTED = "Rejected", "Rejected"

    saved_project_expense_fk = models.ForeignKey(
        SavedProjectExpense,
        on_delete=models.CASCADE,
        related_name="submissions",
        db_column="Saved_Project_Expense_FK",
        verbose_name="Saved Project Expense",
    )
    # Mirror key fields from SavedProjectExpense for easy review/audit
    project_details_fk = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="project_submission_projects",
        db_column="Project_FK",
        verbose_name="Project",
    )
    user_fk = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="project_submission_users",
        db_column="User_FK",
        verbose_name="User",
        null=True,
        blank=True,
    )
    manager_fk = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="project_submission_managers",
        db_column="Manager_FK",
        verbose_name="Manager",
        null=True,
        blank=True,
    )
    expense_date = models.DateField(
        db_column="Expense_Date", verbose_name="Expense Date", null=True, blank=True
    )
    expense = models.CharField(
        max_length=255, db_column="Expense", verbose_name="Expense", blank=True, null=True
    )
    notes = models.TextField(
        max_length=500, db_column="Notes", verbose_name="Notes", blank=True, null=True
    )
    amount = models.IntegerField(default=0, db_column="amount", verbose_name="amount")
    status = models.CharField(
        max_length=20,
        choices=StatusTypes.choices,
        default=StatusTypes.SUBMITTED,
        db_column="Status",
        verbose_name="Status",
    )
    submitted_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="project_expense_submissions",
        db_column="Submitted_By",
        verbose_name="Submitted By",
    )
    action_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="project_expense_actions",
        db_column="Action_By",
        verbose_name="Action By",
        null=True,
        blank=True,
    )
    submitted_at = models.DateTimeField(auto_now_add=True, db_column="Submitted_At")
    acted_at = models.DateTimeField(null=True, blank=True, db_column="Acted_At")

    class Meta:
        db_table = "Saved_Project_Expense_Submission"
        verbose_name = "Saved Project Expense Submission"
        verbose_name_plural = "Saved Project Expense Submissions"
        ordering = ["-created_at"]


class ClientExpenseSubmission(BaseModel):
    class StatusTypes(models.TextChoices):
        SUBMITTED = "Submitted", "Submitted"
        APPROVED = "Approved", "Approved"
        REJECTED = "Rejected", "Rejected"

    saved_client_expense_fk = models.ForeignKey(
        SavedClientExpense,
        on_delete=models.CASCADE,
        related_name="submissions",
        db_column="Saved_Client_Expense_FK",
        verbose_name="Saved Client Expense",
    )
    # Mirror key fields from SavedClientExpense for easy review/audit
    client_details_fk = models.ForeignKey(
        ClientDetails,
        on_delete=models.CASCADE,
        related_name="client_submission_client_details",
        db_column="Client_Detail_FK",
        verbose_name="Client"
    )
    user_fk = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="client_submission_users",
        db_column="User_FK",
        verbose_name="User",
        null=True,
        blank=True,
    )
    expense_date = models.DateField(
        db_column="Expense_Date", verbose_name="Expense Date", null=True, blank=True
    )
    materials = models.ManyToManyField(
        Material,
        blank=True,
        related_name="saved_client_expense_submissions",
        verbose_name="Materials",
    )
    vendor = models.CharField(
        max_length=255, db_column="Vendor", verbose_name="Vendor", blank=True, null=True
    )
    notes = models.TextField(
        max_length=500, db_column="Notes", verbose_name="Notes", blank=True, null=True
    )
    quantity = models.IntegerField(default=0, db_column="Quantity", verbose_name="Quantity")
    amount = models.IntegerField(default=0, db_column="amount", verbose_name="amount")
    expense_category = models.CharField(
        max_length=50, db_column="Expense_Category", verbose_name="Expense Category", blank=True, null=True
    )
    status = models.CharField(
        max_length=20,
        choices=StatusTypes.choices,
        default=StatusTypes.SUBMITTED,
        db_column="Status",
        verbose_name="Status",
    )
    submitted_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="client_expense_submissions",
        db_column="Submitted_By",
        verbose_name="Submitted By",
    )
    action_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="client_expense_actions",
        db_column="Action_By",
        verbose_name="Action By",
        null=True,
        blank=True,
    )
    submitted_at = models.DateTimeField(auto_now_add=True, db_column="Submitted_At")
    acted_at = models.DateTimeField(null=True, blank=True, db_column="Acted_At")

    class Meta:
        db_table = "Saved_Client_Expense_Submission"
        verbose_name = "Saved Client Expense Submission"
        verbose_name_plural = "Saved Client Expense Submissions"
        ordering = ["-created_at"]