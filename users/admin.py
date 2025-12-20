from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserQuery
from .forms import CustomUserCreationForm, CustomUserChangeForm


class AdminUser(BaseUserAdmin):
    """
    Custom User Admin with proper forms and fieldsets
    """

    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = [
        "id",
        "username",
        "email",
        "phone_number_nn",
        "user_type_nn",
        "residential_or_commercial",
        "status_nn",
        "is_active",
        "is_staff",
    ]

    search_fields = [
        "username",
        "phone_number_nn",
        "email",
    ]

    list_filter = [
        "is_active",
        "is_staff",
        "user_type_nn",
        "status_nn",
        "residential_or_commercial",
    ]

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal Info",
            {
                "fields": (
                    "first_name_nn",
                    "last_name_nn",
                    "email",
                    "phone_number_nn",
                    "address_nn",
                    "location_nn",
                )
            },
        ),
        (
            "User Details",
            {"fields": ("user_type_nn", "residential_or_commercial", "status_nn")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important Dates", {"fields": ("last_login", "registered_date")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
        (
            "Personal Info",
            {
                "classes": ("wide",),
                "fields": (
                    "first_name_nn",
                    "last_name_nn",
                    "phone_number_nn",
                    "address_nn",
                    "location_nn",
                ),
            },
        ),
        (
            "User Details",
            {
                "classes": ("wide",),
                "fields": ("user_type_nn", "residential_or_commercial", "status_nn"),
            },
        ),
        (
            "Permissions",
            {
                "classes": ("wide",),
                "fields": ("is_active", "is_staff", "is_superuser"),
            },
        ),
    )

    readonly_fields = ("registered_date", "last_login")

    def save_model(self, request, obj, form, change):
        """
        Override save_model to add custom logic
        """
        if not change:
            if obj.user_type_nn in ["admin", "super_admin", "accountant"]:
                obj.is_staff = True
            else:
                obj.is_staff = False

        super().save_model(request, obj, form, change)


class AdminQuery(admin.ModelAdmin):
    """
    Admin configuration for UserQuery model
    """

    list_display = ["id", "user_fk", "category_nn", "subject_nn"]
    search_fields = [
        "id",
        "user_fk__username",
        "user_fk__email",
        "category_nn",
        "subject_nn",
    ]
    list_filter = ["category_nn"]

    def get_queryset(self, request):
        """
        Make user_fk searchable with better display
        """
        return super().get_queryset(request).select_related("user_fk")


admin.site.register(User, AdminUser)
admin.site.register(UserQuery, AdminQuery)
