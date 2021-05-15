from decimal import Decimal
from django.conf import settings

def design_request_context(request):
    
    design_request = []
    size = 0
    price = 0

    context = {
    'design_request' : design_request,
    'size ' : size ,
    'price ' : price, 
    }

    return context