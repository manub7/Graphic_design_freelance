from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.db.models.functions import Lower
from .models import Order
from design_requests.models import DesignRequest, Category
from django.conf import settings


# Create your views here.
def all_orders(request):
    """ A view to show all projects in the portofolie including sorting and search queries  """
    design_requests = DesignRequest.objects.all()
    orders = Order.objects.all()

    query = None
    categories = None
    sort = None
    direction = None
    
    if request.GET:
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'name':
                sortkey = 'lower_name'
                orders = orders.annotate(lower_name=Lower('name'))
            if sortkey == 'category':
                sortkey = 'category__name'
            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            design_requests = design_requests.order_by(sortkey) 
        
        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            design_requests = design_requests.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query :
                messages.error(request, " You didn't enter any search criteria!")
                return redirect(reverse('products'))

            queries = Q(name__icontains=query) | Q(description__icontains=query)
            design_requests = design_requests.filter(queries)

    current_sorting = f'{sort}_{direction}'

    context = {
        'orders': orders,
        'design_requests':design_requests,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
    }
    return render(request, 'orders/orders.html', context)



def order_detail(request, design_request_id):

    """ A view to show the individual product detail  """
    order = get_object_or_404(DesignRequest, design_request=design_request_id)
    #order = Order.objects.prefetch_related(
    #    Prefetch('design_request', queryset=DesignRequest.objects.filter(id_contains=design_request_id))).all()
   
    #print(order)
    context = {
            'order': order,
        }

    return render(request, 'orders/order_detail.html', context)