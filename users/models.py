"""
This model represents a user information and allows to create user(client).
"""

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

from .utils import upload_screenshot_path


class UserManager(BaseUserManager):
    """
    Custom user manager that implements the methods to create new users and superusers.
    Attributes:
        model (Model): The user model class that this manager is associated with.
    """

    def create_user(self, username, password, **extra_fields):
        """
        Creates a new user with the given username, password, and optional extra fields.
        Args:
            username (str): The username for the new user.
            password (str): The password for the new user.
        Raises:
            ValueError: If the username is not provided.
        Returns:
            User: The newly created user object.
        """
        if not username:
            raise ValueError("The Username must be set")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        """
        Creates a new superuser with the given username, password, and optional extra fields.
        Args:
            username (str): The username for the superuser.
            password (str): The password for the superuser.
        Returns:
            User: The newly created superuser object.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that extends Django's default User model with additional fields
    and enhanced functionality for user management.
    This model leverages `AbstractBaseUser` and `PermissionsMixin` to provide
    core user authentication and permission functionalities. It also includes a custom
    `UserManager` (defined elsewhere) for creating new users and superusers.
    Methods:
        __str__() (str): Returns a string representation of the user (username).
    """

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["email"]

    username = models.CharField(max_length=150, unique=True)
    first_name_nn = models.CharField(max_length=150, verbose_name="first name")
    last_name_nn = models.CharField(max_length=150, verbose_name="last name")
    phone_number_nn = models.CharField(max_length=20, verbose_name="Phone Number")
    address_nn = models.CharField(max_length=200, verbose_name="address")
    location_nn = models.CharField(max_length=200, verbose_name="location")
    email = models.EmailField(unique=True)
    user_type_choices = [
        ("client", "Client"),
        ("admin", "Admin"),
        ("super_admin", "Super_Admin"),
        ("accountant", "Accountant"),
        ("telecaller", "Telecaller"),
        ("salesman", "Salesman"),
        ("supervisor", "Supervisor")
    ]
    user_type_nn = models.CharField(
        max_length=20,
        choices=user_type_choices,
        default="client",
        verbose_name="user type",
    )
    residential_or_commercial_choices = [
        ("residential", "Residential"),
        ("commercial", "Commercial"),
    ]
    residential_or_commercial = models.CharField(
        max_length=20, choices=residential_or_commercial_choices
    )
    status_choices = (
        ("pending", "Pending"),
        ("in progress", "In Progress"),
        ("completed", "Completed"),
    )
    status_nn = models.CharField(
        max_length=20, choices=status_choices, verbose_name="status"
    )
    registered_date = models.DateTimeField(default=timezone.now)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    def __str__(self):
        return str(self.username)


class UserQuery(models.Model):
    """
    The model to keep record of each users request, feedback queries.
    frields: user_fk,
    """

    class CategoryChoices(models.TextChoices):
        """
        Choices for category field
        """

        DESIGN_FEEDBACK = "design_feedback", "Design Feedback"
        PAYMENT_ISSUES = "payment_issues", "Payment Issues"
        VIDEO_UPLOAD_PROBLEM = "video_upload_problem", "Video Upload Problem"
        GENERAL_INQUIRY = "general_inquiry", "General Inquiry"

    user_fk = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="query",
        verbose_name="username",
        null=True,
        blank=True,
    )
    category_nn = models.CharField(
        max_length=20,
        choices=CategoryChoices.choices,
        null=False,
        db_column="category",
        verbose_name="Category",
    )
    subject_nn = models.CharField(max_length=400)
    message_nn = models.TextField()
    screenshots = models.ImageField(
        upload_to=upload_screenshot_path,
        null=True,
        blank=True,
        db_column="screenshots",
        verbose_name="Screenshots",
    )

    def __str__(self):
        return f"Query from {self.user_fk} - {self.subject_nn}"
