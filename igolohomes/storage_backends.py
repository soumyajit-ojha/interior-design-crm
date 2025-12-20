"""
File to setup storages for AWS
"""
from storages.backends.s3boto3 import S3Boto3Storage

class MediaStorage(S3Boto3Storage):
    """
    Custom storage backend for handling media files using Amazon S3.

    This class inherits from S3Boto3Storage and sets the storage location to 'media'.
    Files uploaded using this storage will not overwrite existing files with the same name.

    Attributes:
        location (str): The S3 bucket subdirectory where media files are stored.
        file_overwrite (bool): Determines whether files with the same name are overwritten.
    """
    location = "media"
    file_overwrite = False

class StaticStorage(S3Boto3Storage):
    """
    Custom storage backend for serving static files using Amazon S3.
    This class inherits from S3Boto3Storage and sets the storage location to 'static'.
    Files stored using this backend will be publicly readable by default.
    Attributes:
        location (str): The S3 bucket folder where static files are stored.
        default_acl (str): The default access control list for stored files ('public-read').
    """

    location = "static"
    # default_acl = "public-read"
