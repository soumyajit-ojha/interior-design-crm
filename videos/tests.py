"""
This file contains unit tests for the application.
Each test function focuses on a particular aspect of the code,
        ensuring its expected behavior and correctness.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import Permission
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from rest_framework import status
from videos.serializers import VideoUserSerializer
from videos.models import VideoUser
from users.models import User


class TestUrls(TestCase):
    """
    Test class to verify the resolution of various URLs in the 'videos' app.
    """

    def test_video_users_url_resolved(self):
        """
        Tests if the URL for the VideoUser is resolved correctly.

        - Reverses the URL pattern named 'videos:video_users'.
        - Asserts that the reversed URL matches the expected '/videos:video_users' path.
        """
        url = reverse("videos:video_users")
        self.assertEqual(url, "/videos/video_users/")

    def test_video_user_url_resolved(self):
        """
        Tests if the URL for the videso user is resolved correctly with a specific primary key.
        Args:
            pk (int): The primary key of the user for the detail view.
        """
        pk = 1
        url = reverse("videos:video_user", kwargs={"pk": pk})
        expected_url = f"/videos/video_user/{pk}/"
        self.assertEqual(url, expected_url)

    def test_video_user_detail_url_resolved(self):
        """
        Tests if the URL for the video user detail is resolved correctly with a
        specific primary key.
        Args:
            pk (int): The primary key of the user for the detail view.
        """
        pk = 1
        url = reverse("videos:video_user_detail", kwargs={"pk": pk})
        expected_url = f"/videos/video_user_detail/{pk}/"
        self.assertEqual(url, expected_url)


class VideoUserModelTest(TestCase):
    """
    Test class to verify the functionality of the VideoUserModel.
    """

    @classmethod
    def setUpTestData(cls):
        test_user = User.objects.create_user(username="rahul123", password="rahul12345")
        VideoUser.objects.create(
            user_fk=test_user,
            title_nn="Hall",
            url="https://example.com/video",
            description="Hall  description",
        )

    def test_user_username_in_str_method(self):
        """
        Tests that the VideoUser __str__ method returns the associated user's username.
        """
        video_user = VideoUser.objects.get(title_nn="Hall")
        expected_username = video_user.user.username
        self.assertEqual(expected_username, str(video_user))


class VideoUserSerializerTest(TestCase):
    """
    Test class to verify the functionality of the VideoUserSerializer.
    """

    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username="rahul", email="rahul123@gmail.com", password="rahul123"
        )
        self.client_user = User.objects.create_user(
            username="client123", email="client@gamil.com", password="client123"
        )
        permission = Permission.objects.get(codename="add_videouser")
        self.admin_user.user_permissions.add(permission)
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin_user)

    def test_create_video_user(self):
        """
        Tests successful video creation with valid data.
        """
        data = {
            "user_fk": self.client_user.id,
            "title_nn": "Bed Room",
            "url": "https://example.com/new_video",
            "description": "Bed Room description",
        }
        response = self.client.post("/videos/video_users/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        video_user = VideoUser.objects.get(title_nn="Bed Room")
        self.assertEqual(video_user.user, self.client_user)
        self.assertEqual(video_user.url, "https://example.com/new_video")


class VideoUserListAPIViewTest(APITestCase):
    """
    Test class to verify the functionality of the video user list.
    """

    def setUp(self):
        self.user = User.objects.create_user(username="rahul123", password="rahul12345")
        self.client.force_authenticate(user=self.user)

    def test_get_video_users_list(self):
        """
        Tests successful retrieval of video users list for a specific user.
        """
        video_user1 = VideoUser.objects.create(
            user_fk=self.user, title_nn="Bed Room", url="http://example.com/video1"
        )
        video_user2 = VideoUser.objects.create(
            user_fk=self.user, title_nn="Kitchen", url="http://example.com/video2"
        )

        response = self.client.get("/videos/video_users/{}/".format(self.user.pk))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = VideoUserSerializer([video_user1, video_user2], many=True)
        self.assertEqual(response.data, serializer.data)

    def test_create_video_user(self):
        """
        Tests successful creation of a video user with valid data.
        """
        data = {
            "user_fk": self.user.pk,
            "title_nn": "Hall",
            "url": "http://example.com/new_video",
            "description": "Hall Hall",
        }

        response = self.client.post("/videos/video_users/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(
            VideoUser.objects.filter(
                title_nn="Hall", url="http://example.com/new_video"
            ).exists()
        )


class VideoUserDetailAPIViewTest(APITestCase):
    """
    Test class to verify the functionality of the video user detail.
    """

    def setUp(self):
        self.user = User.objects.create_user(username="rahul123", password="rahul12345")
        self.video_user = VideoUser.objects.create(
            user_fk=self.user, title_nn="Hall", url="https://example.com/video"
        )

        self.client.force_authenticate(user=self.user)

    def test_get_video_user_detail(self):
        """
        Tests successful retrieval of video users detail for a specific user.
        """
        response = self.client.get("/videos/video_users/{}/".format(self.video_user.pk))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = VideoUserSerializer(instance=self.video_user)
        self.assertEqual(response.data, serializer.data)

    def test_update_video_user_detail(self):
        """
        Tests successful update of a video user with valid data.
        """
        data = {
            "user_fk": self.user.pk,
            "title_nn": "Bed Room",
            "url": "https://example.com/updated_video",
            "description": "Test Video haha",
        }
        response = self.client.put(
            "/videos/video_users/{}/".format(self.video_user.pk), data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.video_user.refresh_from_db()
        self.assertEqual(self.video_user.title, "Bed Room")
        self.assertEqual(self.video_user.url, "https://example.com/updated_video")

    def test_delete_video_user_detail(self):
        """
        Tests successful deletion of a video user by the authenticated user.
        """
        response = self.client.delete(
            "/videos/video_users/{}/".format(self.video_user.pk)
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(VideoUser.objects.filter(pk=self.video_user.pk).exists())
