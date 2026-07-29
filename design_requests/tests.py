import json
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from orders.models import Order
from profiles.models import Client
from .models import DesignRequest, Category
from .forms import OrderFormDesignRequest, OrderFormDesignRequestSuser, OrderFormCheckOut
from .webhook_handler import StripeWH_handler


class StripeObject(dict):
    """Minimal stand-in for Stripe's dict-with-attribute-access objects.
    webhook_handler.py relies on both styles (e.g. `.address.items()` and
    `.address.country`, plus item assignment)."""
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value


def make_design_request(client=None, **kwargs):
    defaults = dict(
        name='Test Request', height=100, width=100, description='desc',
    )
    defaults.update(kwargs)
    return DesignRequest.objects.create(client=client, **defaults)


class CategoryModelTests(TestCase):

    def test_str_returns_name(self):
        category = Category.objects.create(name='Logo')
        self.assertEqual(str(category), 'Logo')


class DesignRequestModelTests(TestCase):

    def test_save_computes_size_and_price(self):
        design_request = make_design_request(height=100, width=100)
        # size = int(width) * int(height) * 3 / 1024
        expected_size = int(100 * 100 * 3 / 1024)
        self.assertEqual(int(design_request.size), expected_size)
        expected_price = int(expected_size) * 27 / 1000
        self.assertAlmostEqual(float(design_request.price), expected_price, places=2)


class DesignRequestFormsTests(TestCase):
    """Regression tests: both forms used to be broken by copy-paste mistakes
    (a queryset assigned over the 'category' field, and a trailing comma
    turning 'processed_image' into a 1-tuple) that raised AttributeError the
    moment the form was instantiated."""

    def test_order_form_design_request_instantiates(self):
        form = OrderFormDesignRequest()
        self.assertIn('category', form.fields)
        self.assertTrue(hasattr(form.fields['category'], 'widget'))

    def test_order_form_design_request_suser_instantiates(self):
        form = OrderFormDesignRequestSuser()
        self.assertTrue(hasattr(form.fields['processed_image'], 'widget'))

    def test_order_form_checkout_valid(self):
        form = OrderFormCheckOut(data={
            'full_name': 'Jane Doe',
            'phone_number': '01234567890',
            'street_address1': '1 Main St',
            'street_address2': '',
            'town_or_city': 'London',
            'county': 'Greater London',
            'postcode': 'AB1 2CD',
            'country': 'GB',
        })
        self.assertTrue(form.is_valid())


class DesignRequestContextProcessorTests(TestCase):

    def test_anonymous_user_sees_zero_uncomplete(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.context['uncomplete_items'], 0)
        self.assertFalse(response.context['uncomplete_requests_bool'])

    def test_owner_sees_only_own_uncomplete_requests(self):
        user = User.objects.create_user(username='owner', password='pw12345')
        owner_client = Client.objects.get(user=user)
        other_user = User.objects.create_user(username='other', password='pw12345')
        other_client = Client.objects.get(user=other_user)

        make_design_request(client=owner_client, order_number='')
        make_design_request(client=other_client, order_number='')

        self.client.force_login(user)
        response = self.client.get(reverse('home'))
        self.assertEqual(response.context['uncomplete_items'], 1)

    def test_superuser_sees_all_uncomplete_requests(self):
        user = User.objects.create_user(username='owner2', password='pw12345')
        owner_client = Client.objects.get(user=user)
        make_design_request(client=owner_client, order_number='')
        make_design_request(client=None, order_number='')

        superuser = User.objects.create_superuser(username='admin2', password='pw12345', email='a@a.com')
        self.client.force_login(superuser)
        response = self.client.get(reverse('home'))
        self.assertEqual(response.context['uncomplete_items'], 2)


class DesignRequestListViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='listuser', password='pw12345')
        self.client_obj = Client.objects.get(user=self.user)

    def test_requires_login(self):
        response = self.client.get(reverse('design_request_list'))
        self.assertEqual(response.status_code, 302)

    def test_counts_processed_and_unprocessed_orders(self):
        processed_dr = make_design_request(client=self.client_obj, is_processed=True)
        unprocessed_dr = make_design_request(client=self.client_obj, is_processed=False)
        Order.objects.create(design_request=processed_dr, client=self.client_obj, price=10)
        Order.objects.create(design_request=unprocessed_dr, client=self.client_obj, price=10)

        self.client.force_login(self.user)
        response = self.client.get(reverse('design_request_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['processed_requests'], 1)
        self.assertEqual(response.context['unprocessed_requests'], 1)


class UpdateDesignRequestViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='owner3', password='pw12345')
        self.client_obj = Client.objects.get(user=self.user)
        self.other_user = User.objects.create_user(username='intruder3', password='pw12345')
        self.design_request = make_design_request(client=self.client_obj)

    def test_non_owner_blocked(self):
        self.client.force_login(self.other_user)
        response = self.client.get(reverse('update_design_request', args=[self.design_request.id]))
        self.assertEqual(response.status_code, 302)

    def test_owner_can_update_existing_instance(self):
        # Regression: the POST branch used to construct OrderFormDesignRequest
        # without instance=design_request, which created a *new* DesignRequest
        # instead of updating the existing one.
        self.client.force_login(self.user)
        count_before = DesignRequest.objects.count()
        response = self.client.post(
            reverse('update_design_request', args=[self.design_request.id]),
            data={
                'name': 'Updated Name',
                'height': 50,
                'width': 50,
                'description': 'updated desc',
                'provide_source_files': False,
                'is_processed': False,
            },
        )
        self.assertEqual(DesignRequest.objects.count(), count_before)
        self.design_request.refresh_from_db()
        self.assertEqual(self.design_request.name, 'Updated Name')
        self.assertEqual(response.status_code, 302)


class DeleteDesignRequestViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='owner4', password='pw12345')
        self.client_obj = Client.objects.get(user=self.user)
        self.other_user = User.objects.create_user(username='intruder4', password='pw12345')

    def test_non_owner_blocked(self):
        design_request = make_design_request(client=self.client_obj)
        self.client.force_login(self.other_user)
        response = self.client.get(reverse('delete_design_request', args=[design_request.id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(DesignRequest.objects.filter(pk=design_request.id).exists())

    def test_owner_can_delete_unordered_request(self):
        design_request = make_design_request(client=self.client_obj)
        self.client.force_login(self.user)
        response = self.client.get(reverse('delete_design_request', args=[design_request.id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(DesignRequest.objects.filter(pk=design_request.id).exists())

    def test_already_ordered_request_shows_error_without_crashing(self):
        # Regression: this used to render(request, 'template', context) - a
        # literal string instead of the `template` variable - which raised
        # TemplateDoesNotExist instead of showing the error message.
        design_request = make_design_request(client=self.client_obj, order_number='ABC123')
        self.client.force_login(self.user)
        response = self.client.get(reverse('delete_design_request', args=[design_request.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(DesignRequest.objects.filter(pk=design_request.id).exists())


class DesignRequestDetailViewsOwnershipTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='owner5', password='pw12345')
        self.client_obj = Client.objects.get(user=self.user)
        self.other_user = User.objects.create_user(username='intruder5', password='pw12345')
        self.design_request = make_design_request(client=self.client_obj)

    def test_design_request_detail_blocks_non_owner(self):
        self.client.force_login(self.other_user)
        response = self.client.get(reverse('design_request_detail', args=[self.design_request.id]))
        self.assertEqual(response.status_code, 302)

    def test_design_request_detail_allows_owner(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('design_request_detail', args=[self.design_request.id]))
        self.assertEqual(response.status_code, 200)

    def test_testimonial_blocks_non_owner(self):
        self.client.force_login(self.other_user)
        response = self.client.get(reverse('design_request_testimonial', args=[self.design_request.id]))
        self.assertEqual(response.status_code, 302)

    def test_detail_from_profile_blocks_non_owner(self):
        self.client.force_login(self.other_user)
        response = self.client.get(reverse('design_request_detail_from_profile', args=[self.design_request.id]))
        self.assertEqual(response.status_code, 302)

    def test_superuser_bypasses_ownership_checks(self):
        superuser = User.objects.create_superuser(username='admin5', password='pw12345', email='a@a.com')
        self.client.force_login(superuser)
        response = self.client.get(reverse('design_request_detail', args=[self.design_request.id]))
        self.assertEqual(response.status_code, 200)


class DesignRequestProcessRequestViewTests(TestCase):

    def setUp(self):
        self.superuser = User.objects.create_superuser(username='admin6', password='pw12345', email='a@a.com')
        self.user = User.objects.create_user(username='normal6', password='pw12345')

    def test_non_superuser_blocked(self):
        design_request = make_design_request()
        Order.objects.create(design_request=design_request, price=10)
        self.client.force_login(self.user)
        response = self.client.get(reverse('design_request_process_request', args=[design_request.id]))
        self.assertEqual(response.status_code, 302)

    def test_handles_order_with_no_client_without_crashing(self):
        # Regression: order.client can be None (FK is SET_NULL); the view used
        # to read order.client.user.email unconditionally.
        design_request = make_design_request(client=None)
        Order.objects.create(design_request=design_request, client=None, price=10)
        self.client.force_login(self.superuser)
        response = self.client.post(
            reverse('design_request_process_request', args=[design_request.id]),
            data={
                'category': '', 'name': design_request.name, 'height': 100, 'width': 100,
                'description': 'desc', 'provide_source_files': False,
                'is_processed': True, 'testimonial': '',
            },
        )
        self.assertEqual(response.status_code, 302)


class DesignRequestCheckoutViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='checkoutuser', password='pw12345')
        self.client_obj = Client.objects.get(user=self.user)
        self.design_request = make_design_request(client=self.client_obj)

    def test_requires_login(self):
        response = self.client.get(reverse('design_request_checkout', args=[self.design_request.id]))
        self.assertEqual(response.status_code, 302)

    @patch('design_requests.views.stripe.PaymentIntent.create')
    def test_get_renders_checkout_page(self, mock_create):
        mock_create.return_value = SimpleNamespace(client_secret='secret_test_123')
        self.client.force_login(self.user)
        response = self.client.get(reverse('design_request_checkout', args=[self.design_request.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('stripe_price', response.context)

    @patch('design_requests.views.stripe.PaymentIntent.create')
    def test_invalid_post_rerenders_without_crashing(self, mock_create):
        # Regression: stripe_price was only ever assigned in the GET/else
        # branch, so any POST that fell through to the final render (e.g. an
        # invalid form) raised UnboundLocalError.
        mock_create.return_value = SimpleNamespace(client_secret='secret_test_123')
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('design_request_checkout', args=[self.design_request.id]),
            data={
                # invalid country code -> the only Order field that isn't
                # blank=True-permissive, so this is the one way to make the
                # form genuinely invalid.
                'full_name': '', 'phone_number': '', 'country': 'ZZ',
                'postcode': '', 'town_or_city': '', 'street_address1': '',
                'street_address2': '', 'county': '',
                'client_secret': 'secret_test_123',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('stripe_price', response.context)

    def test_already_ordered_redirects_instead_of_crashing(self):
        # Regression: this used to fall through to a final render() that
        # referenced an unbound `stripe_price`.
        self.design_request.order_number = 'ALREADY-ORDERED'
        self.design_request.save()
        Order.objects.create(design_request=self.design_request, client=self.client_obj, price=10)

        self.client.force_login(self.user)
        response = self.client.post(
            reverse('design_request_checkout', args=[self.design_request.id]),
            data={'client_secret': 'secret_test_123'},
        )
        self.assertEqual(response.status_code, 302)

    @patch('design_requests.views.stripe.PaymentIntent.create')
    def test_valid_post_creates_order_and_redirects(self, mock_create):
        mock_create.return_value = SimpleNamespace(client_secret='secret_test_123')
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('design_request_checkout', args=[self.design_request.id]),
            data={
                'full_name': 'Jane Doe', 'phone_number': '01234567890',
                'country': 'GB', 'postcode': 'AB1 2CD', 'town_or_city': 'London',
                'street_address1': '1 Main St', 'street_address2': '', 'county': 'Greater London',
                'client_secret': 'secret_test_123',
                'save-info': 'on',
            },
        )
        self.assertEqual(response.status_code, 302)
        order = Order.objects.get(design_request=self.design_request)
        self.assertEqual(order.client, self.client_obj)
        self.assertIn('save_info', self.client.session)


class DesignRequestCheckoutSuccessViewTests(TestCase):

    def setUp(self):
        self.owner = User.objects.create_user(username='successowner', password='pw12345')
        self.owner_client = Client.objects.get(user=self.owner)
        self.intruder = User.objects.create_user(username='successintruder', password='pw12345')
        self.design_request = make_design_request(client=self.owner_client)

    def test_requires_login(self):
        order = Order.objects.create(design_request=self.design_request, price=10)
        response = self.client.get(reverse('design_request_checkout_success', args=[order.order_number]))
        self.assertEqual(response.status_code, 302)

    def test_attaches_client_when_order_has_none(self):
        order = Order.objects.create(design_request=self.design_request, client=None, price=10)
        self.client.force_login(self.owner)
        response = self.client.get(reverse('design_request_checkout_success', args=[order.order_number]))
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.client, self.owner_client)

    def test_blocks_non_owner_from_viewing_someone_elses_order(self):
        # Regression: this view used to unconditionally reassign order.client
        # to whichever user loaded the URL - a real IDOR/data-corruption bug.
        order = Order.objects.create(design_request=self.design_request, client=self.owner_client, price=10)
        self.client.force_login(self.intruder)
        response = self.client.get(reverse('design_request_checkout_success', args=[order.order_number]))
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.client, self.owner_client)


class CacheCheckoutDataViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='cacheuser', password='pw12345')

    def test_requires_login(self):
        response = self.client.post(reverse('cache_checkout_data'), data={'client_secret': 'secret_test_123'})
        self.assertEqual(response.status_code, 302)

    @patch('design_requests.views.stripe.PaymentIntent.modify')
    def test_stores_username_not_user_object_in_metadata(self, mock_modify):
        self.client.force_login(self.user)
        response = self.client.post(reverse('cache_checkout_data'), data={'client_secret': 'secret_test_123'})
        self.assertEqual(response.status_code, 200)
        _, kwargs = mock_modify.call_args
        self.assertEqual(kwargs['metadata']['client'], 'cacheuser')


class StripeWebhookHandlerTests(TestCase):
    """Direct unit tests of StripeWH_handler, bypassing Stripe signature
    verification (handled separately in webhooks.webhook)."""

    def setUp(self):
        user = User.objects.create_user(username='webhookuser', password='pw12345')
        self.client_obj = Client.objects.get(user=user)
        self.design_request = make_design_request(client=self.client_obj)

    def _make_intent(self, design_request_id):
        return SimpleNamespace(
            id='pi_test_123',
            metadata=SimpleNamespace(
                design_request_session=json.dumps({'design_request_id': str(design_request_id)}),
                save_info=None,
                client='webhookuser',
            ),
            shipping=SimpleNamespace(
                name='Jane Doe', phone='01234567890',
                address=StripeObject(
                    country='GB', postal_code='AB1 2CD', city='London',
                    line1='1 Main St', line2='', state='Greater London',
                ),
            ),
        )

    def _make_event(self, intent):
        # Real Stripe Event objects support both dict-style ["type"] access
        # and attribute-style .data.object access; webhook_handler.py uses
        # both, so the test double needs to as well.
        event = {'type': 'payment_intent.succeeded'}
        event = type('FakeEvent', (dict,), {})(event)
        event.data = SimpleNamespace(object=intent)
        return event

    def test_creates_order_for_correct_design_request(self):
        # Regression: the handler used to do `int(design_request_id) + 1`,
        # always attaching the order to the *next* DesignRequest by id.
        intent = self._make_intent(self.design_request.id)
        event = self._make_event(intent)
        handler = StripeWH_handler(request=MagicMock())
        response = handler.handle_payment_intent_succeeded(event)

        self.assertEqual(response.status_code, 200)
        order = Order.objects.get(stripe_pid='pi_test_123')
        self.assertEqual(order.design_request_id, self.design_request.id)

    def test_returns_200_on_duplicate_webhook_delivery(self):
        intent = self._make_intent(self.design_request.id)
        event = self._make_event(intent)
        handler = StripeWH_handler(request=MagicMock())

        first = handler.handle_payment_intent_succeeded(event)
        second = handler.handle_payment_intent_succeeded(event)

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(Order.objects.filter(stripe_pid='pi_test_123').count(), 1)
