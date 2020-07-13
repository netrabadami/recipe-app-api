from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer


INGREDIENT_URL = reverse('recipe:ingredient-list')


class PublicIngredientsApiTest(TestCase):
    """Test the publicaly available API"""

    def setUp(self):
        self.client = APIClient()

    # def test_login_required(self):
    #     """Test that the login is required for retrieving ingredients"""

    #     res = self.client.get(INGREDIENT_URL)
    #     # res.status_code = 401
    #     self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTest(TestCase):
    """Test the authorized user ingredients API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'newuser@test.com',
            'newuser'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieving_ingredient_list(self):
        """Test retrieving ingredient list"""
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Salt')

        res = self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        ingredient_serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, ingredient_serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that the ingredients are returned to authenticated user"""
        user2 = get_user_model().objects.create_user(
            'user3@test.com',
            'somepass'
        )

        Ingredient.objects.create(user=user2, name='Broccoli')
        ingredient = Ingredient.objects.create(user=self.user, name='Sugar')

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_success(self):
        """Create a new ingredient"""
        payload = {'name': 'New Ingredient'}
        self.client.post(INGREDIENT_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """Test creating ingredient with invalid payload"""
        payload = {'name': ''}

        res = self.client.post(INGREDIENT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)



