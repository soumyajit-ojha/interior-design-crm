"""
This module contains utility functions, classes, and helpers that are
shared across this app's view to make it minimal and easy to understand.
These utilities are designed to keep the codebase clean, reduce duplication
and provide reusable logic for common operations.
"""

import re
from django.core.exceptions import ValidationError
from django.db.models import Q
from users.models import User


def validate_name(name: str, ignored_chars: str = "") -> str:
    """
    Validate a name:
    - Only allows uppercase/lowercase letters, spaces, dot, apostrophe, and hyphen.
    - Disallows digits and other special characters.

    Args:
        name (str): The input name to validate.
        ignored_chars (str): Characters to ignore during validation.
    Returns:
        name (str): validated_name
    Raises:
        ValidationError: If the name is invalid.
    """
    if not name or not name.strip():
        raise ValidationError("Name is required to validate.")

    name = name.strip()
    # Remove ignored characters before validation
    if ignored_chars:
        pattern = f"[{re.escape(ignored_chars)}]"
        cleaned_name = re.sub(pattern, "", name)
    else:
        cleaned_name = name

    if not re.match(r"^[A-Za-z .'\-]+$", cleaned_name):
        raise ValidationError(f"Invalid format. Use letters and .'-{ignored_chars}")

    return name


def validate_email(email: str, min_len: int = 5, max_len: int = 254) -> str:
    """
    Validate an email address:
    - Must be lowercase only.
    - Valid format: local@domain.extension
    - Only lowercase letters, numbers, '.', '-', and '_' allowed.
    - No spaces or other special characters.
    - Length between `min_len` and `max_len`.

    Returns:
        str: The cleaned and valid email address.

    Raises:
        ValidationError: if the email is invalid.
    """
    email = email.strip()
    if not email:
        raise ValidationError("Email is required.")

    # Basic regex for lowercase emails (RFC 5322 simplified)
    regex = r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$"
    if not re.match(regex, email):
        raise ValidationError(
            "Invalid email format. Use lowercase only (e.g., dummy12@email.com)."
        )

    # Check length
    if not min_len < len(email) <= max_len:
        raise ValidationError(
            f"Email length must be between {min_len} and {max_len} characters."
        )

    return email


def validate_phone_number(phone_number: str) -> str:
    """
    Validate phone:
    - Must start with '+' followed by country code and number groups.
    - Only digits allowed after the '+'.
    Example: +919876543210
    Returns:
        phone (str): value
    Raises:
        ValidationError: If the phone number is invalid.
    """
    if not phone_number or not phone_number.strip():
        raise ValidationError("Phone number is required.")

    phone_number = phone_number.strip()

    if not re.match(r"^\+\d{7,15}$", phone_number):
        raise ValidationError(
            "Invalid phone number format. Use format like +919876543210."
        )

    return phone_number


def validate_password(password: str) -> str:
    """
    Validate password strength:
    - At least 8 characters long.
    - Must contain at least one uppercase letter.
    - Must contain at least one lowercase letter.
    - Must contain at least one digit.
    - Must contain at least one special character (!@#$%^&*()_+).

    Raises:
        ValidationError: if the password does not meet requirements.

    Returns:
        str: The valid password.
    """
    if not password or not password.strip():
        raise ValidationError("Password is required.")

    regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+])[A-Za-z\d!@#$%^&*()_+]{8,}$"
    if not re.match(regex, password):
        raise ValidationError(
            "Password must be at least 8 characters long and include at least one uppercase letter,"
            "one lowercase letter, one number, and one special character (!@#$%^&*()_+)."
        )

    return password


def validate_unique_user_fields(username: str, email: str, phone_number: str):
    """
    Check existance of username, email and phone number.

    Returns:
        ValueError (str): if data already exist
    """
    existing_users = User.objects.filter(
        Q(username__iexact=username)
        | Q(email__iexact=email)
        | Q(phone_number_nn=phone_number)
    )

    if existing_users:
        if existing_users.filter(username__iexact=username):
            raise ValueError("This username already exists.")
        if existing_users.filter(email__iexact=email):
            raise ValueError("This email already exists.")
        if existing_users.filter(phone_number_nn__iexact=phone_number):
            raise ValueError("This phone number already exists.")
