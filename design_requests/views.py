from django.shortcuts import render
from decimal import Decimal
from django.conf import settings

# Create your views here.
def design_requests(request):
    
     price = 0
     width = 0 
     height = 0 
     size= 0 
    
     if 'width' in request.POST:
         width = request.POST['width']
     if 'height' in request.POST:
         height = request.POST['height']
     
     size = width*height/1024

     price = size * settings.PRICE_FACTOR

    context = {
        'price': price,
        'width': width,
        'height': height,
        'size':size,
        'price_factor':settings.PRICE_FACTOR,
    }
    
    return render(request, 'design_requests/design_requests.html',  )