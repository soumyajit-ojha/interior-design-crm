from .base import *

ALLOWED_HOSTS = ["api.igolohomes.com", "dashboard.igolohomes.com"]
AWS_ACCESS_KEY_ID = getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = getenv("AWS_S3_REGION_NAME", "us-east-1")
AWS_S3_ENDPOINT_URL = f"https://s3.{AWS_S3_REGION_NAME}.amazonaws.com"
AWS_DEFAULT_ACL = None
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com"


# Storage classes for Django 4.2+
STORAGES = {
	"default": {
		"BACKEND": "igolohomes.storage_backends.MediaStorage",
	},
	"staticfiles": {
		"BACKEND": "igolohomes.storage_backends.StaticStorage",
	},
}
MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"
STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"

PASSWORD_RESET_TIMEOUT = 300 # 5 minutes in seconds

IGOLO_FRONTEND_URL = "https://dashboard.igolohomes.com"
