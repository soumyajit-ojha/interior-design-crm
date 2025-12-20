"""
This file defines the URL patterns for the vidoes application.

It maps URL paths to corresponding views, allowing users to interact with the application.

"""

from django.urls import path
from .views import VideoUserList, VideoUserDetail, UserVideos

app_name = "videos"

urlpatterns = [
    path("video_users/", VideoUserList.as_view(), name="video_users"),
    path("video_user/<int:pk>/", VideoUserList.as_view(), name="video_user"),
    path("user_videos/", UserVideos.as_view(), name="user_videos"),
    path(
        "video_user_details/<int:pk>/",
        VideoUserDetail.as_view(),
        name="video_user_detail",
    ),
]
