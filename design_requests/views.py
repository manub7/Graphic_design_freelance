from django.shortcuts import render, get_object_or_404, redirect, reverse
from decimal import Decimal
from django.conf import settings
from .models import DesignRequest, Category
from profiles.models import Client
from .forms import OrderFormDesignRequest, OrderFormCheckOut
from orders.models import Order
import json


# def design_requests(request, item_id):
# """ A view that renders the design requests page """
# return render(request, 'design_requests/design_requests.html', context )

# A view to create, calculate and capture a design request

def add_design_requests(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        form = OrderFormDesignRequest(request.POST, request.FILES)

        if form.is_valid():
            design_request = form.save()
            design_request.save()
            #messages.success(request, 'Successfully added product!')
            return redirect(reverse('design_request_checkout', args=[design_request.id]))
        # else:
           # messages.error(request, 'Failed to add product. Please ensure the form is valid.')
    else:
        form = OrderFormDesignRequest()

    context = {
        'form': form,
        'categories': categories,
        'price_factor':settings.PRICE_FACTOR,
    }

    return render(request, 'design_requests/design_requests.html', context)


def design_request_detail(request, design_request_id):

    design_request = get_object_or_404(DesignRequest, pk=design_request_id)
    design_request_form =  OrderFormDesignRequest(instance=design_request)

    context = {
        'design_request_form': design_request_form,
    }
    return render(request, 'design_requests/design_request_detail.html', context)


def design_request_checkout(request, design_request_id):
    
    design_request = get_object_or_404(DesignRequest, pk=design_request_id)
    if request.method == "POST":
        client = Client.objects.get(user=request.user)
        order_form = OrderFormCheckOut(request.POST)
        if order_form.is_valid():
           order = order_form.save()
           order.design_request = design_request
           order.client = client
           order.price = design_request.price
           order.save()
            #return redirect(reverse(''))
    else:
        order_form = OrderFormCheckOut()

    context = {
        'design_request': design_request,
        'order_form': order_form,
        'stripe_public_key':'pk_test_51IN1mAKgBHROkVrvsSTn1p7xjOP81z6uMSF1OhloutXVKTZHZfvEl7XAgw4LjXr28y1nSnoWe76fcsDAhdYepvoR000dTwA9qG',
        'client_secret': 'test client secret',
    }

    return render(request, 'design_requests/design_request_checkout.html', context)
