from django.test import TestCase
from django.urls import reverse

from design_requests.models import DesignRequest, Category
from .models import Order


class OrderModelTests(TestCase):

    def test_order_number_auto_generated(self):
        order = Order.objects.create(price=10)
        self.assertTrue(order.order_number)

    def test_order_number_not_regenerated_on_resave(self):
        order = Order.objects.create(price=10)
        original_number = order.order_number
        order.price = 20
        order.save()
        self.assertEqual(order.order_number, original_number)

    def test_str_returns_order_number(self):
        order = Order.objects.create(price=10)
        self.assertEqual(str(order), order.order_number)


class AllOrdersViewTests(TestCase):

    def setUp(self):
        self.logo = Category.objects.create(name='Logo')
        self.poster = Category.objects.create(name='Poster')
        self.a = DesignRequest.objects.create(
            name='Alpha', height=10, width=10, description='d',
            category=self.logo, is_processed=True,
        )
        self.b = DesignRequest.objects.create(
            name='Beta', height=10, width=10, description='d',
            category=self.poster, is_processed=True,
        )

    def test_lists_processed_design_requests(self):
        response = self.client.get(reverse('orders'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.a, response.context['design_requests'])
        self.assertIn(self.b, response.context['design_requests'])

    def test_sort_by_name_does_not_crash(self):
        # Regression: ?sort=name used to raise FieldError (annotated the
        # wrong queryset with a field that doesn't exist on Order).
        response = self.client.get(reverse('orders'), {'sort': 'name'})
        self.assertEqual(response.status_code, 200)
        names = [dr.name for dr in response.context['design_requests']]
        self.assertEqual(names, sorted(names))

    def test_sort_by_name_desc(self):
        response = self.client.get(reverse('orders'), {'sort': 'name', 'direction': 'desc'})
        self.assertEqual(response.status_code, 200)
        names = [dr.name for dr in response.context['design_requests']]
        self.assertEqual(names, sorted(names, reverse=True))

    def test_sort_by_category(self):
        response = self.client.get(reverse('orders'), {'sort': 'category'})
        self.assertEqual(response.status_code, 200)

    def test_filter_by_category(self):
        response = self.client.get(reverse('orders'), {'category': 'Logo'})
        self.assertIn(self.a, response.context['design_requests'])
        self.assertNotIn(self.b, response.context['design_requests'])

    def test_search_query(self):
        response = self.client.get(reverse('orders'), {'q': 'Alpha'})
        self.assertIn(self.a, response.context['design_requests'])
        self.assertNotIn(self.b, response.context['design_requests'])

    def test_empty_search_query_redirects_with_error(self):
        response = self.client.get(reverse('orders'), {'q': ''})
        self.assertRedirects(response, reverse('orders'))


class OrderDetailViewTests(TestCase):

    def test_existing_order_returns_200(self):
        design_request = DesignRequest.objects.create(
            name='Gamma', height=10, width=10, description='d', is_processed=True,
        )
        Order.objects.create(design_request=design_request, price=10)
        response = self.client.get(reverse('order_detail', args=[design_request.id]))
        self.assertEqual(response.status_code, 200)

    def test_missing_order_returns_404(self):
        design_request = DesignRequest.objects.create(
            name='Delta', height=10, width=10, description='d', is_processed=True,
        )
        response = self.client.get(reverse('order_detail', args=[design_request.id]))
        self.assertEqual(response.status_code, 404)
