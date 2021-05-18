from django.shortcuts import render,get_object_or_404, redirect, reverse
from decimal import Decimal
from django.conf import settings
from products.models import Category, Product
from orders.models import Order , Category
from profiles.models import Client
from design_requests.forms import OrderFormDesignRequest


#def design_requests(request, item_id):
    # """ A view that renders the design requests page """ 
     # return render(request, 'design_requests/design_requests.html', context )

# A view to create, calculate and capture a design request

def add_design_requests(request):
    
    price = 0
    width = 0 
    height = 0 
    size= 0 

   

    design_request = request.session.get('design_request', {})

    print(request.session.get('design_request'))

        
    #design_request['category']  = request.POST.get('category')
    #design_request['name']  = request.POST.get('name')
    
    #if 'width' in request.POST:
    #     width = request.POST.get('width')
    #design_request['width']  = request.POST.get('width') 
     
    #if 'height' in request.POST:
    #     height = request.POST.get('height')
    #design_request['height']  = request.POST.get('height')
    #design_request['description']  = request.POST.get('description')
    #size = int(width) * int(height)*3/1024
    #design_request['size'] = size
    #price = format(size * settings.PRICE_FACTOR / 1000,".2f")
    #design_request['price'] = price

    #checked = request.POST.get("provide_source_files")
    #print(checked)

    #if (checked == None):
    #     design_request['provide_source_files'] = False
    #else:  
    #     design_request['provide_source_files'] = True

    #if 'attachements' in request.POST:
    #     design_request['img_source']  = request.FILES

    categories = Category.objects.all()

    

    if request.method == 'POST':
        client = Client.objects.get(user=request.user)
        form = OrderFormDesignRequest(request.POST, request.FILES,client)

        if form.is_valid():
            order = form.save()
            order.client = client
            order.save()
            #messages.success(request, 'Successfully added product!')
            return redirect(reverse('design_request_detail', args=[order.id]))
        #else:
           # messages.error(request, 'Failed to add product. Please ensure the form is valid.')
    else:
        form = OrderFormDesignRequest()
     
 

    context = {
         
        #'price': price,
        #'width': width,
        #'height': height,
        #'size':size,
        #'price_factor':settings.PRICE_FACTOR,
        'form':form,
        'categories': categories,
    }

    #print(request.session.get('design_request'))

    return render(request, 'design_requests/design_requests.html', context )


def design_request_detail(request,order_id):

    order = get_object_or_404(Order, pk=order_id)
    order_form = OrderFormDesignRequest(instance=order)
    context = {
        'order_form':order_form,
    }
    return render( request, 'design_requests/design_request_detail.html',context)


"""def checkout(request):

    

          #if design_request:
          
          order_data = {

            'category': design_request.category,
            'name': design_request.name,
            'description': design_request.description,
            'height': design_request.height,
            'width': design_request.width,
            'provide_source_files': design_request.provide_source_files,

          }
   
     order_form = OrderForm(order_data)

     template = 'design_requests/checkout.html'

     context = {
  
    }
          
     return render(request,template,context)"""