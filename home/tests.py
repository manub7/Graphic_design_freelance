from django.test import TestCase
from django.urls import reverse

from design_requests.models import DesignRequest, Category
from profiles.models import Client
from django.contrib.auth.models import User


class HomeIndexViewTests(TestCase):

    def setUp(self):
        self.category = Category.objects.create(name='Logo')
        user = User.objects.create_user(username='client_user', password='pw12345')
        self.owned_client = Client.objects.get(user=user)

    def test_shows_public_processed_design_requests(self):
        public = DesignRequest.objects.create(
            name='Public Portfolio Item', height=100, width=100,
            description='desc', category=self.category,
            is_processed=True, client=None,
        )
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(public, response.context['design_requests'])

    def test_hides_unprocessed_design_requests(self):
        unprocessed = DesignRequest.objects.create(
            name='Unprocessed Item', height=100, width=100,
            description='desc', category=self.category,
            is_processed=False, client=None,
        )
        response = self.client.get(reverse('home'))
        self.assertNotIn(unprocessed, response.context['design_requests'])

    def test_hides_client_owned_design_requests(self):
        owned = DesignRequest.objects.create(
            name='Private Item', height=100, width=100,
            description='desc', category=self.category,
            is_processed=True, client=self.owned_client,
        )
        response = self.client.get(reverse('home'))
        self.assertNotIn(owned, response.context['design_requests'])
