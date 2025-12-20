"""
Django's default apps file
"""
from django.apps import AppConfig


class ClientManagementConfig(AppConfig):
    """
    Django's Default app config
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'client_management'
