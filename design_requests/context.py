from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from .models import DesignRequest, Category
from profiles.models import Client


def design_requests_contents(request):
    
    uncomplete_requests_bool = False
    design_request_list_uncomplete = []
    uncomplete_items = 0
    design_requests = DesignRequest.objects.all
    if request.user.is_authenticated:
        client = get_object_or_404(Client, user=request.user)
        design_requests = DesignRequest.objects.all()
        if request.user.is_superuser:
            
            design_requests = design_requests.filter(order_number__exact='')
            uncomplete_items = design_requests.count()
        else: 
            design_requests = design_requests.filter(order_number__exact='', client = client)
            design_request_list_uncomplete.append(design_requests)
            uncomplete_items = design_requests.count()
            
    else: 
        design_requests = DesignRequest.objects.all

    if (   uncomplete_items  > 0 ):
            uncomplete_requests_bool = True
    else : 
             uncomplete_requests_bool = False


    context = {
        'design_request_list_uncomplete' : design_request_list_uncomplete,
        'uncomplete_items':uncomplete_items,
        'uncomplete_requests_bool':uncomplete_requests_bool,
    }

    return context