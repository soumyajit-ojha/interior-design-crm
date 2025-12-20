from .base import *

DEBUG = True
ALLOWED_HOSTS = ["dev.igolohomes.com"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
STATIC_URL = "/api/static/"
STATIC_ROOT = BASE_DIR / "static"

LOGIN_URL = '/api/admin/'
FORCE_SCRIPT_NAME = "/api"

PASSWORD_RESET_TIMEOUT = 300 # 5 minutes in seconds

IGOLO_FRONTEND_URL = "https://dev.igolohomes.com"
