from django.shortcuts import render
from decimal import Decimal
from django.conf import settings
from products.models import Category, Product

<<<<<<< HEAD
<<<<<<< HEAD

# Create your views here.

# A view to create, calculate and capture a design request


# Create your views here.

=======
# Create your views here.
>>>>>>> parent of 3b3750f ( Fixed the jquery on the request design page and moved al js in the include folder)
=======
# Create your views here.
>>>>>>> parent of 3b3750f ( Fixed the jquery on the request design page and moved al js in the include folder)
def design_requests(request):
    
    price = 0
    width = 0 
    height = 0 
    size= 0 
    
    if 'width' in request.POST:
         width = request.POST['width']
<<<<<<< HEAD
<<<<<<< HEAD

=======
>>>>>>> parent of 3b3750f ( Fixed the jquery on the request design page and moved al js in the include folder)
=======
>>>>>>> parent of 3b3750f ( Fixed the jquery on the request design page and moved al js in the include folder)
         print(width)
    if 'height' in request.POST:
         height = request.POST['height']
         print(height)
     
    size = int(width) * int(height)*3/1024
    print(size)

    price = size * settings.PRICE_FACTOR
    print(price)
<<<<<<< HEAD
<<<<<<< HEAD

         print(width)

    if 'height' in request.POST:
         height = request.POST['height']
         print(height)
     
    size = int(width) * int(height)*3/1024

    price = format(size * settings.PRICE_FACTOR,".2f")


    print(size)

    price = size * settings.PRICE_FACTOR
    print(price)

=======
>>>>>>> parent of 3b3750f ( Fixed the jquery on the request design page and moved al js in the include folder)
=======
>>>>>>> parent of 3b3750f ( Fixed the jquery on the request design page and moved al js in the include folder)
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