from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from design_requests.models import DesignRequest
from orders.models import Order
from .models import Client
from .forms import ClientForm


def make_order(client_obj, **kwargs):
    design_request = DesignRequest.objects.create(
        name='Test Request', height=100, width=100, description='desc', client=client_obj,
    )
    return Order.objects.create(design_request=design_request, client=client_obj, price=10, **kwargs)


class ClientModelTests(TestCase):

    def test_client_auto_created_on_user_creation(self):
        user = User.objects.create_user(username='alice', password='pw12345')
        self.assertTrue(Client.objects.filter(user=user).exists())

    def test_client_str_returns_username(self):
        user = User.objects.create_user(username='bob', password='pw12345')
        client = Client.objects.get(user=user)
        self.assertEqual(str(client), 'bob')


class ClientFormTests(TestCase):

    def test_valid_data(self):
        form = ClientForm(data={
            'default_full_name': 'Jane Doe',
            'default_phone_number': '01234567890',
            'default_street_address1': '1 Main St',
            'default_street_address2': '',
            'default_town_or_city': 'London',
            'default_county': 'Greater London',
            'default_postcode': 'AB1 2CD',
            'default_country': 'GB',
        })
        self.assertTrue(form.is_valid())


class ProfileViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='owner', password='pw12345')
        self.client_obj = Client.objects.get(user=self.user)
        self.other_user = User.objects.create_user(username='intruder', password='pw12345')

    def test_profile_requires_login(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('account_login'), response.url)

    def test_profile_renders_for_logged_in_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)

    def test_profile_post_updates_client(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('profile'), data={
            'default_full_name': 'Updated Name',
            'default_phone_number': '',
            'default_street_address1': '',
            'default_street_address2': '',
            'default_town_or_city': '',
            'default_county': '',
            'default_postcode': '',
            'default_country': '',
        })
        self.client_obj.refresh_from_db()
        self.assertEqual(self.client_obj.default_full_name, 'Updated Name')

    def test_order_history_requires_login(self):
        order = make_order(self.client_obj)
        response = self.client.get(reverse('order_history', args=[order.order_number]))
        self.assertEqual(response.status_code, 302)

    def test_order_history_owner_can_view(self):
        order = make_order(self.client_obj)
        self.client.force_login(self.user)
        response = self.client.get(reverse('order_history', args=[order.order_number]))
        self.assertEqual(response.status_code, 200)

    def test_order_history_blocks_non_owner(self):
        order = make_order(self.client_obj)
        self.client.force_login(self.other_user)
        response = self.client.get(reverse('order_history', args=[order.order_number]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('profile'))

    def test_order_history_superuser_can_view_any(self):
        order = make_order(self.client_obj)
        superuser = User.objects.create_superuser(username='admin', password='pw12345', email='a@a.com')
        self.client.force_login(superuser)
        response = self.client.get(reverse('order_history', args=[order.order_number]))
        self.assertEqual(response.status_code, 200)
