from django.db import models
from django.contrib.auth import get_user_model

from utils.utils import BaseModel
from utils.utils import company_logo_upload_path, quotation_logo_upload_path
from leads_app.models import CustomerLead

User = get_user_model()

# Independent Models


class Project(BaseModel):
    project_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_column="Project_Name",
        verbose_name="Project Name",
    )
    city_or_area = models.CharField(
        max_length=255, db_column="City_Or_Area", verbose_name="City/Area", blank=True
    )
    society_type = models.CharField(
        max_length=100,
        db_column="Society_Type",
        verbose_name="Society Type",
        blank=True,
    )
    pincode = models.CharField(
        max_length=6, db_column="Pin_Code", verbose_name="Pin Code", blank=True
    )

    def __str__(self):
        return self.project_name


class BHKType(BaseModel):
    bhk_name = models.CharField(
        max_length=20, db_column="Bhk_Name", verbose_name="BHK Name"
    )
    description = models.TextField(
        null=True, blank=True, db_column="Description", verbose_name="Description"
    )

    def __str__(self):
        return self.bhk_name


class ScopeOfWork(BaseModel):
    scope_of_work = models.CharField(
        max_length=20, db_column="Scope_of_Work", verbose_name="Scope Of Work"
    )
    description = models.TextField(
        null=True, blank=True, db_column="Description", verbose_name="Description"
    )

    def __str__(self):
        return self.scope_of_work


class MaterialTier(BaseModel):
    tier_name = models.CharField(
        max_length=50, db_column="Tier_Name", verbose_name="Tier Name"
    )
    tier_description = models.TextField(
        null=True,
        blank=True,
        db_column="Tier_Description",
        verbose_name="Tier Description",
    )

    def __str__(self):
        return self.tier_name


class RoomType(BaseModel):
    room_name = models.CharField(
        max_length=50, db_column="Room_Name", verbose_name="Room Name"
    )
    room_description = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        db_column="Room_Description",
        verbose_name="Room Description",
    )

    def __str__(self):
        return self.room_name


class Unit(BaseModel):
    unit_abbreviation = models.CharField(
        max_length=10, db_column="Unit_Abbreviation", verbose_name="Unit Abbreviation"
    )
    unit_name = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        db_column="Unit_Name",
        verbose_name="Unit Name",
    )

    def __str__(self):
        return self.unit_abbreviation


class ShutterFinish(BaseModel):
    shutter_finish_name = models.CharField(
        max_length=100,
        db_column="Shutter_Finish_name",
        verbose_name="Shutter Finish Name",
    )
    description = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        db_column="Description",
        verbose_name="Description",
    )

    def __str__(self):
        return self.shutter_finish_name


class Item(BaseModel):
    item_name = models.CharField(
        max_length=50, db_column="Item_Name", verbose_name="Item Name"
    )
    has_dimension = models.BooleanField(
        default=True, db_column="Has_Dimension", verbose_name="Has Dimension"
    )
    item_description = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_column="Item_Description",
        verbose_name="Item Description",
    )

    def __str__(self):
        return self.item_name


# Main Model
class Quotation(BaseModel):
    class StatusChoices(models.TextChoices):
        """Status choices"""

        DRAFT = "Draft", "Draft"
        SENT = "Sent", "Sent"
        APPROVED = "Approved", "Approved"

    quotation_title = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_column="Quotation_Title",
        verbose_name="Quotation Title",
    )
    quotation_number = models.CharField(
        max_length=50,
        unique=True,
        db_column="Quotation_Number",
        verbose_name="Quotation Number",
    )
    scope_of_work = models.JSONField(
        default=list,
        null=True,
        blank=True,
        db_column="Scope_Of_Work_Id",
        verbose_name="Scope Of Work Id",
    )
    project_fk = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="quoted_project",
        db_column="Project_Id",
        verbose_name="Project Id",
    )
    client_fk = models.ForeignKey(
        CustomerLead,
        on_delete=models.CASCADE,
        null=True,
        related_name="quotation_client",
        db_column="Client_FK",
        verbose_name="Client",
    )
    salesperson_fk = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name="quotation_salesperson",
        db_column="Salesperson_FK",
        verbose_name="Salesperson",
    )
    bhk_type_fk = models.ForeignKey(
        BHKType,
        on_delete=models.CASCADE,
        null=True,
        db_column="BHK_Type_FK",
        verbose_name="BHK Type",
    )
    material_tier_fk = models.ForeignKey(
        MaterialTier,
        on_delete=models.CASCADE,
        null=True,
        db_column="Material_Tier_FK",
        verbose_name="Material Tier",
    )
    quotation_date = models.DateField(
        null=True, db_column="Quotation_Date", verbose_name="Quotation Date"
    )
    valid_days = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
        db_column="Valid_Days",
        verbose_name="Valid Days",
    )
    valid_until = models.DateField(
        null=True, db_column="Valid_Until", verbose_name="Valid Until"
    )
    subtotal = models.BigIntegerField(
        default=0,
        db_column="Subtotal",
        verbose_name="Subtotal",
    )
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        db_column="Discount_Percentage",
        verbose_name="Discount (%)",
    )
    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        db_column="Discount_Amount",
        verbose_name="Discount Amount",
    )
    tax_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=18,
        db_column="Tax_Percentage",
        verbose_name="Tax (%)",
    )
    tax_amount = models.BigIntegerField(
        default=0,
        db_column="Tax_Amount",
        verbose_name="Tax Amount",
    )
    round_off = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        db_column="Round_Off",
        verbose_name="Round Off",
    )
    grand_total = models.BigIntegerField(
        default=0,
        db_column="Grand_Total",
        verbose_name="Grand Total",
    )
    status = models.CharField(
        max_length=10,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT,
        db_column="Status",
        verbose_name="Status",
    )
    notes = models.TextField(
        null=True, blank=True, db_column="Notes", verbose_name="Notes"
    )

    def __str__(self):
        return self.quotation_number


class QuotationRoom(BaseModel):
    quotation_fk = models.ForeignKey(
        Quotation,
        on_delete=models.CASCADE,
        related_name="rooms",
        db_column="Quotation_FK",
        verbose_name="Quotation",
    )
    room_type_fk = models.ForeignKey(
        RoomType,
        on_delete=models.CASCADE,
        null=True,
        db_column="Room_Type_FK",
        verbose_name="Room Type",
    )
    room_name = models.CharField(
        null=True, max_length=50, db_column="Room_Name", verbose_name="Room Name"
    )
    total_room_amount = models.PositiveIntegerField(
        blank=True,
        default=0,
        db_column="Total_Room_Amount",
        verbose_name="Total Room Amount",
    )

    def __str__(self):
        name = self.room_name or (
            self.room_type_fk.room_name if self.room_type_fk else "Unnamed Room"
        )
        return f"{self.quotation_fk}: {name}"


class QuotationItem(BaseModel):
    quotation_room_fk = models.ForeignKey(
        QuotationRoom,
        on_delete=models.CASCADE,
        related_name="items",
        db_column="Quotation_Room",
        verbose_name="Quotation Room",
    )
    item_fk = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        null=True,
        db_column="Item_FK",
        verbose_name="Item",
    )
    item_length = models.PositiveIntegerField(
        null=True, blank=True, db_column="Item_Length", verbose_name="Item Length"
    )
    item_length_unit_fk = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        null=True,
        db_column="Item_Length_Unit",
        verbose_name="Item Length Unit",
        related_name="item_length_unit",
    )
    item_height = models.PositiveIntegerField(
        null=True, blank=True, db_column="Item_Height", verbose_name="Item Height"
    )
    item_height_unit_fk = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        null=True,
        db_column="Item_Height_Unit",
        verbose_name="Item Height Unit",
        related_name="item_height_unit",
    )
    item_quantity = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="Quantity", verbose_name="Quantity"
    )
    rate = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="Rate", verbose_name="Rate"
    )
    shutter_finish_fk = models.ForeignKey(
        ShutterFinish,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column="Shutter_Finish_Fk",
        verbose_name="Shutter_Finish_Fk",
    )
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, db_column="Amount", verbose_name="Amount"
    )

    def __str__(self):
        return f"{self.quotation_room_fk} - {self.item_fk} x{self.item_quantity}"


class PaymentMilestone(BaseModel):
    quotation_fk = models.ForeignKey(
        Quotation,
        on_delete=models.CASCADE,
        related_name="milestones",
        db_column="Quotation_FK",
        verbose_name="Quotation",
    )
    milestone_name = models.CharField(
        max_length=100, db_column="Milestone_Name", verbose_name="Milestone Name"
    )
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        db_column="Percentage",
        verbose_name="Percentage",
    )
    amount = models.BigIntegerField(db_column="Amount", verbose_name="Amount")
    is_paid = models.BooleanField(
        default=False, db_column="Is_Paid", verbose_name="Is Paid"
    )
    paid_date = models.DateField(
        null=True, blank=True, db_column="Paid_Date", verbose_name="Paid Date"
    )

    def __str__(self):
        return f"{self.quotation_fk.quotation_number} - {self.milestone_name}"


class QuotationTermsAndConditions(BaseModel):
    quotation_fk = models.ForeignKey(
        Quotation,
        on_delete=models.CASCADE,
        related_name="terms_and_conditions",
        db_column="Quotation_FK",
        verbose_name="Quotation ID",
    )
    terms_and_conditions = models.TextField(
        blank=True,
        null=True,
        db_column="Terms_And_Conditions",
        verbose_name="Terms_And_Conditions",
    )
    internal_notes = models.TextField(
        blank=True, null=True, db_column="Internal_Notes", verbose_name="Internal Notes"
    )
    footer_tagline = models.CharField(
        max_length=255,
        blank=True,
        db_column="Footer_Tagline",
        verbose_name="Footer Tagline",
    )
    quotation_logo = models.ImageField(
        upload_to=quotation_logo_upload_path,
        null=True,
        blank=True,
        db_column="Logo_Img",
        verbose_name="Logo Img",
    )
    show_contact_info = models.BooleanField(
        default=True, db_column="Show_Contact_Info", verbose_name="Show_Contact_Info"
    )

    def __str__(self):
        return f"Terms and conditions for {self.quotation_fk}"


class ClientCompanyInfo(BaseModel):
    company_name_nn = models.CharField(
        max_length=200, db_column="Company_Name", verbose_name="Company Name"
    )
    email = models.EmailField(db_column="Email", verbose_name="Email")
    address_nn = models.TextField(db_column="Address", verbose_name="Address")
    phone = models.CharField(db_column="Phone", verbose_name="Phone",max_length=15)
    gst_number = models.CharField(
        db_column="GST_Number", verbose_name="GST Number", null=True, blank=True,
        max_length=20
    )
    pan_number = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        db_column="PAN_Number",
        verbose_name="PAN Number",
    )
    logo = models.ImageField(
        upload_to=company_logo_upload_path,
        null=True,
        blank=True,
        db_column="Logo_Img",
        verbose_name="Logo Img",
    )
    website = models.URLField(
        null=True, blank=True, db_column="Website", verbose_name="Website"
    )

    def __str__(self):
        return self.company_name_nn


class ItemPrice(BaseModel):
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, db_column="Item_FK", verbose_name="Item Id"
    )
    shutter_finish = models.ForeignKey(
        ShutterFinish,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        db_column="Shutter_Finish_Id",
        verbose_name="Shutter Finish Id",
    )
    unit = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column="Unit_FK",
        verbose_name="Unit Id",
    )
    price_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        db_column="price_per_unit",
        verbose_name="Price per Unit",
        help_text="Automatically filled from Material.base_price if not set",
    )

    def __str__(self):
        return f"{self.item}, {self.unit}, {self.shutter_finish} price: {self.price_per_unit}"
