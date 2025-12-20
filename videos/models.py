"""
This model represents a video user association, linking a user with video information.
"""

from django.db import models
from users.models import User
from utils.utils import BaseModel

class VideoUser(BaseModel):
    """
    This model represents a video associated with a specific user.

    Attributes:
        user (ForeignKey): A foreign key relationship to the User model,
        indicating the user who uploaded the video.
        title (CharField): The title of the video (max length 100 characters).
        url (URLField): The URL of the video (max length 200 characters).
        description (TextField): A description of the video (optional, blank=True).

    """

    user_fk = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="videos", verbose_name="username"
    )
    title_nn = models.CharField(max_length=100, db_column="Title", verbose_name="video title")
    url = models.URLField(max_length=200, db_column="URL", verbose_name="video url")
    description = models.TextField(blank=True, db_column="Description", verbose_name="video description")

    def __str__(self):
        return self.user_fk.username 
