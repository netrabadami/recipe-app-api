from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag
from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):
    """Test the publicly availabe tags API"""

    def setUp(self):
        self.client = APIClient()

    # def test_login_required(self):
    #     """Test that login is required for retrieving tags"""
    #     res = self.client.get(TAGS_URL)

    #     self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTest(TestCase):
    """Test the authorized user tags API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'tag@test.com',
            'tag123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieving_tags(self):
        """Test retrieving tags"""
        # DB query to insert data into Tag model
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)

        # Query Tag model to retrieve the tags in reverse
        # and store response in the tags variable
        tags = Tag.objects.all().order_by('-name')
        tag_serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, tag_serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tags are returned to authenticated user"""
        self.user2 = get_user_model().objects.create_user(
            'other@test.com',
            'other123'
        )
        Tag.objects.create(user=self.user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='comfort food')

        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)