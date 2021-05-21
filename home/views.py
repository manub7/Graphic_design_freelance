from django.shortcuts import render, get_object_or_404
from orders.models import Order
from profiles.models import Client
from design_requests.views import DesignRequest


# Create your views here.
def index(request):
    """ A view to return the index page and show  images  """
    

    design_requests = DesignRequest.objects.filter(is_processed=True)
        
    context = {
        'design_requests': design_requests,
    }
    return render(request, 'home/index.html', context)