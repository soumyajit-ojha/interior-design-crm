from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User


class CustomUserCreationForm(UserCreationForm):
    """
    Custom user creation form that includes additional fields
    """

    email = forms.EmailField(required=True)
    first_name_nn = forms.CharField(max_length=150, required=True, label="First Name")
    last_name_nn = forms.CharField(max_length=150, required=True, label="Last Name")
    phone_number_nn = forms.CharField(
        max_length=20, required=True, label="Phone Number"
    )
    address_nn = forms.CharField(max_length=200, required=False, label="Address")
    location_nn = forms.CharField(max_length=200, required=False, label="Location")
    user_type_nn = forms.ChoiceField(
        choices=User.user_type_choices,
        required=True,
        initial="client",
        label="User Type",
    )
    residential_or_commercial = forms.ChoiceField(
        choices=User.residential_or_commercial_choices,
        required=False,
        label="Residential or Commercial",
    )
    status_nn = forms.ChoiceField(
        choices=User.status_choices, required=False, initial="pending", label="Status"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "email",
            "first_name_nn",
            "last_name_nn",
            "phone_number_nn",
            "address_nn",
            "location_nn",
            "user_type_nn",
            "residential_or_commercial",
            "status_nn",
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name_nn = self.cleaned_data["first_name_nn"]
        user.last_name_nn = self.cleaned_data["last_name_nn"]
        user.phone_number_nn = self.cleaned_data["phone_number_nn"]
        user.address_nn = self.cleaned_data["address_nn"]
        user.location_nn = self.cleaned_data["location_nn"]
        user.user_type_nn = self.cleaned_data["user_type_nn"]
        user.residential_or_commercial = self.cleaned_data["residential_or_commercial"]
        user.status_nn = self.cleaned_data["status_nn"]

        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    """
    Custom user change form for editing existing users
    """

    class Meta(UserChangeForm.Meta):
        model = User
        fields = "__all__"
