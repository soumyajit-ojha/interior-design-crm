from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]


# # Use local file storage in dev
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"

PASSWORD_RESET_TIMEOUT = 600 # 2 minutes in seconds

IGOLO_FRONTEND_URL = "http://localhost:5173"
