"""
This module defines serializers for the applications.
Each serializer is associated with a specific model and includes fields relevant to that model.
"""

import re
from bs4 import BeautifulSoup
import requests
from rest_framework import serializers
from .models import VideoUser


def get_video_id(url: str) -> str | None:
    """
    It find out the video_id of youtube video.
    types: mobile, watch, short, embed, with playlist, with timestamp.
    it return the id in str format ot return None if not found any.
    """
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11})(?:\?|&|$)"
    match = re.search(pattern, url)
    return match.group(1) if match else None


class VideoUserSerializer(serializers.ModelSerializer):
    """
    This serializer is used for serializing  VideoUser model instances.

    It inherits from `ModelSerializer` to automatically generate fields based
    on the VideoUser model.
    """

    class Meta:
        """
        Meta class for User Serialize
        """

        model = VideoUser
        fields = ["id", "title_nn", "user_fk", "url", "description", "created_at"]
        read_only_fields = ["title_nn", "description"]

    def to_representation(self, instance):
        data = super(VideoUserSerializer, self).to_representation(instance)
        if data["url"]:
            pattern = r"embed\/(\w+)"
            match = re.search(pattern, data["url"])
            if match:
                data["thumbnail"] = (
                    f"https://i.ytimg.com/vi/{match.group(1)}/maxresdefault.jpg"
                )
        return data

    def validate(self, data):
        """
        Custom validation to set title and description if they are not provided.
        """
        url = data.get("url")
        if url and not data.get("title_nn"):
            video_id = get_video_id(url=url)
            if not video_id:
                raise serializers.ValidationError({"url": "Invalid youtube video url."})
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            if VideoUser.objects.filter(url=video_url).exists():
                raise serializers.ValidationError(
                    {"url": "Video with this URL already exists."}
                )

            try:
                # Modify the URL to fetch the video page instead of the embed URL
                response = requests.get(video_url)
                soup = BeautifulSoup(response.text, "html.parser")
                # Fetch YouTube title from the video page
                title_tag = soup.find("meta", property="og:title")
                if title_tag:
                    title_nn = title_tag.get("content")
                else:
                    raise serializers.ValidationError(
                        {"url": "YouTube title not found in the HTML."}
                    )

                # Fetch YouTube description from the video page
                description_tag = soup.find("meta", itemprop="description")
                if description_tag:
                    description = description_tag.get("content")
                else:
                    # YouTube videos may not have a meta description, fallback to an empty string
                    description = ""
                data["title_nn"] = title_nn
                data["description"] = description
                data["url"] = video_url
            except Exception as e:
                raise serializers.ValidationError({"url": str(e)})
        return data
