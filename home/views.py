from django.shortcuts import render, get_object_or_404
from orders.models import Order
from profiles.models import Client
from profiles.views import profile


# Create your views here.
def index(request):
    """ A view to return the index page and show  images  """
    
    if request.user.is_authenticated:
        client = get_object_or_404(Client, user=request.user)
        if request.user.is_superuser:
            orders = Order.objects.all()
        else: 
            orders = client.orders.all()
    else:
        orders = Order.objects.filter(is_processed=True)
        
    context = {
        'orders': orders,
    }
    return render(request, 'home/index.html', context)