from django.shortcuts import render
from decimal import Decimal
from django.conf import settings
from products.models import Category, Product

<<<<<<< HEAD
# Create your views here.
=======
# A view to create, calculate and capture a design request

>>>>>>> 3b3750f8b661db1e4ab50f186094dc315d01ec68
def design_requests(request):
    
    price = 0
    width = 0 
    height = 0 
    size= 0 
    
    if 'width' in request.POST:
         width = request.POST['width']
<<<<<<< HEAD
         print(width)
    if 'height' in request.POST:
         height = request.POST['height']
         print(height)
     
    size = int(width) * int(height)*3/1024
    print(size)

    price = size * settings.PRICE_FACTOR
    print(price)
=======
    if 'height' in request.POST:
         height = request.POST['height']
     
    size = int(width) * int(height)*3/1024
    price = format(size * settings.PRICE_FACTOR,".2f")
>>>>>>> 3b3750f8b661db1e4ab50f186094dc315d01ec68
    categories = Category.objects.all()

    context = {
        'price': price,
        'width': width,
        'height': height,
        'size':size,
        'price_factor':settings.PRICE_FACTOR,
        'categories': categories,
    }
    
    return render(request, 'design_requests/design_requests.html', context )