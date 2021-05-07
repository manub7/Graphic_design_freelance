from django.shortcuts import render
from products.models import Product


# Create your views here.
def index(request):
    """ A view to return the index page and first 8 products  """
    products = Product.objects.all()
    
    context = {
        'products': products,
    }
    return render(request, 'home/index.html', context)