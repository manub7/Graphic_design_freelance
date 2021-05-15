from django.shortcuts import render
from orders.models import Order


# Create your views here.
def index(request):
    """ A view to return the index page and first 8 products  """
    orders = Order.objects.all()
    
    context = {
        'orders': orders,
    }
    return render(request, 'home/index.html', context)