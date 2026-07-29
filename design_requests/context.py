from decimal import Decimal
from django.conf import settings
from .models import DesignRequest, Category
from profiles.models import Client


def design_requests_contents(request):

    uncomplete_items = 0

    if request.user.is_authenticated:
        # Runs on every page for logged-in users. Use get_or_create so a user
        # without a Client row (e.g. created via Google sign-in or before the
        # profile signal existed) never triggers a site-wide 404/500.
        client, _ = Client.objects.get_or_create(user=request.user)
        if request.user.is_superuser:
            uncomplete_items = DesignRequest.objects.filter(order_number__exact='').count()
        else:
            uncomplete_items = DesignRequest.objects.filter(order_number__exact='', client=client).count()

    context = {
        'uncomplete_items': uncomplete_items,
        'uncomplete_requests_bool': uncomplete_items > 0,
    }

    return context
