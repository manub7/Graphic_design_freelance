from django.shortcuts import render
from decimal import Decimal
from django.conf import settings

# Create your views here.
def design_requests(request):
    
    context = {}
    
    return render(request, 'design_requests/design_requests.html',  )