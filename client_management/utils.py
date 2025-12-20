"""
This module contains utility functions, classes, and helpers that are 
shared across this app's view to make it minimal and easy to understand.
These utilities are designed to keep the codebase clean, reduce duplication
and provide reusable logic for common operations.
"""

import json
from users.models import(
    User
)

def get_users_by_type(user_type:str):
    """
    Method to retrieve queryset(s) of users having a specific user_type.
    """

    querysets = User.objects.filter(user_type_nn=user_type)
    return querysets or None

def get_extra_info_from_payload(payload:dict)-> dict:
    """
    Extracts additional information from an expense payload by removing 
    'level_nn', 'expense_category', 'expense_date', and 'attachments'.

    Args:
        payload (dict): The original expense payload containing all fields.

    Returns:
        dict: A dictionary containing only the extra fields 
              (i.e., excluding 'level_nn', 'expense_category', 
              'expense_date', and 'attachments').
    """
    try:
        copied_payload = payload.copy()
        removable_fields = ("level_nn", "expense_category", "expense_date", "attachments")
        payload = {k: v for k, v in copied_payload.items() if k not in removable_fields}
        data = json.dumps(payload)
    except:
        data = None
    return data
